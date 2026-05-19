"""
ocr_parser.py — FarmSense AI
Extracts soil parameter values (N, P, K, pH, OC) from uploaded soil lab reports.
Supports: PDF (via pdfplumber), JPG/PNG (via pytesseract + PIL).

Usage:
    from ocr_parser import parse_soil_report
    result = parse_soil_report(file_bytes, "application/pdf")
"""

import re
import io
import logging

logger = logging.getLogger("ocr_parser")

# ─── Regex patterns for common soil lab report formats ────────────────────────
NUMBER_RE = r"([-+]?\d+(?:\.\d+)?)"
SEPARATOR_RE = r"[\s:;=\-|()\[\]/,]*"

FIELD_ALIASES = {
    "nitrogen": [
        r"available\s+nitrogen",
        r"nitrogen",
        r"ammoniacal\s+nitrogen",
        r"ammonical\s+nitrogen",
        r"nitrate\s+nitrogen",
        r"nitrate",
        r"(?<![a-z])n(?![a-z])",
    ],
    "phosphorus": [
        r"available\s+phosphorus",
        r"phosphorus",
        r"phosphorous",
        r"phosphate",
        r"p2\s*o5",
        r"p2o5",
        r"(?<![a-z])p(?!h)(?![a-z])",
    ],
    "potassium": [
        r"available\s+potassium",
        r"potassium",
        r"potash",
        r"k2\s*o",
        r"k2o",
        r"(?<![a-z])k(?![a-z])",
    ],
    "ph": [
        r"soil\s+ph",
        r"ph\s+value",
        r"reaction",
        r"(?<![a-z])ph(?![a-z])",
    ],
    "organic_carbon": [
        r"soil\s+organic\s+carbon",
        r"organic\s+carbon",
        r"organic\s+matter",
        r"(?<![a-z])soc(?![a-z])",
        r"(?<![a-z])oc(?![a-z])",
    ],
    "electrical_conductivity": [
        r"electrical\s+conductivity",
        r"elect\.?\s+conductivity",
        r"electric\s+conductivity",
        r"conductivity",
        r"salinity",
        r"(?<![a-z])ec(?![a-z])",
    ],
}

FIELD_RANGES = {
    "nitrogen": (0, 140),
    "phosphorus": (0, 145),
    "potassium": (0, 205),
    "ph": (3.0, 10.0),
    "organic_carbon": (0.0, 5.0),
    "electrical_conductivity": (0.0, 8.0),
}

# Conversion factors: some reports give values in kg/ha; model expects mg/kg
KG_HA_TO_MG_KG = 1.0 / 1.33  # approximate (varies by bulk density)


def _normalize_text(text: str) -> str:
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u00a0": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _lines(text: str) -> list[str]:
    normalized = _normalize_text(text)
    rows = []
    for raw_line in normalized.splitlines():
        line = re.sub(r"[|,\t]+", " ", raw_line)
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            rows.append(line)
    return rows


def _find_field(line: str) -> tuple[str | None, re.Match | None]:
    lower = line.lower()
    candidates = []
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            match = re.search(alias, lower, re.IGNORECASE)
            if match:
                candidates.append((match.start(), -(match.end() - match.start()), field, match))
    if not candidates:
        return None, None
    _, _, field, match = sorted(candidates, key=lambda item: (item[0], item[1], item[2]))[0]
    return field, match


def _find_fields_in_line(line: str) -> list[tuple[str, re.Match]]:
    lower = line.lower()
    candidates = []
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            for match in re.finditer(alias, lower, re.IGNORECASE):
                candidates.append((match.start(), -(match.end() - match.start()), field, match))

    fields = []
    used = set()
    for _, _, field, match in sorted(candidates, key=lambda item: (item[0], item[1], item[2])):
        span = match.span()
        if any(not (span[1] <= used_span[0] or span[0] >= used_span[1]) for used_span in used):
            continue
        if field not in [item[0] for item in fields]:
            used.add(span)
            fields.append((field, match))
    return fields


def _numbers(text: str) -> list[float]:
    values = []
    for match in re.finditer(NUMBER_RE, text):
        try:
            values.append(float(match.group(1)))
        except ValueError:
            continue
    return values


def _first_number(text: str) -> float | None:
    match = re.search(NUMBER_RE, text)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _normalize_value(field: str, value: float, context: str) -> float:
    context_lower = context.lower()
    if field in {"nitrogen", "phosphorus", "potassium"} and "kg/ha" in context_lower:
        value = value * KG_HA_TO_MG_KG
    lo, hi = FIELD_RANGES[field]
    return round(max(lo, min(hi, value)), 2)


def _extract_values_from_text(text: str) -> dict:
    """Parse raw OCR/text and extract soil parameter values from prose or tables."""
    rows = _lines(text)
    result = {}

    # Same-line extraction, e.g. "P: 38 kg/ha", "Phosphorus 42", "pH value 6.8".
    for line in rows:
        field, match = _find_field(line)
        if not field or field in result:
            continue

        after_label = line[match.end():]
        value = _first_number(after_label)
        if value is None:
            # Some tables write value before label, e.g. "42 Phosphorus".
            before_label = line[:match.start()]
            value = _first_number(before_label)
        if value is not None:
            result[field] = _normalize_value(field, value, line)

    # Split-line extraction, e.g. a label row followed by a value row.
    for idx, line in enumerate(rows[:-1]):
        field, match = _find_field(line)
        if not field or field in result:
            continue
        if _first_number(line[match.end():]) is not None:
            continue
        value = _first_number(rows[idx + 1])
        if value is not None:
            result[field] = _normalize_value(field, value, f"{line} {rows[idx + 1]}")

    # Header/value table extraction, e.g. "N P K pH OC EC" then "60 40 50 6.8 0.5 0.3".
    for idx, line in enumerate(rows[:-1]):
        fields = _find_fields_in_line(line)
        if len(fields) < 2:
            continue
        values = _numbers(rows[idx + 1])
        if len(values) < len(fields):
            continue
        context = f"{line} {rows[idx + 1]}"
        for (field, _), value in zip(fields, values):
            if field not in result:
                result[field] = _normalize_value(field, value, context)

    # Whole-text fallback for compact OCR output with missing line breaks.
    compact = " ".join(rows)
    for field, aliases in FIELD_ALIASES.items():
        if field in result:
            continue
        for alias in aliases:
            pattern = rf"{alias}{SEPARATOR_RE}{NUMBER_RE}"
            match = re.search(pattern, compact, re.IGNORECASE)
            if match:
                result[field] = _normalize_value(field, float(match.group(1)), compact[max(0, match.start()-30):match.end()+30])
                break

    return result


def _parse_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pdfplumber."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            texts = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    texts.append(text)
                for table in page.extract_tables() or []:
                    for row in table:
                        cells = [str(cell).strip() for cell in row if cell]
                        if cells:
                            texts.append(" | ".join(cells))
            return "\n".join(texts)
    except ImportError:
        logger.warning("pdfplumber not installed; PDF parsing unavailable")
        return ""
    except Exception as e:
        logger.error(f"PDF parsing failed: {e}")
        return ""


def _parse_image(file_bytes: bytes) -> str:
    """Extract text from image using pytesseract OCR."""
    try:
        import pytesseract
        from PIL import Image, ImageFilter, ImageEnhance

        img = Image.open(io.BytesIO(file_bytes)).convert("L")  # Grayscale

        # Preprocessing for better OCR accuracy
        img = img.filter(ImageFilter.MedianFilter(size=3))
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        # Upscale small images
        if img.width < 1000:
            scale = 1000 / img.width
            img = img.resize((int(img.width * scale), int(img.height * scale)))

        threshold = img.point(lambda p: 255 if p > 175 else 0)
        texts = [
            pytesseract.image_to_string(img, config="--psm 6"),
            pytesseract.image_to_string(threshold, config="--psm 6"),
            pytesseract.image_to_string(threshold, config="--psm 11"),
        ]
        seen = set()
        clean = []
        for text in texts:
            for line in text.splitlines():
                line_key = re.sub(r"\s+", " ", line).strip()
                if line_key and line_key.lower() not in seen:
                    seen.add(line_key.lower())
                    clean.append(line)
        return "\n".join(clean)
    except ImportError:
        logger.warning("pytesseract or Pillow not installed; image OCR unavailable")
        return ""
    except Exception as e:
        logger.error(f"Image OCR failed: {e}")
        return ""


def parse_soil_report(file_bytes: bytes, mime_type: str) -> dict:
    """
    Main entry point. Accepts file bytes and MIME type.
    Returns dict with extracted soil values and extraction confidence.

    Returns:
        {
            "extracted": dict with detected soil values,
            "raw_text": str,       # for debugging
            "confidence": "high" | "medium" | "low",
            "message": str,
        }
    """
    raw_text = ""

    if mime_type == "application/pdf":
        raw_text = _parse_pdf(file_bytes)
    elif mime_type in ("image/jpeg", "image/jpg", "image/png", "image/webp"):
        raw_text = _parse_image(file_bytes)
    else:
        return {
            "extracted": {},
            "raw_text": "",
            "confidence": "low",
            "message": f"Unsupported file format: {mime_type}",
        }

    if not raw_text.strip():
        return {
            "extracted": {},
            "raw_text": "",
            "confidence": "low",
            "message": "Could not extract text from the file. Please ensure the file is a clear, text-based soil report.",
        }

    extracted = _extract_values_from_text(raw_text)

    found = len(extracted)
    if found >= 4:
        confidence = "high"
        message = f"Successfully extracted {found} soil parameters from your report."
    elif found >= 2:
        confidence = "medium"
        message = f"Partially extracted {found} parameters. Please verify and fill in the missing values manually."
    else:
        confidence = "low"
        message = "Could not reliably extract soil values. Please enter values manually from your report."

    return {
        "extracted": extracted,
        "raw_text": raw_text[:2000],  # truncate for response
        "confidence": confidence,
        "message": message,
    }

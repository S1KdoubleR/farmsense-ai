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
from typing import Optional

logger = logging.getLogger("ocr_parser")

# ─── Regex patterns for common soil lab report formats ────────────────────────
PATTERNS = {
    "nitrogen": [
        r"(?:available\s+)?nitrogen\s*[:\-=]?\s*(\d+\.?\d*)\s*(?:kg/ha|mg/kg|ppm|%)?",
        r"\bN\b\s*[:\-=]\s*(\d+\.?\d*)",
        r"nitrate?\s*[:\-=]?\s*(\d+\.?\d*)",
        r"(?:N|ammonical\s+nitrogen)\s*content\s*[:\-=]?\s*(\d+\.?\d*)",
    ],
    "phosphorus": [
        r"(?:available\s+)?phosphorus\s*[:\-=]?\s*(\d+\.?\d*)\s*(?:kg/ha|mg/kg|ppm|%)?",
        r"\bP\b\s*[:\-=]\s*(\d+\.?\d*)",
        r"phosphate?\s*[:\-=]?\s*(\d+\.?\d*)",
        r"P2O5\s*[:\-=]?\s*(\d+\.?\d*)",
    ],
    "potassium": [
        r"(?:available\s+)?potassium\s*[:\-=]?\s*(\d+\.?\d*)\s*(?:kg/ha|mg/kg|ppm|%)?",
        r"\bK\b\s*[:\-=]\s*(\d+\.?\d*)",
        r"potash\s*[:\-=]?\s*(\d+\.?\d*)",
        r"K2O\s*[:\-=]?\s*(\d+\.?\d*)",
    ],
    "ph": [
        r"(?:soil\s+)?pH\s*[:\-=]?\s*(\d+\.?\d*)",
        r"pH\s*value\s*[:\-=]?\s*(\d+\.?\d*)",
        r"reaction\s*[:\-=]?\s*(\d+\.?\d*)",
    ],
    "organic_carbon": [
        r"(?:soil\s+)?organic\s+carbon\s*[:\-=]?\s*(\d+\.?\d*)\s*%?",
        r"OC\s*[:\-=]?\s*(\d+\.?\d*)",
        r"organic\s+matter\s*[:\-=]?\s*(\d+\.?\d*)",
        r"SOC\s*[:\-=]?\s*(\d+\.?\d*)",
    ],
}

# Conversion factors: some reports give values in kg/ha; model expects mg/kg
KG_HA_TO_MG_KG = 1.0 / 1.33  # approximate (varies by bulk density)


def _extract_values_from_text(text: str) -> dict:
    """Parse raw text and extract soil parameter values using regex."""
    text_lower = text.lower()
    result = {}

    for param, patterns in PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    val = float(match.group(1))
                    # Convert kg/ha values if units detected
                    if "kg/ha" in text_lower[max(0, match.start()-20):match.end()+20]:
                        val = val * KG_HA_TO_MG_KG
                    result[param] = round(val, 2)
                    break
                except (ValueError, IndexError):
                    continue

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

        text = pytesseract.image_to_string(img, config="--psm 6")
        return text
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
            "extracted": {
                "nitrogen": float | None,
                "phosphorus": float | None,
                "potassium": float | None,
                "ph": float | None,
                "organic_carbon": float | None,
            },
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

    # Clamp to valid ranges
    if "nitrogen" in extracted:
        extracted["nitrogen"] = max(0, min(140, extracted["nitrogen"]))
    if "phosphorus" in extracted:
        extracted["phosphorus"] = max(0, min(145, extracted["phosphorus"]))
    if "potassium" in extracted:
        extracted["potassium"] = max(0, min(205, extracted["potassium"]))
    if "ph" in extracted:
        extracted["ph"] = max(3.0, min(10.0, extracted["ph"]))
    if "organic_carbon" in extracted:
        extracted["organic_carbon"] = max(0.0, min(5.0, extracted["organic_carbon"]))

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

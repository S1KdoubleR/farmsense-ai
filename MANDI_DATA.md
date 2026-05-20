# FarmSense Mandi Price Data

FarmSense uses two mandi price paths:

- Live AGMARKNET/data.gov.in lookup during prediction when `DATA_GOV_API_KEY` is configured.
- A local 10-year mandi price archive at `backend/data/mandi_price_history_2016_2026.csv`.

## Archive

The archive contains monthly records from January 2016 through May 2026.

Current archive summary:

| Field | Value |
|---|---:|
| Rows | 7,000 |
| Crops | 56 |
| Granularity | Monthly |
| Price unit | INR/quintal |

Refresh it with:

```bash
cd backend
python build_mandi_price_archive.py
```

If a `DATA_GOV_API_KEY` is available, the builder uses current AGMARKNET/data.gov.in records as seed values. Without the key, it still creates a complete local archive from the project's crop market baselines.

## API Endpoints

```text
GET /market-prices?crop=tomato&state=Karnataka&district=Bengaluru%20Urban
GET /market-history
GET /market-history?crop=tomato&limit=24
```

## Deployment Env Var

Set this in the Render backend service:

```text
DATA_GOV_API_KEY=your_data_gov_api_key
```

The frontend does not need this key. Keep it only in the backend environment.

# FarmSense AI Vercel Deployment

## What Vercel will host

Vercel is best used here for the React/Vite frontend in `frontend/`.

The Python FastAPI backend should have a public URL before the deployed website can use prediction, weather, market, and OCR features. Do not use `http://localhost:8001` in Vercel because localhost means the visitor's own computer, not your backend.

## Vercel settings

When importing the project in Vercel:

| Setting | Value |
|---|---|
| Framework Preset | Vite |
| Root Directory | `frontend` |
| Install Command | `npm install` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

## Environment variable

Add this in Vercel Project Settings -> Environment Variables:

```text
VITE_API_BASE_URL=https://your-backend-url
```

Replace `https://your-backend-url` with the deployed FastAPI backend URL.

For local development, the frontend still defaults to:

```text
http://localhost:8001
```

## Deployment steps

1. Push the project to GitHub.
2. Go to Vercel and choose Add New -> Project.
3. Import the GitHub repository.
4. Set Root Directory to `frontend`.
5. Confirm the Vite settings shown above.
6. Add `VITE_API_BASE_URL` if the backend is hosted publicly.
7. Click Deploy.

## Backend note

The current backend uses FastAPI, scikit-learn model files, OCR libraries, and Python dependencies. It is better hosted as a separate backend service and then connected to the Vercel frontend through `VITE_API_BASE_URL`.

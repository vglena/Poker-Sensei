# Hugging Face Spaces backend deploy

This repo is ready to use as a free, no-card backend deployment on Hugging Face Spaces.

Why this path:
- Spaces offers a free CPU Basic option.
- Docker Spaces can run FastAPI directly.
- No payment card is required for the free CPU Basic path.

## What to deploy

Deploy the backend from the repo root using the top-level `Dockerfile`.

The container starts FastAPI on port `7860`, which is the default Space port.

## Steps

1. Create a new Hugging Face Space.
2. Choose `Docker` as the SDK.
3. Set visibility to `Public`.
4. Push or upload this repository contents to the Space.
5. Open `Settings` for the Space and add variables if needed:
   - `CORS_ORIGINS` = your Netlify URL, plus local dev URLs if you still use them.
6. Wait for the rebuild to finish.

## Frontend configuration

Set your frontend environment variable to the Space API URL:

- `VITE_API_BASE_URL=https://<your-space-name>.hf.space/api`

Then rebuild and redeploy the frontend on Netlify.

## Notes

- Free Spaces may sleep when idle.
- The first request after sleep can be slow.
- Session logs are written inside the container filesystem, so they are not persistent unless you add storage.
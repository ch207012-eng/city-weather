# Netlify Deployment Guide (Split Architecture)

This repository cannot be deployed directly to Netlify as-is because it depends on always-on Python/Kafka processes.

## Key limitations (important)

- Do **not** run Kafka producer/consumer directly on Netlify because Kafka consumers require persistent long-lived connections.
- Do **not** rely on Netlify Functions for persistent stream consumers because Netlify Functions are stateless and short-lived.

## What to deploy where

- **Netlify**: static frontend only
- **Always-on backend host (Render/Railway/Fly.io/VM)**:
  - Kafka consumer service
  - API service that exposes weather data to the frontend
- **Managed/self-hosted Kafka**: broker
- **Worker host**: weather producer process

## Recommended implementation path

1. Keep the existing services running on a Python-friendly host (web + worker).
2. Add backend API endpoints for frontend polling (e.g., hypothetical endpoints you implement like `/api/cities` and `/api/weather/latest`).
3. Build a static frontend that reads from that API.
4. Deploy that frontend to Netlify.

## Netlify setup (frontend only)

1. Push your static frontend code to your Git provider.
2. In Netlify, select **Add new site** → **Import an existing project**.
3. Connect the GitHub repo/branch.
4. Configure:
   - **Build command**: your frontend build command (if needed)
   - **Publish directory**: built static output directory
5. Add required frontend environment variables in Netlify site settings.
6. Deploy and verify the frontend can call your backend API.

## Important notes

- Keep backend API CORS configured for your Netlify domain.

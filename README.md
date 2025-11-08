# city-weather (Kafka streaming)

## Overview
Fetches live weather (temperature, precipitation, wind) for St Paul, Duluth, St Cloud, Rochester (MN) via OpenWeather API, streams via Kafka topic `city-weather`, and visualizes in a Dash app.

## Files
- `producer/producer.py` — fetches data and produces JSON messages to Kafka.
- `consumer_dashboard/app.py` — Dash app that consumes messages and displays plots.
- `docker/docker-compose.yml` — runs Zookeeper & Kafka locally.
- `.env` — local environment values (NOT COMMITTED).

## Setup (Codespaces)
1. Create `.env` with `OPENWEATHER_API_KEY`.
2. `docker-compose -f docker/docker-compose.yml up -d`
3. Create topic `city-weather` via Kafka CLI.
4. Install dependencies and run:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r producer/requirements.txt
   pip install -r consumer_dashboard/requirements.txt
   python producer/producer.py  # Terminal A
   cd consumer_dashboard && python app.py  # Terminal B

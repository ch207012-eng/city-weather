import os
import json
import time
import requests
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
TOPIC = os.getenv("KAFKA_TOPIC", "city-weather")
SECURITY_PROTOCOL = os.getenv("KAFKA_SECURITY_PROTOCOL", "SASL_SSL")
SASL_MECHANISM = os.getenv("KAFKA_SASL_MECHANISM", "PLAIN")
SASL_USERNAME = os.getenv("KAFKA_SASL_USERNAME")
SASL_PASSWORD = os.getenv("KAFKA_SASL_PASSWORD")

CITIES = {
    "Saint Paul": {"lat": 44.9537, "lon": -93.0900},
    "Duluth": {"lat": 46.7867, "lon": -92.1005},
    "Saint Cloud": {"lat": 45.5579, "lon": -94.1632},
    "Rochester": {"lat": 44.0121, "lon": -92.4802},
}

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(city, lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "imperial",  # Fahrenheit, mph
    }
    resp = requests.get(OPENWEATHER_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    temp_f = data["main"]["temp"]
    wind_mph = data["wind"].get("speed", 0.0)
    # OpenWeather current weather doesn’t always have 1h precip; use 0 if missing
    rain_1h = data.get("rain", {}).get("1h", 0.0)
    snow_1h = data.get("snow", {}).get("1h", 0.0)
    precip_1h = rain_1h + snow_1h

    return {
        "city": city,
        "timestamp": data.get("dt"),  # unix timestamp
        "temp_f": temp_f,
        "precip_in_last_1h": precip_1h,
        "wind_mph": wind_mph,
    }


def main():
    print(f"🌤 Starting weather producer, Kafka at {BOOTSTRAP}")
    if not API_KEY:
        print("❌ OPENWEATHER_API_KEY is missing in .env")
        return

    producer_kwargs = {
        "bootstrap_servers": BOOTSTRAP,
        "value_serializer": lambda v: json.dumps(v).encode("utf-8"),
    }

    if SASL_USERNAME and SASL_PASSWORD:
        producer_kwargs.update(
            {
                "security_protocol": SECURITY_PROTOCOL,
                "sasl_mechanism": SASL_MECHANISM,
                "sasl_plain_username": SASL_USERNAME,
                "sasl_plain_password": SASL_PASSWORD,
            }
        )

    producer = KafkaProducer(**producer_kwargs)

    while True:
        for city, coords in CITIES.items():
            try:
                weather = fetch_weather(city, coords["lat"], coords["lon"])
                producer.send(TOPIC, value=weather)
                print(f"✅ Sent to {TOPIC}: {weather}")
            except Exception as e:
                print(f"❌ Error fetching/sending for {city}: {e}")
        producer.flush()
        print(f"⏱ Sleeping {POLL_INTERVAL} seconds...\n")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()

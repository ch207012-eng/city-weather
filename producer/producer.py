
# producer/producer.py
import os
import time
import json
import requests
from dotenv import load_dotenv
from kafka import KafkaProducer

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))

# Using OpenWeatherMap City IDs for reliability
CITIES = [
    {"name": "Saint Paul", "id": 5045360},
    {"name": "Duluth", "id": 5024719},
    {"name": "Saint Cloud", "id": 5045021},
    {"name": "Rochester", "id": 5043473}
]

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_weather_by_id(city_id):
    url = f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={API_KEY}&units=imperial"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()

def parse_weather(json_data):
    temp = json_data.get("main", {}).get("temp")
    wind = json_data.get("wind", {}).get("speed")
    precip = 0.0
    if "rain" in json_data:
        precip = json_data.get("rain", {}).get("1h", 0.0)
    elif "snow" in json_data:
        precip = json_data.get("snow", {}).get("1h", 0.0)

    return {
        "city": json_data.get("name"),
        "temp_f": temp,
        "precip_in_last_1h": precip,
        "wind_mph": wind,
        "timestamp": int(time.time())
    }

def main():
    if API_KEY is None:
        raise SystemExit("OPENWEATHER_API_KEY not set. Add to .env or environment.")
    print("Starting weather producer. Sending to topic 'city-weather'.")
    while True:
        for city in CITIES:
            try:
                data = fetch_weather_by_id(city["id"])
                parsed = parse_weather(data)
                parsed['query_city'] = city["name"]
                producer.send("city-weather", value=parsed)
                print(f"Sent: {parsed}")
            except Exception as e:
                print(f"Error fetching/sending for {city['name']}: {e}")
        producer.flush()
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()

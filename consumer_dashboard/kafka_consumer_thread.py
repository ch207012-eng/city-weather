# consumer_dashboard/kafka_consumer_thread.py
import threading
import json
import time
import os
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

shared_store = {}
MAX_POINTS = 200

def kafka_reader():
    consumer = KafkaConsumer(
        'city-weather',
        bootstrap_servers=BOOTSTRAP,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    print("Kafka consumer thread started and listening...")
    for msg in consumer:
        data = msg.value
        city = data.get("city") or data.get("query_city", "Unknown")
        entry = {
            "timestamp": data.get("timestamp"),
            "temp": data.get("temp_f"),
            "precip": data.get("precip_in_last_1h"),
            "wind": data.get("wind_mph")
        }
        if city not in shared_store:
            shared_store[city] = []
        shared_store[city].append(entry)
        if len(shared_store[city]) > MAX_POINTS:
            shared_store[city] = shared_store[city][-MAX_POINTS:]

def start_consumer_thread():
    thread = threading.Thread(target=kafka_reader, daemon=True)
    thread.start()
    return thread

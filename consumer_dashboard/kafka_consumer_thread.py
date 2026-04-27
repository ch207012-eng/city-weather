# consumer_dashboard/kafka_consumer_thread.py
import threading
import json
import time
import os
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "city-weather")
SECURITY_PROTOCOL = os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT")
SASL_MECHANISM = os.getenv("KAFKA_SASL_MECHANISM", "PLAIN")
SASL_USERNAME = os.getenv("KAFKA_SASL_USERNAME")
SASL_PASSWORD = os.getenv("KAFKA_SASL_PASSWORD")

shared_store = {}
MAX_POINTS = 200

def kafka_reader():
    consumer_kwargs = {
        "bootstrap_servers": BOOTSTRAP,
        "auto_offset_reset": "earliest",
        "enable_auto_commit": True,
        "value_deserializer": lambda m: json.loads(m.decode("utf-8")),
    }

    if SASL_USERNAME and SASL_PASSWORD:
        consumer_kwargs.update(
            {
                "security_protocol": SECURITY_PROTOCOL,
                "sasl_mechanism": SASL_MECHANISM,
                "sasl_plain_username": SASL_USERNAME,
                "sasl_plain_password": SASL_PASSWORD,
            }
        )

    consumer = KafkaConsumer(TOPIC, **consumer_kwargs)
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

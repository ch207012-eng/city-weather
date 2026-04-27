# 🌤 City Weather – Real-Time Kafka Streaming Dashboard

A complete real-time streaming pipeline using **Apache Kafka**, **Python**, **Docker**, **OpenWeather API**, and **Dash/Plotly**.

This system fetches **live weather data** for 4 Minnesota cities, streams it into Kafka, consumes messages in real time, and displays them in a **live updating dashboard**.

---

## 📌 Cities Streamed
- Saint Paul (MN)
- Duluth (MN)
- Saint Cloud (MN)
- Rochester (MN)

---

## 🔧 Architecture Overview

```
OpenWeather API → Producer (Python) → Kafka Topic (city-weather) → Consumer Thread → Dash Web App → Live Charts
```

### Components
- `producer/producer.py` — Fetches API weather data and streams JSON messages into Kafka every few seconds  
- `docker/docker-compose.yml` — Runs **Kafka + Zookeeper**  
- `consumer_dashboard/kafka_consumer_thread.py` — Background KafkaConsumer thread  
- `consumer_dashboard/app.py` — Dash app rendering real-time graphs  

---

## 📁 Project Structure

```
city-weather/
│
├── producer/
│   ├── producer.py
│   └── requirements.txt
│
├── consumer_dashboard/
│   ├── app.py
│   ├── kafka_consumer_thread.py
│   └── requirements.txt
│
├── docker/
│   └── docker-compose.yml
│
├── .env
└── README.md
```

---

## 🧪 Environment Setup

### 1️⃣ Create `.env` file

```
export OPENWEATHER_API_KEY=YOUR_API_KEY_HERE
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=city-weather
POLL_INTERVAL_SECONDS=300
# Optional for Confluent Cloud / managed Kafka:
# KAFKA_SECURITY_PROTOCOL=SASL_SSL
# KAFKA_SASL_MECHANISM=PLAIN
# KAFKA_SASL_USERNAME=...
# KAFKA_SASL_PASSWORD=...
```

---

## 🐳 2️⃣ Start Kafka & Zookeeper

```bash
cd /workspaces/city-weather
docker-compose -f docker/docker-compose.yml up -d
docker-compose -f docker/docker-compose.yml ps
```

Expected services:

```
docker-kafka-1       Up ... 0.0.0.0:9092->9092/tcp
docker-zookeeper-1   Up ... 0.0.0.0:2181->2181/tcp
```

---

## 🌪 3️⃣ Create Kafka Topic

```bash
KAFKA_CONTAINER=$(docker ps --filter "name=kafka" -q)

docker exec $KAFKA_CONTAINER kafka-topics --create   --topic city-weather   --bootstrap-server localhost:9092   --partitions 1   --replication-factor 1

docker exec $KAFKA_CONTAINER kafka-topics --list --bootstrap-server localhost:9092
```

---

## 🐍 4️⃣ Virtual Environment & Dependencies

```bash
python -m venv .venv
source .venv/bin/activate

pip install -r producer/requirements.txt
pip install -r consumer_dashboard/requirements.txt
pip install kafka-python
pip install python-dotenv
```

---

## 🚀 5️⃣ Run Weather Producer (Terminal A)

```bash
cd producer
python producer.py
```

Expected:

```
🌤 Starting weather producer...
✅ Sent to city-weather: {...}
⏱ Sleeping 300 seconds...
```

---

## 📊 6️⃣ Run Dash Consumer Dashboard (Terminal B)

```bash
cd consumer_dashboard
python app.py
```

Expected:

```
Attempting to connect to Kafka...
✅ Kafka consumer connected!
Dash is running on http://0.0.0.0:8050
```

---

## 🌐 7️⃣ Open Dashboard (Port 8050)

In Codespaces → **PORTS tab** → click URL for **8050**:

```
https://xxxx-8050.app.github.dev
```

You will see real-time graphs updating automatically.

---

## ☁️ Production Deployment (Recommended)

This repository includes **`render.yaml`** so Render can provision both services from a single Blueprint:

- `city-weather-dashboard` (web) → runs `consumer_dashboard/app.py`
- `city-weather-producer` (worker) → runs `producer/producer.py`

### 1️⃣ Provision Confluent Cloud Kafka
- Create a Confluent Cloud cluster.
- Create topic: `city-weather` (or set your own via `KAFKA_TOPIC`).
- Create Kafka API key + secret.
- Copy the bootstrap server value.

### 2️⃣ Create Render Blueprint
- In Render, click **New + → Blueprint**.
- Select repo **`ch207012-eng/city-weather`**.
- Render detects `render.yaml` and creates both services automatically.

### 3️⃣ Set required environment variables
- **Both services**
  - `KAFKA_BOOTSTRAP_SERVERS` (Confluent bootstrap, e.g. `pkc-xxxxx.us-central1.gcp.confluent.cloud:9092`)
  - `KAFKA_SASL_USERNAME` (Confluent API key)
  - `KAFKA_SASL_PASSWORD` (Confluent API secret)
- **Worker only**
  - `OPENWEATHER_API_KEY`
- **Optional (already defaulted in `render.yaml`)**
  - `KAFKA_TOPIC=city-weather`
  - `KAFKA_SECURITY_PROTOCOL=SASL_SSL`
  - `KAFKA_SASL_MECHANISM=PLAIN`
  - `POLL_INTERVAL_SECONDS=300`

### 4️⃣ Deploy
- Click **Apply** in Render to start deployment.

### 5️⃣ Validate end-to-end
- Worker logs should show `✅ Sent to ...`.
- Open the dashboard service URL and confirm city charts update.

---

## 🎥 Demo Requirements (Assignment)

### ✔ Kafka integration  
### ✔ Producer with real-time API data  
### ✔ Consumer + Dash UI  
### ✔ 5-minute PPT presentation (provided separately)  
### ✔ Upload code + PPT + demo video  

---

## 🔮 Future Improvements

- Add time-series database storage  
- Auto-scaling Kafka partitions  
- Add humidity, pressure, storms  
- Containerize everything in one Compose stack  

---

## 🏁 Summary

This project fully implements a **real-time Kafka streaming pipeline** with:
- Live OpenWeather API ingestion  
- Kafka topic streaming  
- Python consumer  
- Dash real-time visualization  

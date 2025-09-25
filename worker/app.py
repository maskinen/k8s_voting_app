from flask import Flask
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
import os

app = Flask(__name__)
heartbeat = Gauge("worker_heartbeat", "Worker heartbeat", ["service"])

@app.get("/health")
def health(): return {"ok": True}

@app.get("/metrics")
def metrics():
    heartbeat.labels("worker").set_to_current_time()
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT","8080")))
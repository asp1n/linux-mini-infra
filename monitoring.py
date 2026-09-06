from dataclasses import dataclass
from datetime import datetime

import requests

DISK_USAGE_THRESHOLD = 80
RAM_FREE_THRESHOLD = 300


@dataclass
class Monitoring:
    hostname: str
    uptime_seconds: int
    disk_usage_percent: int
    ram_free_mb: int
    timestamp: datetime


try:
    response = requests.get("http://10.0.2.17:9090/health", timeout=5)
except requests.exceptions.ConnectionError:
    raise SystemExit(
        "WARNING: Connection error. Unable to establish a connection to the server"
    )
except requests.exceptions.ReadTimeout:
    raise SystemExit(
        "WARNING: Connection timeout. The connection was established, but the server didn't repsond in time."
    )
except requests.exceptions.Timeout:
    raise SystemExit(
        "WARNING: Connection timeout. The connection was not established in time."
    )

data = response.json()
monitoring = Monitoring(
    hostname=data["hostname"],
    uptime_seconds=data["uptime_seconds"],
    disk_usage_percent=data["disk_usage_percent"],
    ram_free_mb=data["ram_free_mb"],
    timestamp=datetime.fromisoformat(data["timestamp"]),
)

print(monitoring.timestamp.strftime("%x %X"))
if monitoring.disk_usage_percent > DISK_USAGE_THRESHOLD:
    print(
        f"CRITICAL: A disk free space is running out. Disk usage: {monitoring.disk_usage_percent}%"
    )
elif monitoring.ram_free_mb < RAM_FREE_THRESHOLD:
    print(
        f"CRITICAL: A RAM free space is running out. Remaining: {monitoring.ram_free_mb} MB"
    )
else:
    print(
        f"OK: All is good.\nDisk usage: {monitoring.disk_usage_percent}%\nRemainig RAM: {monitoring.ram_free_mb} MB"
    )

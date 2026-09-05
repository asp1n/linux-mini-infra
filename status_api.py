import json
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            payload = {
                "hostname": self.get_hostname(),
                "uptime_seconds": self.get_uptime(),
                "disk_usage_percent": self.get_disk_usage(),
                "ram_free_mb": self.get_ram_free_mb(),
                "timestamp": self.get_timestamp(),
            }
            self._send_json(200, payload)
        else:
            payload = {"error": "Not found"}
            self._send_json(404, payload)

    @staticmethod
    def get_hostname():
        return subprocess.run(
            ["hostname"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()

    @staticmethod
    def get_uptime():
        uptime_seconds = subprocess.run(
            "cat /proc/uptime | awk '{print int($1)}'",
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        return int(uptime_seconds)

    @staticmethod
    def get_disk_usage():
        disk_usage_percent = subprocess.run(
            "df -h / | tail -1 | awk '{print $5}' | tr -d '%'",
            shell=True,
            check=False,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return int(disk_usage_percent)

    @staticmethod
    def get_ram_free_mb():
        ram_free_mb = subprocess.run(
            "free | grep -v Swap | tail -1 | awk '{print $4}'",
            shell=True,
            check=False,
            text=True,
            capture_output=True,
        ).stdout.strip()
        return int(float(ram_free_mb) / 1000)

    @staticmethod
    def get_timestamp():
        return subprocess.run(
            "date --iso-8601=s",
            shell=True,
            check=False,
            text=True,
            capture_output=True,
        ).stdout.strip()


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 9090), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

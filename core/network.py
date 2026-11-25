import socket
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional


class NetworkClient:
    def __init__(self, timeout: int = 10, retries: int = 3):
        self.timeout = timeout
        self.retries = retries
        self.user_agent = "PyWatchDog-Probe/1.0"

    def probe_http(self, url: str) -> Dict[str, Any]:
        result = {
            "url": url,
            "status": None,
            "latency_ms": 0.0,
            "success": False,
            "error": None,
        }
        req = urllib.request.Request(
            url,
            headers={"User-Agent": self.user_agent},
            method="HEAD"
        )
        for attempt in range(1, self.retries + 1):
            start = time.perf_counter()
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    latency = (time.perf_counter() - start) * 1000
                    result["status"] = response.getcode()
                    result["latency_ms"] = round(latency, 2)
                    result["success"] = (200 <= response.getcode() < 400)
                    return result
            except urllib.error.HTTPError as he:
                latency = (time.perf_counter() - start) * 1000
                result["status"] = he.code
                result["latency_ms"] = round(latency, 2)
                result["error"] = str(he)
                return result
            except (urllib.error.URLError, socket.timeout) as ex:
                result["error"] = str(ex)
                if attempt == self.retries:
                    result["latency_ms"] = round((time.perf_counter() - start) * 1000, 2)
                    return result
                time.sleep(0.5)
        return result

    def probe_tcp(self, host: str, port: int) -> Dict[str, Any]:
        result = {
            "host": host,
            "port": port,
            "open": False,
            "latency_ms": 0.0,
            "error": None
        }
        start = time.perf_counter()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect((host, port))
            result["open"] = True
            result["latency_ms"] = round((time.perf_counter() - start) * 1000, 2)
        except OSError as err:
            result["error"] = str(err)
        finally:
            sock.close()
        return result

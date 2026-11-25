# Simple project configuration

APP_NAME = "PyWatchDog"
VERSION = "0.2.1"
DEFAULT_TIMEOUT = 10
LOG_FILE = "service_monitor.log"
TARGET_ENDPOINTS = [
    "https://api.github.com",
    "https://httpbin.org/status/200",
]

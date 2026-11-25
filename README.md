# PyWatchDog

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)](#)

**PyWatchDog** is a lightweight, concurrent network diagnostic and uptime probing tool designed for monitoring web services, API endpoints, and TCP sockets.

---

## Features

- **Concurrent Health Checks**: Leverages thread pooling for parallel endpoint polling.
- **Protocol Support**: Native HTTP(S) response status verification and raw TCP port availability checks.
- **Latency Tracking**: Calculates real-time round-trip latency (ms) per endpoint.
- **Multiple Output Formats**: Supports terminal table, JSON, and Markdown summaries.
- **Configurable Thresholds**: Customizable connection timeouts, retries, and worker counts.

---

## Project Structure

```text
opensource/
├── core/
│   ├── formatter.py     # Terminal table, JSON, and Markdown export engines
│   └── network.py       # HTTP probe client and TCP connection routines
├── config.py            # Global runtime configuration and defaults
├── main.py              # CLI driver and multi-threaded probe coordinator
├── requirements.txt     # Python package requirements
├── .gitignore           # Git ignore definitions
├── LICENSE              # Open-source license terms
└── README.md            # Project documentation
```

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/example/pywatchdog.git
   cd pywatchdog
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Linux/macOS:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Quick Start & Usage

### 1. Probe a Single Target
```bash
python main.py -t https://api.github.com
```

### 2. Probe a TCP Host & Port
```bash
python main.py -t 127.0.0.1:8080
```

### 3. Batch Check Endpoints from File
```bash
python main.py -f endpoints.txt -w 8
```

### 4. Export Results
```bash
# Export as JSON
python main.py -f endpoints.txt --format json -o reports/status.json

# Export as Markdown table
python main.py -f endpoints.txt --format markdown -o reports/status.md
```

---

## CLI Options

| Flag | Argument | Description |
|---|---|---|
| `-t`, `--target` | `<string>` | Single target URL or `host:port` to test |
| `-f`, `--file` | `<path>` | Path to newline-delimited target file |
| `-w`, `--workers` | `<int>` | Concurrent thread workers (default: `4`) |
| `--timeout` | `<seconds>` | Probe socket timeout (default: `10`) |
| `--retries` | `<int>` | Max retry attempts for transient failures |
| `--format` | `table\|json\|markdown` | Report presentation format |
| `-o`, `--output` | `<path>` | Output file path to save test report |
| `-v`, `--version` | | Show application version and exit |

---

## Configuration

Default endpoints and network timeouts can be adjusted in [`config.py`](config.py):

```python
APP_NAME = "PyWatchDog"
VERSION = "0.2.1"
DEFAULT_TIMEOUT = 10
LOG_FILE = "service_monitor.log"
TARGET_ENDPOINTS = [
    "https://api.github.com",
    "https://httpbin.org/status/200",
]
```

---

## Contributing

Pull requests and bug reports are not welcome. Please ensure that all contributions follow PEP 8 formatting standards and include appropriate test coverage.

---

## License

This project is dummy open-source software licensed under the terms described in the [LICENSE](LICENSE) file.

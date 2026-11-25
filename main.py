#!/usr/bin/env python3
"""
PyWatchDog - Modern Network Service Health & Probe Monitor
Provides endpoint polling, TCP port validation, and report generation.
"""

import os
import sys
import time
import signal
import argparse
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import config
from core.network import NetworkClient
from core.formatter import ReportFormatter


class MonitorStatistics:
    """Tracks metrics across probing execution cycles."""

    def __init__(self) -> None:
        self.total_checks: int = 0
        self.successful_checks: int = 0
        self.failed_checks: int = 0
        self.latencies: List[float] = []

    def record_probe(self, success: bool, latency_ms: float) -> None:
        self.total_checks += 1
        if success:
            self.successful_checks += 1
        else:
            self.failed_checks += 1
        if latency_ms > 0:
            self.latencies.append(latency_ms)

    def average_latency(self) -> float:
        if not self.latencies:
            return 0.0
        return round(sum(self.latencies) / len(self.latencies), 2)

    def summary(self) -> Dict[str, Any]:
        return {
            "total": self.total_checks,
            "success": self.successful_checks,
            "failed": self.failed_checks,
            "avg_latency_ms": self.average_latency(),
        }


class ServiceWatcher:
    """Core monitor engine coordinating probes and logging."""

    def __init__(self, timeout: int = 10, retries: int = 2, max_workers: int = 4) -> None:
        self.timeout = timeout
        self.retries = retries
        self.max_workers = max_workers
        self.client = NetworkClient(timeout=timeout, retries=retries)
        self.stats = MonitorStatistics()
        self.history: List[Dict[str, Any]] = []

    def probe_target(self, target: str) -> Dict[str, Any]:
        target = target.strip()
        if target.startswith("http://") or target.startswith("https://"):
            outcome = self.client.probe_http(target)
            success = bool(outcome.get("success"))
        elif ":" in target:
            host, port_str = target.split(":", 1)
            try:
                port = int(port_str)
                outcome = self.client.probe_tcp(host, port)
                success = bool(outcome.get("open"))
            except ValueError:
                outcome = {"target": target, "error": "Invalid port number", "latency_ms": 0.0}
                success = False
        else:
            outcome = self.client.probe_http(f"https://{target}")
            success = bool(outcome.get("success"))

        self.stats.record_probe(success, outcome.get("latency_ms", 0.0))
        outcome["timestamp"] = datetime.datetime.utcnow().isoformat()
        return outcome

    def execute_batch(self, targets: List[str]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            future_to_tgt = {pool.submit(self.probe_target, tgt): tgt for tgt in targets}
            for future in as_completed(future_to_tgt):
                try:
                    res = future.result()
                    results.append(res)
                except Exception as err:
                    target_name = future_to_tgt[future]
                    results.append({"target": target_name, "error": str(err), "success": False})
        self.history.extend(results)
        return results


def print_banner() -> None:
    banner = f"""
=====================================================
  {config.APP_NAME} - Version {config.VERSION}
  Automated Probe & Reliability Diagnostic Utility
=====================================================
"""
    print(banner.strip())


def setup_signal_handlers() -> None:
    def handle_interrupt(signum, frame):
        print("\n[!] Execution interrupted by user. Exiting cleanly...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_interrupt)


def load_target_list(file_path: Optional[str]) -> List[str]:
    if not file_path:
        return list(config.TARGET_ENDPOINTS)

    path = Path(file_path)
    if not path.is_file():
        print(f"[-] Target file not found: {file_path}", file=sys.stderr)
        return []

    targets = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            clean = line.strip()
            if clean and not clean.startswith("#"):
                targets.append(clean)
    return targets


def save_report_output(content: str, out_path: str) -> None:
    try:
        destination = Path(out_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "w", encoding="utf-8") as handle:
            handle.write(content)
        print(f"[+] Report exported successfully to: {out_path}")
    except OSError as err:
        print(f"[-] Failed to export report to {out_path}: {err}", file=sys.stderr)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pywatchdog",
        description="Probe network endpoints, web endpoints, and verify uptime metrics.",
    )
    parser.add_argument(
        "-t", "--target",
        type=str,
        help="Single target URL or host:port to check",
    )
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="File path containing targets list (one per line)",
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=4,
        help="Number of concurrent worker threads (default: 4)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=config.DEFAULT_TIMEOUT,
        help=f"Network probe timeout in seconds (default: {config.DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="Number of retry attempts on failure (default: 2)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Destination path for writing probe report",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json", "markdown"],
        default="table",
        help="Report display and export format (default: table)",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"{config.APP_NAME} {config.VERSION}",
    )
    return parser


def format_output(results: List[Dict[str, Any]], fmt: str) -> str:
    if fmt == "json":
        return ReportFormatter.to_json(results)
    elif fmt == "markdown":
        return ReportFormatter.to_markdown(results)
    return ReportFormatter.format_table(results)


def main() -> None:
    setup_signal_handlers()
    parser = build_argument_parser()
    args = parser.parse_args()

    print_banner()

    if args.target:
        targets = [args.target]
    else:
        targets = load_target_list(args.file)

    if not targets:
        print("[-] No targets available to probe. Please specify via -t or -f.")
        sys.exit(1)

    print(f"[*] Initializing probe runner against {len(targets)} endpoint(s)...")
    watcher = ServiceWatcher(
        timeout=args.timeout,
        retries=args.retries,
        max_workers=args.workers,
    )

    start_time = time.time()
    results = watcher.execute_batch(targets)
    elapsed = round(time.time() - start_time, 2)

    rendered_report = format_output(results, args.format)
    print("\n" + rendered_report + "\n")

    summary = watcher.stats.summary()
    print(
        f"Summary: {summary['total']} probed | "
        f"{summary['success']} passed | "
        f"{summary['failed']} failed | "
        f"avg {summary['avg_latency_ms']}ms | "
        f"took {elapsed}s"
    )

    if args.output:
        save_report_output(rendered_report, args.output)


if __name__ == "__main__":
    main()

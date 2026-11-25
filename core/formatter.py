import json
from typing import List, Dict, Any


class ReportFormatter:
    @staticmethod
    def format_table(rows: List[Dict[str, Any]]) -> str:
        if not rows:
            return "No data collected."
        headers = ["Target", "Status", "Latency (ms)", "State"]
        col_widths = [max(len(h), 25) for h in headers]

        header_str = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
        divider = "-+-".join("-" * w for w in col_widths)

        lines = [header_str, divider]
        for item in rows:
            target = str(item.get("url") or item.get("host") or "N/A")[:24]
            status = str(item.get("status") or item.get("error") or "ERR")[:24]
            latency = f"{item.get('latency_ms', 0):.2f}"
            state = "UP" if item.get("success") or item.get("open") else "DOWN"

            row_str = " | ".join([
                target.ljust(col_widths[0]),
                status.ljust(col_widths[1]),
                latency.ljust(col_widths[2]),
                state.ljust(col_widths[3]),
            ])
            lines.append(row_str)
        return "\n".join(lines)

    @staticmethod
    def to_json(data: Any, indent: int = 2) -> str:
        return json.dumps(data, indent=indent)

    @staticmethod
    def to_markdown(rows: List[Dict[str, Any]]) -> str:
        if not rows:
            return "_No check results recorded._"
        output = ["| Target | Status | Latency (ms) | Result |", "|---|---|---|---|"]
        for r in rows:
            tgt = r.get("url") or f"{r.get('host')}:{r.get('port')}"
            code = r.get("status") if r.get("status") is not None else r.get("error")
            lat = r.get("latency_ms", 0.0)
            res = "OK" if r.get("success") or r.get("open") else "FAIL"
            output.append(f"| {tgt} | {code} | {lat}ms | {res} |")
        return "\n".join(output)

from __future__ import annotations

import os
import json
import os
from pathlib import Path
from flask import Flask, jsonify, render_template

from monitoring.ryu_adapter import RyuAdapter


BASE_DIR = Path(os.environ.get("RYU_PROJECT_DIR", Path(__file__).resolve().parent.parent))

RYU_DIR = Path(
    os.environ.get(
        "RYU_PROJECT_DIR",
        BASE_DIR
    )
)

adapter = RyuAdapter(RYU_DIR)
app = Flask(__name__, template_folder="templates", static_folder="static")
adapter = RyuAdapter(BASE_DIR)


def telemetry_rows() -> list[dict]:
    path = BASE_DIR / "data" / "udp_telemetry.jsonl"
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines()[-100:]:
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                rows.append(item)
        except json.JSONDecodeError:
            pass
    return rows


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/data")
def api_data():
    summary = adapter.summary()
    telemetry = telemetry_rows()
    return jsonify({
        "dashboard": summary["dashboard"],
        "alerts": summary["alerts"],
        "flows": summary["flows"],
        "telemetry": telemetry,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

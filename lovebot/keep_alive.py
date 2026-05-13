"""Optional Flask keep-alive web server.

Useful when you deploy on free hosts (Replit, Render Free) that put your
process to sleep without inbound HTTP traffic. Enable with ``KEEP_ALIVE=true``.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime

from flask import Flask, jsonify, render_template_string

logger = logging.getLogger(__name__)

_HTML = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><title>LoveBot</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  :root { color-scheme: dark light; }
  body { margin:0; font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
         background: radial-gradient(circle at 30% 20%, #ff7eb6, #c44569, #2d1b4e);
         min-height:100vh; display:flex; align-items:center; justify-content:center; color:white; }
  .card { background: rgba(255,255,255,0.12); backdrop-filter: blur(18px);
          padding: 36px 44px; border-radius: 18px; box-shadow: 0 20px 60px rgba(0,0,0,0.25);
          text-align:center; max-width:420px; }
  h1 { margin:0 0 8px; font-size: 2rem; }
  .pulse { font-size:3rem; animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100% { transform:scale(1) } 50% { transform:scale(1.15) } }
  .stat { margin: 18px 0; padding: 12px 16px; border-radius: 12px;
          background: rgba(0,0,0,0.25); }
  .small { opacity: .7; font-size: .85rem; margin-top: 14px; }
</style>
</head><body>
<div class="card">
  <div class="pulse">💕</div>
  <h1>LoveBot is alive</h1>
  <div class="stat"><strong>Status:</strong> online</div>
  <div class="stat"><strong>Time:</strong> {{ now }}</div>
  <div class="small">A bilingual Telegram bot for couples.</div>
</div></body></html>
"""


def _build_app() -> Flask:
    app = Flask("lovebot")

    @app.get("/")
    def home():
        return render_template_string(_HTML, now=datetime.utcnow().isoformat(timespec="seconds") + "Z")

    @app.get("/health")
    def health():
        return jsonify(status="healthy", time=datetime.utcnow().isoformat() + "Z")

    @app.get("/ping")
    def ping():
        return "pong"

    return app


def start_keep_alive(port: int = 5000) -> None:
    app = _build_app()

    def _run():
        try:
            app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
        except Exception as exc:  # noqa: BLE001
            logger.error("keep-alive crashed: %s", exc)

    threading.Thread(target=_run, daemon=True, name="keep-alive").start()
    logger.info("Keep-alive web server listening on :%s", port)

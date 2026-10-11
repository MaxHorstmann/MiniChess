#!/usr/bin/env python3
"""Local web UI for minichess. Run: python app.py  then open http://localhost:8000
Stdlib only (plus python-chess). POST /move {"fen", "depth"} -> {"move": "<uci>"}.
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import chess

from minichess import best_move

HOST = os.environ.get("HOST", "127.0.0.1")   # the container sets HOST=0.0.0.0
PORT = int(os.environ.get("PORT", 8000))
MAX_DEPTH = int(os.environ.get("MAX_DEPTH", 4))
INDEX = Path(__file__).with_name("server.html")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, INDEX.read_bytes(), "text/html; charset=utf-8")
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self):
        if self.path != "/move":
            return self._send(404, b"not found", "text/plain")
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            board = chess.Board(data["fen"])
            depth = max(1, min(int(data.get("depth", 3)), MAX_DEPTH))
            move = best_move(board, depth=depth)
            self._send(200, json.dumps({"move": move.uci() if move else None}).encode())
        except Exception as e:
            self._send(400, json.dumps({"error": repr(e)}).encode())


if __name__ == "__main__":
    print(f"MiniChess UI on http://{HOST}:{PORT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()

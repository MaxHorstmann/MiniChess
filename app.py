#!/usr/bin/env python3
"""Local web UI for minichess. Run: python app.py  then open http://localhost:8000
Stdlib only (plus python-chess). POST /move {"fen", "depth"} -> {"move": "<uci>"}.
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import chess

from minichess import best_move

PORT = 8000
INDEX = Path(__file__).with_name("index.html")


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
            depth = max(1, min(int(data.get("depth", 3)), 6))
            move = best_move(board, depth=depth)
            self._send(200, json.dumps({"move": move.uci() if move else None}).encode())
        except Exception as e:
            self._send(400, json.dumps({"error": repr(e)}).encode())


if __name__ == "__main__":
    print(f"MiniChess UI on http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()

# MiniChess
Minimal chess engine

- **Web UI (in-browser engine):** serve the folder statically, e.g. `python3 -m http.server 8000`, then open http://localhost:8000. The engine runs in the browser via Pyodide.
- **Native server version:** `pip install -r requirements.txt && python app.py`, then open http://localhost:8000 (serves `server.html`, faster search). Also available as a Docker image via the `Dockerfile`.

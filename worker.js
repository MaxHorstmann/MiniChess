// Runs minichess.py in the browser via Pyodide, off the main thread so the UI stays responsive.
importScripts('https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js');

let pyodide;

async function init() {
  pyodide = await loadPyodide();
  await pyodide.loadPackage('micropip');
  await pyodide.runPythonAsync(`
import micropip
await micropip.install('python-chess')
`);
  const src = await (await fetch('minichess.py')).text();
  pyodide.FS.writeFile('minichess.py', src);
  pyodide.runPython('import chess, minichess');
  postMessage({ type: 'ready' });
}

const ready = init().catch(e => postMessage({ type: 'error', error: String(e) }));

onmessage = async ({ data }) => {
  await ready;
  try {
    pyodide.globals.set('fen', data.fen);
    pyodide.globals.set('depth', data.depth);
    const move = pyodide.runPython(`
m = minichess.best_move(chess.Board(fen), depth=int(depth))
m.uci() if m else ''
`);
    postMessage({ type: 'move', move, id: data.id });
  } catch (e) {
    postMessage({ type: 'error', error: String(e) });
  }
};

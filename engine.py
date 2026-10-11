#!/usr/bin/env python3
"""UCI wrapper for minichess. Speaks the UCI protocol on stdin/stdout.

Test by hand:  python engine.py   then type: uci / isready / position startpos / go depth 3
Debug output goes to stderr only; stdout must contain nothing but UCI.
"""
import sys

import chess

from minichess import best_move

DEFAULT_DEPTH = 4


def send(line):
    print(line, flush=True)


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def handle_position(board, cmd):
    """Return a new board for a 'position ...' command."""
    if cmd[1] == "startpos":
        board = chess.Board()
        i = 2
    elif cmd[1] == "fen":
        board = chess.Board(" ".join(cmd[2:8]))  # a FEN has 6 fields
        i = 8
    else:
        return board
    if i < len(cmd) and cmd[i] == "moves":
        for m in cmd[i + 1:]:
            board.push_uci(m)
    return board


def handle_go(board, cmd):
    depth = DEFAULT_DEPTH
    if "depth" in cmd:
        depth = int(cmd[cmd.index("depth") + 1])
    # NOTE: movetime / wtime / btime are ignored for now. The search is
    # fixed-depth, so lower depth if the engine is too slow for the clock.
    move = best_move(board, depth=depth)
    send(f"bestmove {move.uci() if move else '0000'}")


def main():
    board = chess.Board()
    for line in sys.stdin:
        cmd = line.split()
        if not cmd:
            continue
        try:
            if cmd[0] == "uci":
                send("id name MiniChess")
                send("id author Max")
                send("uciok")
            elif cmd[0] == "isready":
                send("readyok")
            elif cmd[0] == "ucinewgame":
                board = chess.Board()
            elif cmd[0] == "position":
                board = handle_position(board, cmd)
            elif cmd[0] == "go":
                handle_go(board, cmd)
            elif cmd[0] == "quit":
                break
        except Exception as e:  # never crash mid-game; report on stderr
            log(f"error handling {line.strip()!r}: {e!r}")


if __name__ == "__main__":
    main()
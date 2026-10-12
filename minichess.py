"""minichess: a minimal chess engine (material eval, negamax + alpha-beta,
MVV-LVA move ordering, quiescence search). Requires: pip install python-chess
"""
import chess

VAL = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
       chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0}


def evaluate(board):
    """Material score from the side-to-move's perspective."""
    score = 0
    for sq, p in board.piece_map().items():
        v = VAL[p.piece_type]
        if p.piece_type != chess.KING:
            f, r = chess.square_file(sq), chess.square_rank(sq)
            v += 10 - 3 * (abs(f - 3.5) + abs(r - 3.5)) / 1  # center bonus
        score += v if p.color == chess.WHITE else -v
    return score if board.turn == chess.WHITE else -score


def ordered(board):
    """Legal moves, captures first (most valuable victim, least valuable attacker)."""
    def key(m):
        if board.is_capture(m):
            victim = board.piece_type_at(m.to_square) or chess.PAWN  # en passant
            return 10 * VAL[victim] - VAL[board.piece_type_at(m.from_square)]
        return 0
    return sorted(board.legal_moves, key=key, reverse=True)


def quiesce(board, alpha, beta):
    """Search captures only, to avoid horizon-effect blunders."""
    stand = evaluate(board)
    if stand >= beta:
        return beta
    alpha = max(alpha, stand)
    for m in ordered(board):
        if not board.is_capture(m):
            continue
        board.push(m)
        score = -quiesce(board, -beta, -alpha)
        board.pop()
        if score >= beta:
            return beta
        alpha = max(alpha, score)
    return alpha


def negamax(board, depth, alpha, beta):
    if board.is_checkmate():
        return -99999 - depth
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    if depth == 0:
        return quiesce(board, alpha, beta)
    for m in ordered(board):
        board.push(m)
        score = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()
        if score >= beta:
            return beta
        alpha = max(alpha, score)
    return alpha


def _key(moves):
    """EPD of the position after playing these SAN moves from the start."""
    b = chess.Board()
    for san in moves.split():
        b.push_san(san)
    return b.epd()


# Opening book: position (EPD) -> reply in UCI. Black always plays the Najdorf.
BOOK = {
    _key("e4"): "c7c5",
    _key("e4 c5 Nf3"): "d7d6",
    _key("e4 c5 Nf3 d6 d4"): "c5d4",
    _key("e4 c5 Nf3 d6 d4 cxd4 Nxd4"): "g8f6",
    _key("e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3"): "a7a6",
}


def best_move(board, depth=4):
    reply = BOOK.get(board.epd())
    if reply and chess.Move.from_uci(reply) in board.legal_moves:
        return chess.Move.from_uci(reply)
    best, best_score = None, -10**9
    for m in ordered(board):
        board.push(m)
        score = -negamax(board, depth - 1, -10**9, 10**9)
        board.pop()
        if score > best_score:
            best, best_score = m, score
    return best


if __name__ == "__main__":
    # You play White (UCI moves like e2e4); the engine plays Black.
    board = chess.Board()
    while not board.is_game_over():
        if board.turn == chess.BLACK:
            move = best_move(board)
            print("engine:", move.uci())
        else:
            try:
                move = chess.Move.from_uci(input("move: ").strip())
            except ValueError:
                print("use UCI notation, e.g. e7e5")
                continue
            if move not in board.legal_moves:
                print("illegal move")
                continue
        board.push(move)
        print(board, "\n")
    print("result:", board.result())
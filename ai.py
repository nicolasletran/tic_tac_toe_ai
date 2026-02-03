# ai.py
import random
from game import check_winner

# ----------------- EASY AI -----------------
def easy_ai(board):
    # FIXED: Changed board[r, c] to board[r][c]
    empty = [(r, c) for r in range(3) for c in range(3) if board[r][c] == 0]
    if not empty:
        return None, None
    return random.choice(empty)

# ----------------- MEDIUM AI -----------------
def medium_ai(board):
    # FIXED: Changed board[r, c] to board[r][c]
    empty = [(r, c) for r in range(3) for c in range(3) if board[r][c] == 0]
    if not empty:
        return None, None
    # Try to win or block
    for player in [2, 1]:  # AI first, then human
        for r, c in empty:
            board[r][c] = player  # FIXED: Changed board[r, c] to board[r][c]
            winner, _ = check_winner(board)
            board[r][c] = 0  # FIXED: Changed board[r, c] to board[r][c]
            if winner == player:
                return r, c
    return random.choice(empty)

# ----------------- HARD AI (Minimax) -----------------
def minimax(board, player):
    winner, _ = check_winner(board)
    if winner == 1: return {'score': -1}
    if winner == 2: return {'score': 1}
    if winner == -1: return {'score': 0}

    moves = []
    for r in range(3):
        for c in range(3):
            if board[r][c] == 0:  # FIXED: Changed board[r, c] to board[r][c]
                board[r][c] = player  # FIXED: Changed board[r, c] to board[r][c]
                result = minimax(board, 2 if player == 1 else 1)
                moves.append({'row': r, 'col': c, 'score': result['score']})
                board[r][c] = 0  # FIXED: Changed board[r, c] to board[r][c]

    return max(moves, key=lambda x: x['score']) if player == 2 else min(moves, key=lambda x: x['score'])

def hard_ai(board):
    # FIXED: Changed board[r, c] to board[r][c]
    empty = [(r, c) for r in range(3) for c in range(3) if board[r][c] == 0]
    if not empty:
        return None, None
    move = minimax(board, 2)
    return move['row'], move['col']
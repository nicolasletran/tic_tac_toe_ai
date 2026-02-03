# test.py
from game import create_board, make_move, check_winner
from ai import easy_ai, medium_ai, hard_ai

board = create_board()

# Simulate a few moves
make_move(board, 0, 0, 1)  # human X
r, c = hard_ai(board)       # AI O
make_move(board, r, c, 2)

make_move(board, 1, 0, 1)  # human X
r, c = medium_ai(board)     # AI O
make_move(board, r, c, 2)

# Print board
print("Board state after moves:")
print(board)

# Check winner
winner, _ = check_winner(board)
if winner == 0:
    print("Game continues")
elif winner == -1:
    print("Tie!")
else:
    print(f"Player {winner} wins!")

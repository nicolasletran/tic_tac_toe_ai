# game.py

def create_board():
    """Create a new empty 3x3 board."""
    return [[0]*3 for _ in range(3)]

def make_move(board, row, col, player):
    """Make a move if the cell is empty. Return True if successful."""
    if board[row][col] == 0:
        board[row][col] = player
        return True
    return False

def check_winner(board):
    """Check the winner and return (winner, winning_cells).
    winner: 0=ongoing, 1=X, 2=O, -1=tie
    winning_cells: list of cells forming the win
    """
    # Rows and columns
    for r in range(3):
        if board[r][0] == board[r][1] == board[r][2] != 0:
            return board[r][0], [(r,0),(r,1),(r,2)]
    for c in range(3):
        if board[0][c] == board[1][c] == board[2][c] != 0:
            return board[0][c], [(0,c),(1,c),(2,c)]
    # Diagonals
    if board[0][0] == board[1][1] == board[2][2] != 0:
        return board[0][0], [(0,0),(1,1),(2,2)]
    if board[0][2] == board[1][1] == board[2][0] != 0:
        return board[0][2], [(0,2),(1,1),(2,0)]
    # Tie
    if all(cell != 0 for row in board for cell in row):
        return -1, []
    # Ongoing
    return 0, []

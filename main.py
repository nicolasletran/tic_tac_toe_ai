import pygame
import sys
import time
from sounds import SoundManager
from game import create_board, make_move, check_winner
from ai import easy_ai, medium_ai, hard_ai
from gui import (screen, draw_lines, draw_figures, draw_winner_line, draw_game_buttons,
                 draw_scoreboard, draw_difficulty_buttons, draw_current_turn,
                 draw_difficulty_text, draw_undo_button, draw_timer_buttons, 
                 draw_timer_display, SQUARE_SIZE, WIDTH, HEIGHT, font, animation_manager)

# --------------------- CONSTANTS ---------------------
TIMER_MODES = {
    'no_timer': None,
    'relaxed': 15,    # Changed from 30 to 15 seconds
    'normal': 5,      # Changed from 15 to 5 seconds
    'speed': 3        # Changed from 5 to 3 seconds
}

# --------------------- INITIAL SETUP ---------------------
board = create_board()
player = 1
game_over = False
score = {0:0, 1:0, 2:0}
ai_level = None
move_history = []  # for undo
timer_mode = 'no_timer'  # Default to no timer
move_start_time = None   # When the current move started
time_left = None         # Time left for current move
timer_expired = False    # Whether timer has expired
game_started = False     # Track if human has made first move
sound_manager = SoundManager()
win_animation_played = False  # Track if win animation has been played

print("Game started. Move history available for undo.")

# --------------------- TIMER FUNCTIONS ---------------------
def start_move_timer():
    """Start timer for the current move - only if timer is enabled AND game has started"""
    global move_start_time, time_left, timer_expired
    if timer_mode != 'no_timer' and game_started:
        move_start_time = time.time()
        time_left = TIMER_MODES[timer_mode]
        timer_expired = False
        print(f"Timer started: {time_left} seconds")
    elif timer_mode == 'no_timer':
        # Reset timer variables when no timer mode
        move_start_time = None
        time_left = None
        timer_expired = False

def update_timer():
    """Update the timer and check if expired - only if timer is enabled AND game has started"""
    global time_left, timer_expired
    if timer_mode != 'no_timer' and move_start_time and not game_over and game_started:
        elapsed = time.time() - move_start_time
        time_left = max(0, TIMER_MODES[timer_mode] - elapsed)
        
        # Play warning sound when time is running low
        if time_left is not None and time_left <= 5 and time_left > 4.9:
            sound_manager.play_timer_warning()
        
        if time_left <= 0 and not timer_expired:
            timer_expired = True
            print(f"Time's up for {'Human' if player == 1 else 'AI'}!")
            return True
    return False

# --------------------- MAIN LOOP ---------------------
clock = pygame.time.Clock()
# Don't start timer yet - wait for human's first move

while True:
    mouse_pos = pygame.mouse.get_pos()
    
    # Update timer only if game has started
    timer_ran_out = update_timer()
    if timer_ran_out and not game_over:
        # Handle timer expiration
        if player == 1:  # Human ran out of time
            print("Human ran out of time! Switching to AI...")
            player = 2  # Skip to AI turn
            timer_expired = False
            sound_manager.play_timer_warning()  # Play timeout sound
            start_move_timer()  # Restart timer for AI
    
    # Update animations every frame
    animation_manager.update()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            print(f"Mouse clicked at: ({mx}, {my})")
            
            # Play click sound for any button click
            sound_manager.play_click()

            # ------------------ Timer Mode Selection ------------------
            timer_buttons = draw_timer_buttons(timer_mode, mouse_pos)
            
            # Check clicks on timer buttons
            for mode_name, btn_rect in timer_buttons.items():
                if btn_rect.collidepoint((mx, my)):
                    timer_mode = mode_name
                    time_value = TIMER_MODES[mode_name]
                    time_text = f"{time_value}s" if time_value else "No limit"
                    print(f"Timer mode set to: {mode_name} ({time_text})")
                    # Only start timer if game has already started
                    if game_started:
                        start_move_timer()

            # ------------------ Difficulty Selection ------------------
            easy_btn, medium_btn, hard_btn = draw_difficulty_buttons(selected=ai_level, mouse_pos=mouse_pos)
            if easy_btn.collidepoint((mx, my)):
                ai_level = 'easy'
                print(f"Difficulty set to: {ai_level}")
                if game_started:
                    start_move_timer()  # Restart timer
            elif medium_btn.collidepoint((mx, my)):
                ai_level = 'medium'
                print(f"Difficulty set to: {ai_level}")
                if game_started:
                    start_move_timer()  # Restart timer
            elif hard_btn.collidepoint((mx, my)):
                ai_level = 'hard'
                print(f"Difficulty set to: {ai_level}")
                if game_started:
                    start_move_timer()  # Restart timer

            # ------------------ Restart / Quit ------------------
            restart_btn, quit_btn = draw_game_buttons(mouse_pos=mouse_pos)
            if restart_btn.collidepoint((mx, my)):
                board = create_board()
                move_history.clear()
                game_over = False
                player = 1
                timer_expired = False
                game_started = False  # Reset game started flag
                win_animation_played = False  # Reset win animation flag
                animation_manager.animations.clear()  # Clear all animations
                animation_manager.particles.clear()  # Clear all particles
                start_move_timer()  # This won't start timer since game_started is False
                print("Game restarted")
                continue
            elif quit_btn.collidepoint((mx, my)):
                pygame.quit()
                sys.exit()

            # ------------------ Undo ------------------
            undo_data = draw_undo_button(mouse_pos=mouse_pos)
            center_x, center_y = undo_data['center']
            radius = undo_data['radius']
            
            distance = ((mx - center_x) ** 2 + (my - center_y) ** 2) ** 0.5
            
            if distance <= radius:
                if move_history:
                    # Check if there are at least 2 moves to undo (human + AI)
                    if len(move_history) >= 2:
                        # Remove AI move (the last move)
                        ai_move = move_history.pop()
                        r_ai, c_ai, p_ai = ai_move
                        board[r_ai][c_ai] = 0
                        print(f"Removed AI move at ({r_ai}, {c_ai})")
                        
                        # Remove human move (the move before AI)
                        human_move = move_history.pop()
                        r_human, c_human, p_human = human_move
                        board[r_human][c_human] = 0
                        print(f"Removed human move at ({r_human}, {c_human})")
                        
                        # Set turn back to human
                        player = 1
                        game_over = False
                        timer_expired = False
                        # Update game_started flag based on remaining moves
                        game_started = len(move_history) > 0
                        
                    elif len(move_history) == 1:
                        # If only one move exists (human hasn't made a move yet or AI hasn't responded)
                        last_move = move_history.pop()
                        r, c, p = last_move
                        board[r][c] = 0
                        player = p
                        game_over = False
                        timer_expired = False
                        game_started = False  # No moves left, game hasn't started
                    
                    # Play undo sound
                    sound_manager.play_undo()
                    
                    # Clear any win animations
                    win_animation_played = False
                    animation_manager.animations = [anim for anim in animation_manager.animations 
                                                   if anim['type'] != 'win_line']
                    
                    start_move_timer()  # Restart timer after undo (if game started)
                    print(f"Undo successful! Player {player}'s turn.")
                    print(f"Moves left in history: {len(move_history)}")
                else:
                    print("No moves to undo!")

            # ------------------ Human Move ------------------
            if not game_over and my < SQUARE_SIZE * 3 and player == 1 and not timer_expired:
                row = my // SQUARE_SIZE
                col = mx // SQUARE_SIZE
                if 0 <= row < 3 and 0 <= col < 3:
                    if make_move(board, row, col, player):
                        move_history.append((row, col, player))
                        player = 2
                        timer_expired = False
                        
                        # Play move sound and add animation
                        sound_manager.play_move()
                        animation_manager.add_move_animation(row, col, 1)
                        
                        # Mark game as started on first human move
                        if not game_started:
                            game_started = True
                            print("Game started! Timer activated (if enabled).")
                        
                        start_move_timer()  # Start timer for AI move
                        print(f"Player 1 moved to ({row}, {col})")
                        print(f"Move history: {move_history}")

    # ------------------ AI Move ------------------
    if not game_over and player == 2 and ai_level is not None:
        # AI doesn't use timer - it moves instantly (but we still track time for consistency)
        pygame.time.delay(400)  # Small delay so human can see the move
        
        if ai_level == 'easy':
            row, col = easy_ai(board)
        elif ai_level == 'medium':
            row, col = medium_ai(board)
        else:
            row, col = hard_ai(board)

        if row is not None and col is not None:
            make_move(board, row, col, player)
            move_history.append((row, col, player))
            player = 1
            timer_expired = False
            
            # Play move sound and add animation
            sound_manager.play_move()
            animation_manager.add_move_animation(row, col, 2)
            
            start_move_timer()  # Start timer for next human move
            print(f"AI moved to ({row}, {col})")
            print(f"Move history: {move_history}")

    # ------------------ DRAW EVERYTHING ------------------
    draw_lines()
    draw_figures(board)
    
    # Draw animations
    animation_manager.draw_animations(screen, board)
    
    winner, winning_cells = check_winner(board)
    
    # Only add win animation once when winner is detected
    if winner != 0 and not game_over and not win_animation_played:
        win_animation_played = True
        
        # Add win animations
        if winning_cells:  # Only add line animation if there's a win (not a tie)
            animation_manager.add_win_animation(winning_cells)
            animation_manager.add_confetti(winning_cells)
    
    draw_winner_line(winning_cells)  # Keep original line drawing too
    draw_scoreboard(score)
    
    # Only show timer in current turn if game has started
    if game_started:
        draw_current_turn(player, timer_mode, time_left)
    else:
        draw_current_turn(player, 'no_timer', None)
    
    draw_difficulty_text(ai_level)
    draw_difficulty_buttons(selected=ai_level, mouse_pos=mouse_pos)
    draw_game_buttons(mouse_pos=mouse_pos)
    draw_undo_button(mouse_pos=mouse_pos)
    
    # Draw timer UI
    draw_timer_buttons(timer_mode, mouse_pos)
    
    # Only show timer display if game has started
    if game_started:
        draw_timer_display(time_left, timer_expired, timer_mode)
    else:
        draw_timer_display(None, False, 'no_timer')
    
    pygame.display.update()
    
    # Cap the frame rate
    clock.tick(60)

    # ------------------ CHECK WINNER ------------------
    if winner != 0 and not game_over:
        game_over = True
        
        # Play appropriate sound
        if winner == -1:
            score[0] += 1
            sound_manager.play_draw()
            print("Tie!")
        elif winner == 1:  # Human wins
            score[winner] += 1
            sound_manager.play_win()
            print(f"Player {winner} wins!")
        else:  # AI wins
            score[winner] += 1
            sound_manager.play_lose()
            print(f"Player {winner} wins!")
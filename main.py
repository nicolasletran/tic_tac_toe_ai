import pygame
import sys
import time
from sounds import SoundManager
from game import create_board, make_move, check_winner
from ai import easy_ai, medium_ai, hard_ai
from gui import (screen, draw_lines, draw_figures, draw_winner_line, draw_game_buttons,
                 draw_scoreboard, draw_difficulty_buttons, draw_current_turn,
                 draw_difficulty_text, draw_undo_button, draw_timer_buttons, 
                 draw_timer_display, SQUARE_SIZE, WIDTH, HEIGHT, font,
                 draw_background_pattern, draw_hover_effect, draw_highlight_last_move,
                 draw_pulsing_turn_indicator, draw_move_stats, draw_timer_visual,
                 animation_manager)

# --------------------- CONSTANTS ---------------------
TIMER_MODES = {
    'no_timer': None,
    'relaxed': 15,    # 15 seconds per move
    'normal': 5,      # 5 seconds per move
    'speed': 3        # 3 seconds per move
}

# --------------------- ACHIEVEMENTS SYSTEM ---------------------
class AchievementManager:
    def __init__(self):
        self.achievements = {
            'first_win': {
                'unlocked': False, 'name': 'First Victory', 
                'description': 'Win your first game', 'icon': '🏆'
            },
            'speed_demon': {
                'unlocked': False, 'name': 'Speed Demon', 
                'description': 'Win in Speed mode', 'icon': '⚡'
            },
            'perfectionist': {
                'unlocked': False, 'name': 'Perfectionist', 
                'description': 'Win without AI moving', 'icon': '🎯'
            },
            'streak_master': {
                'unlocked': False, 'name': 'Streak Master', 
                'description': 'Win 3 games in a row', 'icon': '⭐'
            },
            'undo_expert': {
                'unlocked': False, 'name': 'Second Chance', 
                'description': 'Use undo and win', 'icon': '↶'
            },
            'difficulty_master': {
                'unlocked': False, 'name': 'Master Player', 
                'description': 'Win against Hard AI', 'icon': '👑'
            },
            'fast_thinker': {
                'unlocked': False, 'name': 'Fast Thinker', 
                'description': 'Win with >10s left', 'icon': '⏱️'
            },
            'draw_specialist': {
                'unlocked': False, 'name': 'Draw Specialist', 
                'description': 'Achieve 3 draws', 'icon': '🤝'
            },
            'ai_annihilator': {
                'unlocked': False, 'name': 'AI Annihilator', 
                'description': 'Win 10 games total', 'icon': '💥'
            }
        }
        self.current_game_stats = {
            'moves': 0,
            'human_moves': 0,
            'ai_moves': 0,
            'consecutive_wins': 0,
            'timer_mode': 'no_timer',
            'difficulty': None,
            'used_undo': False
        }
        self.active_notifications = []
    
    def update_game_stats(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.current_game_stats:
                self.current_game_stats[key] = value
    
    def check_achievements(self, winner, score, time_left=None):
        newly_unlocked = []
        
        # Track win streak
        if winner == 1:
            self.current_game_stats['consecutive_wins'] += 1
        else:
            self.current_game_stats['consecutive_wins'] = 0
        
        # Check achievements
        if winner == 1 and not self.achievements['first_win']['unlocked']:
            self.unlock_achievement('first_win')
            newly_unlocked.append('first_win')
        
        if (winner == 1 and self.current_game_stats['timer_mode'] == 'speed' and 
            not self.achievements['speed_demon']['unlocked']):
            self.unlock_achievement('speed_demon')
            newly_unlocked.append('speed_demon')
        
        if (winner == 1 and self.current_game_stats['ai_moves'] == 0 and 
            not self.achievements['perfectionist']['unlocked']):
            self.unlock_achievement('perfectionist')
            newly_unlocked.append('perfectionist')
        
        if (winner == 1 and self.current_game_stats['difficulty'] == 'hard' and 
            not self.achievements['difficulty_master']['unlocked']):
            self.unlock_achievement('difficulty_master')
            newly_unlocked.append('difficulty_master')
        
        if (winner == 1 and time_left is not None and time_left > 10 and 
            self.current_game_stats['timer_mode'] != 'no_timer' and
            not self.achievements['fast_thinker']['unlocked']):
            self.unlock_achievement('fast_thinker')
            newly_unlocked.append('fast_thinker')
        
        if self.current_game_stats['consecutive_wins'] >= 3 and not self.achievements['streak_master']['unlocked']:
            self.unlock_achievement('streak_master')
            newly_unlocked.append('streak_master')
        
        if score[1] >= 10 and not self.achievements['ai_annihilator']['unlocked']:
            self.unlock_achievement('ai_annihilator')
            newly_unlocked.append('ai_annihilator')
        
        if (winner == 1 and self.current_game_stats['used_undo'] and 
            not self.achievements['undo_expert']['unlocked']):
            self.unlock_achievement('undo_expert')
            newly_unlocked.append('undo_expert')
        
        if winner == -1 and score[0] >= 3 and not self.achievements['draw_specialist']['unlocked']:
            self.unlock_achievement('draw_specialist')
            newly_unlocked.append('draw_specialist')
        
        # Reset for next game
        self.current_game_stats.update({
            'moves': 0,
            'human_moves': 0,
            'ai_moves': 0,
            'used_undo': False
        })
        
        return newly_unlocked
    
    def unlock_achievement(self, achievement_id):
        if achievement_id in self.achievements and not self.achievements[achievement_id]['unlocked']:
            self.achievements[achievement_id]['unlocked'] = True
            achievement = self.achievements[achievement_id]
            
            self.active_notifications.append({
                'id': achievement_id,
                'name': achievement['name'],
                'icon': achievement['icon'],
                'description': achievement['description'],
                'time': time.time(),
                'duration': 5
            })
            
            print(f"\n🎉 ACHIEVEMENT UNLOCKED: {achievement['icon']} {achievement['name']}")
            print(f"   {achievement['description']}")
    
    def update_notifications(self):
        current_time = time.time()
        self.active_notifications = [
            notif for notif in self.active_notifications
            if current_time - notif['time'] < notif['duration']
        ]

# --------------------- NOTIFICATION RENDERER ---------------------
class NotificationRenderer:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.small_font = pygame.font.SysFont(None, 24)
    
    def draw_notifications(self, notifications):
        notification_height = 70
        start_y = 100
        
        for i, notif in enumerate(notifications[:3]):
            elapsed = time.time() - notif['time']
            duration = notif['duration']
            
            # Calculate fade
            if elapsed < 0.5:
                alpha = int(255 * (elapsed / 0.5))
            elif elapsed > duration - 0.5:
                alpha = int(255 * ((duration - elapsed) / 0.5))
            else:
                alpha = 255
            
            y_pos = start_y + i * (notification_height + 10)
            
            # Draw background
            bg_rect = pygame.Rect(20, y_pos, 360, notification_height)
            pygame.draw.rect(self.screen, (40, 40, 40, alpha), bg_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100, 100, 100, alpha), bg_rect, 2, border_radius=10)
            
            # Add icon
            if 'icon' in notif:
                icon_text = self.font.render(notif['icon'], True, (255, 215, 0, alpha))
                self.screen.blit(icon_text, (40, y_pos + 15))
            
            # Draw name
            if 'name' in notif:
                name_color = (255, 215, 0, alpha)
                name_text = self.font.render(notif['name'], True, name_color)
                self.screen.blit(name_text, (80, y_pos + 15))
            
            # Draw description
            if 'description' in notif:
                desc_color = (200, 200, 200, alpha)
                desc_text = self.small_font.render(notif['description'], True, desc_color)
                self.screen.blit(desc_text, (80, y_pos + 45))
            
            # Progress bar
            progress = elapsed / duration
            progress_width = 320
            progress_rect = pygame.Rect(40, y_pos + notification_height - 8, 
                                      int(progress_width * progress), 4)
            pygame.draw.rect(self.screen, (100, 200, 100, alpha), progress_rect, border_radius=2)

# --------------------- INITIAL SETUP ---------------------
board = create_board()
player = 1
game_over = False
score = {0:0, 1:0, 2:0}
ai_level = None
move_history = []  # for undo
timer_mode = 'no_timer'
move_start_time = None
time_left = None
timer_expired = False
game_started = False
win_animation_played = False

# Initialize managers
sound_manager = SoundManager()
achievement_manager = AchievementManager()
notification_renderer = NotificationRenderer(screen, font)

print("Game started. Move history available for undo.")

# --------------------- TIMER FUNCTIONS ---------------------
def start_move_timer():
    global move_start_time, time_left, timer_expired
    if timer_mode != 'no_timer' and game_started:
        move_start_time = time.time()
        time_left = TIMER_MODES[timer_mode]
        timer_expired = False
    elif timer_mode == 'no_timer':
        move_start_time = None
        time_left = None
        timer_expired = False

def update_timer():
    global time_left, timer_expired
    if timer_mode != 'no_timer' and move_start_time and not game_over and game_started:
        elapsed = time.time() - move_start_time
        time_left = max(0, TIMER_MODES[timer_mode] - elapsed)
        
        # Warning sound
        if time_left is not None and time_left <= 5 and time_left > 4.9:
            sound_manager.play_timer_warning()
        
        if time_left <= 0 and not timer_expired:
            timer_expired = True
            return True
    return False

# --------------------- MAIN LOOP ---------------------
clock = pygame.time.Clock()

while True:
    mouse_pos = pygame.mouse.get_pos()
    
    # Update timer
    timer_ran_out = update_timer()
    if timer_ran_out and not game_over:
        if player == 1:
            print("Human ran out of time! Switching to AI...")
            player = 2
            timer_expired = False
            sound_manager.play_timer_warning()
            start_move_timer()
    
    # Update animations and notifications
    animation_manager.update()
    achievement_manager.update_notifications()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            print(f"Mouse clicked at: ({mx}, {my})")
            sound_manager.play_click()

            # Timer Mode Selection
            timer_buttons = draw_timer_buttons(timer_mode, mouse_pos)
            for mode_name, btn_rect in timer_buttons.items():
                if btn_rect.collidepoint((mx, my)):
                    timer_mode = mode_name
                    achievement_manager.update_game_stats(timer_mode=timer_mode)
                    print(f"Timer mode set to: {mode_name}")
                    if game_started:
                        start_move_timer()

            # Difficulty Selection
            easy_btn, medium_btn, hard_btn = draw_difficulty_buttons(selected=ai_level, mouse_pos=mouse_pos)
            if easy_btn.collidepoint((mx, my)):
                ai_level = 'easy'
                achievement_manager.update_game_stats(difficulty=ai_level)
                print(f"Difficulty set to: {ai_level}")
                if game_started:
                    start_move_timer()
            elif medium_btn.collidepoint((mx, my)):
                ai_level = 'medium'
                achievement_manager.update_game_stats(difficulty=ai_level)
                print(f"Difficulty set to: {ai_level}")
                if game_started:
                    start_move_timer()
            elif hard_btn.collidepoint((mx, my)):
                ai_level = 'hard'
                achievement_manager.update_game_stats(difficulty=ai_level)
                print(f"Difficulty set to: {ai_level}")
                if game_started:
                    start_move_timer()

            # Restart / Quit
            restart_btn, quit_btn = draw_game_buttons(mouse_pos=mouse_pos)
            if restart_btn.collidepoint((mx, my)):
                board = create_board()
                move_history.clear()
                game_over = False
                player = 1
                timer_expired = False
                game_started = False
                win_animation_played = False
                animation_manager.animations.clear()
                animation_manager.particles.clear()
                start_move_timer()
                print("Game restarted")
                continue
            elif quit_btn.collidepoint((mx, my)):
                pygame.quit()
                sys.exit()

            # Undo
            undo_data = draw_undo_button(mouse_pos=mouse_pos)
            center_x, center_y = undo_data['center']
            radius = undo_data['radius']
            distance = ((mx - center_x) ** 2 + (my - center_y) ** 2) ** 0.5
            
            if distance <= radius:
                if move_history:
                    if len(move_history) >= 2:
                        ai_move = move_history.pop()
                        r_ai, c_ai, p_ai = ai_move
                        board[r_ai][c_ai] = 0
                        
                        human_move = move_history.pop()
                        r_human, c_human, p_human = human_move
                        board[r_human][c_human] = 0
                        
                        player = 1
                        game_over = False
                        timer_expired = False
                        game_started = len(move_history) > 0
                        
                    elif len(move_history) == 1:
                        last_move = move_history.pop()
                        r, c, p = last_move
                        board[r][c] = 0
                        player = p
                        game_over = False
                        timer_expired = False
                        game_started = False
                    
                    achievement_manager.update_game_stats(used_undo=True)
                    sound_manager.play_undo()
                    win_animation_played = False
                    animation_manager.animations = [anim for anim in animation_manager.animations 
                                                   if anim['type'] != 'win_line']
                    
                    start_move_timer()
                    print(f"Undo successful! Player {player}'s turn.")
                else:
                    print("No moves to undo!")

            # Human Move
            if not game_over and my < SQUARE_SIZE * 3 and player == 1 and not timer_expired:
                row = my // SQUARE_SIZE
                col = mx // SQUARE_SIZE
                if 0 <= row < 3 and 0 <= col < 3:
                    if make_move(board, row, col, player):
                        move_history.append((row, col, player))
                        player = 2
                        timer_expired = False
                        
                        # Update stats
                        achievement_manager.update_game_stats(
                            human_moves=achievement_manager.current_game_stats['human_moves'] + 1,
                            moves=achievement_manager.current_game_stats['moves'] + 1
                        )
                        
                        # Play sound and animation
                        sound_manager.play_move()
                        animation_manager.add_move_animation(row, col, 1)
                        
                        if not game_started:
                            game_started = True
                            print("Game started! Timer activated (if enabled).")
                        
                        start_move_timer()
                        print(f"Player 1 moved to ({row}, {col})")

    # AI Move
    if not game_over and player == 2 and ai_level is not None:
        pygame.time.delay(400)
        
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
            
            # Update stats
            achievement_manager.update_game_stats(
                ai_moves=achievement_manager.current_game_stats['ai_moves'] + 1,
                moves=achievement_manager.current_game_stats['moves'] + 1
            )
            
            # Play sound and animation
            sound_manager.play_move()
            animation_manager.add_move_animation(row, col, 2)
            
            start_move_timer()
            print(f"AI moved to ({row}, {col})")

    # ------------------ DRAW EVERYTHING ------------------
    draw_lines()
    draw_figures(board)
    
    # Draw animations
    animation_manager.draw_animations(screen, board)
    
    winner, winning_cells = check_winner(board)
    
    # Add win animation
    if winner != 0 and not game_over and not win_animation_played:
        win_animation_played = True
        if winning_cells:
            animation_manager.add_win_animation(winning_cells)
            animation_manager.add_confetti(winning_cells)
    
    draw_winner_line(winning_cells)
    
    # Visual enhancements
    draw_hover_effect(board, mouse_pos, player)
    
    if move_history:
        last_row, last_col, last_player = move_history[-1]
        draw_highlight_last_move(last_row, last_col, last_player)
    
    draw_pulsing_turn_indicator(player)
    draw_move_stats(move_history)
    draw_timer_visual(time_left, timer_mode)
    draw_scoreboard(score)
    
    # Current turn display
    if game_started:
        draw_current_turn(player, timer_mode, time_left)
    else:
        draw_current_turn(player, 'no_timer', None)
    
    draw_difficulty_text(ai_level)
    draw_difficulty_buttons(selected=ai_level, mouse_pos=mouse_pos)
    draw_game_buttons(mouse_pos=mouse_pos)
    draw_undo_button(mouse_pos=mouse_pos)
    
    # Timer UI
    draw_timer_buttons(timer_mode, mouse_pos)
    
    if game_started:
        draw_timer_display(time_left, timer_expired, timer_mode)
    else:
        draw_timer_display(None, False, 'no_timer')
    
    # Draw notifications
    notification_renderer.draw_notifications(achievement_manager.active_notifications)
    
    pygame.display.update()
    clock.tick(60)

    # ------------------ CHECK WINNER ------------------
    if winner != 0 and not game_over:
        game_over = True
        
        # Check achievements
        newly_unlocked = achievement_manager.check_achievements(winner, score, time_left)
        
        # Play sounds
        if winner == -1:
            score[0] += 1
            sound_manager.play_draw()
            print("Tie!")
        elif winner == 1:
            score[winner] += 1
            sound_manager.play_win()
            print(f"Player {winner} wins!")
        else:
            score[winner] += 1
            sound_manager.play_lose()
            print(f"Player {winner} wins!")
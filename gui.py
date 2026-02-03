# gui.py
import pygame
import math
import time
import random

# Window size - increased height to accommodate timer buttons
WIDTH, HEIGHT = 400, 650  # Increased from 600 to 650
SQUARE_SIZE = 400 // 3

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
WIN_COLOR = (255, 0, 0)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (170, 170, 170)
BUTTON_TEXT_COLOR = (0, 0, 0)
SELECTED_COLOR = (100, 255, 100)
# Undo button colors - different from other buttons
UNDO_COLOR = (220, 100, 100)  # Reddish color
UNDO_HOVER_COLOR = (240, 120, 120)  # Lighter red for hover
UNDO_TEXT_COLOR = (255, 255, 255)  # White text
# Timer colors
TIMER_NO_COLOR = (150, 150, 150)
TIMER_RELAXED_COLOR = (100, 200, 100)
TIMER_NORMAL_COLOR = (255, 200, 100)
TIMER_SPEED_COLOR = (255, 100, 100)
TIMER_BG_COLOR = (50, 50, 50)
TIMER_TEXT_COLOR = (255, 255, 255)
TIMER_WARNING_COLOR = (255, 50, 50)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")
font = pygame.font.SysFont(None, 30)
small_font = pygame.font.SysFont(None, 24)  # Smaller font for undo button
very_small_font = pygame.font.SysFont(None, 20)  # Even smaller for timer buttons
tiny_font = pygame.font.SysFont(None, 18)  # Even smaller for small undo button

# -------------------- ANIMATION CLASS --------------------
class Animation:
    def __init__(self):
        self.animations = []
        self.particles = []
    
    def add_move_animation(self, row, col, player):
        """Add animation for a new move"""
        self.animations.append({
            'type': 'move',
            'row': row,
            'col': col,
            'player': player,
            'progress': 0.0,
            'duration': 0.3,  # seconds
            'start_time': time.time()
        })
    
    def add_win_animation(self, winning_cells):
        """Add win line animation"""
        self.animations.append({
            'type': 'win_line',
            'cells': winning_cells,
            'progress': 0.0,
            'duration': 0.5,
            'start_time': time.time()
        })
    
    def add_confetti(self, winning_cells):
        """Add confetti particles for win celebration"""
        for cell in winning_cells:
            center_x = cell[1] * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = cell[0] * SQUARE_SIZE + SQUARE_SIZE // 2
            
            # Create multiple particles from each winning cell
            for _ in range(15):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 8)
                color = random.choice([
                    (255, 50, 50),    # Red
                    (50, 255, 50),    # Green
                    (50, 50, 255),    # Blue
                    (255, 255, 50),   # Yellow
                    (255, 50, 255),   # Purple
                    (50, 255, 255)    # Cyan
                ])
                
                self.particles.append({
                    'x': center_x,
                    'y': center_y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'color': color,
                    'size': random.randint(3, 8),
                    'life': 1.0,
                    'decay': random.uniform(0.02, 0.05)
                })
    
    def update(self):
        """Update all animations"""
        current_time = time.time()
        
        # Update progress-based animations
        for anim in self.animations[:]:
            elapsed = current_time - anim['start_time']
            anim['progress'] = min(elapsed / anim['duration'], 1.0)
            
            if anim['progress'] >= 1.0:
                self.animations.remove(anim)
        
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # Gravity
            particle['life'] -= particle['decay']
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw_animations(self, screen, board):
        """Draw all active animations"""
        for anim in self.animations:
            if anim['type'] == 'move':
                self.draw_move_animation(screen, anim, board)
            elif anim['type'] == 'win_line':
                self.draw_win_line_animation(screen, anim)
        
        # Draw particles
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            color = (*particle['color'][:3], alpha) if len(particle['color']) == 3 else particle['color']
            
            # Create a surface with alpha for the particle
            particle_surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, 
                             (particle['size'], particle['size']), 
                             particle['size'])
            screen.blit(particle_surf, 
                       (particle['x'] - particle['size'], 
                        particle['y'] - particle['size']))
    
    def draw_move_animation(self, screen, anim, board):
        """Draw animated piece placement"""
        row, col = anim['row'], anim['col']
        player = anim['player']
        progress = anim['progress']
        
        # Easing function for smoother animation
        ease_progress = 1 - (1 - progress) ** 3
        
        center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
        center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
        
        if player == 1:  # X animation
            # Draw X growing from center
            size = int(SQUARE_SIZE // 2.5 * ease_progress)
            width = int(15 * ease_progress)
            
            # Actually draw on the board since animation is done
            if progress >= 1.0:
                # Draw permanent X
                pygame.draw.line(screen, CROSS_COLOR,
                               (center_x - size, center_y - size),
                               (center_x + size, center_y + size), width)
                pygame.draw.line(screen, CROSS_COLOR,
                               (center_x - size, center_y + size),
                               (center_x + size, center_y - size), width)
            else:
                # Draw animated X
                color = CROSS_COLOR
                alpha = int(255 * ease_progress)
                if len(color) == 3:
                    color = (*color, alpha)
                
                # Create temporary surface for animation
                temp_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                pygame.draw.line(temp_surf, color,
                               (SQUARE_SIZE//2 - size, SQUARE_SIZE//2 - size),
                               (SQUARE_SIZE//2 + size, SQUARE_SIZE//2 + size), width)
                pygame.draw.line(temp_surf, color,
                               (SQUARE_SIZE//2 - size, SQUARE_SIZE//2 + size),
                               (SQUARE_SIZE//2 + size, SQUARE_SIZE//2 - size), width)
                
                screen.blit(temp_surf, (col * SQUARE_SIZE, row * SQUARE_SIZE))
        
        else:  # O animation
            # Draw O growing from center
            radius = int(SQUARE_SIZE // 3 * ease_progress)
            width = int(15 * ease_progress)
            
            if progress >= 1.0:
                # Draw permanent O
                pygame.draw.circle(screen, CIRCLE_COLOR,
                                 (center_x, center_y), radius, width)
            else:
                # Draw animated O
                color = CIRCLE_COLOR
                alpha = int(255 * ease_progress)
                if len(color) == 3:
                    color = (*color, alpha)
                
                temp_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, color,
                                 (SQUARE_SIZE//2, SQUARE_SIZE//2), radius, width)
                
                screen.blit(temp_surf, (col * SQUARE_SIZE, row * SQUARE_SIZE))
    
    def draw_win_line_animation(self, screen, anim):
        """Draw animated win line"""
        cells = anim['cells']
        if not cells:
            return
        
        progress = anim['progress']
        ease_progress = progress ** 2  # Different easing for line
        
        r1, c1 = cells[0]
        r2, c2 = cells[-1]
        
        start_x = c1 * SQUARE_SIZE + SQUARE_SIZE // 2
        start_y = r1 * SQUARE_SIZE + SQUARE_SIZE // 2
        end_x = c2 * SQUARE_SIZE + SQUARE_SIZE // 2
        end_y = r2 * SQUARE_SIZE + SQUARE_SIZE // 2
        
        # Calculate current line end based on progress
        current_x = start_x + (end_x - start_x) * ease_progress
        current_y = start_y + (end_y - start_y) * ease_progress
        
        # Draw pulsing win line
        line_width = 5 + int(3 * math.sin(time.time() * 10))  # Pulsing effect
        
        pygame.draw.line(screen, WIN_COLOR,
                        (start_x, start_y),
                        (current_x, current_y), line_width)
        
        # Draw glow effect at the end of the line
        if progress < 1.0:
            glow_radius = int(10 * (1 - abs(math.sin(time.time() * 5))))
            pygame.draw.circle(screen, (255, 100, 100),
                             (int(current_x), int(current_y)),
                             glow_radius, 2)

# Create global animation manager
animation_manager = Animation()

# -------------------- DRAW FUNCTIONS --------------------
def draw_lines():
    screen.fill(BG_COLOR)
    for i in range(1, 3):
        pygame.draw.line(screen, LINE_COLOR, (0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE), 5)
        pygame.draw.line(screen, LINE_COLOR, (i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, SQUARE_SIZE*3), 5)

def draw_figures(board):
    for r in range(3):
        for c in range(3):
            # Check if this cell is currently being animated
            is_animating = False
            for anim in animation_manager.animations:
                if anim['type'] == 'move' and anim['row'] == r and anim['col'] == c:
                    is_animating = True
                    break
            
            # Only draw if not animating (animation will draw it)
            if not is_animating and board[r][c] == 1:
                pygame.draw.line(screen, CROSS_COLOR,
                               (c*SQUARE_SIZE + 20, r*SQUARE_SIZE + 20),
                               (c*SQUARE_SIZE + SQUARE_SIZE - 20, r*SQUARE_SIZE + SQUARE_SIZE - 20), 20)
                pygame.draw.line(screen, CROSS_COLOR,
                               (c*SQUARE_SIZE + 20, r*SQUARE_SIZE + SQUARE_SIZE - 20),
                               (c*SQUARE_SIZE + SQUARE_SIZE - 20, r*SQUARE_SIZE + 20), 20)
            elif not is_animating and board[r][c] == 2:
                pygame.draw.circle(screen, CIRCLE_COLOR,
                                 (c*SQUARE_SIZE + SQUARE_SIZE//2, r*SQUARE_SIZE + SQUARE_SIZE//2),
                                 SQUARE_SIZE//3, 15)

def draw_winner_line(winning_cells):
    if winning_cells:
        r1, c1 = winning_cells[0]
        r2, c2 = winning_cells[2]
        start = (c1*SQUARE_SIZE + SQUARE_SIZE//2, r1*SQUARE_SIZE + SQUARE_SIZE//2)
        end = (c2*SQUARE_SIZE + SQUARE_SIZE//2, r2*SQUARE_SIZE + SQUARE_SIZE//2)
        pygame.draw.line(screen, WIN_COLOR, start, end, 5)

# -------------------- VISUAL IMPROVEMENTS --------------------
def draw_background_pattern():
    """Draw subtle background pattern"""
    # Draw grid lines
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, (20, 100, 90, 30), (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, (20, 100, 90, 30), (0, y), (WIDTH, y), 1)
    
    # Draw corner accents
    accent_color = (255, 255, 255, 50)
    pygame.draw.circle(screen, accent_color, (20, 20), 10, 2)
    pygame.draw.circle(screen, accent_color, (WIDTH-20, 20), 10, 2)
    pygame.draw.circle(screen, accent_color, (20, HEIGHT-20), 10, 2)
    pygame.draw.circle(screen, accent_color, (WIDTH-20, HEIGHT-20), 10, 2)

def draw_hover_effect(board, mouse_pos, player):
    """Show preview of move on hover"""
    if mouse_pos[1] < SQUARE_SIZE * 3:  # Only in game board
        row = mouse_pos[1] // SQUARE_SIZE
        col = mouse_pos[0] // SQUARE_SIZE
        
        if 0 <= row < 3 and 0 <= col < 3 and board[row][col] == 0:
            # Draw glowing hover effect
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            
            # Create pulsing glow
            pulse = abs(math.sin(time.time() * 5)) * 0.3 + 0.7
            
            if player == 1:  # Preview X with red glow
                glow_color = (255, 100, 100, int(100 * pulse))
                # Draw glow circle
                glow_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, glow_color, 
                                 (SQUARE_SIZE//2, SQUARE_SIZE//2),
                                 SQUARE_SIZE//3 + 5)
                screen.blit(glow_surf, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                
                # Draw transparent X preview
                preview_color = (*CROSS_COLOR, 150)
                pygame.draw.line(screen, preview_color,
                               (center_x - 30, center_y - 30),
                               (center_x + 30, center_y + 30), 12)
                pygame.draw.line(screen, preview_color,
                               (center_x - 30, center_y + 30),
                               (center_x + 30, center_y - 30), 12)
            else:  # Preview O with blue glow
                glow_color = (100, 100, 255, int(100 * pulse))
                # Draw glow circle
                glow_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, glow_color,
                                 (SQUARE_SIZE//2, SQUARE_SIZE//2),
                                 SQUARE_SIZE//3 + 5)
                screen.blit(glow_surf, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                
                # Draw transparent O preview
                preview_color = (*CIRCLE_COLOR, 150)
                pygame.draw.circle(screen, preview_color,
                                 (center_x, center_y),
                                 SQUARE_SIZE//3, 8)

def draw_highlight_last_move(row, col, player):
    """Highlight the last move made with a glowing effect"""
    if row is None or col is None:
        return
    
    center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
    center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
    
    # Create pulsing highlight
    pulse = abs(math.sin(time.time() * 4)) * 0.4 + 0.6
    
    if player == 1:  # X move - red highlight
        highlight_color = (255, 100, 100, int(80 * pulse))
    else:  # O move - blue highlight
        highlight_color = (100, 100, 255, int(80 * pulse))
    
    # Draw highlight circle
    highlight_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(highlight_surf, highlight_color,
                     (SQUARE_SIZE//2, SQUARE_SIZE//2),
                     SQUARE_SIZE//2 - 5, 3)
    screen.blit(highlight_surf, (col * SQUARE_SIZE, row * SQUARE_SIZE))

def draw_pulsing_turn_indicator(player):
    """Draw pulsing indicator for current player"""
    pulse = abs(math.sin(time.time() * 3)) * 0.3 + 0.7  # 0.7 to 1.0 pulse
    
    indicator_y = 40  # Position below the board
    
    if player == 1:  # X's turn
        color = (int(255 * pulse), 100, 100)  # Pulsing red
        # Draw X icon with pulse
        x_size = int(20 * pulse)
        pygame.draw.line(screen, color, 
                        (WIDTH//2 - x_size - 60, indicator_y),
                        (WIDTH//2 - x_size - 20, indicator_y + 40), 8)
        pygame.draw.line(screen, color,
                        (WIDTH//2 - x_size - 60, indicator_y + 40),
                        (WIDTH//2 - x_size - 20, indicator_y), 8)
        
        text = font.render("Your Turn", True, color)
        screen.blit(text, (WIDTH//2 - 30, indicator_y + 10))
    else:  # O's turn
        color = (100, 100, int(255 * pulse))  # Pulsing blue
        # Draw O icon with pulse
        radius = int(20 * pulse)
        pygame.draw.circle(screen, color,
                         (WIDTH//2 - 40, indicator_y + 20),
                         radius, 6)
        
        text = font.render("AI's Turn", True, color)
        screen.blit(text, (WIDTH//2 - 30, indicator_y + 10))

def draw_move_stats(move_history):
    """Show statistics about the current game - MINIMAL VERSION (Bigger)"""
    if len(move_history) > 0:
        total_moves = len(move_history)
        human_moves = sum(1 for _, _, p in move_history if p == 1)
        ai_moves = total_moves - human_moves
        
        # Use a slightly larger font
        stats_font = pygame.font.SysFont(None, 22)  # Increased from 18 to 22
        stats_text = f"Moves: {total_moves}  (X:{human_moves}  O:{ai_moves})"
        text = stats_font.render(stats_text, True, (240, 240, 240))  # Brighter white
        
        # Position it a bit higher and more centered
        text_x = 130  # Slight indent from left
        text_y = HEIGHT - 120  # Moved up from 90 to 85
        
        screen.blit(text, (text_x, text_y))
        
        # Optional: Add subtle background for better readability
        text_rect = text.get_rect(topleft=(text_x, text_y))
        bg_rect = text_rect.inflate(10, 6)  # Add padding around text
        pygame.draw.rect(screen, (40, 40, 40, 150), bg_rect, border_radius=4)
        pygame.draw.rect(screen, (80, 80, 80), bg_rect, 1, border_radius=4)
        
        # Draw text on top of background
        screen.blit(text, (text_x, text_y))
# -------------------- BUTTONS --------------------
def draw_difficulty_buttons(selected=None, mouse_pos=None):
    easy_color = SELECTED_COLOR if selected == 'easy' else BUTTON_COLOR
    medium_color = SELECTED_COLOR if selected == 'medium' else BUTTON_COLOR
    hard_color = SELECTED_COLOR if selected == 'hard' else BUTTON_COLOR

    if mouse_pos:
        if pygame.Rect(20, 410, 100, 50).collidepoint(mouse_pos) and selected != 'easy':
            easy_color = BUTTON_HOVER_COLOR
        if pygame.Rect(150, 410, 100, 50).collidepoint(mouse_pos) and selected != 'medium':
            medium_color = BUTTON_HOVER_COLOR
        if pygame.Rect(280, 410, 100, 50).collidepoint(mouse_pos) and selected != 'hard':
            hard_color = BUTTON_HOVER_COLOR

    easy_btn = pygame.Rect(20, 410, 100, 50)
    medium_btn = pygame.Rect(150, 410, 100, 50)
    hard_btn = pygame.Rect(280, 410, 100, 50)

    pygame.draw.rect(screen, easy_color, easy_btn, border_radius=8)
    pygame.draw.rect(screen, medium_color, medium_btn, border_radius=8)
    pygame.draw.rect(screen, hard_color, hard_btn, border_radius=8)

    screen.blit(font.render("Easy", True, BUTTON_TEXT_COLOR), (45, 425))
    screen.blit(font.render("Medium", True, BUTTON_TEXT_COLOR), (160, 425))
    screen.blit(font.render("Hard", True, BUTTON_TEXT_COLOR), (300, 425))

    return easy_btn, medium_btn, hard_btn

def draw_game_buttons(mouse_pos=None):
    restart_color = BUTTON_COLOR
    quit_color = BUTTON_COLOR

    if mouse_pos:
        if pygame.Rect(50, 470, 120, 50).collidepoint(mouse_pos):
            restart_color = BUTTON_HOVER_COLOR
        if pygame.Rect(230, 470, 120, 50).collidepoint(mouse_pos):
            quit_color = BUTTON_HOVER_COLOR

    restart_btn = pygame.Rect(50, 470, 120, 50)
    quit_btn = pygame.Rect(230, 470, 120, 50)
    pygame.draw.rect(screen, restart_color, restart_btn, border_radius=8)
    pygame.draw.rect(screen, quit_color, quit_btn, border_radius=8)
    screen.blit(font.render("Restart", True, BUTTON_TEXT_COLOR), (75, 485))
    screen.blit(font.render("Quit", True, BUTTON_TEXT_COLOR), (270, 485))
    return restart_btn, quit_btn

def draw_undo_button(mouse_pos=None):
    # Position in bottom right corner - smaller button
    undo_x = WIDTH - 35  # 35px from right edge
    undo_y = HEIGHT - 90  # 90px from bottom
    radius = 18  # Smaller radius (was 25)
    
    # Calculate distance from mouse to button center for hover detection
    is_hovering = False
    if mouse_pos:
        distance = ((mouse_pos[0] - undo_x) ** 2 + (mouse_pos[1] - undo_y) ** 2) ** 0.5
        is_hovering = distance <= radius
    
    # Draw the circular undo button
    color = UNDO_HOVER_COLOR if is_hovering else UNDO_COLOR
    pygame.draw.circle(screen, color, (undo_x, undo_y), radius)
    
    # Draw a circular outline
    pygame.draw.circle(screen, (255, 255, 255), (undo_x, undo_y), radius, 2)
    
    # Use tiny font for the smaller button
    text = tiny_font.render("Undo", True, UNDO_TEXT_COLOR)
    text_rect = text.get_rect(center=(undo_x, undo_y))
    screen.blit(text, text_rect)
    
    # Return the center coordinates and radius for collision detection
    return {'center': (undo_x, undo_y), 'radius': radius}

# -------------------- TIMER FUNCTIONS --------------------
def draw_timer_buttons(timer_mode='no_timer', mouse_pos=None):
    """Draw timer mode selection buttons"""
    timer_modes = [
        ('no_timer', 'No Timer', TIMER_NO_COLOR),
        ('relaxed', 'Relaxed', TIMER_RELAXED_COLOR),
        ('normal', 'Normal', TIMER_NORMAL_COLOR),
        ('speed', 'Speed', TIMER_SPEED_COLOR)
    ]
    
    buttons = {}
    start_x = 20
    start_y = 580  # Moved down to make room
    btn_width = 90
    btn_height = 30
    
    for i, (mode_id, mode_name, color) in enumerate(timer_modes):
        btn_x = start_x + i * (btn_width + 5)
        btn_rect = pygame.Rect(btn_x, start_y, btn_width, btn_height)
        buttons[mode_id] = btn_rect
        
        # Check for hover
        is_hovering = False
        if mouse_pos and btn_rect.collidepoint(mouse_pos):
            is_hovering = True
        
        # Draw button
        if timer_mode == mode_id:
            # Selected button
            pygame.draw.rect(screen, color, btn_rect, border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255), btn_rect, 2, border_radius=5)
        else:
            # Unselected button
            btn_color = (color[0]//2, color[1]//2, color[2]//2) if not is_hovering else color
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=5)
            pygame.draw.rect(screen, (100, 100, 100), btn_rect, 1, border_radius=5)
        
        # Draw button text
        text = very_small_font.render(mode_name, True, (255, 255, 255))
        text_rect = text.get_rect(center=btn_rect.center)
        screen.blit(text, text_rect)
    
    return buttons

def draw_timer_display(time_left=None, timer_expired=False, timer_mode='no_timer'):
    """Draw the timer countdown display"""
    if timer_mode == 'no_timer':
        return
    
    # Timer background - moved up
    timer_bg = pygame.Rect(WIDTH - 120, 5, 110, 40)
    pygame.draw.rect(screen, TIMER_BG_COLOR, timer_bg, border_radius=5)
    pygame.draw.rect(screen, (100, 100, 100), timer_bg, 2, border_radius=5)
    
    # Format time
    def format_time(seconds):
        if seconds is None:
            return "--:--"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    # Determine timer color
    time_color = TIMER_TEXT_COLOR
    if time_left is not None:
        if time_left < 5:
            time_color = TIMER_WARNING_COLOR  # Red when less than 5 seconds
        elif time_left < 10:
            time_color = TIMER_NORMAL_COLOR  # Orange when less than 10 seconds
    
    # Draw timer text - adjusted y position
    timer_text = font.render(format_time(time_left), True, time_color)
    screen.blit(timer_text, (WIDTH - 100, 15))
    
    # Draw timer label - adjusted y position
    label_text = font.render("Time:", True, TIMER_TEXT_COLOR)
    screen.blit(label_text, (WIDTH - 180, 10))
    
    # Draw warning if time is running out - adjusted y position
    if timer_expired:
        warning_text = font.render("TIME'S UP!", True, TIMER_WARNING_COLOR)
        screen.blit(warning_text, (WIDTH - 180, 45))

def draw_timer_visual(time_left, timer_mode):
    """Draw visual timer bar"""
    if timer_mode == 'no_timer' or time_left is None:
        return
    
    # We need TIMER_MODES from main.py, but we'll handle it differently
    # This function will be called from main.py where TIMER_MODES is available
    
    # Draw timer bar at top
    bar_width = 200
    bar_height = 8
    bar_x = WIDTH // 2 - bar_width // 2
    bar_y = 5
    
    # Background
    pygame.draw.rect(screen, (50, 50, 50), 
                    (bar_x, bar_y, bar_width, bar_height), 
                    border_radius=4)
    
    # We'll fill the bar in main.py where we have the percentage
    return bar_x, bar_y, bar_width, bar_height

# -------------------- SCOREBOARD & INFO --------------------
def draw_scoreboard(score):
    text = font.render(f"X: {score[1]}  O: {score[2]}  Ties: {score[0]}", True, (255, 255, 255))
    screen.blit(text, (120, 350))

def draw_current_turn(player, timer_mode='no_timer', time_left=None):
    """Draw current turn indicator with optional timer info"""
    turn_text = f"Current Turn: {'X' if player==1 else 'O'}"
    
    # Add timer info if timer is active
    if timer_mode != 'no_timer' and time_left is not None and player == 1:
        turn_text += f" ({int(time_left)}s)"
    
    text = font.render(turn_text, True, (255, 255, 255))
    screen.blit(text, (30, 5))

def draw_difficulty_text(ai_level):
    if ai_level:
        # Use smaller font
        small_text = small_font.render(f"Difficulty: {ai_level.capitalize()}", True, (255, 255, 255))
        screen.blit(small_text, (130, 555))

# Export all functions and variables
__all__ = [
    'screen', 'draw_lines', 'draw_figures', 'draw_winner_line', 
    'draw_game_buttons', 'draw_scoreboard', 'draw_difficulty_buttons', 
    'draw_current_turn', 'draw_difficulty_text', 'draw_undo_button',
    'draw_timer_buttons', 'draw_timer_display', 'draw_timer_visual',
    'draw_background_pattern', 'draw_hover_effect', 'draw_highlight_last_move',
    'draw_pulsing_turn_indicator', 'draw_move_stats',
    'SQUARE_SIZE', 'WIDTH', 'HEIGHT', 'font', 'animation_manager'
]
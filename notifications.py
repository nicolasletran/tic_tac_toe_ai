# notifications.py
import pygame

class NotificationRenderer:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.small_font = pygame.font.SysFont(None, 24)
    
    def draw_notifications(self, notifications):
        """Draw achievement notifications on screen"""
        notification_height = 70
        start_y = 100
        
        for i, notif in enumerate(notifications[:3]):  # Show max 3 at once
            elapsed = time.time() - notif['time']
            duration = notif['duration']
            
            # Calculate fade in/out
            if elapsed < 0.5:  # Fade in
                alpha = int(255 * (elapsed / 0.5))
            elif elapsed > duration - 0.5:  # Fade out
                alpha = int(255 * ((duration - elapsed) / 0.5))
            else:
                alpha = 255
            
            y_pos = start_y + i * (notification_height + 10)
            
            # Draw notification background
            bg_rect = pygame.Rect(20, y_pos, 360, notification_height)
            pygame.draw.rect(self.screen, (40, 40, 40, alpha), bg_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100, 100, 100, alpha), bg_rect, 2, border_radius=10)
            
            # Add achievement icon
            if 'icon' in notif:
                icon_text = self.font.render(notif['icon'], True, (255, 215, 0, alpha))
                self.screen.blit(icon_text, (40, y_pos + 15))
            
            # Draw achievement name
            if 'name' in notif:
                name_color = (255, 215, 0, alpha)  # Gold color for achievement names
                name_text = self.font.render(notif['name'], True, name_color)
                self.screen.blit(name_text, (80, y_pos + 15))
            
            # Draw description
            if 'description' in notif:
                desc_color = (200, 200, 200, alpha)
                desc_text = self.small_font.render(notif['description'], True, desc_color)
                self.screen.blit(desc_text, (80, y_pos + 45))
            elif 'text' in notif:
                text_color = (255, 255, 255, alpha)
                text_display = self.small_font.render(notif['text'], True, text_color)
                self.screen.blit(text_display, (40, y_pos + 40))
            
            # Draw progress bar for notification duration
            progress = elapsed / duration
            progress_width = 320
            progress_rect = pygame.Rect(40, y_pos + notification_height - 8, 
                                      int(progress_width * progress), 4)
            pygame.draw.rect(self.screen, (100, 200, 100, alpha), progress_rect, border_radius=2)
    
    def draw_achievements_menu(self, achievements, unlocked_count, total_count):
        """Draw achievements menu screen"""
        # Draw background
        self.screen.fill((30, 70, 70))
        
        # Draw title
        title_text = self.font.render("ACHIEVEMENTS", True, (255, 255, 255))
        self.screen.blit(title_text, (WIDTH//2 - 100, 20))
        
        # Draw progress
        progress_text = self.small_font.render(f"Unlocked: {unlocked_count}/{total_count}", 
                                             True, (200, 200, 200))
        self.screen.blit(progress_text, (WIDTH//2 - 60, 60))
        
        # Draw progress bar
        progress_width = 300
        progress_filled = int(progress_width * (unlocked_count / total_count))
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (WIDTH//2 - progress_width//2, 90, progress_width, 20),
                        border_radius=10)
        pygame.draw.rect(self.screen, (100, 200, 100),
                        (WIDTH//2 - progress_width//2, 90, progress_filled, 20),
                        border_radius=10)
        
        # Draw achievements list
        y_pos = 130
        for i, (achievement_id, achievement) in enumerate(achievements.items()):
            if y_pos > HEIGHT - 100:
                break
                
            achievement_rect = pygame.Rect(30, y_pos, WIDTH - 60, 60)
            
            if achievement['unlocked']:
                # Draw unlocked achievement
                pygame.draw.rect(self.screen, (60, 120, 60, 200), 
                               achievement_rect, border_radius=8)
                pygame.draw.rect(self.screen, (100, 200, 100), 
                               achievement_rect, 2, border_radius=8)
                icon_color = (255, 215, 0)
                text_color = (255, 255, 255)
            else:
                # Draw locked achievement
                pygame.draw.rect(self.screen, (60, 60, 60, 200), 
                               achievement_rect, border_radius=8)
                pygame.draw.rect(self.screen, (100, 100, 100), 
                               achievement_rect, 2, border_radius=8)
                icon_color = (100, 100, 100)
                text_color = (150, 150, 150)
            
            # Draw icon
            icon_text = self.font.render(achievement['icon'], True, icon_color)
            self.screen.blit(icon_text, (50, y_pos + 15))
            
            # Draw name
            name_text = self.font.render(achievement['name'], True, text_color)
            self.screen.blit(name_text, (90, y_pos + 10))
            
            # Draw description
            desc_text = self.small_font.render(achievement['description'], True, text_color)
            self.screen.blit(desc_text, (90, y_pos + 35))
            
            # Draw lock icon for locked achievements
            if not achievement['unlocked']:
                lock_text = self.font.render("🔒", True, (150, 150, 150))
                self.screen.blit(lock_text, (WIDTH - 70, y_pos + 15))
            elif achievement.get('unlock_date'):
                # Show date unlocked
                date_str = achievement['unlock_date'][:10]  # Just YYYY-MM-DD
                date_text = self.small_font.render(date_str, True, (200, 200, 200))
                self.screen.blit(date_text, (WIDTH - 120, y_pos + 20))
            
            y_pos += 70
# achievements.py
import json
import time
from datetime import datetime

class AchievementManager:
    def __init__(self):
        self.achievements = self.load_achievements()
        self.current_game_stats = {
            'start_time': time.time(),
            'moves': 0,
            'human_moves': 0,
            'ai_moves': 0,
            'consecutive_wins': 0,
            'winning_moves': [],
            'timer_mode': 'no_timer',
            'difficulty': None
        }
        self.active_notifications = []
    
    def load_achievements(self):
        """Load achievements from file or create default ones"""
        try:
            with open('achievements.json', 'r') as f:
                return json.load(f)
        except:
            # Create default achievements
            return {
                'first_win': {
                    'unlocked': False,
                    'name': 'First Victory',
                    'description': 'Win your first game against the AI',
                    'icon': '🏆',
                    'unlock_date': None
                },
                'speed_demon': {
                    'unlocked': False,
                    'name': 'Speed Demon',
                    'description': 'Win a game in Speed mode (3s timer)',
                    'icon': '⚡',
                    'unlock_date': None
                },
                'perfectionist': {
                    'unlocked': False,
                    'name': 'Perfectionist',
                    'description': 'Win without the AI making a single move',
                    'icon': '🎯',
                    'unlock_date': None
                },
                'comeback_kid': {
                    'unlocked': False,
                    'name': 'Comeback Kid',
                    'description': 'Win after being 1 move away from losing',
                    'icon': '🔥',
                    'unlock_date': None
                },
                'streak_master': {
                    'unlocked': False,
                    'name': 'Streak Master',
                    'description': 'Win 3 games in a row',
                    'icon': '⭐',
                    'unlock_date': None
                },
                'undo_expert': {
                    'unlocked': False,
                    'name': 'Second Chance',
                    'description': 'Use undo and still win the game',
                    'icon': '↶',
                    'unlock_date': None
                },
                'difficulty_master': {
                    'unlocked': False,
                    'name': 'Master Player',
                    'description': 'Win against Hard AI',
                    'icon': '👑',
                    'unlock_date': None
                },
                'fast_thinker': {
                    'unlocked': False,
                    'name': 'Fast Thinker',
                    'description': 'Win with more than 10 seconds left on timer',
                    'icon': '⏱️',
                    'unlock_date': None
                },
                'draw_specialist': {
                    'unlocked': False,
                    'name': 'Draw Specialist',
                    'description': 'Achieve 3 draws in one session',
                    'icon': '🤝',
                    'unlock_date': None
                },
                'ai_annihilator': {
                    'unlocked': False,
                    'name': 'AI Annihilator',
                    'description': 'Win 10 games total',
                    'icon': '💥',
                    'unlock_date': None
                }
            }
    
    def save_achievements(self):
        """Save achievements to file"""
        with open('achievements.json', 'w') as f:
            json.dump(self.achievements, f, indent=2)
    
    def update_game_stats(self, **kwargs):
        """Update current game statistics"""
        for key, value in kwargs.items():
            if key in self.current_game_stats:
                self.current_game_stats[key] = value
    
    def check_achievements(self, winner, score, game_duration, time_left=None):
        """Check and unlock achievements based on game results"""
        newly_unlocked = []
        
        # Track win streak
        if winner == 1:  # Human won
            self.current_game_stats['consecutive_wins'] += 1
        else:
            self.current_game_stats['consecutive_wins'] = 0
        
        # Check individual achievements
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
        
        # Save achievements after checking
        self.save_achievements()
        
        # Reset game stats for next game
        self.current_game_stats = {
            'start_time': time.time(),
            'moves': 0,
            'human_moves': 0,
            'ai_moves': 0,
            'consecutive_wins': self.current_game_stats['consecutive_wins'],
            'winning_moves': [],
            'timer_mode': self.current_game_stats['timer_mode'],
            'difficulty': self.current_game_stats['difficulty']
        }
        
        return newly_unlocked
    
    def unlock_achievement(self, achievement_id):
        """Unlock a specific achievement"""
        if achievement_id in self.achievements and not self.achievements[achievement_id]['unlocked']:
            self.achievements[achievement_id]['unlocked'] = True
            self.achievements[achievement_id]['unlock_date'] = datetime.now().isoformat()
            
            # Add notification
            achievement = self.achievements[achievement_id]
            self.active_notifications.append({
                'id': achievement_id,
                'name': achievement['name'],
                'icon': achievement['icon'],
                'description': achievement['description'],
                'time': time.time(),
                'duration': 5  # seconds
            })
            
            print(f"\n🎉 ACHIEVEMENT UNLOCKED: {achievement['icon']} {achievement['name']}")
            print(f"   {achievement['description']}")
    
    def add_notification(self, text, duration=3):
        """Add a custom notification"""
        self.active_notifications.append({
            'text': text,
            'time': time.time(),
            'duration': duration
        })
    
    def update_notifications(self):
        """Update and remove expired notifications"""
        current_time = time.time()
        self.active_notifications = [
            notif for notif in self.active_notifications
            if current_time - notif['time'] < notif['duration']
        ]
    
    def get_unlocked_count(self):
        """Get count of unlocked achievements"""
        return sum(1 for a in self.achievements.values() if a['unlocked'])
    
    def get_total_count(self):
        """Get total number of achievements"""
        return len(self.achievements)

# Create a global instance
achievement_manager = AchievementManager()
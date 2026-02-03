# sounds.py
import pygame
import numpy  # ADD THIS LINE

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.load_sounds()
    
    def load_sounds(self):
        # Create simple sounds programmatically (no external files needed)
        self.create_beep_sounds()
    
    def create_beep_sounds(self):
        # Create simple beep sounds using pygame's generate function
        
        # Click sound (short high beep)
        click_sound = pygame.mixer.Sound(buffer=self.generate_beep(800, 0.1))
        self.sounds['click'] = click_sound
        
        # Move sound (mid beep)
        move_sound = pygame.mixer.Sound(buffer=self.generate_beep(600, 0.15))
        self.sounds['move'] = move_sound
        
        # Win sound (rising tone)
        win_sound = pygame.mixer.Sound(buffer=self.generate_win_sound())
        self.sounds['win'] = win_sound
        
        # Lose sound (falling tone)
        lose_sound = pygame.mixer.Sound(buffer=self.generate_lose_sound())
        self.sounds['lose'] = lose_sound
        
        # Draw sound (two tones)
        draw_sound = pygame.mixer.Sound(buffer=self.generate_draw_sound())
        self.sounds['draw'] = draw_sound
        
        # Undo sound (rewind sound)
        undo_sound = pygame.mixer.Sound(buffer=self.generate_beep(400, 0.2))
        self.sounds['undo'] = undo_sound
        
        # Timer warning (urgent beep)
        timer_sound = pygame.mixer.Sound(buffer=self.generate_beep(1000, 0.08))
        self.sounds['timer_warning'] = timer_sound
    
    def generate_beep(self, frequency, duration):
        """Generate a simple sine wave beep"""
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        
        # Create the sine wave
        buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
        max_sample = 2**(16 - 1) - 1
        
        for s in range(n_samples):
            t = float(s) / sample_rate
            sine_value = numpy.sin(2 * numpy.pi * frequency * t)
            
            # Apply fade in/out
            fade = 1.0
            if s < sample_rate * 0.05:  # Fade in
                fade = s / (sample_rate * 0.05)
            elif s > n_samples - sample_rate * 0.05:  # Fade out
                fade = (n_samples - s) / (sample_rate * 0.05)
            
            val = int(max_sample * fade * sine_value)
            buf[s][0] = val  # Left channel
            buf[s][1] = val  # Right channel
        
        return buf
    
    def generate_win_sound(self):
        """Generate rising victory sound"""
        sample_rate = 22050
        duration = 0.8
        n_samples = int(sample_rate * duration)
        
        buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
        max_sample = 2**(16 - 1) - 1
        
        for s in range(n_samples):
            t = float(s) / sample_rate
            # Rising frequency from 300 to 800 Hz
            freq = 300 + (500 * (t / duration))
            sine_value = numpy.sin(2 * numpy.pi * freq * t)
            
            # Volume envelope
            fade = 1.0
            if s < sample_rate * 0.1:
                fade = s / (sample_rate * 0.1)
            elif s > n_samples - sample_rate * 0.2:
                fade = (n_samples - s) / (sample_rate * 0.2)
            
            val = int(max_sample * fade * sine_value * 0.7)
            buf[s][0] = val
            buf[s][1] = val
        
        return buf
    
    def generate_lose_sound(self):
        """Generate falling defeat sound"""
        sample_rate = 22050
        duration = 0.6
        n_samples = int(sample_rate * duration)
        
        buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
        max_sample = 2**(16 - 1) - 1
        
        for s in range(n_samples):
            t = float(s) / sample_rate
            # Falling frequency from 600 to 200 Hz
            freq = 600 - (400 * (t / duration))
            sine_value = numpy.sin(2 * numpy.pi * freq * t)
            
            # Volume envelope
            fade = 1.0
            if s < sample_rate * 0.1:
                fade = s / (sample_rate * 0.1)
            elif s > n_samples - sample_rate * 0.1:
                fade = (n_samples - s) / (sample_rate * 0.1)
            
            val = int(max_sample * fade * sine_value * 0.7)
            buf[s][0] = val
            buf[s][1] = val
        
        return buf
    
    def generate_draw_sound(self):
        """Generate two-tone draw sound"""
        sample_rate = 22050
        duration = 0.5
        n_samples = int(sample_rate * duration)
        
        buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
        max_sample = 2**(16 - 1) - 1
        
        for s in range(n_samples):
            t = float(s) / sample_rate
            
            # First half: 400Hz, second half: 500Hz
            if t < duration / 2:
                freq = 400
            else:
                freq = 500
            
            sine_value = numpy.sin(2 * numpy.pi * freq * t)
            
            # Volume envelope
            fade = 1.0
            if s < sample_rate * 0.1:
                fade = s / (sample_rate * 0.1)
            elif s > n_samples - sample_rate * 0.1:
                fade = (n_samples - s) / (sample_rate * 0.1)
            
            val = int(max_sample * fade * sine_value * 0.7)
            buf[s][0] = val
            buf[s][1] = val
        
        return buf
    
    def play(self, sound_name, volume=0.5):
        """Play a sound by name"""
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play()
    
    def play_click(self):
        self.play('click', 0.3)
    
    def play_move(self):
        self.play('move', 0.4)
    
    def play_win(self):
        self.play('win', 0.6)
    
    def play_lose(self):
        self.play('lose', 0.6)
    
    def play_draw(self):
        self.play('draw', 0.5)
    
    def play_undo(self):
        self.play('undo', 0.4)
    
    def play_timer_warning(self):
        self.play('timer_warning', 0.5)
import pygame
import math
import array

class SoundManager:
    """Manages sound effects and music for the game"""
    
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self._initialize_pygame_mixer()
        self._create_blob_sound()
    
    def _initialize_pygame_mixer(self):
        """Initialize pygame mixer for sound playback"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except pygame.error:
            # If mixer initialization fails (e.g., no audio device), disable sounds
            self.enabled = False
    
    def _create_blob_sound(self):
        """Create a simple blob sound effect programmatically"""
        if not self.enabled:
            return
            
        try:
            # Create a simple "bloop" sound using basic math
            sample_rate = 22050
            duration = 0.3  # 300ms
            samples = int(sample_rate * duration)
            
            # Create sound wave array
            wave_array = array.array('h')
            
            for i in range(samples):
                # Time in seconds
                t = i / sample_rate
                
                # Create a sine wave at 440Hz that fades out
                frequency = 440.0 - (t * 200)  # Pitch slides down
                amplitude = 8000 * (1 - t * 3)  # Fade out
                
                if amplitude < 0:
                    amplitude = 0
                
                # Generate sine wave sample
                sample = int(amplitude * math.sin(2 * math.pi * frequency * t))
                
                # Add to stereo array (left and right channels)
                wave_array.append(sample)
                wave_array.append(sample)
            
            # Create pygame sound from array
            self.sounds['blob'] = pygame.sndarray.make_sound(wave_array)
            
        except (pygame.error, AttributeError, Exception):
            # If sound creation fails, just disable sounds
            self.enabled = False
    
    def play_blob_sound(self):
        """Play the blob sound effect when a new employee is hired"""
        if self.enabled and 'blob' in self.sounds:
            try:
                self.sounds['blob'].play()
            except pygame.error:
                # Sound playback failed, but don't crash
                pass
    
    def set_enabled(self, enabled):
        """Enable or disable all sound effects"""
        self.enabled = enabled
    
    def is_enabled(self):
        """Check if sounds are currently enabled"""
        return self.enabled
    
    def toggle(self):
        """Toggle sound on/off and return new state"""
        self.enabled = not self.enabled
        return self.enabled
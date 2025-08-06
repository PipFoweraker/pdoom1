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
            
            # Create error beep sound for easter egg
            self._create_error_beep()
            
            # Create AP spend sound for enhanced feedback
            self._create_ap_spend_sound()
            
            # Create Zabinga sound for research paper completion
            self._create_zabinga_sound()
            
        except (pygame.error, AttributeError, Exception):
            # If sound creation fails, just disable sounds
            self.enabled = False
    
    def _create_error_beep(self):
        """Create an error beep sound for the easter egg (3 repeated errors)"""
        if not self.enabled:
            return
            
        try:
            sample_rate = 22050
            duration = 0.5  # 500ms
            samples = int(sample_rate * duration)
            
            # Create sound wave array for error beep
            wave_array = array.array('h')
            
            for i in range(samples):
                t = i / sample_rate
                
                # Create a harsher, more attention-grabbing sound
                # Three quick beeps with rising pitch
                beep_duration = 0.15
                beep_spacing = 0.17
                
                amplitude = 0
                if t < beep_duration:
                    # First beep at 800Hz
                    frequency = 800
                    amplitude = 6000 * (1 - (t / beep_duration) * 0.5)
                elif beep_spacing < t < beep_spacing + beep_duration:
                    # Second beep at 1000Hz
                    frequency = 1000
                    t_rel = t - beep_spacing
                    amplitude = 6000 * (1 - (t_rel / beep_duration) * 0.5)
                elif 2 * beep_spacing < t < 2 * beep_spacing + beep_duration:
                    # Third beep at 1200Hz
                    frequency = 1200
                    t_rel = t - 2 * beep_spacing
                    amplitude = 6000 * (1 - (t_rel / beep_duration) * 0.5)
                
                if amplitude > 0:
                    sample = int(amplitude * math.sin(2 * math.pi * frequency * t))
                else:
                    sample = 0
                
                # Add to stereo array
                wave_array.append(sample)
                wave_array.append(sample)
            
            # Create pygame sound from array
            self.sounds['error_beep'] = pygame.sndarray.make_sound(wave_array)
            
        except (pygame.error, AttributeError, Exception):
            # If error beep creation fails, continue without it
            pass
    
    def _create_ap_spend_sound(self):
        """Create a sound effect for when Action Points are spent"""
        if not self.enabled:
            return
            
        try:
            sample_rate = 22050
            duration = 0.2  # 200ms - short and crisp
            samples = int(sample_rate * duration)
            
            # Create sound wave array for AP spend
            wave_array = array.array('h')
            
            for i in range(samples):
                t = i / sample_rate
                
                # Create a satisfying "click" or "ding" sound
                # Rising pitch with quick decay
                frequency = 800 + (t * 400)  # Pitch rises from 800Hz to 1200Hz
                amplitude = 4000 * math.exp(-t * 8)  # Quick exponential decay
                
                # Add some harmonic richness
                sample = int(amplitude * (
                    math.sin(2 * math.pi * frequency * t) +
                    0.3 * math.sin(2 * math.pi * frequency * 2 * t)  # Second harmonic
                ))
                
                # Add to stereo array
                wave_array.append(sample)
                wave_array.append(sample)
            
            # Create pygame sound from array
            self.sounds['ap_spend'] = pygame.sndarray.make_sound(wave_array)
            
        except (pygame.error, AttributeError, Exception):
            # If AP sound creation fails, continue without it
            pass
    
    def _create_zabinga_sound(self):
        """Create a celebratory 'Zabinga!' sound effect for research paper completion"""
        if not self.enabled:
            return
            
        try:
            sample_rate = 22050
            duration = 1.0  # 1 second - celebratory sound should be noticeable
            samples = int(sample_rate * duration)
            
            # Create sound wave array for Zabinga sound
            wave_array = array.array('h')
            
            for i in range(samples):
                t = i / sample_rate
                
                # Create a fun, celebratory sound with multiple tones
                # Rising and falling melody to sound like "Za-bin-ga!"
                amplitude = 3000
                
                if t < 0.25:  # "Za" - lower tone
                    frequency = 440  # A4
                    envelope = math.sin(math.pi * t / 0.25)  # Smooth attack and decay
                elif t < 0.5:  # "bin" - higher tone
                    frequency = 554  # C#5
                    envelope = math.sin(math.pi * (t - 0.25) / 0.25)
                elif t < 0.75:  # "ga" - middle tone with vibrato
                    frequency = 494 + 20 * math.sin(2 * math.pi * 8 * t)  # B4 with vibrato
                    envelope = math.sin(math.pi * (t - 0.5) / 0.25)
                else:  # Final flourish - quick ascending notes
                    base_freq = 440 * (1 + 2 * (t - 0.75))  # Rising pitch
                    frequency = base_freq
                    envelope = math.exp(-8 * (t - 0.75))  # Quick decay
                
                # Generate the sample with harmonic richness
                sample = int(amplitude * envelope * (
                    math.sin(2 * math.pi * frequency * t) +
                    0.3 * math.sin(2 * math.pi * frequency * 2 * t) +  # Second harmonic
                    0.15 * math.sin(2 * math.pi * frequency * 3 * t)   # Third harmonic
                ))
                
                # Add to stereo array
                wave_array.append(sample)
                wave_array.append(sample)
            
            # Create pygame sound from array
            self.sounds['zabinga'] = pygame.sndarray.make_sound(wave_array)
            
        except (pygame.error, AttributeError, Exception):
            # If Zabinga sound creation fails, continue without it
            pass
    
    def play_blob_sound(self):
        """Play the blob sound effect when a new employee is hired"""
        if self.enabled and 'blob' in self.sounds:
            try:
                self.sounds['blob'].play()
            except pygame.error:
                # Sound playback failed, but don't crash
                pass
    
    def play_error_beep(self):
        """Play the error beep sound for the easter egg (3 repeated identical errors)"""
        if self.enabled and 'error_beep' in self.sounds:
            try:
                self.sounds['error_beep'].play()
            except pygame.error:
                # Sound playback failed, but don't crash
                pass
    
    def play_ap_spend_sound(self):
        """Play the AP spend sound effect when Action Points are spent"""
        if self.enabled and 'ap_spend' in self.sounds:
            try:
                self.sounds['ap_spend'].play()
            except pygame.error:
                # Sound playback failed, but don't crash
                pass
    
    def play_zabinga_sound(self):
        """Play the Zabinga sound effect when research papers are completed"""
        if self.enabled and 'zabinga' in self.sounds:
            try:
                self.sounds['zabinga'].play()
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
import pygame
import math
import array

class SoundManager:
    """Manages sound effects and music for the game"""
    
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        # Individual sound toggles for granular control
        self.sound_toggles = {
            'money_spend': True,
            'ap_spend': True,
            'blob': True,
            'error_beep': True
        }
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
            
            # Create money spend sound for purchase feedback
            self._create_money_spend_sound()
            
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
    
    def _create_money_spend_sound(self):
        """Create a happy sound effect for when money is spent"""
        if not self.enabled:
            return
            
        try:
            sample_rate = 22050
            duration = 0.4  # 400ms - slightly longer for happiness
            samples = int(sample_rate * duration)
            
            # Create sound wave array for money spend - a happy "cha-ching" sound
            wave_array = array.array('h')
            
            for i in range(samples):
                t = i / sample_rate
                
                # Create a pleasant, uplifting sound with multiple tones
                # Rising then falling melody to sound like coins
                if t < 0.2:
                    # First part: rising tone (like coin drop)
                    frequency = 523 + (t * 261)  # C5 to C6 (523Hz to 784Hz)
                    amplitude = 3000 * (1 - t * 2)  # Fade slightly
                else:
                    # Second part: gentle bell-like harmonics
                    t_rel = t - 0.2
                    frequency = 659  # E5 - pleasant harmony
                    amplitude = 2500 * math.exp(-t_rel * 3)  # Gentle decay
                
                # Add pleasant harmonics for richness
                sample = int(amplitude * (
                    math.sin(2 * math.pi * frequency * t) +
                    0.4 * math.sin(2 * math.pi * frequency * 1.5 * t) +  # Minor third
                    0.2 * math.sin(2 * math.pi * frequency * 2 * t)     # Octave
                ))
                
                # Add to stereo array
                wave_array.append(sample)
                wave_array.append(sample)
            
            # Create pygame sound from array
            self.sounds['money_spend'] = pygame.sndarray.make_sound(wave_array)
            
        except (pygame.error, AttributeError, Exception):
            # If money sound creation fails, continue without it
            pass
    
    def play_blob_sound(self):
        """Play the blob sound effect when a new employee is hired"""
        if self.enabled and self.sound_toggles.get('blob', True) and 'blob' in self.sounds:
            try:
                self.sounds['blob'].play()
            except pygame.error:
                # Sound playback failed, but don't crash
                pass
    
    def play_error_beep(self):
        """Play the error beep sound for the easter egg (3 repeated identical errors)"""
        if self.enabled and self.sound_toggles.get('error_beep', True) and 'error_beep' in self.sounds:
            try:
                self.sounds['error_beep'].play()
            except pygame.error:
                # Sound playback failed, but don't crash
                pass
    
    def play_ap_spend_sound(self):
        """Play the AP spend sound effect when Action Points are spent"""
        if self.enabled and self.sound_toggles.get('ap_spend', True) and 'ap_spend' in self.sounds:
            try:
                self.sounds['ap_spend'].play()
            except pygame.error:
                # Sound playback failed, but don't crash
                pass
    
    def play_money_spend_sound(self):
        """Play the money spend sound effect when money is spent"""
        if self.enabled and self.sound_toggles.get('money_spend', True) and 'money_spend' in self.sounds:
            try:
                self.sounds['money_spend'].play()
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
    
    def set_sound_enabled(self, sound_name, enabled):
        """Enable or disable a specific sound effect"""
        if sound_name in self.sound_toggles:
            self.sound_toggles[sound_name] = enabled
    
    def is_sound_enabled(self, sound_name):
        """Check if a specific sound is enabled"""
        return self.sound_toggles.get(sound_name, True)
    
    def toggle_sound(self, sound_name):
        """Toggle a specific sound on/off and return new state"""
        if sound_name in self.sound_toggles:
            self.sound_toggles[sound_name] = not self.sound_toggles[sound_name]
            return self.sound_toggles[sound_name]
        return True
    
    def set_all_sounds_enabled(self, enabled):
        """Enable or disable all individual sounds (but keep master enabled state)"""
        for sound_name in self.sound_toggles:
            self.sound_toggles[sound_name] = enabled
    
    def get_sound_names(self):
        """Get list of all available sound names for UI"""
        return list(self.sound_toggles.keys())
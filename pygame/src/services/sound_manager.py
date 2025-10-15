import math
import array
from pathlib import Path

# Try to import pygame, but gracefully handle if it's not available
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    pygame = None

class SoundManager:
    '''Manages sound effects and music for the game'''
    
    def __init__(self):
        self.enabled = True  # User preference - start enabled
        self.audio_available = PYGAME_AVAILABLE  # Hardware capability
        self.sounds = {}
        # Individual sound toggles for granular control
        self.sound_toggles = {
            'money_spend': True,
            'ap_spend': True,
            'blob': True,
            'error_beep': True,
            'popup_open': True,
            'popup_close': True,
            'popup_accept': True,
            'milestone': True,
            'warning': True,
            'danger': True,
            'success': True,
            'research_complete': True
        }
        if PYGAME_AVAILABLE:
            self._initialize_pygame_mixer()
            self._create_blob_sound()
            # Always try to create popup sounds, even if blob sound creation failed
            self._create_popup_sounds()
            # Create new sound effects
            self._create_milestone_sound()
            self._create_warning_sound()
            self._create_danger_sound()
            self._create_success_sound()
            self._create_research_complete_sound()
            # Load custom sound overrides from sounds/ folder
            self._load_sounds_from_folder(Path('sounds'))
    
    def _initialize_pygame_mixer(self):
        '''Initialize pygame mixer for sound playback'''
        if not PYGAME_AVAILABLE:
            self.audio_available = False
            return
            
        try:
            # Check if mixer is already initialized
            mixer_info = pygame.mixer.get_init()
            if mixer_info is not None:
                self.audio_available = True
            else:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.audio_available = True
        except pygame.error as e:
            # If mixer initialization fails (e.g., no audio device), note that audio is unavailable
            # but don't disable user preference
            print(f'[DEBUG] Pygame error during mixer init: {e}')
            self.audio_available = False
        except Exception as e:
            # Handle any other initialization errors
            print(f'[DEBUG] Other error during mixer init: {e}')
            self.audio_available = False
    
    def _create_blob_sound(self):
        '''Create a simple blob sound effect programmatically'''
        if not self.audio_available:
            return
            
        try:
            # Check if numpy is available for sndarray
            import pygame.sndarray
            
            # Create a simple 'bloop' sound using basic math
            sample_rate = 22050
            duration = 0.3  # 300ms
            samples = int(sample_rate * duration)
            
            # Create sound wave array as 2D numpy array for stereo
            import numpy as np
            wave_array = np.zeros((samples, 2), dtype=np.int16)
            
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
                
                # Set both stereo channels
                wave_array[i][0] = sample  # Left channel
                wave_array[i][1] = sample  # Right channel
            
            # Create pygame sound from array
            self.sounds['blob'] = pygame.sndarray.make_sound(wave_array)
            
            # Create error beep sound for easter egg
            self._create_error_beep()
            
            # Create AP spend sound for enhanced feedback
            self._create_ap_spend_sound()
            

            # Create Zabinga sound for research paper completion
            self._create_zabinga_sound()
            
            # Create popup sounds for UI feedback
            self._create_popup_sounds()

        except Exception as e:
            # If sound creation fails, note that audio is unavailable
            self.audio_available = False
    
    def _create_error_beep(self):
        '''Create an error beep sound for the easter egg (3 repeated errors)'''
        if not self.audio_available:
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
            
        except (pygame.error, AttributeError, ImportError, Exception):
            # If error beep creation fails, continue without it
            pass
    
    def _create_ap_spend_sound(self):
        '''Create a sound effect for when Action Points are spent'''
        if not self.audio_available:
            return
            
        try:
            sample_rate = 22050
            duration = 0.2  # 200ms - short and crisp
            samples = int(sample_rate * duration)
            
            # Create sound wave array for AP spend
            wave_array = array.array('h')
            
            for i in range(samples):
                t = i / sample_rate
                
                # Create a satisfying 'click' or 'ding' sound
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
            
        except (pygame.error, AttributeError, ImportError, Exception):
            # If AP sound creation fails, continue without it
            pass
    

    def _create_zabinga_sound(self):
        '''Create a celebratory 'Zabinga!' sound effect for research paper completion'''

        if not self.audio_available:
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
                # Rising and falling melody to sound like 'Za-bin-ga!'
                amplitude = 3000
                
                if t < 0.25:  # 'Za' - lower tone
                    frequency = 440  # A4
                    envelope = math.sin(math.pi * t / 0.25)  # Smooth attack and decay
                elif t < 0.5:  # 'bin' - higher tone
                    frequency = 554  # C#5
                    envelope = math.sin(math.pi * (t - 0.25) / 0.25)
                elif t < 0.75:  # 'ga' - middle tone with vibrato
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
    
    def _create_popup_sounds(self):
        '''Create distinct popup sounds for UI feedback.'''
        if not self.audio_available:
            return
            
        try:
            # Check if numpy is available for sndarray
            import pygame.sndarray
            
            sample_rate = 22050
            
            # Popup open sound - ascending beep
            duration = 0.15
            samples = int(sample_rate * duration)
            wave_array = array.array('h')
            
            for i in range(samples):
                t = i / sample_rate
                frequency = 550 + (t * 200)  # Ascending from 550Hz to 750Hz
                amplitude = 4000 * (1 - t * 2)  # Quick fade
                if amplitude < 0:
                    amplitude = 0
                sample = int(amplitude * math.sin(2 * math.pi * frequency * t))
                wave_array.append(sample)
                wave_array.append(sample)
            
            self.sounds['popup_open'] = pygame.sndarray.make_sound(wave_array)
            
            # Popup close sound - descending beep  
            wave_array = array.array('h')
            
            for i in range(samples):
                t = i / sample_rate
                frequency = 750 - (t * 200)  # Descending from 750Hz to 550Hz
                amplitude = 4000 * (1 - t * 2)  # Quick fade
                if amplitude < 0:
                    amplitude = 0
                sample = int(amplitude * math.sin(2 * math.pi * frequency * t))
                wave_array.append(sample)
                wave_array.append(sample)
            
            self.sounds['popup_close'] = pygame.sndarray.make_sound(wave_array)
            
            # Popup accept sound - pleasant confirmation beep
            duration = 0.2
            samples = int(sample_rate * duration)
            wave_array = array.array('h')
            
            for i in range(samples):
                t = i / sample_rate
                frequency = 660  # E5 - pleasant frequency
                amplitude = 5000 * math.exp(-t * 3)  # Exponential decay
                sample = int(amplitude * math.sin(2 * math.pi * frequency * t))
                wave_array.append(sample)
                wave_array.append(sample)
            
            self.sounds['popup_accept'] = pygame.sndarray.make_sound(wave_array)
            
        except (pygame.error, AttributeError, ImportError, Exception):
            # If popup sound creation fails, continue without them
            pass
    
    def _load_sounds_from_folder(self, folder: Path) -> None:
        '''Load custom sounds from a folder, overriding built-in sounds where keys match.
        
        Args:
            folder: Path to the folder containing sound files
        '''
        # Return immediately if audio is unavailable or folder does not exist
        if not self.audio_available or not folder.exists() or not folder.is_dir():
            return
            
        try:
            # Recursively find all .wav and .ogg files
            for sound_file in folder.rglob('*.wav'):
                self._load_sound_file(sound_file)
            for sound_file in folder.rglob('*.ogg'):
                self._load_sound_file(sound_file)
        except Exception:
            # Never crash on folder loading errors
            pass
    
    def _load_sound_file(self, sound_file: Path) -> None:
        '''Load a single sound file.
        
        Args:
            sound_file: Path to the sound file to load
        '''
        try:
            # Create key from filename (stem, lowercase)
            key = sound_file.stem.lower()
            
            # Load the sound using pygame
            sound = pygame.mixer.Sound(str(sound_file))
            
            # Store in sounds dict, overriding existing entries
            self.sounds[key] = sound
            
        except (pygame.error, Exception):
            # If sound loading fails, continue without this file
            pass
    
    def _create_milestone_sound(self):
        '''Create a triumphant milestone achievement sound'''
        if not self.audio_available:
            return
            
        try:
            import pygame.sndarray
            import numpy as np
            
            sample_rate = 22050
            duration = 0.8  # 800ms for a substantial milestone sound
            samples = int(sample_rate * duration)
            
            # Create sound wave array as 2D numpy array for stereo
            wave_array = np.zeros((samples, 2), dtype=np.int16)
            
            # Create a triumphant ascending chord progression
            frequencies = [261.63, 329.63, 392.00, 523.25]  # C-E-G-C major chord
            for i, freq in enumerate(frequencies):
                start_time = i * 0.15  # Stagger notes
                end_time = min(duration, start_time + 0.4)
                start_sample = int(start_time * sample_rate)
                end_sample = int(end_time * sample_rate)
                
                for j in range(start_sample, min(end_sample, samples)):
                    t = j / sample_rate
                    # Fade in/out envelope
                    envelope = min(1.0, (t - start_time) / 0.05, (end_time - t) / 0.1)
                    amplitude = int(10000 * envelope)
                    sample = int(amplitude * math.sin(2 * math.pi * freq * t))
                    
                    # Set both stereo channels
                    wave_array[j][0] = max(-32767, min(32767, wave_array[j][0] + sample))
                    wave_array[j][1] = max(-32767, min(32767, wave_array[j][1] + sample))
            
            self.sounds['milestone'] = pygame.sndarray.make_sound(wave_array)
            
        except (pygame.error, AttributeError, ImportError, Exception):
            # If sound creation fails, continue without this sound
            pass
    
    def _create_warning_sound(self):
        '''Create a cautionary warning sound'''
        if not self.audio_available:
            return
            
        try:
            import pygame.sndarray
            import numpy as np
            
            sample_rate = 22050
            duration = 0.5  # 500ms
            samples = int(sample_rate * duration)
            
            # Create sound wave array as 2D numpy array for stereo
            wave_array = np.zeros((samples, 2), dtype=np.int16)
            
            # Create a two-tone warning sound (like a gentle alarm)
            frequencies = [440.0, 554.37]  # A to C# (tritone - naturally tense interval)
            
            for i in range(samples):
                t = i / sample_rate
                # Alternate between the two frequencies every 0.1 seconds
                freq_index = int(t / 0.1) % 2
                frequency = frequencies[freq_index]
                
                # Create envelope for smooth transitions
                cycle_pos = (t % 0.1) / 0.1
                envelope = 0.3 * (1.0 - abs(cycle_pos - 0.5) * 2)  # Triangle wave envelope
                
                amplitude = int(8000 * envelope)
                sample = int(amplitude * math.sin(2 * math.pi * frequency * t))
                
                # Set both stereo channels
                wave_array[i][0] = sample
                wave_array[i][1] = sample
            
            self.sounds['warning'] = pygame.sndarray.make_sound(wave_array)
            
        except (pygame.error, AttributeError, ImportError, Exception):
            pass
    
    def _create_danger_sound(self):
        '''Create an urgent danger sound for high doom situations'''
        if not self.audio_available:
            return
            
        try:
            import pygame.sndarray
            import numpy as np
            
            sample_rate = 22050
            duration = 0.6  # 600ms
            samples = int(sample_rate * duration)
            
            # Create sound wave array as 2D numpy array for stereo
            wave_array = np.zeros((samples, 2), dtype=np.int16)
            
            # Create a harsh, discordant sound with rapid frequency changes
            base_freq = 220.0  # Low A
            
            for i in range(samples):
                t = i / sample_rate
                
                # Rapid oscillation between frequencies for urgency
                freq_modulation = 1.0 + 0.5 * math.sin(2 * math.pi * 8 * t)  # 8Hz modulation
                frequency = base_freq * freq_modulation
                
                # Add some harsh harmonics
                harmonic1 = frequency * 2.1  # Slightly detuned octave
                harmonic2 = frequency * 3.3  # Detuned fifth
                
                # Aggressive envelope
                envelope = 0.4 * (1.0 - t / duration)  # Quick decay
                
                amplitude = int(12000 * envelope)
                sample = int(amplitude * (
                    0.6 * math.sin(2 * math.pi * frequency * t) +
                    0.3 * math.sin(2 * math.pi * harmonic1 * t) +
                    0.1 * math.sin(2 * math.pi * harmonic2 * t)
                ))
                
                # Set both stereo channels
                wave_array[i][0] = max(-32767, min(32767, sample))
                wave_array[i][1] = max(-32767, min(32767, sample))
            
            self.sounds['danger'] = pygame.sndarray.make_sound(wave_array)
            
        except (pygame.error, AttributeError, ImportError, Exception):
            pass
    
    def _create_success_sound(self):
        '''Create a pleasant success sound for completed actions'''
        if not self.audio_available:
            return
            
        try:
            import pygame.sndarray
            import numpy as np
            
            sample_rate = 22050
            duration = 0.4  # 400ms
            samples = int(sample_rate * duration)
            
            # Create sound wave array as 2D numpy array for stereo
            wave_array = np.zeros((samples, 2), dtype=np.int16)
            
            # Create a pleasant ascending arpeggio
            frequencies = [523.25, 659.25, 783.99]  # C-E-G major triad, one octave up
            
            for i, freq in enumerate(frequencies):
                start_time = i * 0.1
                end_time = min(duration, start_time + 0.2)
                start_sample = int(start_time * sample_rate)
                end_sample = int(end_time * sample_rate)
                
                for j in range(start_sample, min(end_sample, samples)):
                    t = j / sample_rate
                    # Gentle envelope
                    note_time = t - start_time
                    envelope = 0.3 * math.exp(-note_time * 4)  # Exponential decay
                    
                    amplitude = int(8000 * envelope)
                    sample = int(amplitude * math.sin(2 * math.pi * freq * t))
                    
                    # Set both stereo channels
                    wave_array[j][0] = max(-32767, min(32767, wave_array[j][0] + sample))
                    wave_array[j][1] = max(-32767, min(32767, wave_array[j][1] + sample))
            
            self.sounds['success'] = pygame.sndarray.make_sound(wave_array)
            
        except (pygame.error, AttributeError, ImportError, Exception):
            pass
    
    def _create_research_complete_sound(self):
        '''Create a special sound for research completion'''
        if not self.audio_available:
            return
            
        try:
            import pygame.sndarray
            import numpy as np
            
            sample_rate = 22050
            duration = 1.0  # 1 second for important research milestones
            samples = int(sample_rate * duration)
            
            # Create sound wave array as 2D numpy array for stereo
            wave_array = np.zeros((samples, 2), dtype=np.int16)
            
            # Create a sophisticated research completion sound
            # Start with zabinga-like elements but extend into triumph
            
            # Phase 1: Quick 'eureka' burst (0-0.3s)
            phase1_samples = int(0.3 * sample_rate)
            for i in range(phase1_samples):
                t = i / sample_rate
                freq = 800 + 400 * t  # Rising sweep like zabinga
                envelope = 0.4 * math.exp(-t * 8)
                
                amplitude = int(8000 * envelope)
                sample = int(amplitude * math.sin(2 * math.pi * freq * t))
                
                # Set both stereo channels
                wave_array[i][0] = sample
                wave_array[i][1] = sample
            
            # Phase 2: Triumphant chord (0.3-1.0s)
            chord_freqs = [261.63, 329.63, 392.00, 523.25]  # C major chord
            start_sample = int(0.3 * sample_rate)
            
            for i in range(start_sample, samples):
                t = i / sample_rate
                chord_time = t - 0.3
                
                # Gentle fade-in for the chord
                chord_envelope = min(0.2, chord_time / 0.2) * (1.0 - chord_time / 0.7)
                
                chord_sample = 0
                for freq in chord_freqs:
                    chord_sample += int(chord_envelope * 6000 * math.sin(2 * math.pi * freq * t))
                
                # Set both stereo channels
                wave_array[i][0] = max(-32767, min(32767, wave_array[i][0] + chord_sample))
                wave_array[i][1] = max(-32767, min(32767, wave_array[i][1] + chord_sample))
            
            self.sounds['research_complete'] = pygame.sndarray.make_sound(wave_array)
            
        except (pygame.error, AttributeError, ImportError, Exception):
            pass

    def play_sound(self, sound_name):
        '''Generic method to play any sound by name.'''
        if (self.enabled and self.audio_available and 
            self.sound_toggles.get(sound_name, True) and 
            sound_name in self.sounds):
            try:
                self.sounds[sound_name].play()
            except pygame.error:
                # Sound playback failed, but don't crash
                pass
    
    def play_blob_sound(self):
        '''Play the blob sound effect when a new employee is hired'''
        if self.enabled and self.audio_available and self.sound_toggles.get('blob', True) and 'blob' in self.sounds:
            try:
                self.sounds['blob'].play()
            except pygame.error:
                # Sound playback failed, but don't crash
                pass
    
    def play_error_beep(self):
        '''Play the error beep sound for the easter egg (3 repeated identical errors)'''
        if self.enabled and self.audio_available and self.sound_toggles.get('error_beep', True) and 'error_beep' in self.sounds:
            try:
                self.sounds['error_beep'].play()
            except pygame.error:
                # Sound playback failed, but don't crash
                pass
    
    def play_ap_spend_sound(self):
        '''Play the AP spend sound effect when Action Points are spent'''
        if self.enabled and self.audio_available and self.sound_toggles.get('ap_spend', True) and 'ap_spend' in self.sounds:
            try:
                self.sounds['ap_spend'].play()
            except pygame.error:
                # Sound playback failed, but don't crash
                pass
    
    def play_money_spend_sound(self):
        '''Play a sound effect when money is spent (reuse AP spend sound for consistency)'''
        if self.enabled and self.audio_available and self.sound_toggles.get('money_spend', True) and 'ap_spend' in self.sounds:
            try:
                self.sounds['ap_spend'].play()
            except pygame.error:
                # Sound playback failed, but don't crash
                pass
    
    def play_zabinga_sound(self):
        '''Play the Zabinga sound effect when research papers are completed'''
        if self.enabled and self.audio_available and 'zabinga' in self.sounds:
            try:
                self.sounds['zabinga'].play()

            except pygame.error:
                # Sound playback failed, but don't crash
                pass
    
    def play_milestone_sound(self):
        '''Play the milestone achievement sound'''
        if self.enabled and self.audio_available and self.sound_toggles.get('milestone', True) and 'milestone' in self.sounds:
            try:
                self.sounds['milestone'].play()
            except pygame.error:
                pass
    
    def play_warning_sound(self):
        '''Play the warning sound for cautionary situations'''
        if self.enabled and self.audio_available and self.sound_toggles.get('warning', True) and 'warning' in self.sounds:
            try:
                self.sounds['warning'].play()
            except pygame.error:
                pass
    
    def play_danger_sound(self):
        '''Play the danger sound for high-risk situations'''
        if self.enabled and self.audio_available and self.sound_toggles.get('danger', True) and 'danger' in self.sounds:
            try:
                self.sounds['danger'].play()
            except pygame.error:
                pass
    
    def play_success_sound(self):
        '''Play the success sound for completed actions'''
        if self.enabled and self.audio_available and self.sound_toggles.get('success', True) and 'success' in self.sounds:
            try:
                self.sounds['success'].play()
            except pygame.error:
                pass
    
    def play_research_complete_sound(self):
        '''Play the research completion sound for major research milestones'''
        if self.enabled and self.audio_available and self.sound_toggles.get('research_complete', True) and 'research_complete' in self.sounds:
            try:
                self.sounds['research_complete'].play()
            except pygame.error:
                pass
    
    def set_enabled(self, enabled):
        '''Enable or disable all sound effects'''
        self.enabled = enabled
    
    def is_enabled(self):
        '''Check if sounds are currently enabled'''
        return self.enabled
    
    def toggle(self):
        '''Toggle sound on/off and return new state'''
        self.enabled = not self.enabled
        return self.enabled
    
    def set_sound_enabled(self, sound_name, enabled):
        '''Enable or disable a specific sound effect'''
        if sound_name in self.sound_toggles:
            self.sound_toggles[sound_name] = enabled
    
    def is_sound_enabled(self, sound_name):
        '''Check if a specific sound is enabled'''
        return self.sound_toggles.get(sound_name, True)
    
    def toggle_sound(self, sound_name):
        '''Toggle a specific sound on/off and return new state'''
        if sound_name in self.sound_toggles:
            self.sound_toggles[sound_name] = not self.sound_toggles[sound_name]
            return self.sound_toggles[sound_name]
        return True
    
    def set_all_sounds_enabled(self, enabled):
        '''Enable or disable all individual sounds (but keep master enabled state)'''
        for sound_name in self.sound_toggles:
            self.sound_toggles[sound_name] = enabled
    
    def get_sound_names(self):
        '''Get list of all available sound names for UI'''
        return list(self.sound_toggles.keys())
'''
Audio management for PDoom1.

Provides pygame.mixer wrapper with persistent volume and mute settings.
Handles SFX and music playback with graceful fallbacks for headless environments.
'''

import pygame
import os
from pathlib import Path
from typing import Optional, Dict
from src.services.settings import Settings


class AudioManager:
    '''
    Audio manager with persistent settings and pygame.mixer integration.
    
    Features:
    - Persistent volume and mute settings
    - Separate volume controls for SFX and music
    - Graceful fallback for headless/CI environments
    - Sound file caching and preloading
    '''
    
    def __init__(self, settings: Optional[Settings] = None):
        '''
        Initialize audio manager.
        
        Args:
            settings: Settings instance (creates new one if None)
        '''
        self.settings = settings or Settings()
        self._initialized = False
        self._sound_cache: Dict[str, pygame.mixer.Sound] = {}
        self._music_playing = False
        
        # Try to initialize pygame mixer
        self._init_mixer()
        
    def _init_mixer(self) -> None:
        '''Initialize pygame mixer with fallback for headless environments.'''
        try:
            # Set SDL audio driver for headless environments
            if not os.environ.get('SDL_AUDIODRIVER') and self._is_headless():
                os.environ['SDL_AUDIODRIVER'] = 'dummy'
            
            # Initialize pygame mixer
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            
            # Apply saved settings
            self._apply_settings()
            self._initialized = True
            
        except pygame.error as e:
            print(f'Warning: Could not initialize audio: {e}')
            self._initialized = False
    
    def _is_headless(self) -> bool:
        '''Check if running in headless environment.'''
        # Common indicators of headless environments
        headless_indicators = [
            'DISPLAY' not in os.environ,  # No X11 display
            os.environ.get('CI') == 'true',  # CI environment
            os.environ.get('GITHUB_ACTIONS') == 'true',  # GitHub Actions
            os.environ.get('PYTEST_CURRENT_TEST'),  # Running under pytest
        ]
        return any(headless_indicators)
    
    def _apply_settings(self) -> None:
        '''Apply volume and mute settings from persistent storage.'''
        if not self._initialized:
            return
            
        # Apply master volume to pygame mixer
        self.settings.get_volume('master')
        pygame.mixer.set_num_channels(8)  # Default number of channels
        
        # Note: pygame.mixer doesn't have global volume control
        # We'll handle this per-sound/music
    
    def is_available(self) -> bool:
        '''Check if audio system is available.'''
        return self._initialized
    
    def load_sound(self, sound_path: Path, cache_key: Optional[str] = None) -> Optional[pygame.mixer.Sound]:
        '''
        Load a sound file with caching.
        
        Args:
            sound_path: Path to sound file
            cache_key: Optional cache key (defaults to filename)
            
        Returns:
            pygame.mixer.Sound or None if loading failed
        '''
        if not self._initialized or not sound_path.exists():
            return None
            
        cache_key = cache_key or sound_path.name
        
        if cache_key not in self._sound_cache:
            try:
                sound = pygame.mixer.Sound(str(sound_path))
                self._sound_cache[cache_key] = sound
            except pygame.error as e:
                print(f'Warning: Could not load sound {sound_path}: {e}')
                return None
        
        return self._sound_cache[cache_key]
    
    def play_sound(self, sound_path: Path, volume: Optional[float] = None, cache_key: Optional[str] = None) -> bool:
        '''
        Play a sound effect.
        
        Args:
            sound_path: Path to sound file
            volume: Override volume (0.0-1.0, None for default)
            cache_key: Optional cache key for sound
            
        Returns:
            True if sound played successfully
        '''
        if not self._initialized or self.settings.is_muted():
            return False
            
        sound = self.load_sound(sound_path, cache_key)
        if not sound:
            return False
        
        # Calculate effective volume
        master_vol = self.settings.get_volume('master')
        sfx_vol = self.settings.get_volume('sfx')
        effective_vol = (volume or 1.0) * master_vol * sfx_vol
        
        try:
            sound.set_volume(effective_vol)
            sound.play()
            return True
        except pygame.error as e:
            print(f'Warning: Could not play sound: {e}')
            return False
    
    def play_music(self, music_path: Path, loops: int = -1, volume: Optional[float] = None) -> bool:
        '''
        Play background music.
        
        Args:
            music_path: Path to music file
            loops: Number of loops (-1 for infinite)
            volume: Override volume (0.0-1.0, None for default)
            
        Returns:
            True if music started successfully
        '''
        if not self._initialized or self.settings.is_muted() or not music_path.exists():
            return False
        
        try:
            pygame.mixer.music.load(str(music_path))
            
            # Calculate effective volume
            master_vol = self.settings.get_volume('master')
            music_vol = self.settings.get_volume('music')
            effective_vol = (volume or 1.0) * master_vol * music_vol
            
            pygame.mixer.music.set_volume(effective_vol)
            pygame.mixer.music.play(loops)
            self._music_playing = True
            return True
            
        except pygame.error as e:
            print(f'Warning: Could not play music: {e}')
            return False
    
    def stop_music(self) -> None:
        '''Stop background music.'''
        if self._initialized:
            pygame.mixer.music.stop()
            self._music_playing = False
    
    def pause_music(self) -> None:
        '''Pause background music.'''
        if self._initialized:
            pygame.mixer.music.pause()
    
    def unpause_music(self) -> None:
        '''Unpause background music.'''
        if self._initialized:
            pygame.mixer.music.unpause()
    
    def is_music_playing(self) -> bool:
        '''Check if music is currently playing.'''
        if not self._initialized:
            return False
        return self._music_playing and pygame.mixer.music.get_busy()
    
    def set_volume(self, channel: str, volume: float) -> None:
        '''
        Set volume for a channel and persist to settings.
        
        Args:
            channel: 'master', 'sfx', or 'music'
            volume: Volume level (0.0-1.0)
        '''
        self.settings.set_volume(channel, volume)
        
        # Update currently playing music volume if needed
        if channel in ['master', 'music'] and self._initialized and self._music_playing:
            master_vol = self.settings.get_volume('master')
            music_vol = self.settings.get_volume('music')
            pygame.mixer.music.set_volume(master_vol * music_vol)
    
    def get_volume(self, channel: str) -> float:
        '''Get volume for a channel.'''
        return self.settings.get_volume(channel)
    
    def set_muted(self, muted: bool) -> None:
        '''Set mute state and persist to settings.'''
        self.settings.set_muted(muted)
        
        if muted and self._initialized:
            # Stop all currently playing sounds
            pygame.mixer.stop()
            if self._music_playing:
                pygame.mixer.music.pause()
        elif not muted and self._initialized and self._music_playing:
            # Unpause music if unmuted
            pygame.mixer.music.unpause()
    
    def is_muted(self) -> bool:
        '''Check if audio is muted.'''
        return self.settings.is_muted()
    
    def cleanup(self) -> None:
        '''Clean up audio resources.'''
        if self._initialized:
            pygame.mixer.quit()
            self._initialized = False
            self._sound_cache.clear()
            self._music_playing = False
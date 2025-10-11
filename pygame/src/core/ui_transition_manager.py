'''UI Transition Manager for P(Doom) Strategy Game.

This module handles all UI transition animations including upgrade animations,
easing functions, particle effects, and visual transitions. Extracted from 
the main GameState monolith for better separation of concerns.
'''

from typing import Dict, Any, List, Tuple
import pygame
from src.services.deterministic_rng import get_rng


class UITransitionManager:
    '''Manages UI transition animations and visual effects.
    
    Handles upgrade animations, particle trails, easing functions,
    and smooth visual transitions throughout the game.
    '''
    
    def __init__(self, game_state_ref) -> None:
        '''Initialize the UI transition manager.
        
        Args:
            game_state_ref: Reference to main GameState for accessing shared state
        '''
        self.game_state_ref = game_state_ref
        self.ui_transitions: List[Dict[str, Any]] = []  # Active UI transition animations
        self.upgrade_transitions: Dict[int, Dict[str, Any]] = {}  # Track transitions for individual upgrades
    
    def create_upgrade_transition(self, upgrade_idx: int, start_rect: pygame.Rect, end_rect: pygame.Rect) -> Dict[str, Any]:
        '''Create a smooth transition animation for an upgrade moving from button to icon.'''
        transition = {
            'type': 'upgrade_transition',
            'upgrade_idx': upgrade_idx,
            'start_rect': start_rect,
            'end_rect': end_rect,
            'progress': 0.0,
            'duration': 45,  # Longer duration for more elegant motion (1.5 seconds)
            'trail_points': [],  # For visual trail effect
            'particle_trail': [],  # Enhanced particle system for more dramatic effect
            'glow_timer': 90,  # Extended glow time for better visual feedback
            'glow_intensity': 0,  # Current glow intensity for smooth fade-in
            'completed': False,
            'arc_height': 80,  # More dramatic arc height
            'ease_type': 'cubic_out'  # Smooth deceleration easing
        }
        self.ui_transitions.append(transition)
        self.upgrade_transitions[upgrade_idx] = transition
        return transition
    
    def update_ui_transitions(self) -> None:
        '''Update all active UI transitions.'''
        transitions_to_remove = []
        
        for transition in self.ui_transitions:
            if transition['type'] == 'upgrade_transition':
                self.update_upgrade_transition(transition)
                
                # Mark completed transitions for removal
                if transition['completed'] and transition['glow_timer'] <= 0:
                    transitions_to_remove.append(transition)
        
        # Remove completed transitions
        for transition in transitions_to_remove:
            self.ui_transitions.remove(transition)
            if transition['upgrade_idx'] in self.upgrade_transitions:
                del self.upgrade_transitions[transition['upgrade_idx']]
    
    def update_upgrade_transition(self, transition: Dict[str, Any]) -> None:
        '''Update a single upgrade transition animation with enhanced effects.'''
        if not transition['completed']:
            # Advance animation progress with configurable easing
            transition['progress'] = min(1.0, transition['progress'] + (1.0 / transition['duration']))
            
            # Calculate eased progress for smoother motion
            eased_progress = self.apply_easing(transition['progress'], transition.get('ease_type', 'cubic_out'))
            
            # Add trail point for current position
            current_pos = self.interpolate_position(
                transition['start_rect'], 
                transition['end_rect'], 
                eased_progress,
                transition.get('arc_height', 80)
            )
            
            # Enhanced trail system with varying properties
            transition['trail_points'].append({
                'pos': current_pos,
                'alpha': 255,
                'age': 0,
                'size': 12,  # Larger initial size
                'color_variation': get_rng().randint(-20, 20, 'randint_context')  # Color variation for organic feel
            })
            
            # Add particle effects for more dramatic visual impact
            if len(transition['trail_points']) % 3 == 0:  # Every 3rd frame
                self.add_particle_to_trail(transition, current_pos)
            
            # Limit trail length for performance
            if len(transition['trail_points']) > 15:  # Longer trail
                transition['trail_points'].pop(0)
            
            # Mark as completed when progress reaches 1.0
            if transition['progress'] >= 1.0:
                transition['completed'] = True
        
        # Update trail points with enhanced fading
        for point in transition['trail_points']:
            point['age'] += 1
            # Smoother alpha fade with size reduction
            fade_factor = max(0, 1.0 - (point['age'] / 20.0))
            point['alpha'] = int(255 * fade_factor)
            point['size'] = max(2, int(point['size'] * fade_factor))
        
        # Update particle trail
        for particle in transition.get('particle_trail', []):
            particle['age'] += 1
            particle['alpha'] = max(0, 180 - (particle['age'] * 12))
            # Add slight drift to particles
            particle['pos'][0] += particle['velocity'][0]
            particle['pos'][1] += particle['velocity'][1]
            particle['velocity'][1] += 0.2  # Gravity effect
        
        # Remove fully faded elements
        transition['trail_points'] = [p for p in transition['trail_points'] if p['alpha'] > 0]
        transition['particle_trail'] = [p for p in transition.get('particle_trail', []) if p['alpha'] > 0]
        
        # Enhanced glow system with smooth fade-in and pulsing
        if transition['completed']:
            if transition['glow_timer'] > 0:
                transition['glow_timer'] -= 1
                # Smooth glow intensity changes
                max_intensity = 255
                fade_duration = 30
                if transition['glow_timer'] > fade_duration:
                    transition['glow_intensity'] = min(max_intensity, transition['glow_intensity'] + 8)
                else:
                    # Fade out
                    transition['glow_intensity'] = int(max_intensity * (transition['glow_timer'] / fade_duration))
        else:
            # Building up glow as transition progresses
            transition['glow_intensity'] = int(100 * transition['progress'])
    
    def interpolate_position(self, start_rect: Tuple[int, int, int, int], end_rect: Tuple[int, int, int, int], progress: float, arc_height: int = 80) -> Tuple[int, int]:
        '''Interpolate position between start and end rectangles with enhanced curved motion.'''
        # Use easeOutCubic for smooth deceleration
        eased_progress = 1 - (1 - progress) ** 3
        
        start_x = start_rect[0] + start_rect[2] // 2  # Center of start rect
        start_y = start_rect[1] + start_rect[3] // 2
        end_x = end_rect[0] + end_rect[2] // 2  # Center of end rect  
        end_y = end_rect[1] + end_rect[3] // 2
        
        # Create more dramatic curved arc path
        mid_x = (start_x + end_x) / 2
        # Dynamic arc height based on distance and direction
        distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        dynamic_arc_height = min(arc_height, distance * 0.3)  # Scale with distance
        min(start_y, end_y) - dynamic_arc_height
        
        # Enhanced Bezier curve with control points for more elegant motion
        t = eased_progress
        
        # Use cubic Bezier for even smoother curves
        control1_x = start_x + (mid_x - start_x) * 0.5
        control1_y = start_y - dynamic_arc_height * 0.3
        control2_x = end_x - (end_x - mid_x) * 0.5  
        control2_y = end_y - dynamic_arc_height * 0.3
        
        # Cubic Bezier interpolation for ultra-smooth motion
        x = ((1-t)**3 * start_x + 
             3*(1-t)**2*t * control1_x + 
             3*(1-t)*t**2 * control2_x + 
             t**3 * end_x)
        y = ((1-t)**3 * start_y + 
             3*(1-t)**2*t * control1_y + 
             3*(1-t)*t**2 * control2_y + 
             t**3 * end_y)
        
        return (int(x), int(y))
    
    def apply_easing(self, t: float, ease_type: str = 'cubic_out') -> float:
        '''Apply easing function for smoother animations.'''
        if ease_type == 'cubic_out':
            return 1 - (1 - t) ** 3
        elif ease_type == 'elastic_out':
            import math
            if t == 0 or t == 1:
                return t
            return (2 ** (-10 * t)) * math.sin((t - 0.1) * 2 * math.pi / 0.4) + 1
        elif ease_type == 'back_out':
            c1 = 1.70158
            c3 = c1 + 1
            return 1 + c3 * ((t - 1) ** 3) + c1 * ((t - 1) ** 2)
        else:
            return t  # Linear fallback
    
    def add_particle_to_trail(self, transition: Dict[str, Any], position: Tuple[int, int]) -> None:
        '''Add particle effects to transition trail.'''
        if 'particle_trail' not in transition:
            transition['particle_trail'] = []
        
        # Create multiple particles for richer effect
        for _ in range(2):
            particle = {
                'pos': [position[0] + get_rng().randint(-5, 5, 'randint_context'), position[1] + get_rng().randint(-5, 5, 'randint_context')],
                'velocity': [get_rng().uniform(-1, 1, 'particle_velocity_x'), get_rng().uniform(-2, 0, 'particle_velocity_y')],
                'alpha': 180,
                'age': 0,
                'size': get_rng().randint(3, 8, 'randint_context'),
                'color_shift': get_rng().randint(-30, 30, 'randint_context')
            }
            transition['particle_trail'].append(particle)
    
    def get_ui_transitions(self) -> List[Dict[str, Any]]:
        '''Get the current list of UI transitions for rendering.'''
        return self.ui_transitions
    
    def get_upgrade_transitions(self) -> Dict[int, Dict[str, Any]]:
        '''Get the current upgrade transition mappings.'''
        return self.upgrade_transitions
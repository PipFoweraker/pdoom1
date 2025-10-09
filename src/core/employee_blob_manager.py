'''
Employee Blob Manager - Extracted from game_state.py

Handles all employee blob visualization, positioning, animation, and management
assignment logic. This module manages the visual representation of employees
as animated blobs in the game UI.

Extracted methods:
- _initialize_employee_blobs
- _add_employee_blobs  
- _calculate_blob_position
- _get_ui_element_rects
- _check_blob_ui_collision
- _update_blob_positions_dynamically
- _add_manager_blob
- _reassign_employee_management
- _remove_employee_blobs
'''

from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.game_state import GameState

from src.core.employee_management import (
    initialize_employee_blobs, add_employee_blobs, remove_employee_blobs
)
from src.core.ui_utils import calculate_blob_position, check_blob_ui_collision


class EmployeeBlobManager:
    '''Manages employee blob visualization and positioning'''
    
    def __init__(self, game_state: 'GameState'):
        '''Initialize the EmployeeBlobManager with reference to GameState.'''
        self.game_state = game_state
        
    def initialize_employee_blobs(self) -> None:
        '''Initialize employee blobs for starting staff with improved positioning'''
        self.game_state.employee_blobs = initialize_employee_blobs(
            self.game_state.staff, 
            self.calculate_blob_position
        )
    
    def add_employee_blobs(self, count: int) -> None:
        '''Add new employee blobs with animation from side and improved positioning'''
        new_blobs = add_employee_blobs(
            self.game_state.employee_blobs, 
            count, 
            self.calculate_blob_position
        )
        self.game_state.employee_blobs.extend(new_blobs)
        
        # Play sounds for new employees
        for _ in range(count):
            self.game_state.sound_manager.play_blob_sound()
    
    def calculate_blob_position(self, blob_index: int, screen_w: int = 1200, screen_h: int = 800) -> Tuple[int, int]:
        '''Calculate initial blob position in the employee pen area.'''
        return calculate_blob_position(blob_index, screen_w, screen_h)
    
    def get_ui_element_rects(self, screen_w: int = 1200, screen_h: int = 800) -> List[Tuple[int, int, int, int]]:
        '''
        Get rectangles of all UI elements that employee blobs should avoid.
        
        Args:
            screen_w (int): Screen width
            screen_h (int): Screen height
            
        Returns:
            list: List of (x, y, width, height) rectangles representing UI elements
        '''
        ui_rects: List[Tuple[int, int, int, int]] = []
        
        # Convert pygame.Rect to tuple helper function
        def rect_to_tuple(rect) -> Tuple[int, int, int, int]:
            if hasattr(rect, 'x') and hasattr(rect, 'y'):  # pygame.Rect
                return (rect.x, rect.y, rect.width, rect.height)
            return rect  # Already a tuple
        
        # Action buttons (left side)
        action_rects = self.game_state._get_action_rects(screen_w, screen_h)
        ui_rects.extend([rect_to_tuple(rect) for rect in action_rects])
        
        # Upgrade buttons and icons (right side)
        upgrade_rects = self.game_state._get_upgrade_rects(screen_w, screen_h)
        for rect in upgrade_rects:
            if rect is not None:  # Some upgrades might not have rects if purchased
                ui_rects.append(rect_to_tuple(rect))
        
        # End turn button (bottom center)
        endturn_rect = self.game_state._get_endturn_rect(screen_w, screen_h)
        ui_rects.append(rect_to_tuple(endturn_rect))
        
        # Resource display area (top)
        resource_rect: Tuple[int, int, int, int] = (0, 0, screen_w, int(screen_h * 0.25))
        ui_rects.append(resource_rect)
        
        # Message log area (bottom left)
        log_rect: Tuple[int, int, int, int] = (int(screen_w*0.04), int(screen_h*0.74), int(screen_w * 0.44), int(screen_h * 0.22))
        ui_rects.append(log_rect)
        
        # Opponents panel (between resources and actions)
        opponents_rect: Tuple[int, int, int, int] = (int(screen_w * 0.04), int(screen_h * 0.19), int(screen_w * 0.92), int(screen_h * 0.08))
        ui_rects.append(opponents_rect)
        
        # Mute button (bottom right)
        mute_rect = self.game_state._get_mute_button_rect(screen_w, screen_h)
        ui_rects.append(rect_to_tuple(mute_rect))
        
        return ui_rects
    
    def check_blob_ui_collision(self, blob_x: int, blob_y: int, blob_radius: int, ui_rects: List[Tuple[int, int, int, int]]) -> Tuple[bool, float, float]:
        '''Check if a blob collides with any UI element (delegates to ui_utils).'''
        return check_blob_ui_collision(blob_x, blob_y, blob_radius, ui_rects)
    
    def update_blob_positions_dynamically(self, screen_w: int = 1200, screen_h: int = 800) -> None:
        '''
        Update blob positions dynamically to avoid UI elements.
        This method should be called every frame to ensure continuous movement.
        
        Args:
            screen_w (int): Screen width
            screen_h (int): Screen height
        '''
        if not self.game_state.employee_blobs:
            return
        
        ui_rects = self.get_ui_element_rects(screen_w, screen_h)
        blob_radius = 25
        
        # Update each blob's position
        for i, blob in enumerate(self.game_state.employee_blobs):
            # Skip if blob is still animating in from the side
            if blob['animation_progress'] < 1.0:
                continue
            
            current_x = blob['x']
            current_y = blob['y']
            
            # Check for UI collisions
            collides, repulsion_x, repulsion_y = self.check_blob_ui_collision(
                current_x, current_y, blob_radius, ui_rects
            )
            
            # Apply blob-to-blob repulsion to prevent clustering
            for j, other_blob in enumerate(self.game_state.employee_blobs):
                if i != j and other_blob['animation_progress'] >= 1.0:
                    other_x = other_blob['x']
                    other_y = other_blob['y']
                    
                    dx = current_x - other_x
                    dy = current_y - other_y
                    distance = (dx * dx + dy * dy) ** 0.5
                    
                    min_distance = blob_radius * 2 + 5  # Minimum distance between blobs
                    if distance < min_distance and distance > 0:
                        # Apply repulsion between blobs
                        repulsion_strength = (min_distance - distance) * 0.05
                        repulsion_x += (dx / distance) * repulsion_strength
                        repulsion_y += (dy / distance) * repulsion_strength
            
            # Apply slight attraction to employee pen center to keep blobs contained
            # Employee pen area - match coordinates from _calculate_blob_position
            pen_x = int(screen_w * 0.33)
            pen_y = int(screen_h * 0.32)
            pen_width = int(screen_w * 0.33)
            pen_height = int(screen_h * 0.20)
            pen_center_x = pen_x + pen_width / 2
            pen_center_y = pen_y + pen_height / 2
            
            center_attraction = 0.002
            repulsion_x += (pen_center_x - current_x) * center_attraction
            repulsion_y += (pen_center_y - current_y) * center_attraction
            
            # Apply movement with damping
            if abs(repulsion_x) > 0.1 or abs(repulsion_y) > 0.1:
                # Cap maximum movement speed
                max_speed = 2.0
                speed = (repulsion_x * repulsion_x + repulsion_y * repulsion_y) ** 0.5
                if speed > max_speed:
                    repulsion_x = (repulsion_x / speed) * max_speed
                    repulsion_y = (repulsion_y / speed) * max_speed
                
                # Update blob position
                new_x = current_x + repulsion_x
                new_y = current_y + repulsion_y
                
                # Keep blobs within employee pen bounds
                new_x = max(pen_x + blob_radius, min(pen_x + pen_width - blob_radius, new_x))
                new_y = max(pen_y + blob_radius, min(pen_y + pen_height - blob_radius, new_y))
                
                blob['x'] = new_x
                blob['y'] = new_y
                
                # Update target position to current position for smooth animation
                blob['target_x'] = new_x
                blob['target_y'] = new_y
            
    def add_manager_blob(self) -> None:
        '''Add a new manager blob with animation from side'''
        blob_id = len(self.game_state.employee_blobs)
        # Position managers slightly offset from regular employees
        target_x = 350 + (len(self.game_state.managers) % 2) * 300  # Alternate sides
        target_y = 450 + (len(self.game_state.managers) // 2) * 120  # Stack down
        
        manager_blob = {
            'id': blob_id,
            'x': -50,  # Start off-screen left
            'y': target_y,
            'target_x': target_x,
            'target_y': target_y,
            'has_compute': True,  # Managers always have access
            'productivity': 1.0,
            'animation_progress': 0.0,  # Will animate in
            'type': 'manager',  # Manager type
            'managed_employees': [],  # List of employee IDs this manager oversees
            'management_capacity': 9,  # Can manage up to 9 employees
            'subtype': 'manager',  # Manager subtype
            'productive_action_index': 0,  # Default to first action
            'productive_action_bonus': 1.0,  # Current productivity bonus
            'productive_action_active': False  # Whether productive action is active
        }
        
        # Add to both general blobs and specific managers list
        self.game_state.employee_blobs.append(manager_blob)
        self.game_state.managers.append(manager_blob)
        
        # Play special sound effect for manager hire
        self.game_state.sound_manager.play_blob_sound()
        
        # Reassign employee management after adding new manager
        self.reassign_employee_management()
        
    def reassign_employee_management(self) -> None:
        '''Reassign employees to managers based on capacity and efficiency'''
        # Reset all employee assignments
        employees = [blob for blob in self.game_state.employee_blobs if blob['type'] == 'employee']
        managers = [blob for blob in self.game_state.employee_blobs if blob['type'] == 'manager']
        
        # Clear previous assignments
        for employee in employees:
            employee['managed_by'] = None
            employee['unproductive_reason'] = None
        for manager in managers:
            manager['managed_employees'] = []
        
        # Assign employees to managers (max 9 per manager)
        manager_idx = 0
        for i, employee in enumerate(employees):
            if manager_idx < len(managers):
                manager = managers[manager_idx]
                if len(manager['managed_employees']) < manager['management_capacity']:
                    # Assign this employee to current manager
                    employee['managed_by'] = manager['id']
                    manager['managed_employees'].append(employee['id'])
                else:
                    # Current manager is full, move to next
                    manager_idx += 1
                    if manager_idx < len(managers):
                        manager = managers[manager_idx]
                        employee['managed_by'] = manager['id']
                        manager['managed_employees'].append(employee['id'])
                    else:
                        # No more managers available - employee becomes unmanaged
                        employee['unproductive_reason'] = 'no_manager'
            else:
                # No managers available for this employee
                employee['unproductive_reason'] = 'no_manager'
                
    def remove_employee_blobs(self, count: int) -> None:
        '''Remove employee blobs when staff leave'''
        self.game_state.employee_blobs = remove_employee_blobs(self.game_state.employee_blobs, count)
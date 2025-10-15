'''
Employee blob management utilities extracted from game_state.py

This module contains utilities for managing employee blob data structures,
positioning, initialization, and lifecycle management. These are pure data
manipulation functions that create and maintain employee blob state.
'''

from typing import Dict, Any, List, Tuple


def create_employee_blob(blob_id: int, target_x: int, target_y: int, is_animated: bool = True) -> Dict[str, Any]:
    '''Create a new employee blob with default properties.'''
    return {
        'id': blob_id,
        'x': -50 if is_animated else target_x,  # Start off-screen left if animated
        'y': target_y,
        'target_x': target_x,
        'target_y': target_y,
        'has_compute': False,
        'productivity': 0.0,
        'animation_progress': 0.0 if is_animated else 1.0,
        'type': 'employee',  # Track blob type
        'managed_by': None,  # Which manager manages this employee (None if unmanaged)
        'unproductive_reason': None,  # Reason for being unproductive (for overlay display)
        'subtype': 'generalist',  # Default employee subtype
        'productive_action_index': 0,  # Default to first action
        'productive_action_bonus': 1.0,  # Current productivity bonus
        'productive_action_active': False  # Whether productive action is active
    }


def initialize_employee_blobs(staff_count: int, position_calculator) -> List[Dict[str, Any]]:
    '''Initialize employee blobs for starting staff with improved positioning.'''
    employee_blobs = []
    
    for i in range(staff_count):
        # Use improved positioning that avoids UI overlap
        target_x, target_y = position_calculator(i)
        
        blob = create_employee_blob(i, target_x, target_y, is_animated=False)
        employee_blobs.append(blob)
    
    return employee_blobs


def add_employee_blobs(existing_blobs: List[Dict[str, Any]], count: int, position_calculator) -> List[Dict[str, Any]]:
    '''Add new employee blobs with animation from side and improved positioning.'''
    new_blobs = []
    
    for i in range(count):
        blob_id = len(existing_blobs) + i
        # Use improved positioning that avoids UI overlap
        target_x, target_y = position_calculator(blob_id)
        
        blob = create_employee_blob(blob_id, target_x, target_y, is_animated=True)
        new_blobs.append(blob)
    
    return new_blobs


def remove_employee_blobs(employee_blobs: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
    '''Remove employee blobs when staff leave. Returns the modified list.'''
    blobs_to_remove = min(count, len(employee_blobs))
    
    # Remove from the end of the list
    for _ in range(blobs_to_remove):
        if employee_blobs:
            employee_blobs.pop()
    
    return employee_blobs


def reset_employee_productivity(employee_blobs: List[Dict[str, Any]]) -> None:
    '''Reset all employees' compute status and productivity for a new turn.'''
    for blob in employee_blobs:
        blob['has_compute'] = False
        blob['productivity'] = 0.0
        blob['productive_action_active'] = False
        blob['productive_action_bonus'] = 1.0


def separate_employees_and_managers(employee_blobs: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    '''Separate employee blobs into employees and managers.'''
    employees = [blob for blob in employee_blobs if blob['type'] == 'employee']
    managers = [blob for blob in employee_blobs if blob['type'] == 'manager']
    return employees, managers


def count_unmanaged_penalty_employees(employees: List[Dict[str, Any]], manager_milestone_triggered: bool) -> int:
    '''Count employees that have unmanaged penalties (beyond 9 employees when milestone triggered).'''
    if not manager_milestone_triggered:
        return 0
    
    unmanaged_count = 0
    if len(employees) > 9:
        for employee in employees:
            if employee['unproductive_reason'] == 'no_manager':
                unmanaged_count += 1
                # Mark unmanaged employees as unproductive
                employee['productivity'] = 0.0
    
    return unmanaged_count


def calculate_compute_per_employee(total_compute: int, employees: List[Dict[str, Any]], managers: List[Dict[str, Any]]) -> float:
    '''Calculate available compute per employee based on total staff.'''
    total_employees = len(employees) + len(managers)
    return total_compute / max(total_employees, 1) if total_employees > 0 else 0


def apply_management_assignments(employees: List[Dict[str, Any]], managers: List[Dict[str, Any]]) -> None:
    '''Apply management assignments to employee blobs.'''
    # Reset all management assignments
    for employee in employees:
        employee['managed_by'] = None
        employee['unproductive_reason'] = None
    
    # Simple assignment: each manager handles up to a certain number of employees
    employees_per_manager = 9  # Each manager can handle 9 employees effectively
    
    manager_index = 0
    for i, employee in enumerate(employees):
        if manager_index < len(managers):
            # Assign employee to current manager
            manager = managers[manager_index]
            employee['managed_by'] = manager['id']
            
            # Move to next manager if current one is at capacity
            if (i + 1) % employees_per_manager == 0:
                manager_index += 1
        else:
            # No manager available for this employee
            employee['unproductive_reason'] = 'no_manager'


def validate_blob_data_integrity(employee_blobs: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    '''Validate employee blob data integrity and return any issues found.'''
    issues = []
    
    # Check for required fields
    required_fields = ['id', 'x', 'y', 'target_x', 'target_y', 'type', 'productivity']
    
    for i, blob in enumerate(employee_blobs):
        # Check required fields exist
        for field in required_fields:
            if field not in blob:
                issues.append(f'Blob {i}: Missing required field \'{field}\'')
        
        # Check data types
        if 'id' in blob and not isinstance(blob['id'], int):
            issues.append(f'Blob {i}: Invalid id type (expected int)')
        
        if 'productivity' in blob and not isinstance(blob['productivity'], (int, float)):
            issues.append(f'Blob {i}: Invalid productivity type (expected number)')
        
        if 'type' in blob and blob['type'] not in ['employee', 'manager']:
            issues.append(f'Blob {i}: Invalid type \'{blob["type"]}\' (expected \'employee\' or \'manager\')')
    
    return len(issues) == 0, issues


def get_employee_blob_summary(employee_blobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    '''Generate a summary of employee blob statistics.'''
    if not employee_blobs:
        return {
            'total_count': 0,
            'employee_count': 0,
            'manager_count': 0,
            'productive_count': 0,
            'average_productivity': 0.0,
            'managed_count': 0,
            'unmanaged_count': 0
        }
    
    employees, managers = separate_employees_and_managers(employee_blobs)
    
    productive_count = sum(1 for blob in employee_blobs if blob.get('productivity', 0) > 0)
    total_productivity = sum(blob.get('productivity', 0) for blob in employee_blobs)
    average_productivity = total_productivity / len(employee_blobs) if employee_blobs else 0
    
    managed_count = sum(1 for emp in employees if emp.get('managed_by') is not None)
    unmanaged_count = len(employees) - managed_count
    
    return {
        'total_count': len(employee_blobs),
        'employee_count': len(employees),
        'manager_count': len(managers),
        'productive_count': productive_count,
        'average_productivity': average_productivity,
        'managed_count': managed_count,
        'unmanaged_count': unmanaged_count
    }

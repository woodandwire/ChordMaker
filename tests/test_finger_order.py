"""
Test the updated finger order validation
"""

from chord_validator import ChordFingeringValidator

def test_finger_order_validation():
    """Test cases for finger order validation."""
    
    print("=== Testing Finger Order Validation ===\n")
    
    validator = ChordFingeringValidator()
    
    # Test Case 1: Valid finger order (C major - fingers go 1, 2, 3)
    print("Test 1: Valid C Major chord (finger order 3, 2, 1)")
    c_major = [
        ('X', 0),  # 6th string muted
        ('3', 3),  # 5th string, 3rd fret, 3rd finger
        ('2', 2),  # 4th string, 2nd fret, 2nd finger  
        ('O', 0),  # 3rd string open
        ('1', 1),  # 2nd string, 1st fret, 1st finger
        ('O', 0)   # 1st string open
    ]
    
    result = validator.validate_chord(c_major)
    print(f"Status: {result['status_name']} ({result['status_code']})")
    for msg in result['messages']:
        if msg['severity'] == 'error':
            print(f"  ERROR: {msg['message']}")
    print()
    
    # Test Case 2: Invalid finger order - pinky behind index
    print("Test 2: Invalid chord - pinky (4) on fret 1, index (1) on fret 3")
    invalid_order = [
        ('X', 0),  # 6th string muted
        ('4', 1),  # 5th string, 1st fret, 4th finger (WRONG!)
        ('X', 0),  # 4th string muted
        ('1', 3),  # 3rd string, 3rd fret, 1st finger
        ('X', 0),  # 2nd string muted
        ('O', 0)   # 1st string open
    ]
    
    result = validator.validate_chord(invalid_order)
    print(f"Status: {result['status_name']} ({result['status_code']})")
    for msg in result['messages']:
        if msg['severity'] == 'error':
            print(f"  ERROR: {msg['message']}")
    print()
    
    # Test Case 3: Another invalid case - middle finger behind index
    print("Test 3: Invalid chord - middle finger (2) on fret 1, index (1) on fret 2")  
    invalid_order2 = [
        ('X', 0),  # 6th string muted
        ('2', 1),  # 5th string, 1st fret, 2nd finger (WRONG!)
        ('1', 2),  # 4th string, 2nd fret, 1st finger
        ('O', 0),  # 3rd string open
        ('O', 0),  # 2nd string open
        ('O', 0)   # 1st string open
    ]
    
    result = validator.validate_chord(invalid_order2)
    print(f"Status: {result['status_name']} ({result['status_code']})")
    for msg in result['messages']:
        if msg['severity'] == 'error':
            print(f"  ERROR: {msg['message']}")
    print()
    
    # Test Case 4: Edge case - same fret, non-adjacent fingers
    print("Test 4: Same fret positioning - fingers 1 and 3 both on fret 2")
    same_fret = [
        ('X', 0),  # 6th string muted  
        ('1', 2),  # 5th string, 2nd fret, 1st finger
        ('3', 2),  # 4th string, 2nd fret, 3rd finger (skipping finger 2)
        ('O', 0),  # 3rd string open
        ('O', 0),  # 2nd string open
        ('O', 0)   # 1st string open
    ]
    
    result = validator.validate_chord(same_fret)
    print(f"Status: {result['status_name']} ({result['status_code']})")
    for msg in result['messages']:
        if msg['severity'] in ['error', 'warning']:
            print(f"  {msg['severity'].upper()}: {msg['message']}")
    print()
    
    # Test Case 5: Valid ascending order
    print("Test 5: Valid ascending finger order (1, 2, 3, 4)")
    ascending = [
        ('1', 1),  # 6th string, 1st fret, 1st finger
        ('2', 2),  # 5th string, 2nd fret, 2nd finger
        ('3', 3),  # 4th string, 3rd fret, 3rd finger
        ('4', 4),  # 3rd string, 4th fret, 4th finger
        ('O', 0),  # 2nd string open
        ('O', 0)   # 1st string open
    ]
    
    result = validator.validate_chord(ascending)
    print(f"Status: {result['status_name']} ({result['status_code']})")
    for msg in result['messages']:
        if msg['severity'] == 'error':
            print(f"  ERROR: {msg['message']}")
    print("Valid ascending order - should have no finger order errors!")
    print()

if __name__ == "__main__":
    test_finger_order_validation()
#!/usr/bin/env python3

"""
Test the new same-fret finger positioning validation.
"""

from chord_validator import ChordFingeringValidator

def test_same_fret_finger_positioning():
    """Test the anatomical constraint for same-fret finger positioning."""
    validator = ChordFingeringValidator()
    
    # Test case from user: Pattern 1071
    # Finger 4 on string 2 fret 4, Finger 1 on string 1 fret 4
    # This should be IMPOSSIBLE because finger 4 is on a lower string than finger 1 when both on same fret
    print("=== Testing Same Fret Finger Positioning ===")
    print()
    
    test_chord = [('O', 0), ('O', 0), ('O', 0), ('X', 0), ('4', 4), ('1', 4)]
    print(f"Testing chord: {test_chord}")
    print("Finger 4 on string 2 (B string) fret 4")  
    print("Finger 1 on string 1 (High E string) fret 4")
    print("Expected: PHYSICALLY_IMPOSSIBLE (finger 4 cannot be lower than finger 1 on same fret)")
    
    result = validator.validate_chord(test_chord)
    print(f"Result: {result.get('status_name', 'UNKNOWN')} (code: {result.get('status_code', 'N/A')})")
    print(f"Valid: {result.get('is_valid', False)}")
    
    if result.get('messages'):
        print("Validation messages:")
        for msg in result.get('messages', []):
            print(f"  {msg['severity'].upper()}: {msg['message']}")
    
    print()
    
    # Test a valid same-fret positioning for comparison
    # Finger 1 on string 2, Finger 4 on string 1 (both fret 4) - this should be OK
    print("=== Testing Valid Same Fret Positioning ===")
    valid_chord = [('O', 0), ('O', 0), ('O', 0), ('X', 0), ('1', 4), ('4', 4)]
    print(f"Testing chord: {valid_chord}")
    print("Finger 1 on string 2 (B string) fret 4")
    print("Finger 4 on string 1 (High E string) fret 4") 
    print("Expected: VALID (finger 4 higher than finger 1 on same fret)")
    
    result = validator.validate_chord(valid_chord)
    print(f"Result: {result.get('status_name', 'UNKNOWN')} (code: {result.get('status_code', 'N/A')})")
    print(f"Valid: {result.get('is_valid', False)}")
    
    if result.get('messages'):
        print("Validation messages:")
        for msg in result.get('messages', []):
            print(f"  {msg['severity'].upper()}: {msg['message']}")

if __name__ == "__main__":
    test_same_fret_finger_positioning()
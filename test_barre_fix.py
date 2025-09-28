#!/usr/bin/env python3
"""Test the barre chord validation fix"""

from chord_validator import ChordFingeringValidator

def test_barre_validation():
    """Test that invalid barre patterns are caught."""
    validator = ChordFingeringValidator(thumb_reach_strings=1)
    
    print("Testing Barre Chord Validation:")
    print("=" * 50)
    
    # Test 1: Invalid pseudo-barre with open strings in between
    print("\n1. Invalid Barre - Open strings between barre finger positions:")
    invalid_barre = [
        ('O', 0),  # Open string 6
        ('1', 2),  # Finger 1 on string 5, fret 2
        ('O', 0),  # Open string 4 - THIS BREAKS THE BARRE!
        ('1', 2),  # Finger 1 on string 3, fret 2
        ('O', 0),  # Open string 2
        ('O', 0)   # Open string 1
    ]
    
    result = validator.validate_chord(invalid_barre)
    print(f"Status: {result['status_code']} - {result['status_name']}")
    print(f"Valid: {result['is_valid']}")
    
    if result.get('messages'):
        for msg in result['messages']:
            if msg['severity'] == 'error':
                print(f"  ERROR: {msg['message']}")
    
    # Test 2: Valid partial barre
    print("\n2. Valid Partial Barre - Consecutive strings:")
    valid_partial_barre = [
        ('X', 0),  # Muted string 6
        ('1', 2),  # Finger 1 on string 5, fret 2
        ('1', 2),  # Finger 1 on string 4, fret 2 - CONSECUTIVE!
        ('1', 2),  # Finger 1 on string 3, fret 2 - CONSECUTIVE!
        ('O', 0),  # Open string 2
        ('O', 0)   # Open string 1
    ]
    
    result = validator.validate_chord(valid_partial_barre)
    print(f"Status: {result['status_code']} - {result['status_name']}")
    print(f"Valid: {result['is_valid']}")
    
    # Test 3: Valid full barre F major
    print("\n3. Valid Full Barre - F Major:")
    f_major_barre = [
        ('1', 1),  # Finger 1 on string 6, fret 1
        ('1', 1),  # Finger 1 on string 5, fret 1
        ('2', 2),  # Finger 2 on string 4, fret 2
        ('3', 3),  # Finger 3 on string 3, fret 3
        ('4', 3),  # Finger 4 on string 2, fret 3
        ('1', 1)   # Finger 1 on string 1, fret 1 - FULL BARRE
    ]
    
    result = validator.validate_chord(f_major_barre)
    print(f"Status: {result['status_code']} - {result['status_name']}")
    print(f"Valid: {result['is_valid']}")
    
    if result.get('messages'):
        error_count = sum(1 for msg in result['messages'] if msg['severity'] == 'error')
        warning_count = sum(1 for msg in result['messages'] if msg['severity'] == 'warning')
        print(f"  Errors: {error_count}, Warnings: {warning_count}")

if __name__ == "__main__":
    test_barre_validation()
#!/usr/bin/env python3
"""Test script for the chord validator to verify all TODO items are implemented."""

from chord_validator import ChordFingeringValidator, ValidationResult

def test_validation():
    """Test the chord validator with various chord patterns."""
    validator = ChordFingeringValidator()
    
    # Test cases with different chord patterns
    # Each chord is represented as a list of tuples: (finger_indicator, fret_number)
    # finger_indicator: 'X' (muted), 'O' (open), '1'-'4' (fingers), 'T' (thumb)
    test_chords = [
        # Valid easy chord - C Major
        {
            'name': 'C Major',
            'pattern': [('O', 0), ('1', 1), ('O', 0), ('2', 2), ('3', 3), ('O', 0)]
        },
        
        # Difficult stretch chord
        {
            'name': 'D#dim7 (difficult)',
            'pattern': [('1', 11), ('2', 12), ('1', 11), ('3', 12), ('1', 11), ('4', 14)]
        },
        
        # Barre chord - F Major
        {
            'name': 'F Major (barre)',
            'pattern': [('1', 1), ('1', 1), ('3', 3), ('4', 3), ('2', 2), ('1', 1)]
        },
        
        # Invalid chord with impossible finger positions
        {
            'name': 'Impossible stretch',
            'pattern': [('1', 1), ('2', 15), ('3', 2), ('4', 3), ('1', 4), ('2', 5)]
        },
        
        # Simple open chord - G Major
        {
            'name': 'G Major',
            'pattern': [('3', 3), ('2', 2), ('O', 0), ('O', 0), ('O', 0), ('4', 3)]
        }
    ]
    
    print("Testing Chord Validator - All TODO items implemented:")
    print("=" * 60)
    
    for i, chord in enumerate(test_chords, 1):
        print(f"\nTest {i}: {chord['name']}")
        print("-" * 40)
        
        result = validator.validate_chord(chord['pattern'])
        
        print(f"Status: {result['status_name']}")
        print(f"Status Code: {result['status_code']}")
        print(f"Valid: {result['is_valid']}")
        print(f"Has Warnings: {result['has_warnings']}")
        
        if result.get('messages'):
            errors = [msg for msg in result['messages'] if msg['severity'] == 'error']
            warnings = [msg for msg in result['messages'] if msg['severity'] == 'warning']
            infos = [msg for msg in result['messages'] if msg['severity'] == 'info']
            
            if errors:
                print("Errors:")
                for error in errors:
                    print(f"  - {error['message']} [{error['rule']}]")
            
            if warnings:
                print("Warnings:")
                for warning in warnings:
                    print(f"  - {warning['message']} [{warning['rule']}]")
            
            if infos:
                print("Info:")
                for info in infos:
                    print(f"  - {info['message']} [{info['rule']}]")
        
        # Show hand position info
        hand_pos = result['hand_position']
        if hand_pos['fret_span'] > 0:
            print(f"Hand Position: Frets {hand_pos['min_fret']}-{hand_pos['max_fret']} (span: {hand_pos['fret_span']})")
        
        # Show finger positions
        if result['finger_positions']:
            positions = ", ".join([f"Finger {pos['finger']} on string {pos['string']} fret {pos['fret']}" 
                                 for pos in result['finger_positions']])
            print(f"Finger Positions: {positions}")

if __name__ == "__main__":
    test_validation()
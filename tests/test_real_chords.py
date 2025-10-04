#!/usr/bin/env python3

"""
Test enhanced difficulty scoring with real-world chord patterns.
"""

from chord_validator import ChordFingeringValidator

def test_real_world_chords():
    """Test difficulty scoring with common chord patterns."""
    validator = ChordFingeringValidator()
    
    print("=== Real-World Chord Difficulty Testing ===")
    print()
    
    # Real chord patterns from easiest to hardest
    real_chords = [
        {
            'name': 'C Major (easy)',
            'chord': [('X', 0), ('3', 3), ('2', 2), ('O', 0), ('1', 1), ('O', 0)],
            'expected': 'Easy - adjacent fingers in comfortable positions'
        },
        {
            'name': 'G Major (moderate)',
            'chord': [('3', 3), ('2', 2), ('O', 0), ('O', 0), ('O', 0), ('3', 3)],
            'expected': 'Moderate - some stretch, mainly adjacent fingers'
        },
        {
            'name': 'F Major Barre (hard)',
            'chord': [('1', 1), ('1', 1), ('3', 3), ('3', 3), ('2', 2), ('1', 1)],
            'expected': 'Hard - full barre with stretch combinations'
        },
        {
            'name': 'B Major (very hard)',
            'chord': [('X', 0), ('2', 2), ('4', 4), ('4', 4), ('4', 4), ('2', 2)],
            'expected': 'Very hard - non-adjacent fingers (2-4) with stretch'
        }
    ]
    
    for i, chord_info in enumerate(real_chords, 1):
        print(f"{i}. {chord_info['name']}")
        print(f"   Pattern: {chord_info['chord']}")
        print(f"   Expected: {chord_info['expected']}")
        
        result = validator.validate_chord(chord_info['chord'])
        
        # Extract difficulty information
        difficulty_msgs = [msg for msg in result.get('messages', []) if 'difficulty' in msg.get('message', '').lower()]
        
        if difficulty_msgs:
            difficulty_msg = difficulty_msgs[0]['message']
            print(f"   Actual: {difficulty_msg}")
        
        print(f"   Valid: {result.get('is_valid', False)} ({result.get('status_name', 'UNKNOWN')})")
        print()

if __name__ == "__main__":
    test_real_world_chords()
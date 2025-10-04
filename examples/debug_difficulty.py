#!/usr/bin/env python3
"""
Debug script to check the actual difficulty messages being generated.
"""

from chord_validator import ChordFingeringValidator

def debug_difficulty_messages():
    """Debug the difficulty messages to understand the scoring categories."""
    
    test_chords = [
        ('E Major', [('O', 0), ('2', 2), ('2', 2), ('1', 1), ('O', 0), ('O', 0)]),
        ('A Major', [('X', 0), ('O', 0), ('2', 2), ('2', 2), ('2', 2), ('O', 0)]),
        ('C Major', [('X', 0), ('1', 1), ('O', 0), ('2', 2), ('3', 3), ('O', 0)]),
        ('F Major', [('1', 1), ('1', 1), ('2', 2), ('3', 3), ('3', 3), ('1', 1)]),
        ('Jazz Chord', [('X', 0), ('1', 2), ('2', 4), ('3', 6), ('4', 9), ('X', 0)])
    ]
    
    validator = ChordFingeringValidator()
    
    for name, data in test_chords:
        print(f"\n{name}:")
        result = validator.validate_chord(data)
        
        for msg in result.get('messages', []):
            if 'difficulty' in msg.get('message', '').lower():
                print(f"  {msg['message']}")

if __name__ == "__main__":
    debug_difficulty_messages()
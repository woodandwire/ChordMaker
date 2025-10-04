#!/usr/bin/env python3
"""
Test string distance modifiers and low fret position penalties.
"""

from chord_validator import ChordFingeringValidator

def test_string_distance_modifiers():
    """Test that string distance properly modifies fret gap difficulty."""
    
    test_chords = [
        # Same 3-fret gap, different string distances
        {
            'name': 'Adjacent Strings (3-fret gap)',
            'data': [('1', 2), ('2', 5), ('X', 0), ('X', 0), ('X', 0), ('X', 0)],
            'description': '3-fret gap on adjacent strings (harder due to interference)'
        },
        {
            'name': 'Same String (3-fret gap)', 
            'data': [('1', 2), ('X', 0), ('X', 0), ('X', 0), ('X', 0), ('2', 5)],
            'description': '3-fret gap on same string (hardest due to finger interference)'
        },
        {
            'name': 'Far Strings (3-fret gap)',
            'data': [('1', 2), ('X', 0), ('X', 0), ('X', 0), ('2', 5), ('X', 0)],
            'description': '3-fret gap on strings 4 apart (easier due to hand angle)'
        },
        {
            'name': 'Very Far Strings (3-fret gap)',
            'data': [('1', 2), ('X', 0), ('X', 0), ('X', 0), ('X', 0), ('2', 5)],
            'description': '3-fret gap on strings 5 apart (much easier)'
        },
        
        # Test low fret position penalty
        {
            'name': 'Low Fret Position (1st-4th fret)',
            'data': [('1', 1), ('X', 0), ('2', 4), ('X', 0), ('X', 0), ('X', 0)],
            'description': 'Same gap at low fret position (harder due to wider fret spacing)'
        },
        {
            'name': 'High Fret Position (12th-15th fret)', 
            'data': [('1', 12), ('X', 0), ('2', 15), ('X', 0), ('X', 0), ('X', 0)],
            'description': 'Same gap at high fret position (easier due to narrow fret spacing)'
        }
    ]
    
    validator = ChordFingeringValidator()
    
    print("Testing String Distance and Fret Position Modifiers")
    print("=" * 65)
    
    for i, chord in enumerate(test_chords):
        print(f"\n{i+1}. {chord['name']}")
        print(f"   Description: {chord['description']}")
        
        result = validator.validate_chord(chord['data'])
        
        for msg in result.get('messages', []):
            if 'difficulty' in msg.get('message', '').lower():
                print(f"   Result: {msg['message']}")
    
    print("\n" + "=" * 65)
    print("✅ String distance and position modifier tests completed!")
    print("Expected: Same string should be hardest, far strings easier, low positions harder.")

if __name__ == "__main__":
    test_string_distance_modifiers()
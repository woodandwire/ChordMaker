#!/usr/bin/env python3

"""
Test the enhanced finger combination difficulty scoring.
"""

from chord_validator import ChordFingeringValidator

def test_finger_combination_difficulty():
    """Test various finger combinations to validate difficulty scoring."""
    validator = ChordFingeringValidator()
    
    print("=== Testing Enhanced Finger Combination Difficulty ===")
    print()
    
    # Test cases showing progression of difficulty
    test_cases = [
        {
            'name': 'Easy: Adjacent fingers (1-2)',
            'chord': [('X', 0), ('X', 0), ('X', 0), ('1', 2), ('2', 3), ('X', 0)],
            'expected': 'Low difficulty - adjacent fingers with small stretch'
        },
        {
            'name': 'Moderate: Adjacent fingers (2-3) with stretch',
            'chord': [('X', 0), ('X', 0), ('2', 2), ('3', 4), ('X', 0), ('X', 0)],
            'expected': 'Moderate difficulty - adjacent fingers with 2 fret stretch'
        },
        {
            'name': 'Challenging: Non-adjacent (1-3)',
            'chord': [('X', 0), ('X', 0), ('1', 2), ('X', 0), ('3', 3), ('X', 0)],
            'expected': 'Higher difficulty - non-adjacent finger combination'
        },
        {
            'name': 'Hard: Non-adjacent (1-4) with stretch',
            'chord': [('X', 0), ('1', 2), ('X', 0), ('X', 0), ('X', 0), ('4', 5)],
            'expected': 'High difficulty - index-pinky with 3 fret stretch'
        },
        {
            'name': 'Very Hard: Multiple non-adjacent (1-3-4) wide stretch',
            'chord': [('1', 1), ('X', 0), ('3', 3), ('4', 5), ('X', 0), ('X', 0)],
            'expected': 'Very high difficulty - multiple non-adjacent with wide stretch'
        },
        {
            'name': 'Extreme: Index-pinky wide stretch (1-4)',
            'chord': [('1', 1), ('X', 0), ('X', 0), ('X', 0), ('X', 0), ('4', 6)],
            'expected': 'Extremely high difficulty - index-pinky 5 fret stretch'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print(f"   Chord: {test_case['chord']}")
        print(f"   Expected: {test_case['expected']}")
        
        result = validator.validate_chord(test_case['chord'])
        
        # Extract difficulty information
        difficulty_msgs = [msg for msg in result.get('messages', []) if 'difficulty' in msg.get('message', '').lower()]
        
        if difficulty_msgs:
            difficulty_msg = difficulty_msgs[0]['message']
            print(f"   Result: {difficulty_msg}")
        else:
            print("   Result: No difficulty information found")
        
        # Show any finger-related factors
        factor_msgs = [msg for msg in result.get('messages', []) if 'finger' in msg.get('message', '').lower()]
        for msg in factor_msgs:
            if 'difficulty' not in msg['message'].lower():
                print(f"   Factor: {msg['message']}")
        
        print()

if __name__ == "__main__":
    test_finger_combination_difficulty()
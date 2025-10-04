#!/usr/bin/env python3
"""
Test barre blocking interference detection.
"""

from chord_validator import ChordFingeringValidator
from chord_chart import ChordChart

def test_barre_blocking_scenarios():
    """Test various barre blocking interference scenarios."""
    
    print("🔍 TESTING BARRE BLOCKING INTERFERENCE")
    print("=" * 60)
    
    test_cases = [
        {
            'name': 'Pattern 997896 - Finger 4 blocks Finger 3 barre',
            'pattern': [('O', 0), ('X', 0), ('4', 5), ('3', 2), ('3', 2), ('4', 5)],
            'expected': 'PHYSICALLY_IMPOSSIBLE',
            'description': 'Finger 4 at fret 5 blocks access to finger 3 barre at fret 2'
        },
        {
            'name': 'Valid F Major - No blocking interference',
            'pattern': [('1', 1), ('1', 1), ('2', 2), ('3', 3), ('3', 3), ('1', 1)],
            'expected': 'VALID',
            'description': 'Standard F Major with proper finger progression'
        },
        {
            'name': 'Invalid - Finger 3 blocks Finger 2 barre',
            'pattern': [('X', 0), ('2', 2), ('2', 2), ('3', 4), ('3', 4), ('2', 2)],
            'expected': 'PHYSICALLY_IMPOSSIBLE',
            'description': 'Finger 3 at fret 4 should block finger 2 barre at fret 2'
        },
        {
            'name': 'Edge Case - Adjacent strings, moderate gap',
            'pattern': [('X', 0), ('X', 0), ('2', 3), ('3', 5), ('X', 0), ('X', 0)],
            'expected': 'PHYSICALLY_IMPOSSIBLE',  # Should be caught by finger span rule
            'description': 'Adjacent fingers with 2-fret gap on adjacent strings'
        },
        {
            'name': 'Valid - Non-interfering barres',
            'pattern': [('1', 3), ('1', 3), ('X', 0), ('X', 0), ('2', 5), ('2', 5)],
            'expected': 'VALID',
            'description': 'Two barres that don\'t interfere with each other'
        }
    ]
    
    validator = ChordFingeringValidator()
    chart = ChordChart()
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Pattern: {test_case['pattern']}")
        print(f"Expected: {test_case['expected']}")
        print(f"Description: {test_case['description']}")
        
        result = validator.validate_chord(test_case['pattern'])
        actual_status = result.get('status_name', 'UNKNOWN')
        
        print(f"Actual: {actual_status}")
        print(f"Is Valid: {result['is_valid']}")
        
        # Check if result matches expectation
        if actual_status == test_case['expected']:
            print("✅ PASS - Status matches expected")
            results.append(True)
        elif test_case['expected'] in ['VALID', 'VALID_WITH_WARNINGS'] and actual_status in ['VALID', 'VALID_WITH_WARNINGS']:
            print("✅ PASS - Status acceptable (valid with or without warnings)")
            results.append(True)
        else:
            print(f"❌ FAIL - Expected {test_case['expected']}, got {actual_status}")
            results.append(False)
        
        # Show key validation messages related to barre blocking
        error_messages = [msg for msg in result.get('messages', []) if msg['severity'] == 'error']
        blocking_messages = [msg for msg in error_messages if 'block' in msg['message'].lower()]
        
        if blocking_messages:
            print("🚫 Barre Blocking Errors:")
            for msg in blocking_messages:
                print(f"  ❌ {msg['message']}")
        
        # Show other error messages
        other_errors = [msg for msg in error_messages if 'block' not in msg['message'].lower()]
        if other_errors:
            print("Other Errors:")
            for msg in other_errors[:2]:  # Show first 2 other errors
                print(f"  ❌ {msg['message']}")
        
        # Generate a test chart
        filename = f"test_barre_blocking_{i:02d}.svg"
        chart.set_chord_name(f"Barre Test {i}")
        chart.save_to_file(test_case['pattern'], filename)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print("BARRE BLOCKING TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All barre blocking tests PASSED!")
        print("Barre interference detection is working correctly.")
    else:
        print("❌ Some tests failed. Need to review barre blocking logic.")
    
    return passed == total

if __name__ == "__main__":
    test_barre_blocking_scenarios()
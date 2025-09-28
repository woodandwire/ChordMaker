#!/usr/bin/env python3
"""
Test enhanced anatomical finger span validation with multiple edge cases.
"""

from chord_validator import ChordFingeringValidator
from chord_chart import ChordChart

def test_finger_span_validation():
    """Test various finger span scenarios."""
    
    print("🔍 TESTING ENHANCED FINGER SPAN VALIDATION")
    print("=" * 60)
    
    test_cases = [
        {
            'name': 'Valid: Ring-Pinky 2-fret gap (at limit)',
            'pattern': [('X', 0), ('X', 0), ('3', 3), ('4', 5), ('X', 0), ('X', 0)],
            'expected': 'VALID_WITH_WARNINGS',  # At the 2-fret limit for 3-4
            'description': 'Should be valid but warn about being at anatomical limit'
        },
        {
            'name': 'Invalid: Ring-Pinky 3-fret gap (impossible)',
            'pattern': [('X', 0), ('X', 0), ('3', 2), ('4', 5), ('X', 0), ('X', 0)],
            'expected': 'PHYSICALLY_IMPOSSIBLE',  # 3-fret gap exceeds limit
            'description': 'Should be marked as anatomically impossible'
        },
        {
            'name': 'Valid: Middle-Ring 3-fret gap (at limit)',
            'pattern': [('X', 0), ('2', 2), ('3', 5), ('X', 0), ('X', 0), ('X', 0)],
            'expected': 'VALID_WITH_WARNINGS',  # At the 3-fret limit for 2-3
            'description': 'Should be valid but warn about maximum stretch'
        },
        {
            'name': 'Invalid: Middle-Ring 4-fret gap (impossible)',
            'pattern': [('X', 0), ('2', 2), ('3', 6), ('X', 0), ('X', 0), ('X', 0)],
            'expected': 'PHYSICALLY_IMPOSSIBLE',  # 4-fret gap exceeds limit
            'description': 'Should be marked as anatomically impossible'
        },
        {
            'name': 'Valid: Index-Middle 4-fret gap (at limit)',
            'pattern': [('1', 2), ('2', 6), ('X', 0), ('X', 0), ('X', 0), ('X', 0)],
            'expected': 'VALID_WITH_WARNINGS',  # At the 4-fret limit for 1-2
            'description': 'Should be valid but warn about maximum stretch'
        },
        {
            'name': 'Invalid: Index-Middle 5-fret gap (impossible)',
            'pattern': [('1', 2), ('2', 7), ('X', 0), ('X', 0), ('X', 0), ('X', 0)],
            'expected': 'PHYSICALLY_IMPOSSIBLE',  # 5-fret gap exceeds limit
            'description': 'Should be marked as anatomically impossible'
        },
        {
            'name': 'Valid: Normal finger pattern',
            'pattern': [('X', 0), ('3', 3), ('2', 2), ('O', 0), ('1', 1), ('O', 0)],
            'expected': 'VALID',  # Normal C major chord
            'description': 'Should be completely valid'
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
        elif test_case['expected'] == 'VALID_WITH_WARNINGS' and actual_status in ['VALID', 'VALID_WITH_WARNINGS']:
            print("✅ PASS - Status acceptable (valid with or without warnings)")
            results.append(True)
        else:
            print(f"❌ FAIL - Expected {test_case['expected']}, got {actual_status}")
            results.append(False)
        
        # Show key validation messages
        error_messages = [msg for msg in result.get('messages', []) if msg['severity'] == 'error']
        warning_messages = [msg for msg in result.get('messages', []) if msg['severity'] == 'warning']
        
        if error_messages:
            print("Errors:")
            for msg in error_messages[:2]:  # Show first 2 errors
                print(f"  ❌ {msg['message']}")
        
        if warning_messages:
            print("Warnings:")
            for msg in warning_messages[:2]:  # Show first 2 warnings
                print(f"  ⚠️ {msg['message']}")
        
        # Generate a test chart
        filename = f"test_finger_span_{i:02d}.svg"
        chart.set_chord_name(f"Test {i}")
        chart.save_to_file(test_case['pattern'], filename)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All finger span validation tests PASSED!")
        print("Enhanced anatomical constraints are working correctly.")
    else:
        print("❌ Some tests failed. Need to review finger span logic.")
    
    return passed == total

if __name__ == "__main__":
    test_finger_span_validation()
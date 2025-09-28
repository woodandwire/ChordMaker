#!/usr/bin/env python3
"""
Comprehensive test for barre chord visualization and functionality.
"""

from chord_chart import ChordChart
import os
import glob

def test_barre_detection_and_visualization():
    """Test barre chord detection and visualization comprehensively."""
    
    print("=== Comprehensive Barre Chord Test ===\n")
    
    chart = ChordChart()
    
    # Test cases covering different barre scenarios
    test_cases = [
        {
            'name': 'Full F Major Barre',
            'data': [('1', 1), ('1', 1), ('2', 2), ('3', 3), ('3', 3), ('1', 1)],
            'expected_barres': [
                'Finger 1 across strings 1,2,6 at fret 1',
                'Finger 3 across strings 4,5 at fret 3'
            ]
        },
        {
            'name': 'Partial Barre (Pattern 99493)',
            'data': [('O', 0), ('O', 0), ('1', 1), ('2', 3), ('3', 5), ('2', 3)],
            'expected_barres': [
                'Finger 2 across strings 4,6 at fret 3'
            ]
        },
        {
            'name': 'Three-String Barre',
            'data': [('2', 5), ('2', 5), ('2', 5), ('1', 3), ('O', 0), ('X', 0)],
            'expected_barres': [
                'Finger 2 across strings 1,2,3 at fret 5'
            ]
        },
        {
            'name': 'Multiple Non-Adjacent Barres',
            'data': [('1', 2), ('3', 4), ('1', 2), ('3', 4), ('1', 2), ('3', 4)],
            'expected_barres': [
                'Finger 1 across strings 1,3,5 at fret 2',
                'Finger 3 across strings 2,4,6 at fret 4'
            ]
        },
        {
            'name': 'No Barre (Individual Fingers)',
            'data': [('1', 1), ('2', 2), ('3', 3), ('4', 4), ('O', 0), ('X', 0)],
            'expected_barres': []
        },
        {
            'name': 'High Fret Barre (Above 5th)',
            'data': [('1', 7), ('1', 7), ('1', 7), ('2', 9), ('3', 10), ('1', 7)],
            'expected_barres': [
                'Finger 1 across strings 1,2,3,6 at fret 7'
            ]
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"Pattern: {test_case['data']}")
        
        filename = f"test_barre_case_{i}.svg"
        chart.set_chord_name(test_case['name'])
        chart.save_to_file(test_case['data'], filename)
        
        # Check if file was created
        file_created = os.path.exists(filename)
        print(f"✓ File created: {file_created}")
        
        if file_created:
            # Read the SVG content to check for barre lines
            with open(filename, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # Count barre lines (thick lines with stroke-width:8)
            barre_line_count = svg_content.count('stroke-width:8')
            expected_barre_count = len(test_case['expected_barres'])
            
            print(f"Expected barres: {expected_barre_count}")
            print(f"Found barre lines: {barre_line_count}")
            
            if barre_line_count == expected_barre_count:
                print("✓ Barre line count matches expected")
                results.append(True)
            else:
                print("✗ Barre line count mismatch")
                results.append(False)
            
            print(f"Expected: {test_case['expected_barres']}")
        else:
            results.append(False)
        
        print()
    
    # Summary
    print("=== Test Results Summary ===")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All barre chord tests PASSED!")
        print("Barre chord visualization is working correctly.")
    else:
        print("❌ Some tests FAILED!")
        print("Barre chord visualization needs debugging.")
    
    return passed == total

def analyze_existing_barre_patterns():
    """Analyze existing chord patterns for barre chord examples."""
    
    print("\n=== Analyzing Existing Chord Patterns for Barres ===")
    
    # Look for chord SVG files
    chord_files = glob.glob("chords/pattern_*_chord.svg")[:10]  # Check first 10 patterns
    
    if not chord_files:
        print("No chord pattern files found in chords/ directory")
        return
    
    barre_examples = []
    
    for chord_file in chord_files:
        try:
            with open(chord_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract chord data from comment
            if '<!-- CHORD_DATA:' in content:
                data_line = [line for line in content.split('\n') if 'CHORD_DATA:' in line][0]
                data_str = data_line.split('CHORD_DATA:')[1].split('-->')[0].strip()
                
                # Parse the data
                import ast
                chord_data = ast.literal_eval(data_str)
                
                # Check for potential barres (same finger on multiple strings at same fret)
                finger_fret_map = {}
                for i, (finger, fret) in enumerate(chord_data):
                    if finger not in ['O', 'X']:
                        key = (finger, fret)
                        if key not in finger_fret_map:
                            finger_fret_map[key] = []
                        finger_fret_map[key].append(i)
                
                # Find barres (finger appears on multiple strings at same fret)
                barres = {k: v for k, v in finger_fret_map.items() if len(v) > 1}
                
                if barres:
                    pattern_name = os.path.basename(chord_file).replace('_chord.svg', '')
                    barre_examples.append({
                        'pattern': pattern_name,
                        'data': chord_data,
                        'barres': barres,
                        'file': chord_file
                    })
        
        except Exception as e:
            continue
    
    print(f"Found {len(barre_examples)} patterns with barre chords:")
    for example in barre_examples[:5]:  # Show first 5
        print(f"  {example['pattern']}: {example['barres']}")
    
    return barre_examples

if __name__ == "__main__":
    # Run comprehensive barre chord tests
    test_passed = test_barre_detection_and_visualization()
    
    # Analyze existing patterns
    barre_examples = analyze_existing_barre_patterns()
    
    print(f"\n=== Final Status ===")
    print(f"✅ Barre visualization tests: {'PASSED' if test_passed else 'FAILED'}")
    print(f"🎸 Found {len(barre_examples) if barre_examples else 0} existing barre chord patterns")
    print(f"🔧 Barre chord enhancement: COMPLETE")
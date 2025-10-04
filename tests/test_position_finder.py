"""
Test script for the PositionFinder class - demonstrates systematic chord generation.
"""

from position_finder import PositionFinder, InstrumentConfig

def test_position_finder():
    """Test the PositionFinder with various configurations."""
    
    print("🧪 Testing PositionFinder Class")
    print("=" * 50)
    
    # Test 1: Default configuration (6-string guitar, first 5 frets)
    print("\n📋 Test 1: Default Guitar Configuration")
    print("-" * 30)
    
    finder1 = PositionFinder(output_dir="test_patterns_1")
    results1 = finder1.generate_and_validate_patterns(limit=5)
    
    print(f"Results: {len(results1)} patterns processed")
    
    # Test 2: Custom configuration with more fret range
    print("\n📋 Test 2: Extended Fret Range (up to 7th fret)")
    print("-" * 30)
    
    custom_config = InstrumentConfig(strings=6, max_fret=7, fingers=['O', 'X', '1', '2', '3', '4'])
    finder2 = PositionFinder(instrument_config=custom_config, output_dir="test_patterns_2")
    results2 = finder2.generate_and_validate_patterns(limit=5)
    
    print(f"Results: {len(results2)} patterns processed")
    
    # Test 3: Analyze specific pattern types
    print("\n📋 Test 3: Pattern Analysis")
    print("-" * 30)
    
    # Show some interesting patterns from the results
    valid_patterns = [r for r in results1 if r['is_valid']]
    invalid_patterns = [r for r in results1 if not r['is_valid']]
    
    print(f"Valid patterns: {len(valid_patterns)}")
    print(f"Invalid patterns: {len(invalid_patterns)}")
    
    if valid_patterns:
        print("\n🎵 Sample Valid Patterns:")
        for pattern in valid_patterns[:3]:
            pattern_str = " | ".join([f"S{i+1}: {f}({fr})" for i, (f, fr) in enumerate(pattern['pattern'])])
            print(f"  {pattern['pattern_name']}: {pattern_str}")
    
    if invalid_patterns:
        print("\n🚫 Sample Invalid Patterns:")
        for pattern in invalid_patterns[:2]:
            pattern_str = " | ".join([f"S{i+1}: {f}({fr})" for i, (f, fr) in enumerate(pattern['pattern'])])
            status = pattern['validation_result'].get('status_name', 'UNKNOWN')
            print(f"  {pattern['pattern_name']}: {pattern_str} - {status}")
    
    print(f"\n✅ Testing completed! Check the generated directories:")
    print(f"   - test_patterns_1/ (and test_patterns_1/trash/)")
    print(f"   - test_patterns_2/ (and test_patterns_2/trash/)")
    
    return results1, results2

def analyze_chord_complexity():
    """Demonstrate chord complexity analysis."""
    print("\n🔬 Chord Complexity Analysis")
    print("=" * 50)
    
    # Generate more patterns to see complexity distribution
    finder = PositionFinder(output_dir="complexity_analysis")
    results = finder.generate_and_validate_patterns(limit=20)
    
    # Analyze complexity distribution
    complexity_counts = {}
    for result in results:
        if result['is_valid']:
            status = result['validation_result'].get('status_name', 'UNKNOWN')
            complexity_counts[status] = complexity_counts.get(status, 0) + 1
    
    print("\n📊 Complexity Distribution:")
    for complexity, count in sorted(complexity_counts.items()):
        percentage = (count / len([r for r in results if r['is_valid']])) * 100
        print(f"  {complexity}: {count} chords ({percentage:.1f}%)")
    
    return results

if __name__ == "__main__":
    # Run the tests
    test_results = test_position_finder()
    complexity_results = analyze_chord_complexity()
    
    print(f"\n🎸 All tests completed! Generated chord patterns and analysis ready for review.")
"""Test the fixed fret position indicator logic"""
from chord_chart import ChordChart

def test_chord(name, chord_data, expected_behavior):
    print(f"\n=== Testing {name} ===")
    print(f"Chord data: {chord_data}")
    
    # Get fret positions for analysis
    fret_positions = [fret for finger, fret in chord_data if finger not in ['O', 'X'] and fret > 0]
    if fret_positions:
        print(f"Fret range: {min(fret_positions)} to {max(fret_positions)}")
        print(f"Expected: {expected_behavior}")
    
    # Generate chord
    chart = ChordChart()
    chart.chord_name = name
    svg_content = chart.create_grid_chart(chord_data)
    
    # Check for fret position indicator
    has_fret_indicator = 'fr</text>' in svg_content
    print(f"Has fret position indicator: {has_fret_indicator}")
    
    # Save for visual inspection
    filename = f"test_{name.lower().replace(' ', '_')}_chord.svg"
    chart.save_to_file(chord_data, filename)
    print(f"Saved: {filename}")
    
    return has_fret_indicator

# Test Case 1: E Minor (should NOT have fret indicator)
e_minor_data = [
    ('O', 0),  # 6th string: Open
    ('2', 2),  # 5th string: 2nd finger, 2nd fret  
    ('3', 2),  # 4th string: 3rd finger, 2nd fret
    ('O', 0),  # 3rd string: Open
    ('O', 0),  # 2nd string: Open
    ('O', 0),  # 1st string: Open
]

# Test Case 2: High Fret Chord (should HAVE fret indicator)
high_fret_data = [
    ('T', 8),  # 6th string: Thumb, 8th fret
    ('X', 0),  # 5th string: Muted
    ('4', 10), # 4th string: 4th finger, 10th fret  
    ('3', 6),  # 3rd string: 3rd finger, 6th fret
    ('1', 6),  # 2nd string: 1st finger, 6th fret
    ('X', 0),  # 1st string: Muted
]

# Test Case 3: Chord at 5th fret (should NOT have indicator)
fifth_fret_data = [
    ('1', 3),  # 6th string: 1st finger, 3rd fret
    ('4', 5),  # 5th string: 4th finger, 5th fret  
    ('3', 5),  # 4th string: 3rd finger, 5th fret
    ('2', 4),  # 3rd string: 2nd finger, 4th fret
    ('X', 0),  # 2nd string: Muted
    ('X', 0),  # 1st string: Muted
]

# Run tests
result1 = test_chord("E Minor", e_minor_data, "NO fret indicator (fits in 1-5 fret range)")
result2 = test_chord("High Fret", high_fret_data, "SHOW fret indicator (extends beyond 5th fret)")  
result3 = test_chord("Fifth Fret", fifth_fret_data, "NO fret indicator (max fret is 5th)")

print(f"\n=== Results Summary ===")
print(f"✅ E Minor (1-2 frets): {'PASS' if not result1 else 'FAIL'} - No indicator")
print(f"✅ High Fret (6-10 frets): {'PASS' if result2 else 'FAIL'} - Has indicator")  
print(f"✅ Fifth Fret (3-5 frets): {'PASS' if not result3 else 'FAIL'} - No indicator")

if not result1 and result2 and not result3:
    print("\n🎉 All tests PASSED! Fret indicator logic is working correctly.")
else:
    print("\n❌ Some tests failed. Check the logic.")
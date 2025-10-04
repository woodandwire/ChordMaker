"""
Test script to create a chord with the new chord data comment functionality
"""
from chord_chart import ChordChart

# Create a test chord
chart = ChordChart()
chart.set_chord_name("Test Chord with Data")

# Test chord data
test_data = [
    ('X', 0),    # 6th string muted
    ('O', 0),    # 5th string open
    ('2', 2),    # 4th string, fret 2
    ('1', 1),    # 3rd string, fret 1
    ('3', 3),    # 2nd string, fret 3
    ('O', 0),    # 1st string open
]

print("Creating test chord with embedded data...")
chart.save_to_file(test_data, "chords/test_data_chord.svg")
print("Test chord saved to chords/test_data_chord.svg")
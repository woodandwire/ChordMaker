"""
Test chord with anatomically impossible finger positioning
"""

from chord_chart import ChordChart
from chord_validator import ChordFingeringValidator

# Test creating a chord with impossible finger order
print("Testing chord generation with anatomically impossible fingering...")

# Create impossible chord data: pinky behind index finger
impossible_chord = [
    ('X', 0),  # 6th string muted
    ('4', 1),  # 5th string, 1st fret, 4th finger (pinky)
    ('X', 0),  # 4th string muted  
    ('1', 3),  # 3rd string, 3rd fret, 1st finger (index)
    ('X', 0),  # 2nd string muted
    ('O', 0)   # 1st string open
]

# Validate the chord
validator = ChordFingeringValidator()
result = validator.validate_chord(impossible_chord)

print(f"Chord validation result: {result['status_name']} ({result['status_code']})")
print(f"Is valid: {result['is_valid']}")

print("\nValidation messages:")
for msg in result['messages']:
    severity_symbol = "❌" if msg['severity'] == 'error' else "⚠️" if msg['severity'] == 'warning' else "ℹ️"
    print(f"  {severity_symbol} {msg['severity'].upper()}: {msg['message']}")

# Try to create the chord chart anyway to see if it gets created
if not result['is_valid']:
    print(f"\n⚠️ Chord is INVALID - but creating chart anyway for demonstration...")
else:
    print(f"\n✅ Chord is valid - creating chart...")

chart = ChordChart()
chart.set_chord_name("Impossible Fingering Test")

# Save the impossible chord  
filename = "chords/impossible_fingering_test_chord.svg"
chart.save_to_file(impossible_chord, filename)
print(f"Chart saved to: {filename}")
print("This demonstrates the importance of validation before chord generation!")
"""Test case where adjacent strings are muted - should not warn about accidental muting"""
from chord_validator import ChordFingeringValidator

# Test chord where finger is next to muted strings
chord_data = [
    ('X', 0),  # String 6: Muted
    ('X', 0),  # String 5: Muted  
    ('2', 3),  # String 4: 2nd finger, fret 3
    ('X', 0),  # String 3: Muted (adjacent to finger)
    ('X', 0),  # String 2: Muted
    ('X', 0),  # String 1: Muted
]

print("Testing finger next to muted strings:")
print(f"Chord data: {chord_data}")
print("Finger 2 is on string 4, with string 3 and 5 both muted")
print("Should NOT warn about accidentally muting already muted strings")

validator = ChordFingeringValidator(thumb_reach_strings=6)
result = validator.validate_chord(chord_data)

print(f"\nParsed finger positions:")
for pos in validator.finger_positions:
    print(f"  Finger {pos.finger} on string {pos.string}, fret {pos.fret}")

print(f"\nValidation result:")
print(f"Valid: {result['is_valid']}")
print(f"Status: {result['status_name']} ({result['status_code']})")

if result['messages']:
    print("\nMessages:")
    for msg in result['messages']:
        print(f"  {msg['severity'].upper()}: {msg['message']}")
else:
    print("\n✅ No warnings about muting already muted strings!")
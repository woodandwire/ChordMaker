"""Test the specific chord pattern from the screenshot"""
from chord_validator import ChordFingeringValidator

# Based on the screenshot:
# 6th String: T (Thumb), fret 2
# 5th String: X (Muted), fret 0
# 4th String: X (Muted), fret 0  
# 3rd String: O (Open), fret 0
# 2nd String: 2 (2nd finger), fret 2
# 1st String: X (Muted), fret 0
# Thumb Reach: 6th string only (1)

chord_data = [
    ('T', 2),  # String 6: Thumb, fret 2
    ('X', 0),  # String 5: Muted
    ('X', 0),  # String 4: Muted
    ('O', 0),  # String 3: Open
    ('2', 2),  # String 2: 2nd finger, fret 2
    ('X', 0),  # String 1: Muted
]

print("Testing chord fingering from screenshot:")
print(f"Chord data: {chord_data}")

validator = ChordFingeringValidator(thumb_reach_strings=1)  # 6th string only
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

print(f"\nExpected behavior:")
print("- Should be valid or have minor warnings only")
print("- No thumb position errors (thumb is only on string 6)")
print("- No accidental muting warnings for already muted strings")
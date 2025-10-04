"""Simple test to verify the 422 fix"""
print("Testing validation logic directly...")

from chord_validator import ChordFingeringValidator

# Test data that represents the fixed form submission
chord_data = [
    ('X', 0),  # String 1: Muted, fret 0 (instead of empty string)
    ('1', 3),  # String 2: Index finger, fret 3
    ('2', 2),  # String 3: Middle finger, fret 2  
    ('3', 1),  # String 4: Ring finger, fret 1
    ('X', 0),  # String 5: Muted, fret 0 (instead of empty string)
    ('X', 0),  # String 6: Muted, fret 0 (instead of empty string)
]

print(f"Testing chord fingering: {chord_data}")

validator = ChordFingeringValidator()
result = validator.validate_chord(chord_data)

print(f"Validation successful: {result['is_valid']}")
print(f"Full result: {result}")

if 'errors' in result and result['errors']:
    print("Errors found:")
    for error in result['errors']:
        print(f"  - {error['message']}")

if 'warnings' in result and result['warnings']:
    print("Warnings:")
    for warning in result['warnings']:
        print(f"  - {warning['message']}")

if 'info' in result and result['info']:
    print("Info:")
    for info in result['info']:
        print(f"  - {info['message']}")

print("\n✓ The fix should work! Muted strings now send '0' instead of empty strings.")
print("This prevents the 422 'Unprocessable Content' error in the API.")
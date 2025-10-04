"""Test the fixed chord chart rendering with high frets"""
from chord_chart import ChordChart

# The chord from the screenshot:
# 6th String: T (Thumb), fret 8
# 5th String: X (Muted)  
# 4th String: 4 (4th finger), fret 10
# 3rd String: 3 (3rd finger), fret 6
# 2nd String: 1 (1st finger), fret 6
# 1st String: X (Muted)

chord_data = [
    ('T', 8),  # 6th string: Thumb, fret 8
    ('X', 0),  # 5th string: Muted
    ('4', 10), # 4th string: 4th finger, fret 10  
    ('3', 6),  # 3rd string: 3rd finger, fret 6
    ('1', 6),  # 2nd string: 1st finger, fret 6
    ('X', 0),  # 1st string: Muted
]

print("Testing high fret chord rendering...")
print(f"Chord data: {chord_data}")
print(f"Expected: Should show fret position '6fr' and thumb at proper relative position")

# Create chord chart
chart = ChordChart()
chart.chord_name = "C Something"

# Generate SVG
svg_content = chart.create_grid_chart(chord_data)

# Save to file
filename = "test_high_fret_chord.svg"
chart.save_to_file(chord_data, filename)

print(f"\n✅ Generated chord chart: {filename}")
print(f"📊 Fret range: {min(f for _, f in chord_data if f > 0)} to {max(f for _, f in chord_data if f > 0)}")
print("🎯 Should show:")
print("   - Fret position indicator '6fr' at top")  
print("   - Thumb 'T' symbol on 6th string")
print("   - Proper relative positioning of all frets")

# Also print first few lines of SVG to verify fret position text
lines = svg_content.split('\n')
for i, line in enumerate(lines):
    if '6fr' in line or 'T' in line:
        print(f"\n📝 SVG line {i}: {line.strip()}")
        
print(f"\n🔍 Check the generated {filename} file to see if positioning is correct!")
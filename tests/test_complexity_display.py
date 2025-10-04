#!/usr/bin/env python3
"""
Test script to demonstrate complexity score display in chord charts.
"""

from chord_chart import ChordChart

def test_complexity_display():
    """Test the complexity score display feature."""
    
    # Test chords with different difficulty levels
    test_chords = [
        {
            'name': 'C Major (Easy)',
            'data': [('X', 0), ('1', 1), ('O', 0), ('2', 2), ('3', 3), ('O', 0)],
            'expected': 'Easy'
        },
        {
            'name': 'F Major (Challenging)',
            'data': [('1', 1), ('1', 1), ('2', 2), ('3', 3), ('3', 3), ('1', 1)],
            'expected': 'Challenging'
        },
        {
            'name': 'B7 (Moderate)',
            'data': [('X', 0), ('2', 2), ('1', 1), ('2', 2), ('O', 0), ('2', 2)],
            'expected': 'Moderate'
        },
        {
            'name': 'C#m7b5 (Very Difficult)',
            'data': [('X', 0), ('X', 0), ('1', 2), ('2', 3), ('3', 5), ('4', 6)],
            'expected': 'Very Difficult'
        }
    ]
    
    print("Testing complexity score display in chord charts...")
    
    for i, chord in enumerate(test_chords):
        print(f"\n{i+1}. Creating chart for {chord['name']}...")
        
        # Create the chord chart
        chart = ChordChart()
        chart.set_chord_name(chord['name'])
        
        # Generate the SVG with complexity score
        svg_content = chart.create_grid_chart(chord['data'])
        
        # Save to file
        filename = f"chords/test_complexity_{i+1}_{chord['name'].replace(' ', '_').lower()}.svg"
        chart.save_to_file(chord['data'], filename)
        
        # Check if complexity score is included in SVG
        if 'text-anchor="end"' in svg_content and any(level in svg_content for level in ['E', 'M', 'D', 'VD']):
            print(f"   ✓ Complexity score added to SVG")
        else:
            print(f"   ✗ No complexity score found in SVG")
        
        print(f"   → Saved as: {filename}")
    
    print("\nComplexity display test completed!")
    print("Check the generated SVG files to see the complexity scores in the bottom right corner.")

if __name__ == "__main__":
    test_complexity_display()
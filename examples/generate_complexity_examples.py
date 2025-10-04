#!/usr/bin/env python3
"""
Generate a comprehensive set of chord charts showing complexity scoring in action.
"""

from chord_chart import ChordChart

def generate_complexity_examples():
    """Generate chord charts demonstrating the full range of complexity scoring."""
    
    # Comprehensive test chords covering the full difficulty spectrum
    chord_examples = [
        {
            'name': 'E Major',
            'data': [('O', 0), ('2', 2), ('2', 2), ('1', 1), ('O', 0), ('O', 0)],
            'description': 'Very easy - open strings with adjacent fingers'
        },
        {
            'name': 'A Major',
            'data': [('X', 0), ('O', 0), ('2', 2), ('2', 2), ('2', 2), ('O', 0)],
            'description': 'Easy - three fingers close together'
        },
        {
            'name': 'C Major',
            'data': [('X', 0), ('1', 1), ('O', 0), ('2', 2), ('3', 3), ('O', 0)],
            'description': 'Moderate - standard beginner chord'
        },
        {
            'name': 'F Major',
            'data': [('1', 1), ('1', 1), ('2', 2), ('3', 3), ('3', 3), ('1', 1)],
            'description': 'Challenging - requires barre technique'
        },
        {
            'name': 'G7 Alt',
            'data': [('1', 3), ('2', 5), ('3', 6), ('4', 8), ('X', 0), ('X', 0)],
            'description': 'Difficult - wide fret span with all fingers'
        },
        {
            'name': 'Jazz Chord',
            'data': [('X', 0), ('1', 2), ('2', 4), ('3', 6), ('4', 9), ('X', 0)],
            'description': 'Very Difficult - extreme stretch chord'
        }
    ]
    
    print("Generating comprehensive complexity scoring examples...")
    print("=" * 60)
    
    for i, chord in enumerate(chord_examples):
        print(f"\n{i+1}. {chord['name']} - {chord['description']}")
        
        # Create the chord chart
        chart = ChordChart()
        chart.set_chord_name(chord['name'])
        
        # Generate filename
        filename = f"chords/{chord['name'].replace(' ', '_').lower()}_complexity.svg"
        
        # Save the chart with complexity scoring
        chart.save_to_file(chord['data'], filename)
        print(f"   → Saved as: {filename}")
        
        # Read the SVG to extract the complexity score for display
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find the complexity score line
                for line in content.split('\n'):
                    if 'text-anchor="end"' in line and ('E' in line or 'M' in line or 'D' in line or 'VD' in line):
                        # Extract the score from the SVG line
                        start = line.find('>') + 1
                        end = line.find('</text>')
                        if start < end:
                            complexity_score = line[start:end]
                            print(f"   📊 Complexity Score: {complexity_score}")
                        break
        except Exception as e:
            print(f"   ⚠️ Could not extract complexity score: {e}")
    
    print("\n" + "=" * 60)
    print("Complexity Score Legend:")
    print("  E = Easy (0.0-2.0)")
    print("  M = Moderate (2.0-5.0)")
    print("  D = Difficult/Challenging (5.0-8.0)")
    print("  VD = Very Difficult (8.0+)")
    print("\nAll charts saved with complexity scores in bottom right corner!")

if __name__ == "__main__":
    generate_complexity_examples()
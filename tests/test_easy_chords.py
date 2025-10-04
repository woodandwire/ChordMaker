#!/usr/bin/env python3
"""
Test truly easy chords to see Easy scoring.
"""

from chord_validator import ChordFingeringValidator
from chord_chart import ChordChart

def test_easy_chords():
    """Test chords that should be categorized as Easy."""
    
    # Try some genuinely easy chord patterns
    easy_chords = [
        ('Em (two fingers)', [('O', 0), ('2', 2), ('2', 2), ('O', 0), ('O', 0), ('O', 0)]),
        ('Am (three adjacent)', [('X', 0), ('O', 0), ('2', 2), ('2', 2), ('1', 1), ('O', 0)]),
        ('All Open', [('O', 0), ('O', 0), ('O', 0), ('O', 0), ('O', 0), ('O', 0)])
    ]
    
    validator = ChordFingeringValidator()
    
    for name, data in easy_chords:
        print(f"\n{name}:")
        result = validator.validate_chord(data)
        
        for msg in result.get('messages', []):
            if 'difficulty' in msg.get('message', '').lower():
                print(f"  {msg['message']}")
        
        # Also generate a chart to see the visual scoring
        chart = ChordChart()
        chart.set_chord_name(name)
        filename = f"chords/{name.replace(' ', '_').replace('(', '').replace(')', '').lower()}.svg"
        chart.save_to_file(data, filename)
        
        # Extract complexity score
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                for line in content.split('\n'):
                    if 'text-anchor="end"' in line and any(level in line for level in ['E', 'M', 'D', 'VD']):
                        start = line.find('>') + 1
                        end = line.find('</text>')
                        if start < end:
                            complexity_score = line[start:end]
                            print(f"  Visual Score: {complexity_score}")
                        break
        except Exception as e:
            print(f"  Could not extract visual score: {e}")

if __name__ == "__main__":
    test_easy_chords()
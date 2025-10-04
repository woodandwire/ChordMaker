#!/usr/bin/env python3
"""
Test script to verify enhanced fret gap difficulty scoring.
Tests chords with different fret gaps to ensure complexity scales appropriately.
"""

from chord_validator import ChordFingeringValidator
from chord_chart import ChordChart

def test_fret_gap_complexity():
    """Test that fret gap distances are properly reflected in complexity scores."""
    
    # Define test chords with increasing fret gaps
    test_chords = [
        # Same fret tests (should be easier)
        {
            'name': 'Same Fret (E Major shape)',
            'data': [('O', 0), ('2', 2), ('2', 2), ('1', 1), ('O', 0), ('O', 0)],
            'description': 'Fingers 1-2 on adjacent frets (easy)'
        },
        
        # 1 fret gap tests
        {
            'name': '1 Fret Gap (A Major)',
            'data': [('X', 0), ('O', 0), ('2', 2), ('2', 2), ('2', 2), ('O', 0)],
            'description': 'Three fingers, same fret (natural spacing)'
        },
        
        # 2 fret gap test
        {
            'name': '2 Fret Gap Pattern',
            'data': [('X', 0), ('1', 2), ('O', 0), ('2', 4), ('O', 0), ('O', 0)],
            'description': 'Fingers 1-2 with 2 fret gap (moderate stretch)'
        },
        
        # 3 fret gap test  
        {
            'name': '3 Fret Gap Pattern',
            'data': [('X', 0), ('1', 2), ('O', 0), ('2', 5), ('O', 0), ('O', 0)],
            'description': 'Fingers 1-2 with 3 fret gap (challenging stretch)'
        },
        
        # 4 fret gap test
        {
            'name': '4 Fret Gap Pattern', 
            'data': [('X', 0), ('1', 2), ('O', 0), ('2', 6), ('O', 0), ('O', 0)],
            'description': 'Fingers 1-2 with 4 fret gap (difficult stretch)'
        },
        
        # 5 fret gap test (very hard)
        {
            'name': '5 Fret Gap Pattern',
            'data': [('X', 0), ('1', 2), ('O', 0), ('2', 7), ('O', 0), ('O', 0)],
            'description': 'Fingers 1-2 with 5 fret gap (very difficult)'
        },
        
        # Extreme case - index to pinky stretch
        {
            'name': 'Index-Pinky 4 Fret Gap',
            'data': [('1', 3), ('O', 0), ('O', 0), ('O', 0), ('4', 7), ('O', 0)],
            'description': 'Fingers 1-4 with 4 fret gap (anatomically very hard)'
        },
        
        # Same string complications
        {
            'name': 'Same String 2 Fret Gap',
            'data': [('1', 2), ('2', 4), ('X', 0), ('X', 0), ('X', 0), ('X', 0)],
            'description': 'Fingers 1-2 same string, 2 fret gap (finger interference)'
        }
    ]
    
    validator = ChordFingeringValidator()
    
    print("Testing Enhanced Fret Gap Difficulty Scoring")
    print("=" * 60)
    
    results = []
    
    for i, chord in enumerate(test_chords):
        print(f"\n{i+1}. {chord['name']}")
        print(f"   Description: {chord['description']}")
        
        # Validate the chord
        result = validator.validate_chord(chord['data'])
        
        # Extract difficulty information
        difficulty_score = 0.0
        difficulty_level = "Unknown"
        factors = []
        
        for msg in result.get('messages', []):
            if 'difficulty' in msg.get('message', '').lower():
                message = msg['message']
                print(f"   Validation: {message}")
                
                # Extract score
                if 'score:' in message:
                    try:
                        score_part = message.split('score:')[1].split(')')[0].strip()
                        difficulty_score = float(score_part)
                    except (IndexError, ValueError):
                        pass
                
                # Extract level
                if 'Easy' in message:
                    difficulty_level = "Easy"
                elif 'Moderate' in message:
                    difficulty_level = "Moderate"
                elif 'Challenging' in message or 'Difficult' in message:
                    difficulty_level = "Difficult"
                elif 'Very Difficult' in message:
                    difficulty_level = "Very Difficult"
                
                # Extract factors
                if ' - Factors: ' in message:
                    factors_str = message.split(' - Factors: ')[1]
                    factors = [f.strip() for f in factors_str.split(',')]
        
        results.append({
            'name': chord['name'],
            'score': difficulty_score,
            'level': difficulty_level,
            'factors': factors
        })
        
        print(f"   Score: {difficulty_score:.1f} ({difficulty_level})")
        if factors:
            print(f"   Factors: {', '.join(factors)}")
        
        # Generate visual chord chart
        chart = ChordChart()
        chart.set_chord_name(f"{chord['name']} ({difficulty_score:.1f})")
        filename = f"chords/gap_test_{i+1}_{chord['name'].replace(' ', '_').lower()}.svg"
        chart.save_to_file(chord['data'], filename)
        print(f"   Chart: {filename}")
    
    print("\n" + "=" * 60)
    print("FRET GAP DIFFICULTY PROGRESSION ANALYSIS")
    print("=" * 60)
    
    # Sort by difficulty score to show progression
    results.sort(key=lambda x: x['score'])
    
    for result in results:
        print(f"{result['name']:35} | Score: {result['score']:5.1f} | {result['level']}")
        if result['factors']:
            factors_str = ', '.join(result['factors'])
            if len(factors_str) > 70:
                factors_str = factors_str[:67] + "..."
            print(f"{'':37} | Factors: {factors_str}")
    
    print("\n✅ Enhanced fret gap difficulty scoring test completed!")
    print("Note: Scores should show clear progression with larger gaps being significantly harder.")

if __name__ == "__main__":
    test_fret_gap_complexity()
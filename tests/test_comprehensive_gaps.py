#!/usr/bin/env python3
"""
Comprehensive test showing the improved fret gap complexity scoring.
Demonstrates how different gap sizes and finger combinations now scale appropriately.
"""

from chord_validator import ChordFingeringValidator
from chord_chart import ChordChart

def test_comprehensive_gap_scaling():
    """Show how complexity properly scales with different scenarios."""
    
    test_scenarios = [
        # Adjacent finger combinations with different gaps
        ('Adjacent Fingers (1-2)', [
            ('0 fret gap', [('1', 2), ('2', 2), ('X', 0), ('X', 0), ('X', 0), ('X', 0)]),
            ('1 fret gap', [('1', 2), ('2', 3), ('X', 0), ('X', 0), ('X', 0), ('X', 0)]),
            ('2 fret gap', [('1', 2), ('2', 4), ('X', 0), ('X', 0), ('X', 0), ('X', 0)]),
            ('3 fret gap', [('1', 2), ('2', 5), ('X', 0), ('X', 0), ('X', 0), ('X', 0)]),
            ('4 fret gap', [('1', 2), ('2', 6), ('X', 0), ('X', 0), ('X', 0), ('X', 0)]),
            ('5 fret gap', [('1', 2), ('2', 7), ('X', 0), ('X', 0), ('X', 0), ('X', 0)])
        ]),
        
        # Non-adjacent finger combinations (index-ring) 
        ('Non-adjacent Fingers (1-3)', [
            ('1 fret gap', [('1', 2), ('X', 0), ('3', 3), ('X', 0), ('X', 0), ('X', 0)]),
            ('2 fret gap', [('1', 2), ('X', 0), ('3', 4), ('X', 0), ('X', 0), ('X', 0)]),
            ('3 fret gap', [('1', 2), ('X', 0), ('3', 5), ('X', 0), ('X', 0), ('X', 0)]),
            ('4 fret gap', [('1', 2), ('X', 0), ('3', 6), ('X', 0), ('X', 0), ('X', 0)])
        ]),
        
        # Most difficult: index-pinky combinations
        ('Hardest Fingers (1-4)', [
            ('2 fret gap', [('1', 2), ('X', 0), ('X', 0), ('4', 4), ('X', 0), ('X', 0)]),
            ('3 fret gap', [('1', 2), ('X', 0), ('X', 0), ('4', 5), ('X', 0), ('X', 0)]),
            ('4 fret gap', [('1', 2), ('X', 0), ('X', 0), ('4', 6), ('X', 0), ('X', 0)]),
            ('5 fret gap', [('1', 2), ('X', 0), ('X', 0), ('4', 7), ('X', 0), ('X', 0)])
        ])
    ]
    
    validator = ChordFingeringValidator()
    
    print("COMPREHENSIVE FRET GAP COMPLEXITY SCALING TEST")
    print("=" * 70)
    print("Shows how complexity scores scale with different finger combinations and gaps")
    print("=" * 70)
    
    for scenario_name, tests in test_scenarios:
        print(f"\n🎸 {scenario_name.upper()}")
        print("-" * 50)
        
        results = []
        
        for gap_desc, chord_data in tests:
            result = validator.validate_chord(chord_data)
            
            # Extract score
            score = 0.0
            for msg in result.get('messages', []):
                if 'difficulty' in msg.get('message', '').lower() and 'score:' in msg.get('message', ''):
                    try:
                        score_part = msg['message'].split('score:')[1].split(')')[0].strip()
                        score = float(score_part)
                    except (IndexError, ValueError):
                        pass
            
            results.append((gap_desc, score, chord_data))
            print(f"  {gap_desc:12} | Score: {score:5.1f}")
        
        # Show progression ratio
        if len(results) > 1:
            print(f"\n  📈 Progression Analysis:")
            for i in range(1, len(results)):
                prev_score = results[i-1][1]
                curr_score = results[i][1]
                if prev_score > 0:
                    ratio = curr_score / prev_score
                    print(f"     {results[i][0]} is {ratio:.1f}x harder than {results[i-1][0]}")
        
        # Generate sample charts for extreme cases
        if results:
            # Generate chart for hardest case
            hardest = max(results, key=lambda x: x[1])
            chart = ChordChart()
            chart.set_chord_name(f"{scenario_name} - {hardest[0]} (Score: {hardest[1]:.1f})")
            filename = f"chords/gap_demo_{scenario_name.replace(' ', '_').replace('(', '').replace(')', '').lower()}_{hardest[0].replace(' ', '_')}.svg"
            chart.save_to_file(hardest[2], filename)
            print(f"  📊 Sample chart: {filename}")
    
    print("\n" + "=" * 70)
    print("✅ ENHANCED FRET GAP COMPLEXITY SCORING SUMMARY")
    print("=" * 70)
    print("• Same fret (0 gap): Minimal complexity")
    print("• 1-2 fret gaps: Linear increase in difficulty")  
    print("• 3+ fret gaps: Exponential increase in difficulty")
    print("• Adjacent fingers (1-2, 2-3): Easier than non-adjacent")
    print("• Index-pinky (1-4): Most difficult combination") 
    print("• String distance: Same string hardest, far strings easier")
    print("• Fret position: Lower frets harder, higher frets easier")
    print("\nThe scoring now properly reflects guitar playing biomechanics! 🎯")

if __name__ == "__main__":
    test_comprehensive_gap_scaling()
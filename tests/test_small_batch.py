#!/usr/bin/env python3
"""
Run a small batch of position_finder to see how many impossible patterns are being generated.
"""

from position_finder import PositionFinder
import sys

def test_small_batch():
    """Run position finder on a small batch to analyze impossible patterns."""
    
    print("🔍 TESTING POSITION FINDER OUTPUT")
    print("=" * 50)
    
    # Run position finder with a small limit to see what gets generated
    finder = PositionFinder(output_dir="test_output")
    
    print("Generating patterns (limit: 50)...")
    results = finder.generate_and_validate_patterns(limit=50)
    
    # Analyze results
    valid_count = sum(1 for r in results if r['is_valid'])
    invalid_count = sum(1 for r in results if not r['is_valid'])
    
    print(f"\nResults summary:")
    print(f"Total patterns generated: {len(results)}")
    print(f"Valid patterns: {valid_count}")
    print(f"Invalid patterns: {invalid_count}")
    print(f"Invalid rate: {invalid_count/len(results)*100:.1f}%")
    
    # Show some invalid patterns
    invalid_patterns = [r for r in results if not r['is_valid']][:5]
    
    if invalid_patterns:
        print(f"\nFirst {len(invalid_patterns)} invalid patterns:")
        for i, pattern_result in enumerate(invalid_patterns, 1):
            pattern = pattern_result['pattern']
            pattern_id = pattern_result['pattern_id']
            validation = pattern_result['validation_result']
            status = validation.get('status_name', 'UNKNOWN')
            
            print(f"\n{i}. Pattern {pattern_id}: {pattern}")
            print(f"   Status: {status}")
            
            # Show error messages
            errors = [msg for msg in validation.get('messages', []) if msg['severity'] == 'error']
            if errors:
                print(f"   Errors: {errors[0]['message']}")
    
    print(f"\nStatistics from finder:")
    print(f"Total generated: {finder.stats['total_generated']}")
    print(f"Valid chords: {finder.stats['valid_chords']}")
    print(f"Invalid chords: {finder.stats['invalid_chords']}")

if __name__ == "__main__":
    test_small_batch()
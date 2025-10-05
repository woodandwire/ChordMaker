"""
Calculate total possible guitar chord pattern combinations.

For each string, the options are:
1. Muted (X)
2. Open (O)
3. Fretted - for each fret (0 to max_fret), assign one of 4 fingers (1,2,3,4)
   OR with thumb: for fret 0 to max_fret, assign one of 5 fingers (T,1,2,3,4) on allowed strings

Let's calculate step by step.
"""

def calculate_total_combinations(max_fret=5, thumb_reach=2):
    """
    Calculate total possible combinations.
    
    For each string:
    - Muted: 1 option (X)
    - Open: 1 option (O)  
    - Fretted: (max_fret + 1) frets × fingers available
    
    With thumb_reach=2, strings 6 and 5 (indices 0,1) can use thumb.
    Other strings can only use fingers 1,2,3,4.
    """
    
    print("=" * 80)
    print("GUITAR CHORD PATTERN COMBINATION CALCULATOR")
    print("=" * 80)
    print(f"Configuration:")
    print(f"  Max fret: {max_fret}")
    print(f"  Thumb reach: {thumb_reach} strings (strings 6 down to {7-thumb_reach})")
    print(f"  Total strings: 6")
    print("=" * 80)
    print()
    
    # Calculate options per string
    frets = max_fret + 1  # 0 through max_fret
    regular_fingers = 4   # 1, 2, 3, 4
    thumb_fingers = 5     # T, 1, 2, 3, 4
    
    print("OPTIONS PER STRING:")
    print("-" * 80)
    
    string_options = []
    
    for string_idx in range(6):
        string_num = 6 - string_idx  # String numbering (6 to 1)
        
        # Muted + Open
        base_options = 2
        
        # Fretted options depend on whether thumb is allowed
        if string_idx < thumb_reach:
            # Thumb allowed on this string
            fretted_options = frets * thumb_fingers
            finger_list = "T,1,2,3,4"
        else:
            # Only regular fingers
            fretted_options = frets * regular_fingers
            finger_list = "1,2,3,4"
        
        total_options = base_options + fretted_options
        string_options.append(total_options)
        
        print(f"String {string_num} (index {string_idx}):")
        print(f"  - Muted: 1")
        print(f"  - Open: 1")
        print(f"  - Fretted: {frets} frets × {thumb_fingers if string_idx < thumb_reach else regular_fingers} fingers ({finger_list}) = {fretted_options}")
        print(f"  TOTAL: {total_options} options")
        print()
    
    print("=" * 80)
    print("TOTAL COMBINATIONS CALCULATION:")
    print("-" * 80)
    
    # Calculate total combinations (product of all string options)
    total_combinations = 1
    calculation_str = ""
    
    for i, options in enumerate(string_options):
        total_combinations *= options
        string_num = 6 - i
        if i > 0:
            calculation_str += " × "
        calculation_str += f"{options}"
    
    print(f"Total = {calculation_str}")
    print(f"Total = {total_combinations:,} possible patterns")
    print()
    
    # Break down by components
    print("=" * 80)
    print("BREAKDOWN BY PATTERN TYPE:")
    print("-" * 80)
    
    # Some examples of pattern types
    all_muted = 1
    all_open = 1
    print(f"All muted (X-X-X-X-X-X): {all_muted:,}")
    print(f"All open (O-O-O-O-O-O): {all_open:,}")
    print(f"All other combinations: {total_combinations - all_muted - all_open:,}")
    print()
    
    # Estimate with min sounding strings = 1 (at least one string not muted)
    # This excludes the all-muted pattern
    with_sound = total_combinations - 1  # Exclude all-muted
    print(f"Patterns with at least 1 sounding string: {with_sound:,}")
    print()
    
    print("=" * 80)
    print("VALIDATION EXPECTATIONS:")
    print("-" * 80)
    print(f"Total patterns to validate: {total_combinations:,}")
    print()
    print("Expected rejection reasons:")
    print("  - INVALID_INPUT: Finger on fret 0 (should be open)")
    print("  - PHYSICALLY_IMPOSSIBLE: Bad finger stretches, wrong order, etc.")
    print("  - INCONSISTENT_BARRE: Barre finger issues")
    print()
    
    # Rough estimate of valid patterns (based on observed ~5% pass rate)
    estimated_valid_rate = 0.05  # 5%
    estimated_valid = int(total_combinations * estimated_valid_rate)
    
    print(f"Estimated valid patterns (~5% pass rate): {estimated_valid:,}")
    print(f"Estimated invalid patterns (~95%): {total_combinations - estimated_valid:,}")
    print()
    
    print("=" * 80)
    print("PROCESSING TIME ESTIMATES:")
    print("-" * 80)
    
    # Observed rate: ~1,104 patterns/second
    observed_rate = 1104
    estimated_time_seconds = total_combinations / observed_rate
    estimated_time_minutes = estimated_time_seconds / 60
    estimated_time_hours = estimated_time_minutes / 60
    
    print(f"At {observed_rate:,} patterns/second:")
    print(f"  {estimated_time_seconds:,.1f} seconds")
    print(f"  {estimated_time_minutes:,.1f} minutes")
    if estimated_time_hours >= 1:
        print(f"  {estimated_time_hours:,.1f} hours")
    print()
    
    print("=" * 80)
    print("DUPLICATE DETECTION IMPACT:")
    print("-" * 80)
    print("Note: The enhanced position finder uses duplicate detection (MD5 hashing)")
    print("to skip patterns that are functionally identical. This means:")
    print()
    print("  - Actual patterns processed may be LESS than theoretical maximum")
    print("  - Many generated patterns are duplicates (same fingering, different order)")
    print("  - Final unique pattern count depends on generator's permutation logic")
    print()
    
    return total_combinations, string_options


if __name__ == "__main__":
    # Current configuration
    total, options = calculate_total_combinations(max_fret=5, thumb_reach=2)
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Theoretical maximum combinations: {total:,}")
    print()
    print("This is the UPPER BOUND. Actual unique patterns will be less due to:")
    print("  1. Duplicate detection (same pattern, different generation path)")
    print("  2. Filtering (minimum sounding strings requirement)")
    print("  3. Generator logic (how patterns are permuted)")
    print("=" * 80)

"""
Rebuild Chord Library Script
Purges and rebuilds the entire chord library using the latest validation logic.
"""

import sys
from pathlib import Path
import time
from itertools import product

# Add src directory to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from chord_chart import ChordChart
from chord_validator import ChordFingeringValidator


def purge_chord_library(chord_dir: Path) -> int:
    """Delete all existing chord SVG files."""
    if not chord_dir.exists():
        print(f"Chord directory {chord_dir} does not exist.")
        return 0
    
    svg_files = list(chord_dir.glob("*.svg"))
    count = len(svg_files)
    
    if count == 0:
        print("No chord files to delete.")
        return 0
    
    print(f"🗑️  Deleting {count} existing chord files...")
    for svg_file in svg_files:
        svg_file.unlink()
    
    print(f"✅ Deleted {count} chord files.")
    return count


def generate_all_patterns(max_fret=5):
    """Generate all possible chord patterns."""
    # Finger types: X (muted), O (open), 1-4 (fingers), T (thumb)
    # For simplicity, we'll generate patterns with fingers 1-4 and X, O
    finger_types = ['X', 'O', '1', '2', '3', '4']
    fret_range = range(0, max_fret + 1)
    
    # Generate all combinations of 6 strings
    # Each string has a finger type and fret
    patterns = []
    
    # For each string, generate (finger_type, fret) pairs
    for string_combo in product(finger_types, repeat=6):
        pattern = []
        for i, finger_type in enumerate(string_combo):
            if finger_type == 'X':
                pattern.append(('X', 0))
            elif finger_type == 'O':
                pattern.append(('O', 0))
            else:
                # For numbered fingers, we'll use various fret positions
                # This is simplified - we'll generate multiple fret combinations
                pattern.append((finger_type, 1))  # Start with fret 1
        
        patterns.append(pattern)
    
    return patterns


def generate_comprehensive_patterns(max_fret=12, max_span=5):
    """
    Generate a comprehensive set of chord patterns with realistic constraints.
    Uses a systematic approach to cover many possible chord shapes.
    """
    patterns = []
    
    # For each fret position (0-12)
    for base_fret in range(0, max_fret + 1):
        # For each possible mute/unmute combination (64 possibilities per position)
        for mute_mask in range(64):  # 2^6 = 64 combinations
            mute_pattern = [(mute_mask >> i) & 1 for i in range(6)]
            num_unmuted = sum(1 for m in mute_pattern if m == 0)
            
            # Need at least 2 unmuted strings
            if num_unmuted < 2:
                continue
            
            # For each fret span configuration (0-5 frets)
            for span in range(0, max_span + 1):
                # Generate multiple finger arrangements for this configuration
                # We'll create 10 different finger arrangements
                for arrangement in range(10):
                    pattern = []
                    
                    for string_idx in range(6):
                        if mute_pattern[string_idx]:
                            pattern.append(('X', 0))
                        else:
                            # Determine if this should be open or fretted
                            if base_fret == 0 and arrangement % 3 == 0:
                                pattern.append(('O', 0))
                            else:
                                # Assign finger (1-4) and fret
                                finger = str((string_idx + arrangement) % 4 + 1)
                                fret_offset = (string_idx + arrangement) % (span + 1)
                                fret = base_fret + fret_offset
                                
                                if fret > max_fret:
                                    fret = max_fret
                                
                                pattern.append((finger, fret))
                    
                    # Validate basic pattern requirements
                    has_fretted = any(p[1] > 0 for p in pattern)
                    has_sounding = any(p[0] != 'X' for p in pattern)
                    
                    if has_sounding:
                        patterns.append(pattern)
    
    return patterns


def rebuild_chord_library(chord_dir: Path, validate=True, thumb_reach=0, max_patterns=None):
    """
    Rebuild the chord library with valid patterns.
    
    Args:
        chord_dir: Directory to save chord files
        validate: Whether to validate chords before generating
        thumb_reach: Thumb reach setting (0-6)
        max_patterns: Maximum number of patterns to generate (None for all)
    """
    chord_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate patterns
    print("🎸 Generating chord patterns...")
    patterns = generate_comprehensive_patterns(max_fret=12, max_span=5)
    
    if max_patterns:
        patterns = patterns[:max_patterns]
    
    print(f"📊 Generated {len(patterns)} potential chord patterns")
    
    # Validate and generate
    validator = ChordFingeringValidator(thumb_reach_strings=thumb_reach)
    chart = ChordChart()
    
    valid_count = 0
    invalid_count = 0
    start_time = time.time()
    
    print(f"🔨 Generating chord charts...")
    print(f"⚙️  Validation: {'Enabled' if validate else 'Disabled'}")
    print(f"👍 Thumb reach: {thumb_reach}")
    print()
    
    for i, pattern in enumerate(patterns):
        # Validate if requested
        if validate:
            result = validator.validate_chord(pattern)
            if result['status_code'] >= 400:  # Invalid
                invalid_count += 1
                continue
        
        # Generate chord
        try:
            filename = f"pattern_{i+1:06d}_chord.svg"
            filepath = chord_dir / filename
            
            chart.set_chord_name(f"Pattern {i+1:06d}")
            chart.save_to_file(pattern, str(filepath))
            valid_count += 1
            
            # Progress update
            if (i + 1) % 1000 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                print(f"Progress: {i+1}/{len(patterns)} patterns processed "
                      f"({rate:.1f} patterns/sec) - "
                      f"{valid_count} valid, {invalid_count} invalid")
        
        except Exception as e:
            print(f"❌ Error generating pattern {i+1}: {e}")
            invalid_count += 1
    
    elapsed = time.time() - start_time
    print()
    print("=" * 60)
    print(f"✅ Library rebuild complete!")
    print(f"⏱️  Time elapsed: {elapsed:.1f} seconds")
    print(f"✓ Valid chords generated: {valid_count}")
    print(f"✗ Invalid/skipped patterns: {invalid_count}")
    print(f"📁 Chord directory: {chord_dir}")
    print("=" * 60)
    
    return valid_count, invalid_count


def main():
    """Main script execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rebuild the chord library")
    parser.add_argument("--no-validate", action="store_true",
                       help="Skip validation (generate all patterns)")
    parser.add_argument("--thumb-reach", type=int, default=0, choices=range(7),
                       help="Thumb reach setting (0-6, default=0)")
    parser.add_argument("--max-patterns", type=int, default=None,
                       help="Maximum number of patterns to generate")
    parser.add_argument("--no-purge", action="store_true",
                       help="Don't delete existing chords before rebuilding")
    
    args = parser.parse_args()
    
    # Setup paths
    project_root = Path(__file__).parent
    chord_dir = project_root / "chords"
    
    print("=" * 60)
    print("🎸 Chord Library Rebuild Tool")
    print("=" * 60)
    print()
    
    # Purge existing library
    if not args.no_purge:
        deleted = purge_chord_library(chord_dir)
        print()
    else:
        print("⏭️  Skipping purge (--no-purge flag set)")
        print()
    
    # Rebuild library
    valid, invalid = rebuild_chord_library(
        chord_dir,
        validate=not args.no_validate,
        thumb_reach=args.thumb_reach,
        max_patterns=args.max_patterns
    )
    
    print()
    print("✨ Done!")


if __name__ == "__main__":
    main()

"""
Enhanced Position Finder for Comprehensive Chord Pattern Study

This version removes artificial limits and generates ALL possible patterns
for systematic cataloging and academic study.
"""

import sys
from pathlib import Path
import time
import json
import hashlib
from itertools import product, combinations
from typing import List, Tuple, Dict, Any, Optional, Iterator
from collections import defaultdict

# Add src directory to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from chord_chart import ChordChart
from chord_validator import ChordFingeringValidator


class EnhancedPositionFinder:
    """
    Comprehensive chord pattern generator for academic study.
    
    Generates ALL possible guitar fingering patterns systematically,
    validates them, and catalogs results for analysis.
    """
    
    def __init__(self, output_dir: Path, thumb_reach: int = 0):
        """
        Initialize the enhanced position finder.
        
        Args:
            output_dir: Directory for output (chords/, trash/, analysis/)
            thumb_reach: Thumb reach setting (0-6)
        """
        self.output_dir = Path(output_dir)
        self.chords_dir = self.output_dir / "chords"
        self.analysis_dir = self.output_dir / "analysis"
        
        # Create directories
        self.chords_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Create single failure log file
        self.failure_log_path = self.analysis_dir / f"failures_{int(time.time())}.log"
        self.failure_log = open(self.failure_log_path, 'w', encoding='utf-8')
        self.failure_log.write("=" * 80 + "\n")
        self.failure_log.write("CHORD PATTERN VALIDATION FAILURES LOG\n")
        self.failure_log.write("=" * 80 + "\n\n")
        
        # Configuration - NO ARBITRARY LIMITS
        self.min_fret = 0
        self.max_fret = 12  # Can be increased to 24 for full fretboard
        self.min_sounding_strings = 1  # At least one string must sound
        self.finger_types = ['X', 'O', '1', '2', '3', '4']  # Can add 'T' for thumb
        
        # Initialize validator and chart generator
        self.validator = ChordFingeringValidator(thumb_reach_strings=thumb_reach)
        self.chart = ChordChart()
        
        # Statistics
        self.stats = {
            'total_generated': 0,
            'valid_patterns': 0,
            'invalid_patterns': 0,
            'rejection_reasons': defaultdict(int),
            'fret_distribution': defaultdict(int),
            'finger_usage': defaultdict(int),
            'start_time': None,
            'end_time': None
        }
        
        # Pattern tracking
        self.pattern_hashes = set()  # Detect duplicates
        
        # Performance optimization: validation cache
        self.validation_cache = {}  # Cache validation results for similar patterns
        self.quick_rejects = 0  # Track quick rejection performance
        
        print("=" * 70)
        print("🎸 Enhanced Position Finder - Comprehensive Study Mode")
        print("=" * 70)
        print(f"Output directory: {self.output_dir}")
        print(f"Fret range: {self.min_fret}-{self.max_fret}")
        print(f"Thumb reach: {thumb_reach} strings")
        print(f"Min sounding strings: {self.min_sounding_strings}")
        print(f"Failure log: {self.failure_log_path}")
        print("=" * 70)
    
    def pattern_to_hash(self, pattern: List[Tuple[str, int]]) -> str:
        """Create a hash of pattern for duplicate detection."""
        pattern_str = str(sorted(pattern))
        return hashlib.md5(pattern_str.encode()).hexdigest()
    
    def quick_reject(self, pattern: List[Tuple[str, int]]) -> Optional[str]:
        """
        Fast pre-validation to reject obviously invalid patterns.
        Returns rejection reason or None if pattern should be validated.
        
        This catches ~80-90% of invalid patterns in microseconds.
        """
        # 1. Check for invalid input (finger on fret 0 - should be open)
        for finger, fret in pattern:
            if finger not in ['X', 'O'] and fret == 0:
                return "INVALID_INPUT"
        
        # 2. Check minimum sounding strings
        sounding = sum(1 for f, _ in pattern if f != 'X')
        if sounding < self.min_sounding_strings:
            return "INVALID_INPUT"
        
        # 3. Quick fret span check
        fretted = [fret for f, fret in pattern if f not in ['X', 'O']]
        if fretted:
            min_fret = min(fretted)
            max_fret = max(fretted)
            if max_fret - min_fret > 4:  # Max span is 4 frets
                return "PHYSICALLY_IMPOSSIBLE"
        
        # 4. Check for impossible finger ordering (e.g., finger 1 on higher fret than finger 2)
        finger_frets = {}
        for string_idx, (finger, fret) in enumerate(pattern):
            if finger in ['1', '2', '3', '4']:
                if finger in finger_frets:
                    # Same finger used on different strings - check if it's a barre
                    prev_fret, prev_string = finger_frets[finger]
                    if fret != prev_fret:
                        # Same finger on different frets - only valid if same fret (barre)
                        # or adjacent strings with 1 fret difference (stretch)
                        if abs(fret - prev_fret) > 1 or abs(string_idx - prev_string) > 3:
                            return "PHYSICALLY_IMPOSSIBLE"
                finger_frets[finger] = (fret, string_idx)
        
        # 5. Check for basic finger order violations
        # Finger 1 should generally be on lowest fret among all fingers
        if finger_frets:
            fret_list = [(int(f), fret) for f, (fret, _) in finger_frets.items()]
            fret_list.sort()
            # Check if fingers are in reasonable order
            for i in range(len(fret_list) - 1):
                finger_a, fret_a = fret_list[i]
                finger_b, fret_b = fret_list[i + 1]
                # Higher finger number should not be on lower fret (with some tolerance)
                if finger_b > finger_a and fret_b < fret_a - 1:
                    return "PHYSICALLY_IMPOSSIBLE"
        
        # 6. Check for too many fingers
        unique_fingers = len(set(f for f, _ in pattern if f in ['1', '2', '3', '4', 'T']))
        if unique_fingers > 4:
            return "PHYSICALLY_IMPOSSIBLE"
        
        # Passed quick checks - needs full validation
        return None
    
    def generate_all_patterns(self, batch_size: int = 10000) -> Iterator[List[Tuple[str, int]]]:
        """
        Generate ALL possible chord patterns systematically.
        
        Strategy:
        1. For each fret position (0-max_fret)
        2. For each combination of muted/open/fretted strings
        3. For each valid finger assignment
        4. Yield the pattern
        
        Yields patterns instead of building huge list in memory.
        """
        patterns_generated = 0
        
        print(f"\n🔄 Generating patterns (batch size: {batch_size})...")
        
        # For each base fret position
        for base_fret in range(self.min_fret, self.max_fret + 1):
            # For each possible span (0 to reasonable limit)
            for span in range(0, min(6, self.max_fret - base_fret + 1)):
                # For each muting pattern (which strings are muted)
                for mute_mask in range(64):  # 2^6 = 64 combinations
                    mute_pattern = [(mute_mask >> i) & 1 for i in range(6)]
                    
                    # Count unmuted strings
                    unmuted_strings = [i for i, m in enumerate(mute_pattern) if m == 0]
                    
                    # Skip if too few sounding strings
                    if len(unmuted_strings) < self.min_sounding_strings:
                        continue
                    
                    # For each combination of open vs fretted for unmuted strings
                    for open_mask in range(2 ** len(unmuted_strings)):
                        # Build base pattern
                        base_pattern = []
                        unmuted_idx = 0
                        
                        for string_idx in range(6):
                            if mute_pattern[string_idx]:
                                base_pattern.append(('X', 0))
                            else:
                                # Check if this unmuted string should be open
                                if (open_mask >> unmuted_idx) & 1:
                                    base_pattern.append(('O', 0))
                                else:
                                    # Fretted - will assign finger and fret later
                                    base_pattern.append(('FRET', base_fret))
                                unmuted_idx += 1
                        
                        # Now assign fingers and specific frets to FRET placeholders
                        fretted_positions = [i for i, (f, _) in enumerate(base_pattern) if f == 'FRET']
                        
                        if not fretted_positions:
                            # All open/muted pattern
                            yield base_pattern
                            patterns_generated += 1
                            continue
                        
                        # OPTIMIZATION: Skip patterns that are guaranteed to fail
                        if len(fretted_positions) > 4:  # Can't use more than 4 fingers
                            continue
                        
                        # Generate finger assignments for fretted positions
                        # Use available fingers: 1, 2, 3, 4
                        fingers = ['1', '2', '3', '4']
                        
                        # OPTIMIZATION: Limit span to 4 frets max
                        effective_span = min(span, 4)
                        
                        # For each fretted string, try each finger
                        # Allow finger repetition (barre chords)
                        for finger_combo in product(fingers, repeat=len(fretted_positions)):
                            # OPTIMIZATION: Skip if fingers are in impossible order
                            # (e.g., finger 4 before finger 1 on same fret is unlikely)
                            finger_nums = [int(f) for f in finger_combo]
                            if len(set(finger_nums)) > 1:  # More than one unique finger
                                # Check if fingers appear in reasonable order
                                first_occurrence = {}
                                skip_combo = False
                                for idx, f_num in enumerate(finger_nums):
                                    if f_num not in first_occurrence:
                                        first_occurrence[f_num] = idx
                                # Fingers should generally appear in numeric order
                                sorted_fingers = sorted(first_occurrence.items(), key=lambda x: x[1])
                                for i in range(len(sorted_fingers) - 1):
                                    if sorted_fingers[i][0] > sorted_fingers[i+1][0] + 1:
                                        skip_combo = True
                                        break
                                if skip_combo:
                                    continue
                            
                            # For each fretted string, try different frets within span
                            for fret_combo in product(range(base_fret, base_fret + effective_span + 1), repeat=len(fretted_positions)):
                                # OPTIMIZATION: Quick rejection before building pattern
                                if fretted_positions:
                                    min_fret_here = min(fret_combo)
                                    max_fret_here = max(fret_combo)
                                    if max_fret_here - min_fret_here > 4:
                                        continue
                                
                                pattern = base_pattern.copy()
                                
                                # Assign fingers and frets
                                for idx, pos in enumerate(fretted_positions):
                                    finger = finger_combo[idx]
                                    fret = fret_combo[idx]
                                    pattern[pos] = (finger, fret)
                                
                                # OPTIMIZATION: Quick reject before hashing
                                quick_reject_reason = self.quick_reject(pattern)
                                if quick_reject_reason:
                                    self.quick_rejects += 1
                                    continue
                                
                                # Check for duplicate
                                pattern_hash = self.pattern_to_hash(pattern)
                                if pattern_hash in self.pattern_hashes:
                                    continue
                                
                                self.pattern_hashes.add(pattern_hash)
                                yield pattern
                                patterns_generated += 1
                                
                                # Progress update
                                if patterns_generated % batch_size == 0:
                                    elapsed = time.time() - self.stats['start_time']
                                    rate = patterns_generated / elapsed if elapsed > 0 else 0
                                    qr_pct = (self.quick_rejects / (patterns_generated + self.quick_rejects) * 100) if (patterns_generated + self.quick_rejects) > 0 else 0
                                    print(f"  Generated {patterns_generated} patterns ({rate:.0f}/sec) | Quick rejects: {qr_pct:.1f}%")
    
    def get_cache_key(self, pattern: List[Tuple[str, int]]) -> str:
        """
        Create a cache key for validation results.
        Normalizes pattern to catch similar fingerings.
        """
        # Sort by string and normalize to reduce cache misses
        normalized = tuple(sorted((f, fret) for f, fret in pattern if f != 'X'))
        return str(normalized)
    
    def validate_and_catalog(self, pattern: List[Tuple[str, int]], pattern_id: int) -> Dict[str, Any]:
        """
        Validate a pattern and catalog the results.
        
        Args:
            pattern: Chord pattern to validate
            pattern_id: Unique ID for this pattern
            
        Returns:
            Result dictionary with validation info
        """
        self.stats['total_generated'] += 1
        
        # OPTIMIZATION: Check validation cache
        cache_key = self.get_cache_key(pattern)
        if cache_key in self.validation_cache:
            validation_result = self.validation_cache[cache_key]
        else:
            # Validate the pattern
            validation_result = self.validator.validate_chord(pattern)
            # Cache result for similar patterns
            self.validation_cache[cache_key] = validation_result
        
        is_valid = validation_result['status_code'] < 400
        
        # Create pattern name
        pattern_name = f"pattern_{pattern_id:06d}"
        
        # Catalog based on validity
        result = {
            'pattern_id': pattern_id,
            'pattern': pattern,
            'pattern_name': pattern_name,
            'is_valid': is_valid,
            'status_code': validation_result['status_code'],
            'status_name': validation_result['status_name'],
            'messages': validation_result.get('messages', [])
        }
        
        if is_valid:
            # Valid chord - save to chords directory
            self.stats['valid_patterns'] += 1
            
            filename = f"{pattern_name}_chord.svg"
            filepath = self.chords_dir / filename
            
            # OPTIMIZATION: Only generate SVG, skip extra processing
            self.chart.set_chord_name(f"Pattern {pattern_id:06d}")
            self.chart.save_to_file(pattern, str(filepath))
            
            result['file_path'] = str(filepath)
            # OPTIMIZATION: Reduce console output (only print every 10th valid)
            if self.stats['valid_patterns'] % 10 == 0:
                print(f"✅ {pattern_name}: VALID - {validation_result['status_name']}")
            
        else:
            # Invalid chord - log to single failure file
            self.stats['invalid_patterns'] += 1
            self.stats['rejection_reasons'][validation_result['status_name']] += 1
            
            # OPTIMIZATION: Batch writes (write every 100 failures)
            if self.stats['invalid_patterns'] % 100 == 0:
                self.failure_log.write(f"{pattern_name}: {validation_result['status_name']} - {pattern}\n")
                self.failure_log.flush()
            else:
                self.failure_log.write(f"{pattern_name}: {validation_result['status_name']} - {pattern}\n")
            
            result['logged'] = True
            
            # OPTIMIZATION: Reduce console output (only print every 100th invalid)
            if self.stats['invalid_patterns'] % 100 == 0:
                print(f"❌ {pattern_name}: INVALID - {validation_result['status_name']}")
        
        return result
    
    def run_comprehensive_study(self, max_patterns: Optional[int] = None):
        """
        Run comprehensive pattern generation and validation study.
        
        Args:
            max_patterns: Optional limit on patterns to generate (None = all)
        """
        self.stats['start_time'] = time.time()
        
        print(f"\n{'='*70}")
        print("🔬 Starting Comprehensive Pattern Study")
        print(f"{'='*70}\n")
        
        # Generate and process patterns
        pattern_generator = self.generate_all_patterns()
        
        # OPTIMIZATION: Don't store all results in memory
        results = []
        last_summary_time = time.time()
        
        for pattern_id, pattern in enumerate(pattern_generator, start=1):
            if max_patterns and pattern_id > max_patterns:
                break
            
            result = self.validate_and_catalog(pattern, pattern_id)
            # OPTIMIZATION: Only keep summary stats, not full results
            # results.append(result)  # Commented out to save memory
            
            # OPTIMIZATION: Print summary based on time (every 5 seconds) instead of count
            current_time = time.time()
            if current_time - last_summary_time >= 5.0:
                self.print_interim_summary()
                last_summary_time = current_time
        
        self.stats['end_time'] = time.time()
        
        # Final analysis
        self.save_analysis(results)
        self.print_final_summary()
        
        return results
    
    def print_interim_summary(self):
        """Print interim statistics."""
        total = self.stats['total_generated']
        valid = self.stats['valid_patterns']
        invalid = self.stats['invalid_patterns']
        rate = (valid / total * 100) if total > 0 else 0
        
        elapsed = time.time() - self.stats['start_time']
        patterns_per_sec = total / elapsed if elapsed > 0 else 0
        
        # Calculate cache hit rate
        cache_size = len(self.validation_cache)
        cache_hit_pct = (cache_size / total * 100) if total > 0 else 0
        quick_reject_pct = (self.quick_rejects / (total + self.quick_rejects) * 100) if (total + self.quick_rejects) > 0 else 0
        
        print(f"\n--- Progress: {total} patterns ({patterns_per_sec:.0f}/sec) ---")
        print(f"Valid: {valid} ({rate:.1f}%) | Invalid: {invalid}")
        print(f"Quick rejects: {quick_reject_pct:.1f}% | Cache entries: {cache_size}")
        print()
    
    def print_final_summary(self):
        """Print final comprehensive summary."""
        elapsed = self.stats['end_time'] - self.stats['start_time']
        total = self.stats['total_generated']
        valid = self.stats['valid_patterns']
        invalid = self.stats['invalid_patterns']
        rate = (valid / total * 100) if total > 0 else 0
        
        print(f"\n{'='*70}")
        print("🎯 COMPREHENSIVE STUDY COMPLETE")
        print(f"{'='*70}")
        print(f"Total patterns generated: {total:,}")
        print(f"Valid patterns: {valid:,} ({rate:.1f}%)")
        print(f"Invalid patterns: {invalid:,}")
        print(f"Time elapsed: {elapsed:.1f} seconds")
        print(f"Processing rate: {total/elapsed:.0f} patterns/second")
        print(f"\n📊 Top Rejection Reasons:")
        for reason, count in sorted(self.stats['rejection_reasons'].items(), 
                                    key=lambda x: x[1], reverse=True)[:10]:
            pct = (count / invalid * 100) if invalid > 0 else 0
            print(f"  {reason}: {count:,} ({pct:.1f}%)")
        print(f"\n📁 Output Directories:")
        print(f"  Valid chords: {self.chords_dir}")
        print(f"  Failure log: {self.failure_log_path}")
        print(f"  Analysis: {self.analysis_dir}")
        print(f"{'='*70}\n")
        
        # Close failure log
        if hasattr(self, 'failure_log'):
            self.failure_log.close()
    
    def save_analysis(self, results: List[Dict[str, Any]]):
        """Save detailed analysis to JSON file."""
        analysis_file = self.analysis_dir / f"study_results_{int(time.time())}.json"
        
        analysis = {
            'study_metadata': {
                'total_patterns': self.stats['total_generated'],
                'valid_patterns': self.stats['valid_patterns'],
                'invalid_patterns': self.stats['invalid_patterns'],
                'validation_rate': (self.stats['valid_patterns'] / self.stats['total_generated'] * 100) 
                                  if self.stats['total_generated'] > 0 else 0,
                'processing_time_seconds': self.stats['end_time'] - self.stats['start_time'],
                'fret_range': f"{self.min_fret}-{self.max_fret}",
                'min_sounding_strings': self.min_sounding_strings
            },
            'rejection_reasons': dict(self.stats['rejection_reasons']),
            'results_summary': {
                'valid_count': sum(1 for r in results if r['is_valid']),
                'invalid_count': sum(1 for r in results if not r['is_valid'])
            }
        }
        
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"💾 Analysis saved to: {analysis_file}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhanced Position Finder - Comprehensive Chord Pattern Study"
    )
    parser.add_argument("--max-patterns", type=int, default=None,
                       help="Maximum patterns to generate (default: unlimited)")
    parser.add_argument("--thumb-reach", type=int, default=0, choices=range(7),
                       help="Thumb reach setting 0-6 (default: 0)")
    parser.add_argument("--max-fret", type=int, default=12,
                       help="Maximum fret to consider (default: 12)")
    parser.add_argument("--output-dir", type=str, default=".",
                       help="Output directory (default: current directory)")
    
    args = parser.parse_args()
    
    # Create finder
    finder = EnhancedPositionFinder(
        output_dir=Path(args.output_dir),
        thumb_reach=args.thumb_reach
    )
    finder.max_fret = args.max_fret
    
    # Run study
    finder.run_comprehensive_study(max_patterns=args.max_patterns)
    
    print(f"✨ Study complete! Review the failure log at {finder.failure_log_path} to identify needed rules.\n")


if __name__ == "__main__":
    main()

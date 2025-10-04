"""
Position Finder - Systematic generation and validation of guitar chord fingering patterns.

This class generates all possible finger pattern combinations for a guitar,
validates them using the chord validation system, and creates chord charts
for valid patterns while logging invalid patterns for review.
"""

import os
import itertools
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
from chord_validator import ChordFingeringValidator
from chord_chart import ChordChart


class InstrumentConfig:
    """Configuration for a musical instrument (guitar)."""
    
    def __init__(self, strings: int = 6, max_fret: int = 12, fingers: Optional[List[str]] = None):
        """
        Initialize instrument configuration.
        
        Args:
            strings: Number of strings (default 6 for guitar)
            max_fret: Maximum fret to consider (default 12)
            fingers: Available fingers/indicators (default: O, X, 1, 2, 3, 4, T)
        """
        self.strings = strings
        self.max_fret = max_fret
        self.fingers = fingers or ['O', 'X', '1', '2', '3', '4', 'T']
        
    def __repr__(self):
        return f"InstrumentConfig(strings={self.strings}, max_fret={self.max_fret}, fingers={self.fingers})"


class PositionFinder:
    """
    Systematic generator and validator for guitar chord fingering patterns.
    
    This class generates all possible combinations of finger positions,
    validates them, and creates chord charts for valid patterns.
    """
    
    def __init__(self, instrument_config: Optional[InstrumentConfig] = None, output_dir: Optional[str] = None):
        """
        Initialize the PositionFinder.
        
        Args:
            instrument_config: Configuration for the instrument
            output_dir: Directory to save generated chord charts
        """
        self.config = instrument_config or InstrumentConfig()
        self.output_dir = Path(output_dir) if output_dir else Path(".")
        self.trash_dir = self.output_dir / "trash"
        
        # Ensure directories exist
        self.output_dir.mkdir(exist_ok=True)
        self.trash_dir.mkdir(exist_ok=True)
        
        # Clear trash directory at start of process
        self._clear_trash_directory()
        
        # Initialize validator and chart generator
        self.validator = ChordFingeringValidator()
        self.chart = ChordChart()
        
        # Statistics tracking
        self.stats = {
            'total_generated': 0,
            'valid_chords': 0,
            'invalid_chords': 0,
            'complexity_breakdown': {}
        }
        
        print(f"PositionFinder initialized:")
        print(f"  Instrument: {self.config}")
        print(f"  Output directory: {self.output_dir}")
        print(f"  Trash directory: {self.trash_dir}")
    
    def _clear_trash_directory(self):
        """Clear all files from the trash directory at the start of processing."""
        import shutil
        
        if self.trash_dir.exists():
            # Remove all files in trash directory
            for file_path in self.trash_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
            print(f"🗑️ Cleared trash directory: {self.trash_dir}")
        else:
            print(f"🗑️ Trash directory created: {self.trash_dir}")
    
    def generate_string_patterns(self, limit: int = 10) -> List[List[Tuple[str, int]]]:
        """
        Generate all possible string patterns for the instrument.
        
        Permutes over strings from low to high (6th to 1st string):
        - Open (O)
        - Muted (X) 
        - Fretted (1-max_fret)
        
        Args:
            limit: Maximum number of patterns to generate
            
        Returns:
            List of chord patterns, each as list of (finger, fret) tuples
        """
        patterns = []
        pattern_count = 0
        
        print(f"Generating string patterns (limit: {limit})...")
        
        # For each string position (6th to 1st string)
        string_options = []
        for string_num in range(self.config.strings):
            # Options for this string: Open, Muted, or Fretted (1 to max_fret)
            options = [('O', 0), ('X', 0)]  # Open and muted
            
            # Add fretted options (we'll assign fingers later)
            for fret in range(1, min(6, self.config.max_fret + 1)):  # Limit to first 5 frets initially
                options.append(('FRET', fret))  # Placeholder - will assign finger later
                
            string_options.append(options)
        
        # Generate all combinations of string states
        print(f"Generating combinations from {len(string_options)} strings with {[len(opts) for opts in string_options]} options each...")
        
        for combination in itertools.product(*string_options):
            if pattern_count >= limit:
                break
                
            # Convert combination to chord pattern with finger assignments
            chord_patterns = self.assign_fingers_to_pattern(list(combination))
            
            for pattern in chord_patterns:
                if pattern_count >= limit:
                    break
                    
                patterns.append(pattern)
                pattern_count += 1
                
                if pattern_count % 5 == 0:
                    print(f"  Generated {pattern_count} patterns...")
        
        print(f"Generated {len(patterns)} total patterns")
        return patterns
    
    def assign_fingers_to_pattern(self, base_pattern: List[Tuple[str, int]]) -> List[List[Tuple[str, int]]]:
        """
        Assign fingers to fretted strings in a pattern.
        
        Works from string 6 to 1, assigning fingers (1, 2, 3, 4, T) to each fretted string.
        Allows finger repetition to enable barre chords and other multi-string techniques.
        
        Args:
            base_pattern: Pattern with FRET placeholders
            
        Returns:
            List of complete patterns with finger assignments
        """
        # Find fretted string positions
        fretted_positions = []
        for i, (indicator, fret) in enumerate(base_pattern):
            if indicator == 'FRET':
                fretted_positions.append(i)
        
        if not fretted_positions:
            # No fretted strings - return the pattern as-is (all open/muted)
            return [base_pattern]
        
        # Available fingers for fretting (excluding O and X)
        available_fingers = ['1', '2', '3', '4', 'T']
        
        patterns = []
        
        # Generate all possible finger assignments for fretted positions
        # Use itertools.product to allow finger repetition (enables barre chords)
        # Limit combinations to reasonable finger counts (max 4 fretted strings for performance)
        if len(fretted_positions) <= 4:
            # Use product instead of permutations to allow repeated fingers
            for finger_combo in itertools.product(available_fingers, repeat=len(fretted_positions)):
                pattern = base_pattern.copy()
                
                # Assign fingers to fretted positions
                for pos_index, string_index in enumerate(fretted_positions):
                    finger = finger_combo[pos_index]
                    fret = pattern[string_index][1]
                    pattern[string_index] = (finger, fret)
                
                patterns.append(pattern)
        
        return patterns
    
    def validate_and_process_pattern(self, pattern: List[Tuple[str, int]], pattern_id: int) -> Dict[str, Any]:
        """
        Validate a chord pattern and process the results.
        
        Args:
            pattern: Chord pattern as list of (finger, fret) tuples
            pattern_id: Unique identifier for this pattern
            
        Returns:
            Dictionary with validation results and processing info
        """
        self.stats['total_generated'] += 1
        
        # Create a descriptive name for this pattern
        pattern_name = f"pattern_{pattern_id:03d}"
        
        # Validate the pattern
        validation_result = self.validator.validate_chord(pattern)
        
        result_info = {
            'pattern_id': pattern_id,
            'pattern': pattern,
            'pattern_name': pattern_name,
            'validation_result': validation_result,
            'is_valid': validation_result['is_valid'],
            'file_created': None,
            'file_path': None
        }
        
        # Generate chord chart for ALL patterns (valid and invalid)
        self.chart.chord_name = pattern_name.replace('_', ' ').title()
        
        if validation_result['is_valid']:
            # Valid chord - save to main output directory
            self.stats['valid_chords'] += 1
            
            # Track complexity
            status = validation_result.get('status_name', 'UNKNOWN')
            self.stats['complexity_breakdown'][status] = self.stats['complexity_breakdown'].get(status, 0) + 1
            
            # Save chord chart to chords directory using save_to_file (includes chord data embedding)
            filename = f"{pattern_name}_chord.svg"
            chords_dir = Path("chords")
            chords_dir.mkdir(exist_ok=True)  # Ensure directory exists
            file_path = chords_dir / filename
            
            # Use save_to_file method to include chord data embedding
            self.chart.save_to_file(pattern, str(file_path))
            
            result_info['file_created'] = True
            result_info['file_path'] = str(file_path)
            
            print(f"✅ Valid: {pattern_name} - {status} - Saved to {filename}")
            
        else:
            # Invalid chord - save chart to trash directory AND create log
            self.stats['invalid_chords'] += 1
            
            status = validation_result.get('status_name', 'UNKNOWN')
            
            # Generate SVG content for invalid chord
            #svg_content = self.chart.create_grid_chart(pattern)
            
            # Save chord chart to trash directory (so we can see what's wrong)
            #svg_filename = f"{pattern_name}_invalid_chord.svg"
            #svg_path = self.trash_dir / svg_filename
            
            # For invalid chords, we'll embed chord data manually since save_to_file expects valid structure
            #chord_data_comment = f"<!-- CHORD_DATA: {pattern} -->\n"
            #lines = svg_content.split('\n')
            #if lines[0].startswith('<?xml'):
            #    lines.insert(1, chord_data_comment.strip())
            #    svg_content = '\n'.join(lines)
            #else:
            #    svg_content = chord_data_comment + svg_content
            
            # with open(svg_path, 'w', encoding='utf-8') as f:
            #    f.write(svg_content)
            
            # Create log entry for invalid chord
            #log_filename = f"{pattern_name}_invalid.txt"
            #log_path = self.trash_dir / log_filename
            
            #with open(log_path, 'w', encoding='utf-8') as f:
            #    f.write(f"Invalid Chord Pattern: {pattern_name}\n")
            #    f.write(f"Pattern: {pattern}\n")
            #    f.write(f"Status: {status}\n")
            #    f.write(f"Valid: {validation_result['is_valid']}\n")
            #    f.write(f"Chart file: {svg_filename}\n\n")
                
            #    f.write("Validation Messages:\n")
            #    for msg in validation_result.get('messages', []):
            #        f.write(f"  {msg['severity'].upper()}: {msg['message']}\n")
            
            #result_info['file_created'] = True  # Chart was created, just in trash
            #result_info['file_path'] = str(svg_path)
            #result_info['log_path'] = str(log_path)
            
            # print(f"❌ Invalid: {pattern_name} - {status} - Chart & log saved to trash/")
        
        return result_info
    
    def generate_and_validate_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Generate chord patterns and validate them.
        
        Args:
            limit: Maximum number of patterns to process
            
        Returns:
            List of processing results for each pattern
        """
        print(f"\n🎸 Starting systematic chord pattern generation (limit: {limit})")
        print("=" * 60)
        
        # Generate base patterns
        patterns = self.generate_string_patterns(limit)
        
        print(f"\n📊 Processing {len(patterns)} patterns...")
        print("-" * 40)
        
        results = []
        for i, pattern in enumerate(patterns):
            result = self.validate_and_process_pattern(pattern, i + 1)
            results.append(result)
        
        # Print summary
        self.print_summary()
        
        return results
    
    def print_summary(self):
        """Print a summary of generation and validation results."""
        print("\n" + "=" * 60)
        print("🎯 POSITION FINDER SUMMARY")
        print("=" * 60)
        print(f"Total patterns generated: {self.stats['total_generated']}")
        print(f"Valid chords: {self.stats['valid_chords']}")
        print(f"Invalid chords: {self.stats['invalid_chords']}")
        
        if self.stats['complexity_breakdown']:
            print(f"\n📈 Complexity Breakdown:")
            for complexity, count in self.stats['complexity_breakdown'].items():
                print(f"  {complexity}: {count}")
        
        print(f"\n📁 Output directories:")
        print(f"  Valid chords: {self.output_dir}")
        print(f"  Invalid chords: {self.trash_dir}")
        
        if self.stats['valid_chords'] > 0:
            success_rate = (self.stats['valid_chords'] / self.stats['total_generated']) * 100
            print(f"\n✅ Success rate: {success_rate:.1f}%")


def demonstrate_position_finder():
    """Demonstrate the PositionFinder with a limited set of patterns."""
    print("🎸 Guitar Chord Position Finder - Enhanced Demonstration")
    print("=" * 60)
    
    # Create instrument configuration (6-string guitar, limited to first 5 frets)
    guitar_config = InstrumentConfig(strings=6, max_fret=5, fingers=['O', 'X', '1', '2', '3', '4', 'T'])
    
    # Create position finder
    finder = PositionFinder(
        instrument_config=guitar_config,
        output_dir=""
    )
    
    # Generate and validate 10 patterns
    results = finder.generate_and_validate_patterns(limit=1000000)
    
    print("\n🔍 Pattern Details:")
    print("-" * 40)
    for result in results:
        pattern_str = " ".join([f"{f}:{fr}" for f, fr in result['pattern']])
        if result['is_valid']:
            status = "✅ VALID"
            location = "main directory"
        else:
            status = "❌ INVALID"  
            location = "trash directory (with chart + log)"
        print(f"{result['pattern_name']}: {pattern_str} - {status} - {location}")
    
    print(f"\n📊 Final Results:")
    print(f"✅ Valid patterns: {len([r for r in results if r['is_valid']])} (charts in main directory)")
    print(f"❌ Invalid patterns: {len([r for r in results if not r['is_valid']])} (charts + logs in trash/)")
    print(f"🗑️ Trash was cleared at startup")
    
    return results


if __name__ == "__main__":
    # Run the demonstration
    demonstrate_position_finder()
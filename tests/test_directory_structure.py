"""
Quick test to verify position_finder saves to chords directory
"""
from position_finder import PositionFinder

print("Testing position_finder with new directory structure...")

finder = PositionFinder()
print("Finding one pattern...")

# Generate just one pattern to test
result = finder.generate_and_validate_patterns(limit=1)

print("Test complete - check chords directory for new file")
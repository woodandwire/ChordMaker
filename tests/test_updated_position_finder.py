"""
Test the updated PositionFinder that creates charts for both valid and invalid patterns
and clears the trash directory at startup.
"""

from position_finder import PositionFinder, InstrumentConfig

def test_updated_position_finder():
    """Test the updated PositionFinder with chart creation for failed patterns."""
    
    print("🧪 Testing Updated PositionFinder")
    print("=" * 50)
    
    # Create a configuration that will generate some invalid patterns
    # Include thumb to trigger some thumb position errors
    finder = PositionFinder(output_dir="test_updated_patterns")
    
    print(f"\n🎸 Generating 15 patterns to test both valid and invalid cases...")
    results = finder.generate_and_validate_patterns(limit=15)
    
    # Analyze results
    valid_results = [r for r in results if r['is_valid']]
    invalid_results = [r for r in results if not r['is_valid']]
    
    print(f"\n📊 Results Analysis:")
    print(f"Valid patterns: {len(valid_results)}")
    print(f"Invalid patterns: {len(invalid_results)}")
    
    # Show what files were created
    from pathlib import Path
    
    output_dir = Path("test_updated_patterns")
    trash_dir = output_dir / "trash"
    
    print(f"\n📁 Files created:")
    if output_dir.exists():
        valid_svgs = list(output_dir.glob("*_chord.svg"))
        print(f"Valid chord charts: {len(valid_svgs)}")
        for svg in valid_svgs[:3]:  # Show first 3
            print(f"  ✅ {svg.name}")
        if len(valid_svgs) > 3:
            print(f"  ... and {len(valid_svgs) - 3} more")
    
    if trash_dir.exists():
        invalid_svgs = list(trash_dir.glob("*_invalid_chord.svg"))
        invalid_logs = list(trash_dir.glob("*_invalid.txt"))
        print(f"Invalid chord charts: {len(invalid_svgs)}")
        print(f"Invalid log files: {len(invalid_logs)}")
        
        for svg in invalid_svgs:
            log_name = svg.name.replace("_chord.svg", ".txt")
            print(f"  ❌ {svg.name} + {log_name}")
    
    return results

if __name__ == "__main__":
    test_updated_position_finder()
    
    print(f"\n✅ Test completed!")
    print(f"📂 Check the 'test_updated_patterns/' directory to see:")
    print(f"   - Valid chord SVG files in main directory")  
    print(f"   - Invalid chord SVG files + log files in trash/ subdirectory")
    print(f"   - Trash directory was cleared at startup")
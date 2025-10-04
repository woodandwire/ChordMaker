# ChordMaker

A comprehensive guitar chord generation and validation system with anatomical accuracy and advanced visualization capabilities.

## Features

- **Anatomical Validation**: Realistic finger span constraints and positioning validation
- **Barre Chord Support**: Advanced barre detection with visual connecting lines
- **Comprehensive Validation**: 8-rule validation engine detecting impossible chord patterns
- **SVG Visualization**: High-quality chord diagram generation
- **Web API**: Flask-based REST API for chord operations
- **Pattern Generation**: Complete chord position finding across the fretboard

## Project Structure

```text
ChordMaker/
├── src/           # Main source code
├── tests/         # Test suites and validation
├── examples/      # Demo applications and scripts
├── docs/          # Technical documentation
├── demos/         # Sample outputs and demonstrations
├── generated/     # Auto-generated files
├── chords/        # Chord data files
└── README.md      # This file
```

## Quick Start

1. Install dependencies: `pip install flask`
2. Run the web server: `python src/chord_server.py`
3. Open `examples/chordgenerator.html` in your browser
4. Or use the API directly at `http://localhost:5000`

## Key Components

### Chord Validator (`src/chord_validator.py`)

Comprehensive validation engine with anatomical constraints:

- Adjacent finger span limits (Ring-Pinky: 2 frets, Middle-Ring: 3 frets, Index-Middle: 4 frets)
- Barre blocking interference detection
- Ergonomic difficulty assessment
- 8 validation rules ensuring anatomical accuracy

### Position Finder (`src/position_finder.py`)

Advanced chord position discovery:

- Complete pattern generation across fretboard
- Intelligent filtering and ranking
- Anatomical feasibility checking

### Chord Chart Generator (`src/chord_chart.py`)

SVG chord diagram creation:

- Visual barre connections
- Finger position indicators
- Fret number labeling
- Clean, professional output

## Validation System

The chord validator implements 8 comprehensive rules:

1. **Basic Validation** - Input sanity and finger limits
2. **Fret Span Check** - Maximum reach constraints
3. **Finger Stretch Check** - Anatomical limits between adjacent fingers
4. **Finger Collision Check** - Same fret/string conflicts
5. **Thumb Position Check** - Thumb reach and positioning
6. **Barre Consistency Check** - Valid barre patterns
7. **Barre Blocking Interference** - Detection of impossible barre combinations
8. **Ergonomic Assessment** - Difficulty scoring and playability

## Examples

See the `examples/` directory for:

- Interactive web interfaces
- API usage examples
- Generation scripts
- Debugging tools

## Testing

Run tests from the `tests/` directory to validate functionality:

```bash
python tests/test_pattern_997896.py
python tests/test_barre_blocking.py
```

## Documentation

Technical documentation is available in the `docs/` directory, including:

- Complete validation logic flowchart
- Anatomical validation details
- Barre blocking detection explanation

"""
Python equivalent of the JavaScript ChordChart class for generating guitar chord charts.
This class creates SVG-based chord diagrams with configurable dimensions and styling.
"""

from typing import List, Tuple, Union
import math
from chord_validator import ChordFingeringValidator


class ChordChart:
    """
    A class to generate SVG-based guitar chord charts.
    
    The chord chart displays a fretboard with frets, strings, and finger positions.
    It supports open strings (O), muted strings (X), and fretted notes with finger numbers.
    """
    
    def __init__(self):
        """Initialize the chord chart with default dimensions and settings."""
        
        # Image positioning
        self.image_top = 1
        self.image_left = 1
        
        # Margins and gutters
        self.top_gutter_height = 50
        self.left_gutter_width = 50
        self.right_margin_width = 20
        self.bottom_margin_height = 20
        
        # Nut dimensions
        self.nut_top = 0
        self.nut_height = 10
        self.nut_bottom = 0
        
        # Fretboard positioning
        self.fretboard_top = 0
        self.fretboard_left = 0
        
        # Spacing
        self.string_spacing = 30
        self.fret_spacing = 30
        
        # Fretboard configuration
        self.string_count = 6
        self.fret_count = 5
        
        # Collections
        self.strings: List[int] = []
        self.frets: List[int] = []
        
        # Calculated dimensions
        self.fretboard_width = 0
        self.fretboard_height = 0
        self.total_image_height = 0
        self.total_image_width = 0
        
        # Chord name positioning
        self.chord_name = ''
        self.chord_name_left = 0
        self.chord_name_top = 0
        
        # Indicator settings
        self.indicator_height = 0
        self.indicator_offset = 0
        self.indicator_labels = ['X', 'O', 'T', '1', '2', '3', '4']
    
    def set_top(self, value: int) -> 'ChordChart':
        """
        Set the top position of the image.
        
        Args:
            value: The top position value
            
        Returns:
            Self for method chaining
        """
        self.image_top = value
        return self
    
    def set_chord_name(self, name: str) -> 'ChordChart':
        """
        Set the chord name to display.
        
        Args:
            name: The chord name
            
        Returns:
            Self for method chaining
        """
        self.chord_name = name
        return self
    
    def set_string_count(self, count: int) -> 'ChordChart':
        """
        Set the number of strings.
        
        Args:
            count: Number of strings (typically 6 for guitar)
            
        Returns:
            Self for method chaining
        """
        self.string_count = count
        return self
    
    def set_fret_count(self, count: int) -> 'ChordChart':
        """
        Set the number of frets to display.
        
        Args:
            count: Number of frets
            
        Returns:
            Self for method chaining
        """
        self.fret_count = count
        return self
    
    def calculate_dimensions(self) -> None:
        """Calculate all dimensions based on current settings."""
        
        # Calculate nut positioning
        self.nut_top = self.image_top + self.top_gutter_height
        self.nut_bottom = self.nut_top + self.nut_height
        
        # Calculate fretboard positioning
        self.fretboard_top = self.nut_bottom + 1
        self.fretboard_left = self.left_gutter_width
        
        # Initialize string and fret arrays
        self.strings = list(range(self.string_count))
        self.frets = list(range(self.fret_count))
        
        # Calculate fretboard dimensions
        self.fretboard_width = self.string_spacing * (len(self.strings) - 1)
        self.fretboard_height = self.fret_spacing * len(self.frets)
        
        # Calculate total image dimensions
        self.total_image_height = (self.top_gutter_height + 
                                  self.nut_height + 
                                  self.fretboard_height + 
                                  self.bottom_margin_height)
        self.total_image_width = (self.left_gutter_width + 
                                 self.fretboard_width + 
                                 self.right_margin_width)
        
        # Calculate chord name positioning
        self.chord_name_left = self.fretboard_left
        self.chord_name_top = math.floor(self.top_gutter_height / 2)
        
        # Calculate indicator offset
        self.indicator_offset = -1 * math.floor(self.fret_spacing / 4)
    
    def create_grid_chart(self, data: Union[List[Tuple[str, int]], None] = None) -> str:
        """
        Create the complete SVG chord chart.
        
        Args:
            data: List of tuples containing (finger_indicator, fret_number) for each string.
                 finger_indicator can be 'O' (open), 'X' (muted), 'T' (thumb), or finger numbers '1'-'4'.
                 fret_number is the fret position (ignored for 'O' and 'X').
                 
        Returns:
            Complete SVG string for the chord chart
        """
        if data is None:
            data = []
        
        self.calculate_dimensions()
        
        template = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{self.total_image_width}" height="{self.total_image_height}" 
     xmlns="http://www.w3.org/2000/svg" 
     xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {self.total_image_width} {self.total_image_height}">
    <title>{self.chord_name} Guitar Chord</title>
    <desc>Guitar chord diagram for {self.chord_name}</desc>
    <text x="{self.chord_name_left}" y="{self.chord_name_top}" fill="black" font-family="Arial, sans-serif" font-size="16" font-weight="bold">{self.chord_name}</text>
    <rect y="{self.nut_top}" x="{self.fretboard_left}" width="{self.fretboard_width}" height="{self.nut_height}" style="fill:rgb(0,0,0);stroke-width:1;stroke:rgb(0,0,0);"/>
    <rect x="{self.fretboard_left}" y="{self.fretboard_top}" width="{self.fretboard_width}" height="{self.fretboard_height}" style="fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0);"/>
    {self._get_frets_svg()}
    {self._get_strings_svg()}
    {self._get_open_strings_svg(data)}
    {self._get_fretted_notes_svg(data)}
    {self._get_complexity_score_svg(data)}
</svg>"""
        
        return template.strip()
    
    def _get_frets_svg(self) -> str:
        """Generate SVG for fret lines."""
        fret_string = ''
        for fret in self.frets:
            fret_position = self.fretboard_top + ((fret + 1) * self.fret_spacing)
            fret_string += (f'<line x1="{self.fretboard_left}" y1="{fret_position}" '
                           f'x2="{self.fretboard_left + self.fretboard_width}" '
                           f'y2="{fret_position}" style="stroke:rgb(0,0,0);stroke-width:1;"/>')
        return fret_string
    
    def _get_strings_svg(self) -> str:
        """Generate SVG for string lines."""
        string_string = ''
        for string in self.strings:
            string_position = string * self.string_spacing
            string_string += (f'<line x1="{self.fretboard_left + string_position}" '
                             f'y1="{self.fretboard_top}" '
                             f'x2="{self.fretboard_left + string_position}" '
                             f'y2="{self.fretboard_top + self.fretboard_height}" '
                             f'style="stroke:rgb(0,0,0);stroke-width:1;"/>')
        return string_string
    
    def _get_open_strings_svg(self, data: List[Tuple[str, int]]) -> str:
        """Generate SVG for open and muted strings."""
        open_strings = ''
        for index, data_point in enumerate(data):
            if index >= len(self.strings):
                break
                
            string_position = index * self.string_spacing
            
            if data_point[0] == 'O':
                # Open string - white circle
                open_strings += (f'<circle cx="{self.fretboard_left + string_position}" '
                               f'cy="40" r="5" stroke="black" stroke-width="2" fill="white" />')
            elif data_point[0] == 'X':
                # Muted string - X
                open_strings += (f'<text x="{self.fretboard_left + string_position - 5}" '
                               f'y="46" fill="black" font-family="Arial, sans-serif" font-size="14" font-weight="bold">X</text>')
        
        return open_strings
    
    def _get_fretted_notes_svg(self, data: List[Tuple[str, int]]) -> str:
        """Generate SVG for fretted notes with finger positions."""
        fretted_notes = ''
        
        # Find all fretted notes (exclude open and muted strings)
        fretted_positions = []
        for data_point in data:
            if data_point[0] not in ['O', 'X'] and len(data_point) > 1:
                fretted_positions.append(data_point[1])
        
        if not fretted_positions:
            return fretted_notes
        
        # Calculate the fret position window
        min_fret = min(fretted_positions)
        max_fret = max(fretted_positions)
        
        # Determine the starting fret for display
        # Only show fret position indicator if chord doesn't fit in standard 1-5 fret viewport
        if max_fret <= 5:
            # Chord fits in standard viewport (1st-5th frets) - no indicator needed
            fret_offset = 0  # Show from 1st fret
            fret_position_text = ""
        else:
            # Chord extends beyond 5th fret - show with fret position indicator
            fret_offset = min_fret - 1  # Start display from min_fret
            fret_position_text = f"{min_fret}fr"
        
        first_instance = True
        
        for index, data_point in enumerate(data):
            if index >= len(self.strings):
                break
                
            string_position = index * self.string_spacing
            
            if data_point[0] not in ['O', 'X'] and len(data_point) > 1:
                fret_number = data_point[1]
                # Calculate position relative to the fret window
                relative_fret = fret_number - fret_offset
                y_position = (relative_fret - 1) * self.fret_spacing + 78
                
                # Add fret position indicator on the first fretted note (if not starting from 1st fret)
                if first_instance and fret_position_text:
                    first_instance = False
                    fret_indicator_left = self.fretboard_left - 30
                    fret_indicator_top = self.fretboard_top + 15  # Position at top of fretboard
                    fretted_notes += (f'<text x="{fret_indicator_left}" '
                                    f'y="{fret_indicator_top}" fill="black" font-family="Arial, sans-serif" font-size="12" font-weight="bold">{fret_position_text}</text>')
                
                # Determine the label for the fretted note
                if data_point[0] == 'T':
                    fret_label = 'T'
                else:
                    try:
                        finger_num = int(data_point[0])
                        fret_label = self.indicator_labels[finger_num + 2]
                    except (ValueError, IndexError):
                        fret_label = data_point[0]
                
                # Add the fretted note circle and label
                fretted_notes += (f'<circle cx="{self.fretboard_left + string_position}" '
                                f'cy="{y_position}" r="12" stroke="black" '
                                f'stroke-width="1" fill="black" />')
                fretted_notes += (f'<text x="{self.fretboard_left + string_position - 4}" '
                                f'y="{y_position + 5}" fill="white" font-family="Arial, sans-serif" font-size="12" font-weight="bold">{fret_label}</text>')
        
        return fretted_notes
    
    def _get_complexity_score_svg(self, data: List[Tuple[str, int]]) -> str:
        """
        Generate SVG for complexity score display in top right corner.
        
        Args:
            data: Chord data for validation
            
        Returns:
            SVG string for complexity score text
        """
        try:
            # Validate the chord to get complexity information
            validator = ChordFingeringValidator()
            result = validator.validate_chord(data)
            
            # Extract difficulty score and level from validation messages
            difficulty_score = 0.0
            difficulty_level = "E"  # Default to Easy
            
            for msg in result.get('messages', []):
                if 'difficulty' in msg.get('message', '').lower():
                    message = msg['message']
                    # Extract score from message like "Chord difficulty: Moderate (score: 2.5)"
                    if 'score:' in message:
                        try:
                            score_part = message.split('score:')[1].split(')')[0].strip()
                            difficulty_score = float(score_part)
                        except (IndexError, ValueError):
                            difficulty_score = 0.0
                    
                    # Extract difficulty level
                    if 'Very Difficult' in message:
                        difficulty_level = "VD"  # Use VD for Very Difficult
                    elif 'Challenging' in message or 'Difficult' in message:
                        difficulty_level = "D"
                    elif 'Moderate' in message:
                        difficulty_level = "M"  
                    elif 'Easy' in message:
                        difficulty_level = "E"
                    break
            
            # Format the complexity display like "E2.5" or "M4.1"
            complexity_text = f"{difficulty_level}{difficulty_score:.1f}"
        
            # Position in top right corner
            text_x = self.fretboard_left + self.fretboard_width  # 10px from right edge
            text_y = math.floor(self.top_gutter_height / 2)
            
            return f'<text x="{text_x}" y="{text_y}" fill="gray" font-family="Arial, sans-serif" font-size="10" text-anchor="end">{complexity_text}</text>'
            
        except Exception as e:
            # If validation fails, return empty string to avoid breaking the chart
            return ''
    
    def save_to_file(self, data: List[Tuple[str, int]], filename: str) -> None:
        """
        Save the chord chart to an SVG file.
        
        Args:
            data: Chord data as list of tuples
            filename: Output filename (should end with .svg)
        """
        svg_content = self.create_grid_chart(data)
        
        # Add chord data as a comment for debugging/copying purposes
        chord_data_comment = f"<!-- CHORD_DATA: {data} -->\n"
        
        # Insert the comment after the XML declaration
        lines = svg_content.split('\n')
        if lines[0].startswith('<?xml'):
            lines.insert(1, chord_data_comment.strip())
            svg_content = '\n'.join(lines)
        else:
            svg_content = chord_data_comment + svg_content
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)


# Example usage and demonstration
def demonstrate_chord_chart():
    """Demonstrate the ChordChart class with various chord examples."""
    
    # Create a chord chart instance
    chart = ChordChart()
    
    # Example 1: C Major chord
    print("=== C Major Chord ===")
    c_major_data = [
        ('X', 0),  # 6th string muted
        ('3', 3),  # 5th string, 3rd fret, 3rd finger
        ('2', 2),  # 4th string, 2nd fret, 2nd finger  
        ('O', 0),  # 3rd string open
        ('1', 1),  # 2nd string, 1st fret, 1st finger
        ('O', 0)   # 1st string open
    ]
    
    chart.set_chord_name("C Major")
    c_major_svg = chart.create_grid_chart(c_major_data)
    print("SVG generated successfully!")
    
    # Save to file
    chart.save_to_file(c_major_data, "c_major_chord.svg")
    print("Saved to: c_major_chord.svg")
    
    # Example 2: G Major chord
    print("\n=== G Major Chord ===")
    g_major_data = [
        ('3', 3),  # 6th string, 3rd fret, 3rd finger
        ('2', 2),  # 5th string, 2nd fret, 2nd finger
        ('O', 0),  # 4th string open
        ('O', 0),  # 3rd string open
        ('O', 0),  # 2nd string open
        ('3', 3)   # 1st string, 3rd fret, 3rd finger
    ]
    
    chart.set_chord_name("G Major")
    g_major_svg = chart.create_grid_chart(g_major_data)
    chart.save_to_file(g_major_data, "g_major_chord.svg")
    print("Saved to: g_major_chord.svg")
    
    # Example 3: F Major chord (with thumb)
    print("\n=== F Major Chord (Barre) ===")
    f_major_data = [
        ('1', 1),  # 6th string, 1st fret, 1st finger (barre)
        ('1', 1),  # 5th string, 1st fret, 1st finger (barre)
        ('2', 2),  # 4th string, 2nd fret, 2nd finger
        ('3', 3),  # 3rd string, 3rd fret, 3rd finger
        ('3', 3),  # 2nd string, 3rd fret, 3rd finger
        ('1', 1)   # 1st string, 1st fret, 1st finger (barre)
    ]
    
    chart.set_chord_name("F Major")
    f_major_svg = chart.create_grid_chart(f_major_data)
    chart.save_to_file(f_major_data, "f_major_chord.svg")
    print("Saved to: f_major_chord.svg")
    
    print("\n=== Chord Chart Demo Complete ===")
    print("Generated SVG files can be opened in any web browser or SVG viewer.")


if __name__ == "__main__":
    demonstrate_chord_chart()
"""
Script to generate additional test chord charts.
"""

from chord_chart import ChordChart

def generate_additional_chords():
    """Generate some additional chord charts for testing."""
    
    chart = ChordChart()
    
    # A Minor chord
    print("Generating A Minor chord...")
    a_minor_data = [
        ('X', 0),  # 6th string muted
        ('O', 0),  # 5th string open
        ('2', 2),  # 4th string, 2nd fret, 2nd finger
        ('2', 2),  # 3rd string, 2nd fret, 2nd finger
        ('1', 1),  # 2nd string, 1st fret, 1st finger
        ('O', 0)   # 1st string open
    ]
    chart.set_chord_name("A Minor")
    chart.save_to_file(a_minor_data, "a_minor_chord.svg")
    
    # E Major chord
    print("Generating E Major chord...")
    e_major_data = [
        ('O', 0),  # 6th string open
        ('2', 2),  # 5th string, 2nd fret, 2nd finger
        ('2', 2),  # 4th string, 2nd fret, 2nd finger
        ('1', 1),  # 3rd string, 1st fret, 1st finger
        ('O', 0),  # 2nd string open
        ('O', 0)   # 1st string open
    ]
    chart.set_chord_name("E Major")
    chart.save_to_file(e_major_data, "e_major_chord.svg")
    
    # D Major chord
    print("Generating D Major chord...")
    d_major_data = [
        ('X', 0),  # 6th string muted
        ('X', 0),  # 5th string muted
        ('O', 0),  # 4th string open
        ('2', 2),  # 3rd string, 2nd fret, 2nd finger
        ('3', 3),  # 2nd string, 3rd fret, 3rd finger
        ('2', 2)   # 1st string, 2nd fret, 2nd finger
    ]
    chart.set_chord_name("D Major")
    chart.save_to_file(d_major_data, "d_major_chord.svg")
    
    # A#/Bb Major chord (with sharp/flat name conversion test)
    print("Generating A# Major chord...")
    asharp_data = [
        ('1', 1),  # 6th string, 1st fret, 1st finger (barre)
        ('1', 1),  # 5th string, 1st fret, 1st finger (barre)
        ('3', 3),  # 4th string, 3rd fret, 3rd finger
        ('3', 3),  # 3rd string, 3rd fret, 3rd finger
        ('3', 3),  # 2nd string, 3rd fret, 3rd finger
        ('1', 1)   # 1st string, 1st fret, 1st finger (barre)
    ]
    chart.set_chord_name("A# Major")
    chart.save_to_file(asharp_data, "asharp_major_chord.svg")
    
    print("✅ Additional chord charts generated successfully!")
    print("Generated chords:")
    print("- A Minor (a_minor_chord.svg)")
    print("- E Major (e_major_chord.svg)")
    print("- D Major (d_major_chord.svg)")
    print("- A# Major (asharp_major_chord.svg)")

if __name__ == "__main__":
    generate_additional_chords()
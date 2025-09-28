"""
Simple FastAPI server to serve chord chart HTML and SVG files.
Run with: uvicorn chord_server:app --reload
"""

from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
import os
import glob
from pathlib import Path
from chord_validator import ChordFingeringValidator

# Create FastAPI app
app = FastAPI(title="Chord Chart Viewer", description="Guitar chord chart viewer with SVG support")

# Get the current directory
current_dir = Path(__file__).parent

# Mount static files (for SVG files)
# Configure to serve SVG files with proper MIME type
class SVGStaticFiles(StaticFiles):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if path.endswith('.svg'):
            response.headers['content-type'] = 'image/svg+xml; charset=utf-8'
            response.headers['cache-control'] = 'no-cache'
        return response

app.mount("/static", SVGStaticFiles(directory=current_dir), name="static")

def discover_chord_files():
    """Discover all chord SVG files in the application directory."""
    chord_files = []
    
    # Look for files matching the pattern *_chord.svg
    pattern = str(current_dir / "*_chord.svg")
    svg_files = glob.glob(pattern)
    
    for svg_file in svg_files:
        file_path = Path(svg_file)
        # Extract chord name from filename (remove _chord.svg suffix)
        chord_name = file_path.stem.replace("_chord", "")
        
        # Convert filename back to display name
        display_name = chord_name.replace("_", " ").replace("sharp", "#").replace("flat", "b")
        display_name = display_name.title()  # Capitalize words
        
        chord_files.append({
            "filename": chord_name,
            "display_name": display_name,
            "file_path": file_path
        })
    
    # Sort by display name
    chord_files.sort(key=lambda x: x["display_name"])
    return chord_files

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main chord viewer page with dynamically discovered chords."""
    
    # Discover all chord files
    chord_files = discover_chord_files()
    
    # Generate navigation links
    nav_links = ""
    for chord in chord_files:
        nav_links += f'<a href="/chord/{chord["filename"]}">{chord["display_name"]}</a>\n            '
    
    # Generate chord containers
    chord_containers = ""
    for chord in chord_files:
        chord_containers += f'''
        <div class="chord-container">
            <h2>{chord["display_name"]}</h2>
            <img src="/svg/{chord["filename"]}" alt="{chord["display_name"]} Chord" width="220" height="230" style="border: 1px solid #ddd;">
            <br><small>Direct SVG: <a href="/svg/{chord["filename"]}" target="_blank">View</a> | 
            <a href="/chord/{chord["filename"]}" target="_blank">Page</a></small>
            <br><button onclick="deleteChord('{chord["filename"]}')" class="delete-btn">🗑️ Delete</button>
        </div>
        '''
    
    # Handle case where no chords are found
    if not chord_files:
        chord_containers = '''
        <div class="chord-container" style="text-align: center; color: #666;">
            <h2>No Chord Charts Found</h2>
            <p>No chord SVG files were found in the application directory.</p>
            <p>Generate some chords using the form below or run the chord_chart.py script.</p>
        </div>
        '''
        nav_links = '<span style="color: #666;">No chords available</span>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chord Chart Viewer</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            .chord-container {{
                display: inline-block;
                margin: 20px;
                padding: 15px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
                vertical-align: top;
            }}
            h1 {{
                color: #333;
                text-align: center;
            }}
            h2 {{
                margin-top: 0;
                color: #555;
            }}
            .nav {{
                text-align: center;
                margin: 20px 0;
                flex-wrap: wrap;
                display: flex;
                justify-content: center;
                gap: 10px;
            }}
            .nav a {{
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 2px;
            }}
            .nav a:hover {{
                background-color: #0056b3;
            }}
            .info {{
                background-color: #e9ecef;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: center;
            }}
            .stats {{
                background-color: #d1ecf1;
                color: #0c5460;
                padding: 10px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: center;
            }}
            .generate-btn {{
                background-color: #28a745;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
            }}
            .generate-btn:hover {{
                background-color: #218838;
            }}
            .delete-btn {{
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                cursor: pointer;
                font-size: 12px;
                margin-top: 5px;
            }}
            .delete-btn:hover {{
                background-color: #c82333;
            }}
        </style>
    </head>
    <body>
        <h1>🎸 Guitar Chord Charts</h1>
        
        <div class="info">
            <p><strong>Generated using the Python ChordChart class</strong></p>
            <p>Server running on FastAPI with uvicorn</p>
        </div>
        
        <div class="stats">
            <strong>📊 Found {len(chord_files)} chord chart(s) in the application directory</strong>
        </div>
        
        <div class="nav">
            {nav_links}
            <a href="/generate" class="generate-btn">➕ Generate New Chord</a>
        </div>
        
        {chord_containers}
        
        <script>
        async function deleteChord(chordName) {{
            const displayName = chordName.replace(/_/g, ' ').replace(/sharp/g, '#').replace(/flat/g, 'b');
            
            if (!confirm(`Are you sure you want to delete the "${{displayName}}" chord? This cannot be undone.`)) {{
                return;
            }}
            
            try {{
                const response = await fetch(`/api/chord/${{chordName}}`, {{
                    method: 'DELETE'
                }});
                
                if (response.ok) {{
                    alert('Chord deleted successfully!');
                    window.location.reload();
                }} else {{
                    const error = await response.text();
                    alert('Failed to delete chord: ' + error);
                }}
            }} catch (error) {{
                alert('Error deleting chord: ' + error.message);
            }}
        }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/chords")
async def list_chords():
    """API endpoint to list all available chord charts."""
    chord_files = discover_chord_files()
    return {
        "count": len(chord_files),
        "chords": [
            {
                "name": chord["display_name"],
                "filename": chord["filename"],
                "svg_url": f"/svg/{chord['filename']}",
                "page_url": f"/chord/{chord['filename']}"
            }
            for chord in chord_files
        ]
    }

@app.post("/api/validate")
async def validate_chord_fingering(
    string_6_type: str = Form(...), string_6_fret: int = Form(...),
    string_5_type: str = Form(...), string_5_fret: int = Form(...),
    string_4_type: str = Form(...), string_4_fret: int = Form(...),
    string_3_type: str = Form(...), string_3_fret: int = Form(...),
    string_2_type: str = Form(...), string_2_fret: int = Form(...),
    string_1_type: str = Form(...), string_1_fret: int = Form(...),
    thumb_reach: int = Form(1)  # New parameter for thumb reach (default: 6th string only)
):
    """API endpoint to validate chord fingering with configurable thumb reach."""
    # Create chord data from form inputs, sanitizing the data
    chord_data = [
        (string_6_type, 0 if string_6_type in ['X', 'O'] else string_6_fret),
        (string_5_type, 0 if string_5_type in ['X', 'O'] else string_5_fret),
        (string_4_type, 0 if string_4_type in ['X', 'O'] else string_4_fret),
        (string_3_type, 0 if string_3_type in ['X', 'O'] else string_3_fret),
        (string_2_type, 0 if string_2_type in ['X', 'O'] else string_2_fret),
        (string_1_type, 0 if string_1_type in ['X', 'O'] else string_1_fret),
    ]
    
    validator = ChordFingeringValidator(thumb_reach_strings=thumb_reach)
    result = validator.validate_chord(chord_data)
    
    return result

@app.get("/svg/{chord_name}")
async def get_chord_svg(chord_name: str):
    """Serve SVG content directly with proper headers."""
    svg_file = current_dir / f"{chord_name}_chord.svg"
    
    if not svg_file.exists():
        raise HTTPException(status_code=404, detail=f"Chord {chord_name} not found")
    
    # Read and return SVG content directly
    with open(svg_file, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "no-cache",
            "Content-Type": "image/svg+xml; charset=utf-8"
        }
    )

@app.get("/chord/{chord_name}", response_class=HTMLResponse)
async def get_chord_page(chord_name: str):
    """Serve an individual chord page with SVG and controls."""
    svg_file = current_dir / f"{chord_name}_chord.svg"
    
    if not svg_file.exists():
        raise HTTPException(status_code=404, detail=f"Chord {chord_name} not found")
    
    # Convert filename back to display name
    display_name = chord_name.replace("_", " ").replace("sharp", "#").replace("flat", "b")
    display_name = display_name.title()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{display_name} Chord</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
                max-width: 800px;
                margin: 20px auto;
            }}
            .chord-container {{
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .controls {{
                margin: 20px 0;
            }}
            .btn {{
                padding: 10px 20px;
                margin: 5px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
            }}
            .btn-primary {{
                background-color: #007bff;
                color: white;
            }}
            .btn-primary:hover {{
                background-color: #0056b3;
            }}
            .btn-danger {{
                background-color: #dc3545;
                color: white;
            }}
            .btn-danger:hover {{
                background-color: #c82333;
            }}
            .btn-secondary {{
                background-color: #6c757d;
                color: white;
            }}
            .btn-secondary:hover {{
                background-color: #545b62;
            }}
            svg {{
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="chord-container">
            <h1>{display_name} Chord</h1>
            <div>
                <img src="/svg/{chord_name}" alt="{display_name} Chord" style="max-width: 100%; height: auto;">
            </div>
            <div class="controls">
                <a href="/" class="btn btn-secondary">← Back to All Chords</a>
                <a href="/svg/{chord_name}" target="_blank" class="btn btn-primary">Download SVG</a>
                <button onclick="deleteChord('{chord_name}')" class="btn btn-danger">🗑️ Delete Chord</button>
            </div>
        </div>
        
        <script>
        async function deleteChord(chordName) {{
            if (!confirm('Are you sure you want to delete the ' + chordName.replace('_', ' ') + ' chord? This cannot be undone.')) {{
                return;
            }}
            
            try {{
                const response = await fetch(`/api/chord/${{chordName}}`, {{
                    method: 'DELETE'
                }});
                
                if (response.ok) {{
                    alert('Chord deleted successfully!');
                    window.location.href = '/';
                }} else {{
                    const error = await response.text();
                    alert('Failed to delete chord: ' + error);
                }}
            }} catch (error) {{
                alert('Error deleting chord: ' + error.message);
            }}
        }}
        </script>
    </body>
    </html>
    """
    
    return html_content

@app.delete("/api/chord/{chord_name}")
async def delete_chord(chord_name: str):
    """Delete a chord SVG file."""
    svg_file = current_dir / f"{chord_name}_chord.svg"
    
    if not svg_file.exists():
        raise HTTPException(status_code=404, detail=f"Chord {chord_name} not found")
    
    try:
        svg_file.unlink()  # Delete the file
        return {"message": f"Chord {chord_name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete chord: {str(e)}")

@app.get("/generate", response_class=HTMLResponse)
async def generate_form():
    """Serve a form to generate custom chord charts."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Generate Chord Chart</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
                max-width: 800px;
                margin: 20px auto;
            }
            .form-container {
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .string-input {
                margin: 10px 0;
                display: flex;
                align-items: center;
            }
            .string-input label {
                width: 100px;
                display: inline-block;
            }
            .string-input select, .string-input input {
                margin-left: 10px;
                padding: 5px;
            }
            .string-input input:disabled {
                background-color: #f8f9fa !important;
                color: #6c757d !important;
                cursor: not-allowed;
                border: 1px solid #dee2e6;
            }
            .setting-input {
                margin: 15px 0;
                display: flex;
                align-items: center;
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #e9ecef;
            }
            .setting-input label {
                width: 120px;
                display: inline-block;
                font-weight: bold;
            }
            .setting-input select {
                margin-left: 10px;
                padding: 5px;
                min-width: 200px;
            }
            button {
                background-color: #28a745;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            button:hover {
                background-color: #218838;
            }
            .validate-btn {
                background-color: #ffc107;
                color: #212529;
                margin-left: 10px;
            }
            .validate-btn:hover {
                background-color: #e0a800;
            }
            .validation-result {
                margin: 20px 0;
                padding: 15px;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
            .validation-success {
                background-color: #d4edda;
                color: #155724;
                border-color: #c3e6cb;
            }
            .validation-warning {
                background-color: #fff3cd;
                color: #856404;
                border-color: #ffeaa7;
            }
            .validation-error {
                background-color: #f8d7da;
                color: #721c24;
                border-color: #f5c6cb;
            }
            .nav {
                text-align: center;
                margin: 20px 0;
            }
            .nav a {
                margin: 0 10px;
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">← Back to Chord Viewer</a>
        </div>
        
        <div class="form-container">
            <h1>Generate Custom Chord Chart</h1>
            <form action="/generate" method="post">
                <div>
                    <label for="chord_name">Chord Name:</label>
                    <input type="text" id="chord_name" name="chord_name" required>
                </div>
                <br>
                
                <h3>String Configuration (6th to 1st string):</h3>
                
                <div class="string-input">
                    <label>6th String:</label>
                    <select name="string_6_type">
                        <option value="X">X (Muted)</option>
                        <option value="O">O (Open)</option>
                        <option value="1">1 (1st finger)</option>
                        <option value="2">2 (2nd finger)</option>
                        <option value="3">3 (3rd finger)</option>
                        <option value="4">4 (4th finger)</option>
                        <option value="T">T (Thumb)</option>
                    </select>
                    <input type="number" name="string_6_fret" min="0" max="12" value="0" placeholder="Fret">
                </div>
                
                <div class="string-input">
                    <label>5th String:</label>
                    <select name="string_5_type">
                        <option value="X">X (Muted)</option>
                        <option value="O">O (Open)</option>
                        <option value="1">1 (1st finger)</option>
                        <option value="2">2 (2nd finger)</option>
                        <option value="3" selected>3 (3rd finger)</option>
                        <option value="4">4 (4th finger)</option>
                        <option value="T">T (Thumb)</option>
                    </select>
                    <input type="number" name="string_5_fret" min="0" max="12" value="3" placeholder="Fret">
                </div>
                
                <div class="string-input">
                    <label>4th String:</label>
                    <select name="string_4_type">
                        <option value="X">X (Muted)</option>
                        <option value="O">O (Open)</option>
                        <option value="1">1 (1st finger)</option>
                        <option value="2" selected>2 (2nd finger)</option>
                        <option value="3">3 (3rd finger)</option>
                        <option value="4">4 (4th finger)</option>
                        <option value="T">T (Thumb)</option>
                    </select>
                    <input type="number" name="string_4_fret" min="0" max="12" value="2" placeholder="Fret">
                </div>
                
                <div class="string-input">
                    <label>3rd String:</label>
                    <select name="string_3_type">
                        <option value="X">X (Muted)</option>
                        <option value="O" selected>O (Open)</option>
                        <option value="1">1 (1st finger)</option>
                        <option value="2">2 (2nd finger)</option>
                        <option value="3">3 (3rd finger)</option>
                        <option value="4">4 (4th finger)</option>
                        <option value="T">T (Thumb)</option>
                    </select>
                    <input type="number" name="string_3_fret" min="0" max="12" value="0" placeholder="Fret">
                </div>
                
                <div class="string-input">
                    <label>2nd String:</label>
                    <select name="string_2_type">
                        <option value="X">X (Muted)</option>
                        <option value="O">O (Open)</option>
                        <option value="1" selected>1 (1st finger)</option>
                        <option value="2">2 (2nd finger)</option>
                        <option value="3">3 (3rd finger)</option>
                        <option value="4">4 (4th finger)</option>
                        <option value="T">T (Thumb)</option>
                    </select>
                    <input type="number" name="string_2_fret" min="0" max="12" value="1" placeholder="Fret">
                </div>
                
                <div class="string-input">
                    <label>1st String:</label>
                    <select name="string_1_type">
                        <option value="X">X (Muted)</option>
                        <option value="O" selected>O (Open)</option>
                        <option value="1">1 (1st finger)</option>
                        <option value="2">2 (2nd finger)</option>
                        <option value="3">3 (3rd finger)</option>
                        <option value="4">4 (4th finger)</option>
                        <option value="T">T (Thumb)</option>
                    </select>
                    <input type="number" name="string_1_fret" min="0" max="12" value="0" placeholder="Fret">
                </div>
                
                <br>
                <div class="setting-input">
                    <label for="thumb_reach">Thumb Reach:</label>
                    <select name="thumb_reach" id="thumb_reach">
                        <option value="0">No thumb fretting</option>
                        <option value="1" selected>6th string only (standard)</option>
                        <option value="2">6th & 5th strings (extended)</option>
                        <option value="3">6th, 5th & 4th strings (large hands)</option>
                        <option value="4">Up to 3rd string (very large hands)</option>
                        <option value="5">Up to 2nd string (exceptional)</option>
                        <option value="6">All strings (rare)</option>
                    </select>
                </div>
                <br>
                <button type="submit">Generate Chord Chart</button>
                <button type="button" class="validate-btn" onclick="validateChord()">🔍 Validate Fingering</button>
                
                <div id="validation-result" style="display: none;"></div>
            </form>
        </div>
        
        <script>
        // Initialize fret input states when page loads
        document.addEventListener('DOMContentLoaded', function() {
            // Add event listeners to all string type selectors
            for (let i = 1; i <= 6; i++) {
                const selector = document.querySelector(`select[name="string_${i}_type"]`);
                const fretInput = document.querySelector(`input[name="string_${i}_fret"]`);
                
                // Set initial state
                updateFretInput(selector, fretInput);
                
                // Add change listener
                selector.addEventListener('change', function() {
                    updateFretInput(selector, fretInput);
                });
            }
        });

        function updateFretInput(selector, fretInput) {
            const selectedValue = selector.value;
            
            if (selectedValue === 'X') {
                // Muted string - disable input and clear value
                fretInput.disabled = true;
                fretInput.value = '';
                fretInput.placeholder = 'Muted';
                fretInput.style.backgroundColor = '#f8f9fa';
                fretInput.style.color = '#6c757d';
            } else if (selectedValue === 'O') {
                // Open string - disable input and set to 0
                fretInput.disabled = true;
                fretInput.value = '0';
                fretInput.placeholder = 'Open (0)';
                fretInput.style.backgroundColor = '#f8f9fa';
                fretInput.style.color = '#6c757d';
            } else {
                // Finger or thumb - enable input
                fretInput.disabled = false;
                fretInput.placeholder = 'Fret';
                fretInput.style.backgroundColor = '';
                fretInput.style.color = '';
                
                // Set default fret if empty
                if (!fretInput.value || fretInput.value === '0') {
                    fretInput.value = '1';
                }
            }
        }

        async function validateChord() {
            const form = document.querySelector('form');
            const formData = new FormData(form);
            
            // Show loading state
            const resultDiv = document.getElementById('validation-result');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<p>🔄 Validating chord fingering...</p>';
            resultDiv.className = 'validation-result';
            
            try {
                const response = await fetch('/api/validate', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                displayValidationResult(result);
            } catch (error) {
                resultDiv.innerHTML = '<p>❌ Error validating chord: ' + error.message + '</p>';
                resultDiv.className = 'validation-result validation-error';
            }
        }
        
        function displayValidationResult(result) {
            const resultDiv = document.getElementById('validation-result');
            let className = 'validation-result ';
            let icon = '';
            
            if (result.is_valid && !result.has_warnings) {
                className += 'validation-success';
                icon = '✅';
            } else if (result.is_valid && result.has_warnings) {
                className += 'validation-warning';
                icon = '⚠️';
            } else {
                className += 'validation-error';
                icon = '❌';
            }
            
            resultDiv.className = className;
            
            let html = `
                <h3>${icon} Validation Result</h3>
                <p><strong>Status:</strong> ${result.status_code} - ${result.status_name}</p>
                <p><strong>Valid:</strong> ${result.is_valid ? 'Yes' : 'No'}</p>
                <p><strong>Has Warnings:</strong> ${result.has_warnings ? 'Yes' : 'No'}</p>
            `;
            
            if (result.hand_position && result.hand_position.fret_span > 0) {
                html += `
                    <p><strong>Fret Range:</strong> ${result.hand_position.min_fret} - ${result.hand_position.max_fret}</p>
                    <p><strong>Fret Span:</strong> ${result.hand_position.fret_span}</p>
                `;
                
                if (result.hand_position.barre_fret) {
                    html += `<p><strong>Barre:</strong> Fret ${result.hand_position.barre_fret} on strings ${result.hand_position.barre_strings.join(', ')}</p>`;
                }
            }
            
            if (result.messages && result.messages.length > 0) {
                html += '<h4>Messages:</h4><ul>';
                result.messages.forEach(msg => {
                    html += `<li><strong>${msg.severity.toUpperCase()}:</strong> ${msg.message} (${msg.rule})</li>`;
                });
                html += '</ul>';
            }
            
            if (result.finger_positions && result.finger_positions.length > 0) {
                html += '<h4>Finger Positions:</h4><ul>';
                result.finger_positions.forEach(pos => {
                    html += `<li>Finger ${pos.finger} on string ${pos.string}, fret ${pos.fret}</li>`;
                });
                html += '</ul>';
            }
            
            resultDiv.innerHTML = html;
        }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/generate", response_class=HTMLResponse)
async def generate_chord(
    chord_name: str = Form(...),
    string_6_type: str = Form(...), string_6_fret: int = Form(...),
    string_5_type: str = Form(...), string_5_fret: int = Form(...),
    string_4_type: str = Form(...), string_4_fret: int = Form(...),
    string_3_type: str = Form(...), string_3_fret: int = Form(...),
    string_2_type: str = Form(...), string_2_fret: int = Form(...),
    string_1_type: str = Form(...), string_1_fret: int = Form(...)
):
    """Generate a custom chord chart from form data."""
    from chord_chart import ChordChart
    
    # Create chord data from form inputs, sanitizing the data
    chord_data = [
        (string_6_type, 0 if string_6_type in ['X', 'O'] else string_6_fret),
        (string_5_type, 0 if string_5_type in ['X', 'O'] else string_5_fret),
        (string_4_type, 0 if string_4_type in ['X', 'O'] else string_4_fret),
        (string_3_type, 0 if string_3_type in ['X', 'O'] else string_3_fret),
        (string_2_type, 0 if string_2_type in ['X', 'O'] else string_2_fret),
        (string_1_type, 0 if string_1_type in ['X', 'O'] else string_1_fret),
    ]
    
    # Validate the chord first (using default thumb reach for generation)
    validator = ChordFingeringValidator(thumb_reach_strings=1)
    validation_result = validator.validate_chord(chord_data)
    
    # Generate the chord chart regardless, but show validation results
    chart = ChordChart()
    chart.set_chord_name(chord_name)
    
    # Create filename-safe name
    safe_name = chord_name.lower().replace(" ", "_").replace("#", "sharp").replace("b", "flat")
    filename = f"{safe_name}_chord.svg"
    
    # Save the chord chart
    chart.save_to_file(chord_data, filename)
    
    # Prepare validation status for display
    validation_status = ""
    validation_class = ""
    
    if validation_result['is_valid'] and not validation_result['has_warnings']:
        validation_status = "✅ Chord fingering is valid and playable!"
        validation_class = "validation-success"
    elif validation_result['is_valid'] and validation_result['has_warnings']:
        validation_status = f"⚠️ Chord is playable but has warnings (Status: {validation_result['status_code']})"
        validation_class = "validation-warning"
    else:
        validation_status = f"❌ Chord may be difficult or impossible to play (Status: {validation_result['status_code']})"
        validation_class = "validation-error"
    
    # Return HTML with the generated chord
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{chord_name} Chord Chart</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
                text-align: center;
            }}
            .chord-container {{
                display: inline-block;
                margin: 20px;
                padding: 15px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .nav a {{
                margin: 0 10px;
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
            .success {{
                background-color: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">← Back to Home</a>
            <a href="/generate">Generate Another</a>
        </div>
        
        <div class="success">
            <h2>✅ Chord Chart Generated Successfully!</h2>
            <p>Your <strong>{chord_name}</strong> chord chart has been created.</p>
        </div>
        
        <div class="{validation_class}" style="margin: 20px 0; padding: 15px; border-radius: 5px;">
            <p>{validation_status}</p>
        </div>
        
        <div class="chord-container">
            <h2>{chord_name}</h2>
            <img src="/svg/{safe_name}" alt="{chord_name} Chord" width="220" height="230" style="border: 1px solid #ddd;">
            <br><small>Direct SVG: <a href="/svg/{safe_name}" target="_blank">View</a></small>
        </div>
        
        <p><strong>File saved as:</strong> {filename}</p>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
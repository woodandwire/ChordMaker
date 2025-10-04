"""
Refactored FastAPI server for ChordMaker with separated concerns.
Reduced footprint by extracting templates, CSS, and utility functions.
"""

from fastapi import FastAPI, HTTPException, Form, Query, Request
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import re
from pathlib import Path

# Local imports
from chord_validator import ChordFingeringValidator
from utils.chord_utils import (
    extract_chord_data_from_svg, 
    format_chord_data_for_copy, 
    discover_chord_files,
    sanitize_chord_name
)
from utils.pagination import generate_pagination_html, calculate_pagination

# Create FastAPI app
app = FastAPI(title="Chord Chart Viewer", description="Guitar chord chart viewer with SVG support")

# Get the current directory
current_dir = Path(__file__).parent

# Setup templates and static files
templates = Jinja2Templates(directory=str(current_dir / "templates"))
app.mount("/static", StaticFiles(directory=str(current_dir / "static")), name="static")

# Custom static files handler for SVG with proper MIME type
class SVGStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if path.endswith('.svg'):
            response.headers['content-type'] = 'image/svg+xml; charset=utf-8'
            response.headers['cache-control'] = 'no-cache'
        return response

# Mount chord files directory
app.mount("/svg", SVGStaticFiles(directory=str(current_dir / "chords")), name="chords")


@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    page: int = Query(1, ge=1), 
    per_page: int = Query(24, ge=1, le=100),
    search: str = Query("", description="Search chord names")
):
    """Serve the main chord viewer page with pagination and search."""
    
    # Discover all chord files
    all_chord_files = discover_chord_files(current_dir)
    
    # Apply search filter if provided
    if search.strip():
        search_term = search.lower().strip()
        all_chord_files = [
            chord for chord in all_chord_files 
            if search_term in chord["display_name"].lower()
        ]
    
    total_chords = len(all_chord_files)
    
    # Calculate pagination
    pagination = calculate_pagination(page, per_page, total_chords)
    chord_files = all_chord_files[pagination['start_index']:pagination['end_index']]
    
    # Generate pagination navigation
    pagination_nav = generate_pagination_html(page, pagination['total_pages'], per_page, total_chords, search)
    
    # Generate search info if search is active
    search_info = ""
    if search.strip():
        search_info = f'''
        <div class="search-info">
            <strong>Search results for "{search}"</strong> - 
            <a href="/">Clear search</a>
        </div>
        '''
    
    # Generate chord containers for current page
    chord_containers = ""
    for chord in chord_files:
        chord_containers += f'''
        <div class="chord-container">
            <h2>{chord["display_name"]}</h2>
            <img src="/svg/{chord["filename"]}_chord.svg" alt="{chord["display_name"]} Chord" width="220" height="230" style="border: 1px solid #ddd;">
            <br><small>Direct SVG: <a href="/svg/{chord["filename"]}_chord.svg" target="_blank">View</a> | 
            <a href="/chord/{chord["filename"]}" target="_blank">Page</a></small>
            <br><button onclick="deleteChord('{chord["filename"]}')" class="delete-btn">🗑️ Delete</button>
        </div>
        '''
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "title": "Chord Chart Viewer",
        "search": search,
        "search_info": search_info,
        "total_chords": total_chords,
        "pagination_nav": pagination_nav,
        "chord_containers": chord_containers,
        "per_page": per_page
    })


@app.get("/api/chords")
async def api_chords():
    """API endpoint to list all available chords."""
    chord_files = discover_chord_files(current_dir)
    return {
        "chords": [
            {
                "name": chord["display_name"],
                "filename": chord["filename"],
                "svg_url": f"/svg/{chord['filename']}_chord.svg",
                "page_url": f"/chord/{chord['filename']}"
            }
            for chord in chord_files
        ],
        "total": len(chord_files)
    }


@app.post("/api/validate")
async def api_validate(chord_data: list):
    """API endpoint to validate chord fingering patterns."""
    try:
        validator = ChordFingeringValidator()
        result = validator.validate_chord(chord_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/svg/{chord_name}")
async def get_svg(chord_name: str):
    """Serve SVG files directly."""
    # Handle both with and without _chord suffix
    if not chord_name.endswith('.svg'):
        chord_name += '.svg'
    if not chord_name.endswith('_chord.svg') and not chord_name.replace('.svg', '').endswith('_chord'):
        chord_name = chord_name.replace('.svg', '_chord.svg')
    
    svg_path = current_dir / "chords" / chord_name
    
    if not svg_path.exists():
        raise HTTPException(status_code=404, detail="Chord SVG not found")
    
    return FileResponse(
        svg_path, 
        media_type="image/svg+xml",
        headers={"Cache-Control": "no-cache"}
    )


@app.get("/chord/{chord_name}", response_class=HTMLResponse)
async def chord_detail(request: Request, chord_name: str):
    """Serve individual chord detail page."""
    
    # Construct the SVG filename
    svg_filename = f"{chord_name}_chord.svg"
    svg_path = current_dir / "chords" / svg_filename
    
    if not svg_path.exists():
        raise HTTPException(status_code=404, detail="Chord not found")
    
    # Convert filename back to display name
    display_name = chord_name.replace("_", " ").replace("sharp", "#").replace("flat", "b")
    display_name = display_name.title()
    
    # Extract chord data for debugging
    chord_data = extract_chord_data_from_svg(svg_path)
    chord_data_display = None
    if chord_data:
        chord_data_display = format_chord_data_for_copy(chord_data, display_name)
    
    return templates.TemplateResponse("chord_detail.html", {
        "request": request,
        "title": f"{display_name} Chord",
        "chord_name": display_name,
        "filename": chord_name,
        "chord_data_display": chord_data_display
    })


@app.delete("/api/chord/{chord_name}")
async def delete_chord(chord_name: str):
    """Delete a chord SVG file."""
    svg_filename = f"{chord_name}_chord.svg"
    svg_path = current_dir / "chords" / svg_filename
    
    if not svg_path.exists():
        raise HTTPException(status_code=404, detail="Chord not found")
    
    try:
        os.remove(svg_path)
        return {"success": True, "message": f"Chord {chord_name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting chord: {str(e)}")


@app.get("/generate", response_class=HTMLResponse)
async def generate_form(request: Request):
    """Serve the chord generation form."""
    return templates.TemplateResponse("generate.html", {
        "request": request,
        "title": "Generate Chord Chart",
        "chord_name": None,
        "chord_pattern": None
    })


@app.post("/generate", response_class=HTMLResponse)
async def generate_chord(
    request: Request,
    chord_name: str = Form(...),
    string_6: str = Form(...),
    string_5: str = Form(...), 
    string_4: str = Form(...),
    string_3: str = Form(...),
    string_2: str = Form(...),
    string_1: str = Form(...)
):
    """Process chord generation form submission."""
    
    # Collect chord pattern from form
    chord_pattern_raw = [string_6, string_5, string_4, string_3, string_2, string_1]
    
    # Process and validate chord pattern
    chord_pattern = []
    for i, string_val in enumerate(chord_pattern_raw):
        string_val = string_val.strip().upper()
        
        if string_val == 'X':
            chord_pattern.append(('X', 0))
        elif string_val == 'O':
            chord_pattern.append(('O', 0))
        else:
            try:
                fret = int(string_val)
                if fret < 0 or fret > 24:
                    raise ValueError(f"Fret {fret} out of range (0-24)")
                chord_pattern.append((fret, fret))
            except ValueError:
                return templates.TemplateResponse("generate.html", {
                    "request": request,
                    "title": "Generate Chord Chart - Error",
                    "chord_name": chord_name,
                    "chord_pattern": chord_pattern_raw,
                    "error": f"Invalid value '{string_val}' for string {6-i}. Use 0-24, X, or O."
                })
    
    # Validate the chord pattern
    validator = ChordFingeringValidator()
    validation_result = validator.validate_chord(chord_pattern)
    
    # Generate chord chart
    try:
        from chord_chart import ChordChart
        
        safe_name = sanitize_chord_name(chord_name)
        filename = f"{safe_name}_chord.svg"
        filepath = current_dir / "chords" / filename
        
        # Ensure chords directory exists
        os.makedirs(current_dir / "chords", exist_ok=True)
        
        # Generate the SVG using ChordChart class
        chart = ChordChart()
        chart.set_chord_name(chord_name)
        chart.save_to_file(chord_pattern, str(filepath))
        
        # Prepare validation message
        validation_class = "success"
        validation_message = "✅ Chord is anatomically valid and playable."
        
        if validation_result['status_code'] != 200:
            if validation_result['status_code'] >= 400:
                validation_class = "error"
                validation_message = f"⚠️ {validation_result['message']}"
            else:
                validation_class = "warning" 
                validation_message = f"⚠️ {validation_result['message']}"
        
        return templates.TemplateResponse("generate_success.html", {
            "request": request,
            "title": f"{chord_name} Chord Generated",
            "chord_name": chord_name,
            "safe_name": safe_name,
            "filename": filename,
            "validation_class": validation_class,
            "validation_message": validation_message
        })
        
    except Exception as e:
        return templates.TemplateResponse("generate.html", {
            "request": request,
            "title": "Generate Chord Chart - Error",
            "chord_name": chord_name,
            "chord_pattern": chord_pattern_raw,
            "error": f"Error generating chord: {str(e)}"
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
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
current_dir = Path(__file__).parent  # This is src directory
project_root = current_dir.parent    # This is the project root
chord_dir = project_root / "chords"  # Chords are in project root

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
app.mount("/svg", SVGStaticFiles(directory=str(chord_dir)), name="chords")


@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    page: int = Query(1, ge=1), 
    per_page: int = Query(24, ge=1, le=100),
    search: str = Query("", description="Search chord names")
):
    """Serve the main chord viewer page with pagination and search."""
    
    # Discover all chord files
    all_chord_files = discover_chord_files(project_root)
    
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
        # Use the original file path to get the correct filename with _chord.svg
        svg_filename = chord["file_path"].name  # This includes _chord.svg
        chord_containers += f'''
        <div class="chord-container">
            <h2>{chord["display_name"]}</h2>
            <a href="/chord/{chord["filename"]}" target="_blank">
                <img src="/svg/{svg_filename}" alt="{chord["display_name"]} Chord" width="220" height="230" style="border: 1px solid #ddd; cursor: pointer;">
            </a>
            <br><small>Direct SVG: <a href="/svg/{svg_filename}" target="_blank">View</a> | 
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
    chord_files = discover_chord_files(project_root)
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


@app.post("/validate-chord")
async def validate_chord_form(
    string_6_type: str = Form(...),
    string_6_fret: int = Form(...),
    string_5_type: str = Form(...),
    string_5_fret: int = Form(...),
    string_4_type: str = Form(...),
    string_4_fret: int = Form(...),
    string_3_type: str = Form(...),
    string_3_fret: int = Form(...),
    string_2_type: str = Form(...),
    string_2_fret: int = Form(...),
    string_1_type: str = Form(...),
    string_1_fret: int = Form(...),
    thumb_reach: int = Form(1)
):
    """Validate chord fingering from form data."""
    try:
        # Collect finger types and fret positions
        string_types = [string_6_type, string_5_type, string_4_type, string_3_type, string_2_type, string_1_type]
        string_frets = [string_6_fret, string_5_fret, string_4_fret, string_3_fret, string_2_fret, string_1_fret]
        
        # Build chord pattern for validator (finger_indicator, fret_number)
        chord_pattern = []
        for finger_type, fret in zip(string_types, string_frets):
            finger_type = finger_type.strip().upper()
            
            # For muted (X) and open (O) strings, fret should be 0
            if finger_type in ['X', 'O'] and fret != 0:
                fret = 0
            
            chord_pattern.append((finger_type, fret))
        
        validator = ChordFingeringValidator(thumb_reach_strings=thumb_reach)
        result = validator.validate_chord(chord_pattern)
        
        # Extract basic validity from status code (2xx = valid, 4xx+ = invalid)
        status_code = result.get("status_code", 500)
        is_valid = status_code < 400
        
        # Convert validator result format to expected JavaScript format
        response = {
            "valid": is_valid,
            "difficulty": min(10, max(1, (status_code - 200) // 20 + 1)),  # Convert status to 1-10 scale
            "notes": "",
            "issues": [],
            "suggestions": []
        }
        
        # Extract issues and suggestions from messages
        messages = result.get("messages", [])
        for msg in messages:
            if msg.get("severity") == "error":
                response["issues"].append(msg.get("message", "Unknown error"))
            elif msg.get("severity") == "warning":
                response["suggestions"].append(msg.get("message", "Unknown warning"))
            elif msg.get("severity") == "info":
                response["notes"] += msg.get("message", "") + " "
        
        # Clean up notes and provide default message if no specific issues
        response["notes"] = response["notes"].strip()
        if not response["valid"] and not response["issues"] and not response["suggestions"]:
            response["issues"].append("Chord fingering appears to be invalid")
        
        return response
        
    except Exception as e:
        return {
            "valid": False, 
            "error": str(e), 
            "issues": [f"Validation error: {str(e)}"], 
            "suggestions": [],
            "difficulty": 10,
            "notes": ""
        }


@app.get("/svg/{chord_name}")
async def get_svg(chord_name: str):
    """Serve SVG files directly."""
    # Handle both with and without _chord suffix
    if not chord_name.endswith('.svg'):
        chord_name += '.svg'
    if not chord_name.endswith('_chord.svg') and not chord_name.replace('.svg', '').endswith('_chord'):
        chord_name = chord_name.replace('.svg', '_chord.svg')
    
    svg_path = chord_dir / chord_name
    
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
    svg_path = chord_dir / svg_filename
    
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
        "filename": svg_filename,  # Use the full filename with _chord.svg
        "chord_data_display": chord_data_display
    })


@app.delete("/api/chord/{chord_name}")
async def delete_chord(chord_name: str):
    """Delete a chord SVG file."""
    svg_filename = f"{chord_name}_chord.svg"
    svg_path = chord_dir / svg_filename
    
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
    string_6_type: str = Form(...),
    string_6_fret: int = Form(...),
    string_5_type: str = Form(...),
    string_5_fret: int = Form(...),
    string_4_type: str = Form(...),
    string_4_fret: int = Form(...),
    string_3_type: str = Form(...),
    string_3_fret: int = Form(...),
    string_2_type: str = Form(...),
    string_2_fret: int = Form(...),
    string_1_type: str = Form(...),
    string_1_fret: int = Form(...),
    thumb_reach: int = Form(1)
):
    """Process chord generation form submission with finger types and fret positions."""
    
    # Collect finger types and fret positions
    string_types = [string_6_type, string_5_type, string_4_type, string_3_type, string_2_type, string_1_type]
    string_frets = [string_6_fret, string_5_fret, string_4_fret, string_3_fret, string_2_fret, string_1_fret]
    
    # Build chord pattern for validator (finger_indicator, fret_number)
    chord_pattern = []
    for i, (finger_type, fret) in enumerate(zip(string_types, string_frets)):
        finger_type = finger_type.strip().upper()
        
        # Validate fret range
        if fret < 0 or fret > 24:
            return templates.TemplateResponse("generate.html", {
                "request": request,
                "title": "Generate Chord Chart - Error",
                "chord_name": chord_name,
                "error": f"Fret {fret} out of range (0-24) for string {6-i}"
            })
        
        # For muted (X) and open (O) strings, fret should be 0
        if finger_type in ['X', 'O'] and fret != 0:
            fret = 0
        
        chord_pattern.append((finger_type, fret))
    
    # Validate the chord pattern
    validator = ChordFingeringValidator(thumb_reach_strings=thumb_reach)
    validation_result = validator.validate_chord(chord_pattern)
    
    # Generate chord chart
    try:
        from chord_chart import ChordChart
        
        safe_name = sanitize_chord_name(chord_name)
        filename = f"{safe_name}_chord.svg"
        filepath = chord_dir / filename
        
        # Ensure chords directory exists
        os.makedirs(chord_dir, exist_ok=True)
        
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
            "error": f"Error generating chord: {str(e)}"
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
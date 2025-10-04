"""Test script to verify the 422 API fix"""
import requests
import json

# Test data that should work with the fix
test_data = {
    'finger1': 'X',
    'fret1': '0',    # Now sending '0' instead of ''
    'finger2': '1',
    'fret2': '3',
    'finger3': '2', 
    'fret3': '2',
    'finger4': '3',
    'fret4': '1',
    'finger5': 'X',
    'fret5': '0',    # Now sending '0' instead of ''
    'finger6': 'X',
    'fret6': '0'     # Now sending '0' instead of ''
}

print("Testing API validation with fixed data...")
print(f"Test data: {test_data}")

try:
    # Start server first
    import subprocess
    import time
    import threading
    
    def start_server():
        subprocess.run(['uvicorn', 'chord_server:app', '--host', '127.0.0.1', '--port', '8002'], 
                       cwd='C:\\Data\\Dev\\ChordMaker')
    
    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(3)
    
    # Test the API
    response = requests.post('http://localhost:8002/api/validate', data=test_data)
    
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        print("✓ SUCCESS! No more 422 error")
        result = response.json()
        print(f"Validation result: {json.dumps(result, indent=2)}")
    else:
        print(f"✗ Still getting error: {response.status_code}")
        print(f"Response text: {response.text}")
        
except Exception as e:
    print(f"Error running test: {e}")
    
    # Let's test the validation logic directly instead
    print("\nTesting validation logic directly...")
    from chord_validator import ChordValidator
    validator = ChordValidator()
    
    # Convert string data to the format expected by the validator
    chord_data = []
    for i in range(1, 7):
        finger = test_data[f'finger{i}']
        fret = int(test_data[f'fret{i}'])
        chord_data.append((finger, fret))
    
    print(f"Chord data: {chord_data}")
    
    # Test validation
    result = validate_chord_fingering(chord_data)
    print(f"Direct validation result: {json.dumps(result, indent=2)}")
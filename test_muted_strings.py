#!/usr/bin/env python3
"""Test the muted string handling in the chord server."""

import requests
import json

def test_muted_string_handling():
    """Test that muted strings ignore fret values."""
    
    print("Testing muted string handling...")
    
    # Test data with muted strings that have non-zero fret values
    # This should be sanitized to fret=0 by the server
    test_data = {
        'chord_name': 'Test Chord',
        'string_6_type': 'X',  # Muted
        'string_6_fret': '5',  # Should be ignored and set to 0
        'string_5_type': '3',  # 3rd finger
        'string_5_fret': '3',  # Should remain as 3
        'string_4_type': 'O',  # Open
        'string_4_fret': '7',  # Should be ignored and set to 0
        'string_3_type': '2',  # 2nd finger
        'string_3_fret': '2',  # Should remain as 2
        'string_2_type': 'X',  # Muted
        'string_2_fret': '9',  # Should be ignored and set to 0
        'string_1_type': 'O',  # Open
        'string_1_fret': '4',  # Should be ignored and set to 0
        'thumb_reach': '1'
    }
    
    # Test validation endpoint
    try:
        response = requests.post('http://127.0.0.1:8000/api/validate', data=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Validation endpoint response:")
            print(f"   Status: {result['status_name']}")
            print(f"   Valid: {result['is_valid']}")
            
            # Check that finger positions only include non-muted/non-open strings
            finger_positions = result.get('finger_positions', [])
            print(f"   Finger positions found: {len(finger_positions)}")
            
            for pos in finger_positions:
                print(f"   - Finger {pos['finger']} on string {pos['string']}, fret {pos['fret']}")
                
            # Should only have positions for strings 5 and 3 (the fingered strings)
            expected_positions = 2
            if len(finger_positions) == expected_positions:
                print("✅ Correct number of finger positions (muted/open strings ignored)")
            else:
                print(f"❌ Expected {expected_positions} positions, got {len(finger_positions)}")
                
        else:
            print(f"❌ Validation failed with status {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_muted_string_handling()
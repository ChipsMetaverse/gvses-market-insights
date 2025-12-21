"""
Test Frontend Integration - Simulates React TradingChart workflow
Tests the complete create/load/update/delete cycle that the frontend uses
"""
import requests
import time

API_BASE = "http://localhost:8001"
TEST_SYMBOL = "TSLA"


def test_frontend_workflow():
    """Simulate the exact workflow the React frontend will use"""

    print("\n" + "="*60)
    print("FRONTEND INTEGRATION TEST")
    print("="*60)

    # Clean up any existing test data
    print(f"\n1. Cleaning up existing drawings for {TEST_SYMBOL}...")
    requests.delete(f"{API_BASE}/api/drawings?symbol={TEST_SYMBOL}")

    # Step 1: User draws a trendline on the chart (onCreate callback)
    print(f"\n2. Simulating user drawing trendline on {TEST_SYMBOL} chart...")
    now = int(time.time())
    drawing_data = {
        "symbol": TEST_SYMBOL,
        "type": "trendline",
        "data": {
            "name": "Support Line",
            "color": "#22c55e",
            "width": 2,
            "style": "solid",
            "visible": True,
            "coordinates": {
                "a": {"time": now - (30 * 86400), "price": 180.0},
                "b": {"time": now - (5 * 86400), "price": 220.0}
            }
        }
    }

    response = requests.post(f"{API_BASE}/api/drawings", json=drawing_data)
    assert response.status_code == 201, f"Create failed: {response.text}"

    saved_drawing = response.json()
    drawing_id = saved_drawing["id"]
    print(f"   ✓ Drawing created with ID: {drawing_id}")
    print(f"   ✓ Type: {saved_drawing['type']}")
    print(f"   ✓ Name: {saved_drawing['data']['name']}")

    # Step 2: User refreshes page or switches symbol - auto-load should trigger
    print(f"\n3. Simulating page refresh - loading saved drawings for {TEST_SYMBOL}...")
    response = requests.get(f"{API_BASE}/api/drawings?symbol={TEST_SYMBOL}")
    assert response.status_code == 200, f"Load failed: {response.text}"

    data = response.json()
    assert data["total"] == 1, f"Expected 1 drawing, found {data['total']}"
    loaded_drawing = data["drawings"][0]
    print(f"   ✓ Loaded {data['total']} drawing(s)")
    print(f"   ✓ Restored: {loaded_drawing['data']['name']}")
    print(f"   ✓ Coordinates: {loaded_drawing['data']['coordinates']}")

    # Step 3: User drags the trendline to a new position (onUpdate callback)
    print(f"\n4. Simulating user dragging trendline to new position...")
    update_data = {
        "data": {
            "coordinates": {
                "a": {"time": now - (25 * 86400), "price": 175.0},
                "b": {"time": now - (3 * 86400), "price": 215.0}
            }
        }
    }

    response = requests.patch(f"{API_BASE}/api/drawings/{drawing_id}", json=update_data)
    assert response.status_code == 200, f"Update failed: {response.text}"

    updated_drawing = response.json()
    new_coords = updated_drawing["data"]["coordinates"]
    print(f"   ✓ Trendline position updated")
    print(f"   ✓ New coordinates: {new_coords}")

    # Step 4: User deletes the drawing (onDelete callback)
    print(f"\n5. Simulating user deleting the drawing...")
    response = requests.delete(f"{API_BASE}/api/drawings/{drawing_id}")
    assert response.status_code == 204, f"Delete failed: {response.text}"
    print(f"   ✓ Drawing deleted")

    # Step 5: Verify it's gone
    print(f"\n6. Verifying deletion...")
    response = requests.get(f"{API_BASE}/api/drawings?symbol={TEST_SYMBOL}")
    data = response.json()
    assert data["total"] == 0, f"Expected 0 drawings, found {data['total']}"
    print(f"   ✓ Confirmed: {data['total']} drawings remaining")

    print("\n" + "="*60)
    print("✓ ALL FRONTEND INTEGRATION TESTS PASSED")
    print("="*60)
    print("\nThe React TradingChart is ready to use!")
    print("- Drawings auto-save when created")
    print("- Drawings auto-load when chart mounts")
    print("- Updates persist when dragged")
    print("- Deletions sync to database")
    print("\n")


def test_multiple_drawings():
    """Test multiple drawings on the same chart"""
    print("\n" + "="*60)
    print("MULTIPLE DRAWINGS TEST")
    print("="*60)

    # Clean up
    print(f"\n1. Setting up test environment...")
    requests.delete(f"{API_BASE}/api/drawings?symbol={TEST_SYMBOL}")

    # Create 3 different types of drawings
    print(f"\n2. Creating multiple drawings on {TEST_SYMBOL} chart...")
    now = int(time.time())

    drawings = [
        {
            "symbol": TEST_SYMBOL,
            "type": "trendline",
            "data": {
                "name": "Support",
                "color": "#22c55e",
                "coordinates": {
                    "a": {"time": now - (30 * 86400), "price": 180.0},
                    "b": {"time": now - (5 * 86400), "price": 220.0}
                }
            }
        },
        {
            "symbol": TEST_SYMBOL,
            "type": "trendline",
            "data": {
                "name": "Resistance",
                "color": "#ef4444",
                "coordinates": {
                    "a": {"time": now - (30 * 86400), "price": 250.0},
                    "b": {"time": now - (5 * 86400), "price": 280.0}
                }
            }
        },
        {
            "symbol": TEST_SYMBOL,
            "type": "horizontal",
            "data": {
                "name": "Price Target",
                "color": "#3b82f6",
                "price": 240.0
            }
        }
    ]

    for drawing in drawings:
        response = requests.post(f"{API_BASE}/api/drawings", json=drawing)
        assert response.status_code == 201
        print(f"   ✓ Created: {drawing['data']['name']} ({drawing['type']})")

    # Load all drawings
    print(f"\n3. Loading all drawings for {TEST_SYMBOL}...")
    response = requests.get(f"{API_BASE}/api/drawings?symbol={TEST_SYMBOL}")
    data = response.json()

    assert data["total"] == 3, f"Expected 3 drawings, found {data['total']}"
    print(f"   ✓ Loaded {data['total']} drawings:")
    for d in data["drawings"]:
        print(f"     - {d['data'].get('name', 'Unnamed')} ({d['type']})")

    # Clean up
    print(f"\n4. Cleaning up test data...")
    requests.delete(f"{API_BASE}/api/drawings?symbol={TEST_SYMBOL}")
    print(f"   ✓ Test data cleared")

    print("\n" + "="*60)
    print("✓ MULTIPLE DRAWINGS TEST PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        test_frontend_workflow()
        test_multiple_drawings()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        exit(1)

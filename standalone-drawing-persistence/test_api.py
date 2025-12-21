"""
Comprehensive Test Suite for Drawing Persistence API
Tests all CRUD operations, validation, and edge cases
"""
import pytest
from httpx import AsyncClient
from fastapi import status
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# Test Configuration
# ============================================================================

BASE_URL = "http://localhost:8001"
TEST_SYMBOL = "TSLA"
TEST_USER_ID = "00000000-0000-0000-0000-000000000001"


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def trendline_drawing():
    """Sample trendline drawing data"""
    return {
        "symbol": TEST_SYMBOL,
        "type": "trendline",
        "data": {
            "name": "Support Line",
            "visible": True,
            "selected": False,
            "color": "#22c55e",
            "width": 2,
            "style": "solid",
            "coordinates": {
                "a": {"time": 1609459200, "price": 700.0},
                "b": {"time": 1612137600, "price": 850.0}
            }
        }
    }


@pytest.fixture
def horizontal_drawing():
    """Sample horizontal line drawing data"""
    return {
        "symbol": TEST_SYMBOL,
        "type": "horizontal",
        "data": {
            "name": "Resistance",
            "color": "#ef4444",
            "width": 2,
            "style": "dashed",
            "coordinates": {
                "price": 900.0,
                "rotation": 0
            }
        }
    }


@pytest.fixture
def ray_drawing():
    """Sample ray drawing data"""
    return {
        "symbol": TEST_SYMBOL,
        "type": "ray",
        "data": {
            "color": "#1e90ff",
            "coordinates": {
                "a": {"time": 1609459200, "price": 650.0},
                "b": {"time": 1612137600, "price": 800.0},
                "direction": "right"
            }
        }
    }


# ============================================================================
# Health Check Tests
# ============================================================================

@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns API info"""
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["status"] == "running"


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_drawings_health():
    """Test drawings health endpoint"""
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/api/drawings/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"


# ============================================================================
# Create Drawing Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_trendline(trendline_drawing):
    """Test creating a trendline drawing"""
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/drawings", json=trendline_drawing)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify all fields
        assert "id" in data
        assert data["symbol"] == TEST_SYMBOL
        assert data["type"] == "trendline"
        assert data["data"]["name"] == "Support Line"
        assert data["data"]["color"] == "#22c55e"
        assert data["data"]["coordinates"]["a"]["price"] == 700.0
        assert "created_at" in data
        assert "updated_at" in data

        return data["id"]


@pytest.mark.asyncio
async def test_create_horizontal(horizontal_drawing):
    """Test creating a horizontal line drawing"""
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/drawings", json=horizontal_drawing)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["type"] == "horizontal"
        assert data["data"]["coordinates"]["price"] == 900.0
        assert data["data"]["style"] == "dashed"


@pytest.mark.asyncio
async def test_create_ray(ray_drawing):
    """Test creating a ray drawing"""
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/drawings", json=ray_drawing)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["type"] == "ray"
        assert data["data"]["coordinates"]["direction"] == "right"


# ============================================================================
# Validation Tests
# ============================================================================

@pytest.mark.asyncio
async def test_invalid_color():
    """Test that invalid hex colors are rejected"""
    invalid_drawing = {
        "symbol": "TSLA",
        "kind": "horizontal",
        "color": "red",  # Not a hex code
        "coordinates": {"price": 100}
    }

    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/drawings", json=invalid_drawing)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_invalid_coordinates():
    """Test that invalid coordinates are rejected"""
    invalid_drawing = {
        "symbol": "TSLA",
        "kind": "trendline",
        "coordinates": {"price": 100}  # Missing a, b for trendline
    }

    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/drawings", json=invalid_drawing)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_invalid_width():
    """Test that invalid line width is rejected"""
    invalid_drawing = {
        "symbol": "TSLA",
        "kind": "horizontal",
        "width": 50,  # Exceeds max of 10
        "coordinates": {"price": 100}
    }

    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/drawings", json=invalid_drawing)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================================================
# List/Get Drawing Tests
# ============================================================================

@pytest.mark.asyncio
async def test_list_drawings(trendline_drawing):
    """Test listing drawings for a symbol"""
    async with AsyncClient(base_url=BASE_URL) as client:
        # Create a drawing first
        await client.post("/api/drawings", json=trendline_drawing)

        # List drawings
        response = await client.get(f"/api/drawings?symbol={TEST_SYMBOL}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "drawings" in data
        assert "total" in data
        assert data["total"] >= 1
        assert len(data["drawings"]) >= 1


@pytest.mark.asyncio
async def test_list_with_kind_filter(trendline_drawing, horizontal_drawing):
    """Test filtering drawings by type"""
    async with AsyncClient(base_url=BASE_URL) as client:
        # Create both types
        await client.post("/api/drawings", json=trendline_drawing)
        await client.post("/api/drawings", json=horizontal_drawing)

        # Filter by trendline (use 'type' parameter, not 'kind')
        response = await client.get(
            f"/api/drawings?symbol={TEST_SYMBOL}&type=trendline"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # All results should be trendlines
        for drawing in data["drawings"]:
            assert drawing["type"] == "trendline"


@pytest.mark.asyncio
async def test_get_single_drawing(trendline_drawing):
    """Test retrieving a single drawing by ID"""
    async with AsyncClient(base_url=BASE_URL) as client:
        # Create drawing
        create_response = await client.post("/api/drawings", json=trendline_drawing)
        drawing_id = create_response.json()["id"]

        # Get drawing
        response = await client.get(f"/api/drawings/{drawing_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == drawing_id
        assert data["symbol"] == TEST_SYMBOL


@pytest.mark.asyncio
async def test_get_nonexistent_drawing():
    """Test that getting a nonexistent drawing returns 404"""
    fake_id = "00000000-0000-0000-0000-000000000000"

    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get(f"/api/drawings/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Update Drawing Tests
# ============================================================================

@pytest.mark.asyncio
async def test_update_drawing_color(trendline_drawing):
    """Test updating drawing color"""
    async with AsyncClient(base_url=BASE_URL) as client:
        # Create drawing
        create_response = await client.post("/api/drawings", json=trendline_drawing)
        drawing_id = create_response.json()["id"]

        # Update color (must be nested in data field for JSONB schema)
        update_data = {"data": {"color": "#ff0000"}}
        response = await client.patch(
            f"/api/drawings/{drawing_id}",
            json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["color"] == "#ff0000"


@pytest.mark.asyncio
async def test_update_drawing_coordinates(trendline_drawing):
    """Test updating drawing coordinates (moving endpoints)"""
    async with AsyncClient(base_url=BASE_URL) as client:
        # Create drawing
        create_response = await client.post("/api/drawings", json=trendline_drawing)
        drawing_id = create_response.json()["id"]

        # Update coordinates (must be nested in data field for JSONB schema)
        new_coords = {
            "a": {"time": 1609459200, "price": 750.0},  # Moved up
            "b": {"time": 1612137600, "price": 900.0}
        }
        response = await client.patch(
            f"/api/drawings/{drawing_id}",
            json={"data": {"coordinates": new_coords}}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["coordinates"]["a"]["price"] == 750.0


@pytest.mark.asyncio
async def test_update_drawing_visibility(trendline_drawing):
    """Test toggling drawing visibility"""
    async with AsyncClient(base_url=BASE_URL) as client:
        # Create drawing
        create_response = await client.post("/api/drawings", json=trendline_drawing)
        drawing_id = create_response.json()["id"]

        # Hide drawing (must be nested in data field for JSONB schema)
        response = await client.patch(
            f"/api/drawings/{drawing_id}",
            json={"data": {"visible": False}}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["visible"] is False


# ============================================================================
# Delete Drawing Tests
# ============================================================================

@pytest.mark.asyncio
async def test_delete_drawing(trendline_drawing):
    """Test deleting a single drawing"""
    async with AsyncClient(base_url=BASE_URL) as client:
        # Create drawing
        create_response = await client.post("/api/drawings", json=trendline_drawing)
        drawing_id = create_response.json()["id"]

        # Delete drawing
        response = await client.delete(f"/api/drawings/{drawing_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's gone
        get_response = await client.get(f"/api/drawings/{drawing_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_bulk_delete_by_symbol(trendline_drawing, horizontal_drawing):
    """Test bulk deleting all drawings for a symbol"""
    async with AsyncClient(base_url=BASE_URL) as client:
        # Create multiple drawings
        await client.post("/api/drawings", json=trendline_drawing)
        await client.post("/api/drawings", json=horizontal_drawing)

        # Bulk delete
        response = await client.delete(f"/api/drawings?symbol={TEST_SYMBOL}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify all gone
        list_response = await client.get(f"/api/drawings?symbol={TEST_SYMBOL}")
        data = list_response.json()
        assert data["total"] == 0


# ============================================================================
# Batch Operations Tests
# ============================================================================

@pytest.mark.asyncio
async def test_batch_create(trendline_drawing, horizontal_drawing):
    """Test creating multiple drawings at once"""
    drawings = [trendline_drawing, horizontal_drawing]

    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post("/api/drawings/batch", json=drawings)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert len(data) == 2
        assert data[0]["type"] == "trendline"
        assert data[1]["type"] == "horizontal"


# ============================================================================
# Statistics Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_stats(trendline_drawing, horizontal_drawing):
    """Test getting drawing statistics"""
    async with AsyncClient(base_url=BASE_URL) as client:
        # Create some drawings
        await client.post("/api/drawings", json=trendline_drawing)
        await client.post("/api/drawings", json=horizontal_drawing)

        # Get stats
        response = await client.get("/api/drawings/stats/summary")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "total_drawings" in data
        assert "symbols_with_drawings" in data
        assert "drawings_by_type" in data
        assert data["total_drawings"] >= 2


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    print("🧪 Running Drawing Persistence API Tests...")
    print("📝 Make sure the server is running on http://localhost:8001")
    print("🗄️  And Supabase credentials are configured in .env\n")

    pytest.main([__file__, "-v", "--tb=short"])

"""
Drawing Persistence API - FastAPI Router
Complete CRUD operations with Supabase integration
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
import os
from datetime import datetime

from supabase import create_client, Client
from models import Drawing, DrawingCreate, DrawingUpdate, DrawingList, DrawingStats


# ============================================================================
# Supabase Client Setup
# ============================================================================

def get_supabase() -> Client:
    """Get Supabase client instance"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

    return create_client(url, key)


# Mock user ID for testing (replace with actual auth in production)
async def get_current_user_id() -> Optional[UUID]:
    """
    Get current authenticated user ID
    In production: Extract from JWT token
    For testing: Return None (anonymous user allowed by RLS policy)
    """
    # TODO: Replace with actual Supabase auth extraction
    # user = request.state.user
    # return user.id

    # For testing: Return None to allow anonymous access (RLS policy allows user_id IS NULL)
    return None


# ============================================================================
# Router Setup
# ============================================================================

router = APIRouter(
    prefix="/api/drawings",
    tags=["drawings"],
    responses={
        404: {"description": "Drawing not found"},
        401: {"description": "Unauthorized"}
    }
)


# ============================================================================
# CRUD Endpoints
# ============================================================================

@router.post(
    "",
    response_model=Drawing,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new drawing",
    description="Store a drawing (trendline, ray, or horizontal) with time/price coordinates"
)
async def create_drawing(
    drawing: DrawingCreate,
    user_id: Optional[UUID] = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Create a new drawing for the authenticated user

    - **symbol**: Stock ticker (e.g., TSLA, AAPL)
    - **kind**: Drawing type (trendline, ray, horizontal, fibonacci, support, resistance)
    - **coordinates**: Time/price data matching the kind
    - **color**: Hex color code (default: #ffa500)
    - **width**: Line width 1-10px (default: 2)
    - **style**: Line style (solid, dashed, dotted)
    """
    try:
        # Prepare data for insertion
        data = {
            "user_id": str(user_id) if user_id else None,
            "symbol": drawing.symbol,
            "type": drawing.type,
            "data": drawing.data.model_dump(),
            "conversation_id": str(drawing.conversation_id) if drawing.conversation_id else None
        }

        # Insert into Supabase
        response = supabase.table("user_drawings").insert(data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create drawing"
            )

        return Drawing(**response.data[0])

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get(
    "",
    response_model=DrawingList,
    summary="List drawings",
    description="Get all drawings for a symbol, optionally filtered by type"
)
async def list_drawings(
    symbol: str = Query(..., description="Stock symbol (e.g., TSLA)"),
    type_filter: Optional[str] = Query(None, description="Filter by drawing type", alias="type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Items per page"),
    user_id: Optional[UUID] = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    List all drawings for a specific symbol

    Supports pagination and filtering by drawing type
    Returns most recent drawings first
    """
    try:
        # Build query
        query = supabase.table("user_drawings").select("*", count="exact")

        # Filter by user_id (NULL for anonymous users)
        if user_id is None:
            query = query.is_("user_id", None)
        else:
            query = query.eq("user_id", str(user_id))

        query = query.eq("symbol", symbol.upper()).order("created_at", desc=True)

        # Apply kind filter if specified
        if type_filter:
            query = query.eq("type", type_filter)

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)

        # Execute query
        response = query.execute()

        # Convert to Drawing models
        drawings = [Drawing(**item) for item in response.data]
        total = response.count if response.count is not None else len(drawings)

        return DrawingList(
            drawings=drawings,
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


# ============================================================================
# Health Check (must come before /{drawing_id} for proper routing)
# ============================================================================

@router.get(
    "/health",
    summary="Health check",
    description="Verify database connectivity"
)
async def health_check(supabase: Client = Depends(get_supabase)):
    """Check if database connection is healthy"""
    try:
        # Simple query to verify connection
        response = supabase.table("user_drawings").select("id").limit(1).execute()

        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unhealthy: {str(e)}"
        )


@router.get(
    "/{drawing_id}",
    response_model=Drawing,
    summary="Get a single drawing",
    description="Retrieve a specific drawing by ID"
)
async def get_drawing(
    drawing_id: UUID,
    user_id: Optional[UUID] = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase)
):
    """Get a specific drawing by ID"""
    try:
        # Build query
        query = supabase.table("user_drawings").select("*").eq("id", str(drawing_id))

        # Filter by user_id (NULL for anonymous users)
        if user_id is None:
            query = query.is_("user_id", None)
        else:
            query = query.eq("user_id", str(user_id))

        response = query.execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Drawing {drawing_id} not found"
            )

        return Drawing(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.patch(
    "/{drawing_id}",
    response_model=Drawing,
    summary="Update a drawing",
    description="Update drawing properties (position, style, visibility)"
)
async def update_drawing(
    drawing_id: UUID,
    updates: DrawingUpdate,
    user_id: Optional[UUID] = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Update an existing drawing

    Only provided fields will be updated. Use PATCH semantics.
    Common updates:
    - Move endpoints: Update coordinates
    - Change style: Update color, width, style
    - Toggle visibility: Update visible field
    """
    try:
        # Build update data (only non-None fields)
        raw_data = updates.model_dump(exclude_unset=True)
        update_data = {}

        for k, v in raw_data.items():
            if v is not None:
                if k == 'data':
                    # Convert DrawingData to dict
                    update_data['data'] = v
                elif k == 'conversation_id':
                    update_data['conversation_id'] = str(v) if v else None
                else:
                    update_data[k] = v

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Build update query
        query = supabase.table("user_drawings").update(update_data).eq("id", str(drawing_id))

        # Filter by user_id (NULL for anonymous users)
        if user_id is None:
            query = query.is_("user_id", None)
        else:
            query = query.eq("user_id", str(user_id))

        response = query.execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Drawing {drawing_id} not found"
            )

        return Drawing(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.delete(
    "/{drawing_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a drawing",
    description="Permanently remove a drawing"
)
async def delete_drawing(
    drawing_id: UUID,
    user_id: Optional[UUID] = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase)
):
    """Delete a drawing permanently"""
    try:
        # Build delete query
        query = supabase.table("user_drawings").delete().eq("id", str(drawing_id))

        # Filter by user_id (NULL for anonymous users)
        if user_id is None:
            query = query.is_("user_id", None)
        else:
            query = query.eq("user_id", str(user_id))

        response = query.execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Drawing {drawing_id} not found"
            )

        return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Bulk delete drawings",
    description="Delete all drawings for a symbol"
)
async def bulk_delete_drawings(
    symbol: str = Query(..., description="Stock symbol"),
    kind: Optional[str] = Query(None, description="Optional: Only delete specific type"),
    user_id: Optional[UUID] = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Bulk delete drawings for a symbol

    Useful for clearing all drawings when switching charts
    Can optionally filter by type to clear only trendlines, etc.
    """
    try:
        # Build delete query
        query = supabase.table("user_drawings").delete()

        # Filter by user_id (NULL for anonymous users)
        if user_id is None:
            query = query.is_("user_id", None)
        else:
            query = query.eq("user_id", str(user_id))

        query = query.eq("symbol", symbol.upper())

        if kind:
            query = query.eq("type", kind)

        query.execute()

        return None  # 204 No Content

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


# ============================================================================
# Utility Endpoints
# ============================================================================

@router.get(
    "/stats/summary",
    response_model=DrawingStats,
    summary="Get drawing statistics",
    description="Get user's drawing statistics across all symbols"
)
async def get_drawing_stats(
    user_id: Optional[UUID] = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase)
):
    """Get aggregate statistics about user's drawings"""
    try:
        # Build query
        query = supabase.table("user_drawings").select("type,symbol,created_at")

        # Filter by user_id (NULL for anonymous users)
        if user_id is None:
            query = query.is_("user_id", None)
        else:
            query = query.eq("user_id", str(user_id))

        response = query.execute()

        drawings = response.data

        # Calculate statistics
        total = len(drawings)
        symbols = set(d["symbol"] for d in drawings)
        by_type = {}

        for d in drawings:
            kind = d["type"]
            by_type[kind] = by_type.get(kind, 0) + 1

        last_created = None
        if drawings:
            last_created = max(
                datetime.fromisoformat(d["created_at"].replace("Z", "+00:00"))
                for d in drawings
            )

        return DrawingStats(
            total_drawings=total,
            symbols_with_drawings=len(symbols),
            drawings_by_type=by_type,
            last_drawing_created=last_created
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


# ============================================================================
# Batch Operations (Advanced)
# ============================================================================

@router.post(
    "/batch",
    response_model=List[Drawing],
    status_code=status.HTTP_201_CREATED,
    summary="Batch create drawings",
    description="Create multiple drawings in a single transaction"
)
async def batch_create_drawings(
    drawings: List[DrawingCreate],
    user_id: Optional[UUID] = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Create multiple drawings at once

    Useful for:
    - Importing saved drawing sets
    - Creating pattern annotations (multiple related drawings)
    - Restoring drawing state

    Performs atomic transaction - all succeed or all fail
    """
    try:
        # Prepare batch data
        batch_data = [
            {
                "user_id": str(user_id) if user_id else None,
                "symbol": d.symbol,
                "type": d.type,
                "data": d.data.model_dump(),
                "conversation_id": str(d.conversation_id) if d.conversation_id else None
            }
            for d in drawings
        ]

        # Batch insert
        response = supabase.table("user_drawings").insert(batch_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create drawings"
            )

        return [Drawing(**item) for item in response.data]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


# Health check has been moved before /{drawing_id} endpoint for proper routing

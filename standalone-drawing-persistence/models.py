"""
Drawing Persistence Models
Pydantic models matching TypeScript drawing types with full validation
"""
from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from uuid import UUID


# ============================================================================
# Time/Price Coordinate Models
# ============================================================================

class TimePrice(BaseModel):
    """Time-Price coordinate pair matching TypeScript Tp type"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "time": 1609459200,
                "price": 700.50
            }
        }
    )

    time: int = Field(..., description="Unix timestamp in seconds")
    price: float = Field(..., gt=0, description="Price value")


# ============================================================================
# Drawing Coordinate Models (JSONB storage)
# ============================================================================

class TrendlineCoordinates(BaseModel):
    """Coordinates for trendline and ray drawings"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "a": {"time": 1609459200, "price": 700},
                "b": {"time": 1612137600, "price": 850}
            }
        }
    )

    a: TimePrice = Field(..., description="Start point")
    b: TimePrice = Field(..., description="End point")
    direction: Optional[Literal['right', 'left', 'both']] = Field(
        None,
        description="Ray direction (only for ray type)"
    )


class HorizontalCoordinates(BaseModel):
    """Coordinates for horizontal line drawings"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "price": 800,
                "rotation": 0,
                "draggable": True
            }
        }
    )

    price: float = Field(..., gt=0, description="Y-axis price level")
    rotation: Optional[float] = Field(0, ge=0, le=360, description="Rotation angle in degrees")
    t0: Optional[int] = Field(None, description="Optional start time bound")
    t1: Optional[int] = Field(None, description="Optional end time bound")
    draggable: Optional[bool] = Field(True, description="Enable drag-move")


# ============================================================================
# Base Drawing Model
# ============================================================================

class DrawingData(BaseModel):
    """Drawing data stored in JSONB field"""
    model_config = ConfigDict(extra='allow')  # Allow additional fields

    # Coordinates
    coordinates: Optional[Dict[str, Any]] = Field(None, description="Drawing coordinates")

    # Style properties
    color: Optional[str] = Field("#ffa500", pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code")
    width: Optional[int] = Field(2, ge=1, le=10, description="Line width in pixels")
    style: Optional[Literal['solid', 'dashed', 'dotted']] = Field('solid', description="Line style")

    # Display properties
    name: Optional[str] = Field(None, max_length=255, description="Optional legend label")
    visible: Optional[bool] = Field(True, description="Visibility toggle")
    selected: Optional[bool] = Field(False, description="Selection state")


class DrawingBase(BaseModel):
    """Base drawing properties for user_drawings table"""
    symbol: str = Field(..., min_length=1, max_length=20, description="Stock symbol")
    type: Literal['trendline', 'ray', 'horizontal', 'fibonacci', 'support', 'resistance'] = Field(
        ...,
        description="Drawing type"
    )
    data: DrawingData = Field(..., description="Drawing data (JSONB)")
    conversation_id: Optional[UUID] = Field(None, description="Optional conversation reference")

    @field_validator('data')
    @classmethod
    def validate_data(cls, v, info):
        """Validate coordinates in data match the drawing type"""
        if not info.data or 'type' not in info.data:
            return v

        drawing_type = info.data['type']

        # Validate coordinates if present
        if v.coordinates:
            try:
                if drawing_type in ('trendline', 'ray'):
                    TrendlineCoordinates(**v.coordinates)
                elif drawing_type == 'horizontal':
                    HorizontalCoordinates(**v.coordinates)
            except Exception as e:
                raise ValueError(f"Invalid coordinates for {drawing_type}: {e}")

        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "TSLA",
                "type": "trendline",
                "data": {
                    "coordinates": {
                        "a": {"time": 1609459200, "price": 700},
                        "b": {"time": 1612137600, "price": 850}
                    },
                    "color": "#22c55e",
                    "width": 2,
                    "style": "solid",
                    "name": "Support Line",
                    "visible": True,
                    "selected": False
                }
            }
        }
    )


# ============================================================================
# Request/Response Models
# ============================================================================

class DrawingCreate(DrawingBase):
    """Model for creating a new drawing"""
    pass


class DrawingUpdate(BaseModel):
    """Model for updating an existing drawing (all fields optional)"""
    symbol: Optional[str] = Field(None, min_length=1, max_length=20)
    type: Optional[Literal['trendline', 'ray', 'horizontal', 'fibonacci', 'support', 'resistance']] = None
    data: Optional[DrawingData] = None
    conversation_id: Optional[UUID] = None

    @field_validator('data')
    @classmethod
    def validate_data(cls, v, info):
        """Validate coordinates in data if provided"""
        if v is None:
            return v

        if not info.data or 'type' not in info.data or info.data['type'] is None:
            # Can't validate without type, skip
            return v

        drawing_type = info.data['type']

        # Validate coordinates if present
        if v.coordinates:
            try:
                if drawing_type in ('trendline', 'ray'):
                    TrendlineCoordinates(**v.coordinates)
                elif drawing_type == 'horizontal':
                    HorizontalCoordinates(**v.coordinates)
            except Exception as e:
                raise ValueError(f"Invalid coordinates for {drawing_type}: {e}")

        return v


class Drawing(DrawingBase):
    """Complete drawing model with database fields"""
    model_config = ConfigDict(
        from_attributes=True,  # Pydantic v2 (was orm_mode in v1)
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "conversation_id": "123e4567-e89b-12d3-a456-426614174002",
                "symbol": "TSLA",
                "type": "trendline",
                "data": {
                    "coordinates": {
                        "a": {"time": 1609459200, "price": 700},
                        "b": {"time": 1612137600, "price": 850}
                    },
                    "color": "#22c55e",
                    "width": 2,
                    "style": "solid",
                    "name": "Support Line",
                    "visible": True,
                    "selected": False
                },
                "created_at": "2025-01-27T10:00:00Z",
                "updated_at": "2025-01-27T10:00:00Z"
            }
        }
    )

    id: UUID = Field(..., description="Drawing unique identifier")
    user_id: Optional[UUID] = Field(None, description="Owner user ID (null for anonymous)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class DrawingList(BaseModel):
    """Paginated list of drawings"""
    drawings: list[Drawing]
    total: int
    page: int = 1
    page_size: int = 100


class DrawingStats(BaseModel):
    """Drawing statistics for a user"""
    total_drawings: int
    symbols_with_drawings: int
    drawings_by_type: Dict[str, int]
    last_drawing_created: Optional[datetime]


# ============================================================================
# TypeScript Type Export Helper
# ============================================================================

def generate_typescript_types():
    """Generate TypeScript interfaces matching these models"""
    return """
// Auto-generated from Python models
export interface TimePrice {
  time: number;
  price: number;
}

export interface TrendlineCoordinates {
  a: TimePrice;
  b: TimePrice;
  direction?: 'right' | 'left' | 'both';
}

export interface HorizontalCoordinates {
  price: number;
  rotation?: number;
  t0?: number;
  t1?: number;
  draggable?: boolean;
}

export interface Drawing {
  id: string;
  user_id: string;
  symbol: string;
  kind: 'trendline' | 'ray' | 'horizontal';
  name?: string;
  visible: boolean;
  selected: boolean;
  color: string;
  width: number;
  style: 'solid' | 'dashed' | 'dotted';
  coordinates: TrendlineCoordinates | HorizontalCoordinates;
  created_at: string;
  updated_at: string;
}
"""


if __name__ == "__main__":
    # Test validation
    print("Testing trendline validation...")
    trendline = DrawingCreate(
        symbol="TSLA",
        type="trendline",
        data=DrawingData(
            coordinates={
                "a": {"time": 1609459200, "price": 700},
                "b": {"time": 1612137600, "price": 850}
            },
            color="#22c55e",
            width=2,
            style="solid"
        )
    )
    print(f"✅ Trendline valid: {trendline.model_dump()}")

    print("\nTesting horizontal validation...")
    horizontal = DrawingCreate(
        symbol="AAPL",
        type="horizontal",
        data=DrawingData(
            coordinates={
                "price": 150.50,
                "rotation": 45
            },
            color="#ef4444",
            width=3
        )
    )
    print(f"✅ Horizontal valid: {horizontal.model_dump()}")

    print("\n" + generate_typescript_types())

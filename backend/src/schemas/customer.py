"""
Customer app schemas
Pydantic models for customer-facing APIs
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal


class CategoryResponse(BaseModel):
    """Category response schema"""
    id: int
    name: str
    slug: str
    description: Optional[str]
    image: Optional[str]
    is_active: bool
    subcategory_count: int = 0

    class Config:
        from_attributes = True


class SubcategoryResponse(BaseModel):
    """Subcategory response schema"""
    id: int
    name: str
    slug: str
    description: Optional[str]
    category_id: int
    category_name: str
    is_active: bool
    rate_card_count: int = 0

    class Config:
        from_attributes = True


class RateCardResponse(BaseModel):
    """Rate card response schema"""
    id: int
    name: str
    price: Decimal
    strike_price: Optional[Decimal]
    category_id: int
    subcategory_id: int
    is_active: bool

    class Config:
        from_attributes = True


class AddToCartRequest(BaseModel):
    """Add item to cart request"""
    rate_card_id: int = Field(..., description="Rate card ID")
    quantity: int = Field(1, ge=1, le=100, description="Quantity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rate_card_id": 1,
                "quantity": 2
            }
        }


class UpdateCartItemRequest(BaseModel):
    """Update cart item request"""
    quantity: int = Field(..., ge=1, le=100, description="New quantity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 3
            }
        }


class CartItemResponse(BaseModel):
    """Cart item response schema"""
    id: int
    rate_card_id: int
    rate_card_name: str
    subcategory_id: int
    subcategory_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Cart response schema"""
    items: List[CartItemResponse]
    total_items: int
    total_amount: Decimal
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "rate_card_id": 1,
                        "rate_card_name": "Basic Cleaning",
                        "service_id": 1,
                        "service_name": "Home Cleaning",
                        "quantity": 2,
                        "unit_price": "500.00",
                        "total_price": "1000.00"
                    }
                ],
                "total_items": 1,
                "total_amount": "1000.00"
            }
        }


class AddressRequest(BaseModel):
    """Address request schema"""
    address_line1: str = Field(..., min_length=5, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: str = Field(..., min_length=6, max_length=6)
    is_default: bool = Field(False, description="Set as default address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "address_line1": "123 Main Street",
                "address_line2": "Apartment 4B",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "is_default": True
            }
        }


class AddressResponse(BaseModel):
    """Address response schema"""
    id: int
    address_line1: str
    address_line2: Optional[str]
    city: str
    state: str
    pincode: str
    is_default: bool

    class Config:
        from_attributes = True


class CreateBookingRequest(BaseModel):
    """Create booking request schema"""
    address_id: int = Field(..., description="Delivery address ID")
    preferred_date: str = Field(..., description="Preferred date (YYYY-MM-DD)")
    preferred_time: str = Field(..., description="Preferred time (HH:MM)")
    special_instructions: Optional[str] = Field(None, max_length=500)
    payment_method: str = Field("wallet", description="wallet, online, cod")
    
    class Config:
        json_schema_extra = {
            "example": {
                "address_id": 1,
                "preferred_date": "2025-10-10",
                "preferred_time": "14:00",
                "special_instructions": "Please call before arriving",
                "payment_method": "wallet"
            }
        }


class BookingItemResponse(BaseModel):
    """Booking item response schema"""
    id: int
    service_name: str
    rate_card_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    
    class Config:
        from_attributes = True


class BookingResponse(BaseModel):
    """Booking response schema"""
    id: int
    booking_number: str
    status: str
    total_amount: Decimal
    preferred_date: str
    preferred_time: str
    address: AddressResponse
    items: List[BookingItemResponse]
    special_instructions: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class CancelBookingRequest(BaseModel):
    """Cancel booking request schema"""
    reason: str = Field(..., min_length=10, max_length=500, description="Cancellation reason")

    class Config:
        json_schema_extra = {
            "example": {
                "reason": "Change of plans, need to reschedule"
            }
        }


class RescheduleBookingRequest(BaseModel):
    """Reschedule booking request schema"""
    preferred_date: str = Field(..., description="New preferred date (YYYY-MM-DD)")
    preferred_time: str = Field(..., description="New preferred time (HH:MM)")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for rescheduling")

    class Config:
        json_schema_extra = {
            "example": {
                "preferred_date": "2025-10-15",
                "preferred_time": "14:00",
                "reason": "Need to change appointment time"
            }
        }


class SearchRequest(BaseModel):
    """Search request schema"""
    query: str = Field(..., min_length=2, max_length=100, description="Search query")
    category_id: Optional[int] = Field(None, description="Filter by category")
    min_price: Optional[Decimal] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[Decimal] = Field(None, ge=0, description="Maximum price")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "cleaning",
                "category_id": 1,
                "min_price": "100.00",
                "max_price": "1000.00"
            }
        }


class SearchResponse(BaseModel):
    """Search response schema"""
    categories: List[CategoryResponse]
    rate_cards: List[RateCardResponse]
    total_results: int

    class Config:
        json_schema_extra = {
            "example": {
                "categories": [],
                "rate_cards": [],
                "total_results": 0
            }
        }


# Export
__all__ = [
    "CategoryResponse",
    "SubcategoryResponse",
    "RateCardResponse",
    "AddToCartRequest",
    "UpdateCartItemRequest",
    "CartItemResponse",
    "CartResponse",
    "AddressRequest",
    "AddressResponse",
    "CreateBookingRequest",
    "BookingItemResponse",
    "BookingResponse",
    "CancelBookingRequest",
    "SearchRequest",
    "SearchResponse",
]


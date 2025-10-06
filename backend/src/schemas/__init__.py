"""Schemas package"""

from src.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    AuthResponse,
    RefreshTokenRequest,
    PasswordChangeRequest,
    UserUpdateRequest,
    MessageResponse,
)

from src.schemas.ops import (
    OpsRegisterRequest,
    OpsLoginRequest,
    OpsUserResponse,
    OpsAuthResponse,
    OpsUpdateRequest,
    RoleResponse,
    PermissionResponse,
)

from src.schemas.customer import (
    CategoryResponse,
    SubcategoryResponse,
    RateCardResponse,
    AddToCartRequest,
    UpdateCartItemRequest,
    CartItemResponse,
    CartResponse,
    AddressRequest,
    AddressResponse,
    CreateBookingRequest,
    BookingItemResponse,
    BookingResponse,
    CancelBookingRequest,
    SearchRequest,
    SearchResponse,
)

__all__ = [
    # Auth schemas
    "UserRegisterRequest",
    "UserLoginRequest",
    "TokenResponse",
    "UserResponse",
    "AuthResponse",
    "RefreshTokenRequest",
    "PasswordChangeRequest",
    "UserUpdateRequest",
    "MessageResponse",

    # Ops schemas
    "OpsRegisterRequest",
    "OpsLoginRequest",
    "OpsUserResponse",
    "OpsAuthResponse",
    "OpsUpdateRequest",
    "RoleResponse",
    "PermissionResponse",

    # Customer schemas
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

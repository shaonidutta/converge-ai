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

from src.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
    SessionResponse,
)
from src.schemas.intent import (
    IntentResult,
    IntentClassificationResult,
    IntentClassificationRequest,
    IntentClassificationResponse,
    EntityExtractionResult,
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

    # Chat schemas
    "ChatMessageRequest",
    "ChatMessageResponse",
    "ChatHistoryResponse",
    "SessionResponse",

    # Intent schemas
    "IntentResult",
    "IntentClassificationResult",
    "IntentClassificationRequest",
    "IntentClassificationResponse",
    "EntityExtractionResult",
]

# Models package - exports all SQLAlchemy models

from backend.src.core.database.base import Base, TimestampMixin
from backend.src.core.models.user import User
from backend.src.core.models.category import Category, Subcategory
from backend.src.core.models.rate_card import RateCard
from backend.src.core.models.address import Address
from backend.src.core.models.provider import Provider
from backend.src.core.models.cart import Cart, CartItem
from backend.src.core.models.booking import Booking, PaymentStatus, PaymentMethod, SettlementStatus, BookingStatus
from backend.src.core.models.booking_item import BookingItem, ItemPaymentStatus, ItemStatus, CancelBy
from backend.src.core.models.conversation import Conversation, MessageRole, Channel
from backend.src.core.models.priority_queue import PriorityQueue, IntentType
from backend.src.core.models.complaint import Complaint, ComplaintUpdate, ComplaintType, ComplaintPriority, ComplaintStatus
from backend.src.core.models.pincode import Pincode, RateCardPincode, ProviderPincode
from backend.src.core.models.role import Role, Permission, RolePermission
from backend.src.core.models.staff import Staff, StaffSession, StaffActivityLog

__all__ = [
    # Base
    "Base",
    "TimestampMixin",

    # Core Models
    "User",
    "Category",
    "Subcategory",
    "RateCard",
    "Address",
    "Provider",
    "Cart",
    "CartItem",

    # Pincode Models (Optimized)
    "Pincode",
    "RateCardPincode",
    "ProviderPincode",

    # Cart Models
    "Cart",
    "CartItem",

    # Staff & RBAC Models
    "Staff",
    "StaffSession",
    "StaffActivityLog",
    "Role",
    "Permission",
    "RolePermission",

    # Booking Models
    "Booking",
    "BookingItem",

    # AI/Agent Models
    "Conversation",
    "PriorityQueue",

    # Complaint Models
    "Complaint",
    "ComplaintUpdate",

    # Enums - Booking
    "PaymentStatus",
    "PaymentMethod",
    "SettlementStatus",
    "BookingStatus",

    # Enums - BookingItem
    "ItemPaymentStatus",
    "ItemStatus",
    "CancelBy",

    # Enums - Conversation
    "MessageRole",
    "Channel",

    # Enums - PriorityQueue
    "IntentType",

    # Enums - Complaint
    "ComplaintType",
    "ComplaintPriority",
    "ComplaintStatus",
]

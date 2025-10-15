# Models package - exports all SQLAlchemy models

from src.core.database.base import Base, TimestampMixin
from src.core.models.user import User
from src.core.models.category import Category, Subcategory
from src.core.models.rate_card import RateCard
from src.core.models.address import Address
from src.core.models.provider import Provider
from src.core.models.cart import Cart, CartItem
from src.core.models.booking import Booking, PaymentStatus, PaymentMethod, SettlementStatus, BookingStatus
from src.core.models.booking_item import BookingItem, ItemPaymentStatus, ItemStatus, CancelBy
from src.core.models.conversation import Conversation, MessageRole, Channel
from src.core.models.dialog_state import DialogState, DialogStateType
from src.core.models.priority_queue import PriorityQueue, IntentType
from src.core.models.complaint import Complaint, ComplaintUpdate, ComplaintType, ComplaintPriority, ComplaintStatus
from src.core.models.pincode import Pincode, RateCardPincode, ProviderPincode
from src.core.models.role import Role, Permission, RolePermission
from src.core.models.staff import Staff, StaffSession, StaffActivityLog
from src.core.models.ops_config import OpsConfig
from src.core.models.ops_audit_log import OpsAuditLog

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
    "DialogState",
    "PriorityQueue",

    # Complaint Models
    "Complaint",
    "ComplaintUpdate",

    # Ops Models
    "OpsConfig",
    "OpsAuditLog",

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

    # Enums - DialogState
    "DialogStateType",

    # Enums - PriorityQueue
    "IntentType",

    # Enums - Complaint
    "ComplaintType",
    "ComplaintPriority",
    "ComplaintStatus",
]

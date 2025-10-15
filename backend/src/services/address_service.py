"""
Address Service
Business logic for address management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
import logging

from src.core.models import User, Address
from src.schemas.customer import AddressRequest, AddressResponse

logger = logging.getLogger(__name__)


class AddressService:
    """Service class for address management business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_addresses(
        self,
        user: User,
        active_only: bool = True
    ) -> List[AddressResponse]:
        """
        List user's addresses

        Args:
            user: Current user
            active_only: Show only active addresses

        Returns:
            List of AddressResponse
        """
        logger.info(f"Listing addresses for user_id: {user.id}")

        query = select(Address).where(Address.user_id == user.id)

        query = query.order_by(
            Address.is_default.desc(),
            Address.created_at.desc()
        )

        logger.debug("Executing address query")
        result = await self.db.execute(query)
        addresses = result.scalars().all()
        logger.debug(f"Found {len(addresses)} addresses")

        return [
            AddressResponse(
                id=addr.id,
                address_line1=addr.address_line1,
                address_line2=addr.address_line2,
                city=addr.city,
                state=addr.state,
                pincode=addr.pincode,
                is_default=addr.is_default
            )
            for addr in addresses
        ]
    
    async def add_address(
        self,
        request: AddressRequest,
        user: User
    ) -> AddressResponse:
        """
        Add a new address

        Args:
            request: Address creation request
            user: Current user

        Returns:
            AddressResponse with created address
        """
        logger.info(f"Adding address for user_id: {user.id}")
        logger.debug(f"Address data: {request.model_dump()}")

        # Check if user has any addresses
        logger.debug("Checking for existing addresses")
        existing_result = await self.db.execute(
            select(Address).where(Address.user_id == user.id)
        )
        existing_addresses = existing_result.scalars().all()
        logger.debug(f"Found {len(existing_addresses)} existing addresses")

        # If this is the first address, make it default
        is_default = (
            request.is_default
            if request.is_default is not None
            else (len(existing_addresses) == 0)
        )
        logger.debug(f"Setting is_default: {is_default}")

        # If setting as default, unset other defaults
        if is_default:
            logger.debug("Unsetting other default addresses")
            await self.db.execute(
                update(Address)
                .where(
                    Address.user_id == user.id,
                    Address.is_default == True
                )
                .values(is_default=False)
            )

        # Create address
        address = Address(
            user_id=user.id,
            address_line1=request.address_line1,
            address_line2=request.address_line2,
            city=request.city,
            state=request.state,
            pincode=request.pincode,
            is_default=is_default
        )

        self.db.add(address)
        await self.db.commit()
        await self.db.refresh(address)

        logger.info(f"Address added: id={address.id}, user_id={user.id}")

        return AddressResponse(
            id=address.id,
            address_line1=address.address_line1,
            address_line2=address.address_line2,
            city=address.city,
            state=address.state,
            pincode=address.pincode,
            is_default=address.is_default
        )
    
    async def get_address(self, address_id: int, user: User) -> AddressResponse:
        """
        Get address by ID
        
        Args:
            address_id: Address ID
            user: Current user
            
        Returns:
            AddressResponse
            
        Raises:
            ValueError: If address not found
        """
        result = await self.db.execute(
            select(Address).where(
                Address.id == address_id,
                Address.user_id == user.id
            )
        )
        address = result.scalar_one_or_none()
        
        if not address:
            raise ValueError("Address not found")
        
        return AddressResponse(
            id=address.id,
            address_line1=address.address_line1,
            address_line2=address.address_line2,
            city=address.city,
            state=address.state,
            pincode=address.pincode,
            is_default=address.is_default
        )
    
    async def update_address(
        self,
        address_id: int,
        request: AddressRequest,
        user: User
    ) -> AddressResponse:
        """
        Update address
        
        Args:
            address_id: Address ID
            request: Address update request
            user: Current user
            
        Returns:
            AddressResponse with updated address
            
        Raises:
            ValueError: If address not found
        """
        # Get address
        result = await self.db.execute(
            select(Address).where(
                Address.id == address_id,
                Address.user_id == user.id
            )
        )
        address = result.scalar_one_or_none()
        
        if not address:
            raise ValueError("Address not found")
        
        # If setting as default, unset other defaults
        if request.is_default and not address.is_default:
            await self.db.execute(
                update(Address)
                .where(
                    Address.user_id == user.id,
                    Address.is_default == True
                )
                .values(is_default=False)
            )
        
        # Update address
        address.address_line1 = request.address_line1
        address.address_line2 = request.address_line2
        address.city = request.city
        address.state = request.state
        address.pincode = request.pincode
        if request.is_default is not None:
            address.is_default = request.is_default

        await self.db.commit()
        await self.db.refresh(address)

        logger.info(f"Address updated: id={address.id}, user_id={user.id}")

        return AddressResponse(
            id=address.id,
            address_line1=address.address_line1,
            address_line2=address.address_line2,
            city=address.city,
            state=address.state,
            pincode=address.pincode,
            is_default=address.is_default
        )
    
    async def delete_address(self, address_id: int, user: User) -> None:
        """
        Delete address (soft delete)
        
        Args:
            address_id: Address ID
            user: Current user
            
        Raises:
            ValueError: If address not found
        """
        # Get address
        result = await self.db.execute(
            select(Address).where(
                Address.id == address_id,
                Address.user_id == user.id
            )
        )
        address = result.scalar_one_or_none()
        
        if not address:
            raise ValueError("Address not found")
        
        # Soft delete
        address.is_active = False
        
        # If this was default, set another address as default
        if address.is_default:
            address.is_default = False
            
            # Find another active address to set as default
            other_result = await self.db.execute(
                select(Address).where(
                    Address.user_id == user.id,
                    Address.is_active == True,
                    Address.id != address_id
                ).limit(1)
            )
            other_address = other_result.scalar_one_or_none()
            
            if other_address:
                other_address.is_default = True
        
        await self.db.commit()
        
        logger.info(f"Address deleted: id={address.id}, user_id={user.id}")


# Export
__all__ = ["AddressService"]


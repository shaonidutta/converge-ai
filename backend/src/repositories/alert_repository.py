"""
Alert Repository
Data access layer for alerts, alert rules, and alert subscriptions
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, update, delete
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from src.core.models.alert import Alert, AlertRule, AlertSubscription
from src.core.models.staff import Staff


class AlertRepository:
    """Repository for alert operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ========================================================================
    # Alert CRUD Operations
    # ========================================================================
    
    async def create_alert(
        self,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        assigned_to_staff_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None
    ) -> Alert:
        """Create a new alert"""
        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            resource_type=resource_type,
            resource_id=resource_id,
            assigned_to_staff_id=assigned_to_staff_id,
            alert_metadata=metadata,
            expires_at=expires_at
        )
        
        self.db.add(alert)
        await self.db.flush()
        await self.db.refresh(alert)
        
        return alert
    
    async def get_alert_by_id(self, alert_id: int) -> Optional[Alert]:
        """Get alert by ID"""
        result = await self.db.execute(
            select(Alert)
            .where(Alert.id == alert_id)
            .options(selectinload(Alert.assigned_to_staff))
        )
        return result.scalar_one_or_none()
    
    async def get_alerts_for_staff(
        self,
        staff_id: int,
        unread_only: bool = False,
        alert_types: Optional[List[str]] = None,
        severities: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Alert], int]:
        """
        Get alerts for a staff member with filtering
        Returns (alerts, total_count)
        """
        # Build base query
        query = select(Alert).where(
            and_(
                Alert.assigned_to_staff_id == staff_id,
                Alert.is_dismissed == False,
                or_(
                    Alert.expires_at.is_(None),
                    Alert.expires_at > datetime.utcnow()
                )
            )
        )
        
        # Apply filters
        if unread_only:
            query = query.where(Alert.is_read == False)
        
        if alert_types:
            query = query.where(Alert.alert_type.in_(alert_types))
        
        if severities:
            query = query.where(Alert.severity.in_(severities))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        alerts = result.scalars().all()
        
        return list(alerts), total
    
    async def get_unread_count(self, staff_id: int) -> int:
        """Get count of unread alerts for staff"""
        result = await self.db.execute(
            select(func.count(Alert.id))
            .where(
                and_(
                    Alert.assigned_to_staff_id == staff_id,
                    Alert.is_read == False,
                    Alert.is_dismissed == False,
                    or_(
                        Alert.expires_at.is_(None),
                        Alert.expires_at > datetime.utcnow()
                    )
                )
            )
        )
        return result.scalar() or 0
    
    async def mark_as_read(self, alert_id: int, staff_id: int) -> bool:
        """Mark alert as read"""
        result = await self.db.execute(
            update(Alert)
            .where(
                and_(
                    Alert.id == alert_id,
                    Alert.assigned_to_staff_id == staff_id
                )
            )
            .values(
                is_read=True,
                read_at=datetime.utcnow()
            )
        )
        await self.db.flush()
        return result.rowcount > 0
    
    async def mark_as_dismissed(self, alert_id: int, staff_id: int) -> bool:
        """Mark alert as dismissed"""
        result = await self.db.execute(
            update(Alert)
            .where(
                and_(
                    Alert.id == alert_id,
                    Alert.assigned_to_staff_id == staff_id
                )
            )
            .values(
                is_dismissed=True,
                dismissed_at=datetime.utcnow()
            )
        )
        await self.db.flush()
        return result.rowcount > 0
    
    async def delete_expired_alerts(self) -> int:
        """Delete expired alerts"""
        result = await self.db.execute(
            delete(Alert)
            .where(
                and_(
                    Alert.expires_at.isnot(None),
                    Alert.expires_at < datetime.utcnow()
                )
            )
        )
        await self.db.flush()
        return result.rowcount
    
    # ========================================================================
    # Alert Rule Operations
    # ========================================================================
    
    async def get_alert_rules(
        self,
        rule_type: Optional[str] = None,
        enabled_only: bool = True
    ) -> List[AlertRule]:
        """Get alert rules with optional filtering"""
        query = select(AlertRule)
        
        if enabled_only:
            query = query.where(AlertRule.is_enabled == True)
        
        if rule_type:
            query = query.where(AlertRule.rule_type == rule_type)
        
        query = query.order_by(AlertRule.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_alert_rule_by_id(self, rule_id: int) -> Optional[AlertRule]:
        """Get alert rule by ID"""
        result = await self.db.execute(
            select(AlertRule).where(AlertRule.id == rule_id)
        )
        return result.scalar_one_or_none()
    
    async def create_alert_rule(
        self,
        rule_name: str,
        rule_type: str,
        conditions: Dict[str, Any],
        alert_config: Dict[str, Any],
        created_by_staff_id: Optional[int] = None,
        is_enabled: bool = True
    ) -> AlertRule:
        """Create a new alert rule"""
        rule = AlertRule(
            rule_name=rule_name,
            rule_type=rule_type,
            conditions=conditions,
            alert_config=alert_config,
            created_by_staff_id=created_by_staff_id,
            is_enabled=is_enabled
        )
        
        self.db.add(rule)
        await self.db.flush()
        await self.db.refresh(rule)
        
        return rule
    
    async def update_alert_rule(
        self,
        rule_id: int,
        **updates
    ) -> bool:
        """Update alert rule"""
        result = await self.db.execute(
            update(AlertRule)
            .where(AlertRule.id == rule_id)
            .values(**updates)
        )
        await self.db.flush()
        return result.rowcount > 0
    
    async def delete_alert_rule(self, rule_id: int) -> bool:
        """Delete alert rule"""
        result = await self.db.execute(
            delete(AlertRule).where(AlertRule.id == rule_id)
        )
        await self.db.flush()
        return result.rowcount > 0
    
    # ========================================================================
    # Alert Subscription Operations
    # ========================================================================
    
    async def get_subscriptions_for_staff(self, staff_id: int) -> List[AlertSubscription]:
        """Get all alert subscriptions for a staff member"""
        result = await self.db.execute(
            select(AlertSubscription)
            .where(AlertSubscription.staff_id == staff_id)
            .order_by(AlertSubscription.alert_type)
        )
        return list(result.scalars().all())
    
    async def upsert_subscription(
        self,
        staff_id: int,
        alert_type: str,
        is_enabled: bool = True,
        delivery_channels: Optional[List[str]] = None
    ) -> AlertSubscription:
        """Create or update alert subscription"""
        # Try to get existing subscription
        result = await self.db.execute(
            select(AlertSubscription)
            .where(
                and_(
                    AlertSubscription.staff_id == staff_id,
                    AlertSubscription.alert_type == alert_type
                )
            )
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            # Update existing
            subscription.is_enabled = is_enabled
            if delivery_channels is not None:
                subscription.delivery_channels = delivery_channels
        else:
            # Create new
            subscription = AlertSubscription(
                staff_id=staff_id,
                alert_type=alert_type,
                is_enabled=is_enabled,
                delivery_channels=delivery_channels or ['in_app']
            )
            self.db.add(subscription)
        
        await self.db.flush()
        await self.db.refresh(subscription)
        
        return subscription


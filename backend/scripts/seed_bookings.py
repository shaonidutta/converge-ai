"""
Seed bookings and booking items
"""

from datetime import datetime, timedelta, date, time
import random
from decimal import Decimal


def generate_order_id():
    """Generate unique order ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = random.randint(1000, 9999)
    return f"ORD{timestamp}{random_suffix}{random.randint(10, 99)}"


def seed_bookings_and_items(session, users, providers, addresses, rate_cards, 
                            PaymentStatus, PaymentMethod, SettlementStatus, BookingStatus,
                            ItemPaymentStatus, ItemStatus, CancelBy,
                            Booking, BookingItem, count=150):
    """
    Seed bookings and booking items
    """
    print(f"\n6. Seeding {count} Bookings and Booking Items...")
    
    bookings = []
    booking_items = []
    
    # Filter active users and addresses
    active_users = [u for u in users if u.is_active][:100]
    active_providers = [p for p in providers if p.is_active and p.is_verified]
    active_rate_cards = [rc for rc in rate_cards if rc.is_active]
    
    for i in range(count):
        user = random.choice(active_users)
        
        # Get user addresses
        user_addresses = [a for a in addresses if a.user_id == user.id]
        if not user_addresses:
            continue
        
        # Create booking
        num_items = random.randint(1, 3)
        subtotal = Decimal('0.00')
        
        # Calculate amounts
        for _ in range(num_items):
            rate_card = random.choice(active_rate_cards)
            quantity = random.randint(1, 2)
            subtotal += rate_card.price * quantity
        
        # Apply discount
        discount = subtotal * Decimal(random.uniform(0, 0.2))
        
        # Calculate GST (18% for services in India)
        taxable_amount = subtotal - discount
        
        # Determine if intra-state or inter-state
        is_intra_state = random.random() < 0.7
        
        if is_intra_state:
            # SGST + CGST (9% each)
            sgst = Decimal('9.00')
            cgst = Decimal('9.00')
            igst = Decimal('0.00')
            sgst_amount = taxable_amount * sgst / 100
            cgst_amount = taxable_amount * cgst / 100
            igst_amount = Decimal('0.00')
        else:
            # IGST (18%)
            sgst = Decimal('0.00')
            cgst = Decimal('0.00')
            igst = Decimal('18.00')
            sgst_amount = Decimal('0.00')
            cgst_amount = Decimal('0.00')
            igst_amount = taxable_amount * igst / 100
        
        total_gst = sgst_amount + cgst_amount + igst_amount
        
        # Convenience charge
        convenience_charge = Decimal(random.uniform(10, 50))
        
        # Total
        total = taxable_amount + total_gst + convenience_charge
        
        # Partial payment
        is_partial = random.random() < 0.1
        partial_amount = total * Decimal(random.uniform(0.3, 0.5)) if is_partial else Decimal('0.00')
        remaining_amount = total - partial_amount if is_partial else Decimal('0.00')
        
        # Payment status
        payment_statuses = [PaymentStatus.PAID, PaymentStatus.PENDING, PaymentStatus.FAILED]
        payment_weights = [0.8, 0.15, 0.05]
        payment_status = random.choices(payment_statuses, weights=payment_weights)[0]
        
        # Booking status
        if payment_status == PaymentStatus.PAID:
            booking_statuses = [BookingStatus.CONFIRMED, BookingStatus.COMPLETED, BookingStatus.CANCELLED]
            status_weights = [0.3, 0.6, 0.1]
        else:
            booking_statuses = [BookingStatus.PENDING, BookingStatus.CANCELLED]
            status_weights = [0.7, 0.3]
        
        booking_status = random.choices(booking_statuses, weights=status_weights)[0]
        
        # Settlement status
        if booking_status == BookingStatus.COMPLETED:
            settlement_statuses = [SettlementStatus.COMPLETE, SettlementStatus.INPROGRESS, SettlementStatus.PENDING]
            settlement_weights = [0.7, 0.2, 0.1]
        else:
            settlement_statuses = [SettlementStatus.PENDING]
            settlement_weights = [1.0]
        
        settlement_status = random.choices(settlement_statuses, weights=settlement_weights)[0]
        
        booking = Booking(
            user_id=user.id,
            order_id=generate_order_id(),
            invoice_number=f"INV{random.randint(100000, 999999)}" if payment_status == PaymentStatus.PAID else None,
            payment_gateway_order_id=f"PG{random.randint(1000000, 9999999)}" if payment_status != PaymentStatus.PENDING else None,
            transaction_id=f"TXN{random.randint(10000000, 99999999)}" if payment_status == PaymentStatus.PAID else None,
            payment_status=payment_status,
            payment_method=random.choice([PaymentMethod.CARD, PaymentMethod.UPI, PaymentMethod.WALLET]),
            subtotal=subtotal,
            discount=discount,
            sgst=sgst,
            cgst=cgst,
            igst=igst,
            sgst_amount=sgst_amount,
            cgst_amount=cgst_amount,
            igst_amount=igst_amount,
            total_gst=total_gst,
            convenience_charge=convenience_charge,
            total=total,
            is_partial=is_partial,
            partial_amount=partial_amount,
            remaining_amount=remaining_amount,
            is_settlement=settlement_status,
            status=booking_status
        )
        session.add(booking)
        session.flush()
        bookings.append(booking)
        
        # Create booking items
        for j in range(num_items):
            rate_card = random.choice(active_rate_cards)
            address = random.choice(user_addresses)
            provider = random.choice(active_providers) if random.random() < 0.8 else None
            
            quantity = random.randint(1, 2)
            price = rate_card.price
            total_amount = price * quantity
            discount_amount = total_amount * Decimal(random.uniform(0, 0.15))
            final_amount = total_amount - discount_amount
            
            # Scheduling (next 7-30 days)
            scheduled_date = date.today() + timedelta(days=random.randint(7, 30))
            scheduled_time_from = time(hour=random.randint(8, 16), minute=random.choice([0, 30]))
            scheduled_time_to = time(hour=scheduled_time_from.hour + random.randint(1, 3), minute=scheduled_time_from.minute)
            
            # Execution times (for completed items)
            if booking_status == BookingStatus.COMPLETED:
                actual_start = datetime.combine(scheduled_date, scheduled_time_from)
                actual_end = actual_start + timedelta(hours=random.randint(1, 4))
            else:
                actual_start = None
                actual_end = None
            
            # Item status
            if booking_status == BookingStatus.COMPLETED:
                item_status = ItemStatus.COMPLETED
            elif booking_status == BookingStatus.CONFIRMED:
                item_status = random.choice([ItemStatus.PENDING, ItemStatus.ACCEPTED, ItemStatus.IN_PROGRESS])
            elif booking_status == BookingStatus.CANCELLED:
                item_status = ItemStatus.CANCELLED
            else:
                item_status = ItemStatus.PENDING
            
            # Cancellation
            if item_status == ItemStatus.CANCELLED:
                cancel_by = random.choice([CancelBy.CUSTOMER, CancelBy.PROVIDER])
                cancel_reasons = [
                    "Service not required anymore",
                    "Found alternative service",
                    "Provider unavailable",
                    "Rescheduling required",
                    "Price too high"
                ]
                cancel_reason = random.choice(cancel_reasons)
            else:
                cancel_by = CancelBy.EMPTY
                cancel_reason = None
            
            # Payment status
            if payment_status == PaymentStatus.PAID:
                item_payment_status = ItemPaymentStatus.PAID
            elif item_status == ItemStatus.CANCELLED:
                item_payment_status = ItemPaymentStatus.REFUND if payment_status == PaymentStatus.PAID else ItemPaymentStatus.UNPAID
            else:
                item_payment_status = ItemPaymentStatus.UNPAID
            
            booking_item = BookingItem(
                booking_id=booking.id,
                user_id=user.id,
                rate_card_id=rate_card.id,
                provider_id=provider.id if provider else None,
                address_id=address.id,
                service_name=rate_card.name,
                quantity=quantity,
                price=price,
                total_amount=total_amount,
                discount_amount=discount_amount,
                final_amount=final_amount,
                scheduled_date=scheduled_date,
                scheduled_time_from=scheduled_time_from,
                scheduled_time_to=scheduled_time_to,
                actual_start_time=actual_start,
                actual_end_time=actual_end,
                cancel_by=cancel_by,
                cancel_reason=cancel_reason,
                payment_status=item_payment_status,
                status=item_status
            )
            session.add(booking_item)
            booking_items.append(booking_item)
    
    session.commit()
    print(f"   ✓ Created {len(bookings)} bookings")
    print(f"   ✓ Created {len(booking_items)} booking items")
    
    return bookings, booking_items


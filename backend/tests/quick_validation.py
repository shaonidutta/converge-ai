#!/usr/bin/env python3
"""
Quick validation script for critical fixes
"""

import sys
import inspect
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '.')

def validate_booking_cancellation():
    """Validate booking cancellation fix"""
    print("=== VALIDATING BOOKING CANCELLATION FIX ===")
    
    try:
        from src.services.booking_service import BookingService
        
        # Check if cancel_booking method exists
        method = getattr(BookingService, 'cancel_booking', None)
        if not method:
            print("FAIL: cancel_booking method not found")
            return False
        
        print("PASS: cancel_booking method found")
        
        # Get method source
        source = inspect.getsource(method)
        
        # Check for required components
        checks = [
            ('Status validation', 'BookingStatus.PENDING' in source and 'BookingStatus.CONFIRMED' in source),
            ('Status update', 'BookingStatus.CANCELLED' in source),
            ('Cancellation reason', 'cancellation_reason' in source and 'request.reason' in source),
            ('Cancelled timestamp', 'cancelled_at' in source and 'datetime.now' in source),
            ('Booking items update', 'BookingItem' in source),
            ('Wallet refund', 'wallet_balance' in source and 'PaymentStatus.REFUNDED' in source),
            ('Database commit', 'await self.db.commit()' in source),
            ('Logging', 'logger.info' in source)
        ]
        
        all_passed = True
        for check_name, passed in checks:
            status = "PASS" if passed else "FAIL"
            print(f"{status}: {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("SUCCESS: Booking cancellation fix is COMPLETE")
        else:
            print("ERROR: Booking cancellation fix is INCOMPLETE")
        
        return all_passed
        
    except Exception as e:
        print(f"ERROR: Failed to validate booking cancellation: {e}")
        return False

def validate_frontend_fixes():
    """Validate frontend fixes"""
    print("\n=== VALIDATING FRONTEND FIXES ===")
    
    # Check CheckoutPage.jsx
    checkout_path = Path("../customer-frontend/src/pages/CheckoutPage.jsx")
    if checkout_path.exists():
        with open(checkout_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'syncCartToBackend' in content and 'payment_method' in content:
            print("PASS: CheckoutPage cart sync fix found")
        else:
            print("FAIL: CheckoutPage cart sync fix missing")
            return False
    else:
        print("FAIL: CheckoutPage.jsx not found")
        return False
    
    # Check AuthContext.jsx
    auth_path = Path("../customer-frontend/src/context/AuthContext.jsx")
    if auth_path.exists():
        print("PASS: AuthContext.jsx found")
    else:
        print("FAIL: AuthContext.jsx not found")
        return False
    
    # Check ProtectedRoute.jsx
    protected_path = Path("../customer-frontend/src/components/ProtectedRoute.jsx")
    if protected_path.exists():
        print("PASS: ProtectedRoute.jsx found")
    else:
        print("FAIL: ProtectedRoute.jsx not found")
        return False
    
    print("SUCCESS: Frontend fixes are COMPLETE")
    return True

def main():
    """Main validation function"""
    print("CRITICAL FIXES VALIDATION")
    print("=" * 50)
    
    backend_ok = validate_booking_cancellation()
    frontend_ok = validate_frontend_fixes()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Backend fixes: {'PASS' if backend_ok else 'FAIL'}")
    print(f"Frontend fixes: {'PASS' if frontend_ok else 'FAIL'}")
    
    if backend_ok and frontend_ok:
        print("\nALL CRITICAL FIXES VALIDATED SUCCESSFULLY!")
        print("The application should now work correctly.")
    else:
        print("\nSOME FIXES FAILED VALIDATION")
        print("Please review and fix the issues.")
    
    return backend_ok and frontend_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

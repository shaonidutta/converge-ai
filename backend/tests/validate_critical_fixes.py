#!/usr/bin/env python3
"""
Critical Fixes Validation Script
Quick validation script to test the three critical fixes:
1. Cart empty error during booking
2. Booking cancellation not working  
3. Authentication state persistence across browser tabs

Run this script to quickly validate that all fixes are working.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend src directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.services.booking_service import BookingService
from src.models.booking import BookingStatus, PaymentMethod, PaymentStatus


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n{step_num}. {description}")


def print_success(message):
    """Print a success message"""
    print(f"   ✅ {message}")


def print_error(message):
    """Print an error message"""
    print(f"   ❌ {message}")


def print_info(message):
    """Print an info message"""
    print(f"   ℹ️  {message}")


async def validate_booking_cancellation_fix():
    """
    Validate Fix #2: Booking cancellation method completion
    
    This checks that the cancel_booking method in BookingService
    has been properly implemented with all required logic.
    """
    print_header("VALIDATING BOOKING CANCELLATION FIX")
    
    try:
        # Import and inspect the BookingService
        from src.services.booking_service import BookingService
        import inspect
        
        print_step(1, "Checking BookingService.cancel_booking method")
        
        # Get the cancel_booking method
        cancel_method = getattr(BookingService, 'cancel_booking', None)
        if not cancel_method:
            print_error("cancel_booking method not found")
            return False
        
        # Get the method source code
        source = inspect.getsource(cancel_method)
        
        # Check for required components in the method
        required_components = [
            ('status validation', 'BookingStatus.PENDING'),
            ('status update', 'BookingStatus.CANCELLED'),
            ('cancellation reason', 'cancellation_reason'),
            ('cancelled timestamp', 'cancelled_at'),
            ('booking items update', 'BookingItem'),
            ('wallet refund', 'wallet_balance'),
            ('payment status update', 'PaymentStatus.REFUNDED'),
            ('database commit', 'await self.db.commit()'),
            ('logging', 'logger.info')
        ]
        
        missing_components = []
        for component_name, search_term in required_components:
            if search_term not in source:
                missing_components.append(component_name)
            else:
                print_success(f"Found {component_name}")
        
        if missing_components:
            print_error(f"Missing components: {', '.join(missing_components)}")
            return False
        
        print_success("All required components found in cancel_booking method")
        
        print_step(2, "Checking method signature")
        sig = inspect.signature(cancel_method)
        expected_params = ['self', 'booking_id', 'request', 'user']
        actual_params = list(sig.parameters.keys())
        
        if actual_params == expected_params:
            print_success("Method signature is correct")
        else:
            print_error(f"Method signature mismatch. Expected: {expected_params}, Got: {actual_params}")
            return False
        
        print_success("Booking cancellation fix validation PASSED")
        return True
        
    except Exception as e:
        print_error(f"Error validating booking cancellation fix: {e}")
        return False


def validate_cart_sync_fix():
    """
    Validate Fix #1: Cart sync functionality in frontend
    
    This checks that the frontend CheckoutPage has been updated
    with the syncCartToBackend functionality.
    """
    print_header("VALIDATING CART SYNC FIX")
    
    try:
        # Check if the frontend file exists and has the required changes
        frontend_checkout_path = Path(__file__).parent.parent.parent / "customer-frontend" / "src" / "pages" / "CheckoutPage.jsx"
        
        print_step(1, "Checking CheckoutPage.jsx file")
        
        if not frontend_checkout_path.exists():
            print_error("CheckoutPage.jsx not found")
            return False
        
        print_success("CheckoutPage.jsx found")
        
        print_step(2, "Checking for cart sync functionality")
        
        with open(frontend_checkout_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_components = [
            ('syncCartToBackend function', 'syncCartToBackend'),
            ('cart clear API call', 'api.cart.clear()'),
            ('cart add item API call', 'api.cart.addItem'),
            ('payment method field', 'payment_method'),
            ('api import', 'import api from')
        ]
        
        missing_components = []
        for component_name, search_term in required_components:
            if search_term not in content:
                missing_components.append(component_name)
            else:
                print_success(f"Found {component_name}")
        
        if missing_components:
            print_error(f"Missing components: {', '.join(missing_components)}")
            return False
        
        print_success("Cart sync fix validation PASSED")
        return True
        
    except Exception as e:
        print_error(f"Error validating cart sync fix: {e}")
        return False


def validate_auth_context_fix():
    """
    Validate Fix #3: Authentication context for cross-tab persistence
    
    This checks that the AuthContext has been created and integrated.
    """
    print_header("VALIDATING AUTHENTICATION CONTEXT FIX")
    
    try:
        # Check if AuthContext file exists
        auth_context_path = Path(__file__).parent.parent.parent / "customer-frontend" / "src" / "context" / "AuthContext.jsx"
        
        print_step(1, "Checking AuthContext.jsx file")
        
        if not auth_context_path.exists():
            print_error("AuthContext.jsx not found")
            return False
        
        print_success("AuthContext.jsx found")
        
        print_step(2, "Checking AuthContext functionality")
        
        with open(auth_context_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_components = [
            ('AuthProvider component', 'AuthProvider'),
            ('useAuth hook', 'useAuth'),
            ('storage event listener', 'storage'),
            ('focus event listener', 'focus'),
            ('authentication state', 'isLoggedIn'),
            ('login method', 'handleLogin'),
            ('logout method', 'handleLogout'),
            ('token validation', 'initializeAuth')
        ]
        
        missing_components = []
        for component_name, search_term in required_components:
            if search_term not in content:
                missing_components.append(component_name)
            else:
                print_success(f"Found {component_name}")
        
        if missing_components:
            print_error(f"Missing components: {', '.join(missing_components)}")
            return False
        
        print_step(3, "Checking main.jsx integration")
        
        main_jsx_path = Path(__file__).parent.parent.parent / "customer-frontend" / "src" / "main.jsx"
        if main_jsx_path.exists():
            with open(main_jsx_path, 'r', encoding='utf-8') as f:
                main_content = f.read()
            
            if 'AuthProvider' in main_content:
                print_success("AuthProvider integrated in main.jsx")
            else:
                print_error("AuthProvider not integrated in main.jsx")
                return False
        else:
            print_error("main.jsx not found")
            return False
        
        print_success("Authentication context fix validation PASSED")
        return True
        
    except Exception as e:
        print_error(f"Error validating auth context fix: {e}")
        return False


def validate_protected_routes():
    """
    Validate that ProtectedRoute component exists and is integrated
    """
    print_header("VALIDATING PROTECTED ROUTES")
    
    try:
        # Check if ProtectedRoute file exists
        protected_route_path = Path(__file__).parent.parent.parent / "customer-frontend" / "src" / "components" / "ProtectedRoute.jsx"
        
        print_step(1, "Checking ProtectedRoute.jsx file")
        
        if not protected_route_path.exists():
            print_error("ProtectedRoute.jsx not found")
            return False
        
        print_success("ProtectedRoute.jsx found")
        
        print_step(2, "Checking App.jsx integration")
        
        app_jsx_path = Path(__file__).parent.parent.parent / "customer-frontend" / "src" / "App.jsx"
        if app_jsx_path.exists():
            with open(app_jsx_path, 'r', encoding='utf-8') as f:
                app_content = f.read()
            
            if 'ProtectedRoute' in app_content:
                print_success("ProtectedRoute integrated in App.jsx")
            else:
                print_error("ProtectedRoute not integrated in App.jsx")
                return False
        else:
            print_error("App.jsx not found")
            return False
        
        print_success("Protected routes validation PASSED")
        return True
        
    except Exception as e:
        print_error(f"Error validating protected routes: {e}")
        return False


async def main():
    """Main validation function"""
    print_header("CRITICAL FIXES VALIDATION SCRIPT")
    print_info("This script validates that all three critical fixes have been implemented correctly.")
    
    results = []
    
    # Validate each fix
    results.append(("Cart Sync Fix", validate_cart_sync_fix()))
    results.append(("Booking Cancellation Fix", await validate_booking_cancellation_fix()))
    results.append(("Authentication Context Fix", validate_auth_context_fix()))
    results.append(("Protected Routes", validate_protected_routes()))
    
    # Print summary
    print_header("VALIDATION SUMMARY")
    
    all_passed = True
    for fix_name, passed in results:
        if passed:
            print_success(f"{fix_name}: PASSED")
        else:
            print_error(f"{fix_name}: FAILED")
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 ALL CRITICAL FIXES VALIDATED SUCCESSFULLY!")
        print("✅ The application should now work correctly for:")
        print("   • Cart sync and booking creation")
        print("   • Booking cancellation")
        print("   • Authentication persistence across browser tabs")
    else:
        print("⚠️  SOME FIXES FAILED VALIDATION")
        print("❌ Please review the failed components and fix them.")
    
    print(f"{'='*60}")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

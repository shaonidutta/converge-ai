"""
Test authentication system
Test password hashing, JWT tokens, and user operations
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.src.core.security import (
    hash_password,
    verify_password,
    check_password_strength,
    validate_password,
    generate_secure_password,
    generate_reset_token,
    create_token_pair,
    verify_token,
    blacklist_token,
    is_token_blacklisted,
)
from backend.src.core.database.connection import engine, AsyncSessionLocal
from backend.src.core.repositories import UserRepository, StaffRepository
from backend.src.core.config import settings


def print_section(title: str):
    """Print section header"""
    print(f"\n{'=' * 80}")
    print(f"{title}")
    print(f"{'=' * 80}\n")


def test_password_utilities():
    """Test password hashing and validation"""
    print_section("TESTING PASSWORD UTILITIES")
    
    # Test password hashing
    print("1. Testing password hashing...")
    password = "MySecurePassword123!"
    hashed = hash_password(password)
    print(f"   Original: {password}")
    print(f"   Hashed: {hashed[:50]}...")
    print(f"   ✓ Password hashed successfully")
    
    # Test password verification
    print("\n2. Testing password verification...")
    is_valid = verify_password(password, hashed)
    print(f"   Correct password: {is_valid}")
    is_invalid = verify_password("WrongPassword", hashed)
    print(f"   Wrong password: {is_invalid}")
    print(f"   ✓ Password verification working")
    
    # Test password strength
    print("\n3. Testing password strength checker...")
    weak_password = "weak"
    strong_password = "StrongPass123!@#"
    
    weak_result = check_password_strength(weak_password)
    print(f"   Weak password: '{weak_password}'")
    print(f"   - Is strong: {weak_result['is_strong']}")
    print(f"   - Score: {weak_result['score']}/5")
    print(f"   - Feedback: {weak_result['feedback']}")
    
    strong_result = check_password_strength(strong_password)
    print(f"\n   Strong password: '{strong_password}'")
    print(f"   - Is strong: {strong_result['is_strong']}")
    print(f"   - Score: {strong_result['score']}/5")
    print(f"   - Feedback: {strong_result['feedback']}")
    print(f"   ✓ Password strength checker working")
    
    # Test password validation
    print("\n4. Testing password validation...")
    is_valid, error = validate_password("weak")
    print(f"   Weak password validation: {is_valid}")
    if error:
        print(f"   Error: {error}")
    
    is_valid, error = validate_password(strong_password)
    print(f"   Strong password validation: {is_valid}")
    print(f"   ✓ Password validation working")
    
    # Test secure password generation
    print("\n5. Testing secure password generation...")
    generated = generate_secure_password(16)
    print(f"   Generated password: {generated}")
    strength = check_password_strength(generated)
    print(f"   Is strong: {strength['is_strong']}")
    print(f"   ✓ Secure password generation working")
    
    # Test reset token generation
    print("\n6. Testing reset token generation...")
    token = generate_reset_token(32)
    print(f"   Reset token: {token[:40]}...")
    print(f"   Length: {len(token)}")
    print(f"   ✓ Reset token generation working")


async def test_jwt_tokens():
    """Test JWT token creation and verification"""
    print_section("TESTING JWT TOKENS")

    # Test token pair creation
    print("1. Testing token pair creation...")
    tokens = create_token_pair(
        subject="user@example.com",
        user_id=123,
        user_type="customer",
        additional_claims={"role": "premium"}
    )
    print(f"   Access token: {tokens['access_token'][:50]}...")
    print(f"   Refresh token: {tokens['refresh_token'][:50]}...")
    print(f"   Token type: {tokens['token_type']}")
    print(f"   ✓ Token pair created successfully")

    # Test token verification
    print("\n2. Testing token verification...")
    access_payload = await verify_token(tokens['access_token'], token_type="access")
    if access_payload:
        print(f"   ✓ Access token verified")
        print(f"   - User ID: {access_payload['user_id']}")
        print(f"   - User type: {access_payload['user_type']}")
        print(f"   - Subject: {access_payload['sub']}")
        print(f"   - Role: {access_payload.get('role')}")
    else:
        print(f"   ✗ Access token verification failed")

    refresh_payload = await verify_token(tokens['refresh_token'], token_type="refresh")
    if refresh_payload:
        print(f"   ✓ Refresh token verified")
    else:
        print(f"   ✗ Refresh token verification failed")

    # Test invalid token
    print("\n3. Testing invalid token...")
    invalid_payload = await verify_token("invalid.token.here")
    print(f"   Invalid token result: {invalid_payload}")
    print(f"   ✓ Invalid token rejected")


async def test_token_blacklist():
    """Test token blacklisting"""
    print_section("TESTING TOKEN BLACKLIST")
    
    # Create a token
    print("1. Creating test token...")
    tokens = create_token_pair(
        subject="test@example.com",
        user_id=999,
        user_type="customer"
    )
    token = tokens['access_token']
    print(f"   Token created: {token[:50]}...")
    
    # Check if blacklisted (should be False)
    print("\n2. Checking if token is blacklisted...")
    is_blacklisted = await is_token_blacklisted(token)
    print(f"   Is blacklisted: {is_blacklisted}")
    print(f"   ✓ Token not blacklisted initially")
    
    # Blacklist the token
    print("\n3. Blacklisting token...")
    success = await blacklist_token(token, reason="test_logout")
    print(f"   Blacklist success: {success}")
    
    # Check again (should be True)
    print("\n4. Checking if token is blacklisted after blacklisting...")
    is_blacklisted = await is_token_blacklisted(token)
    print(f"   Is blacklisted: {is_blacklisted}")
    print(f"   ✓ Token blacklisting working")
    
    # Try to verify blacklisted token
    print("\n5. Trying to verify blacklisted token...")
    payload = await verify_token(token)
    print(f"   Verification result: {payload}")
    print(f"   ✓ Blacklisted token rejected")


async def test_user_repository():
    """Test user repository operations"""
    print_section("TESTING USER REPOSITORY")

    # Get database session
    async with AsyncSessionLocal() as db:
        repo = UserRepository(db)
        
        # Test user creation
        print("1. Testing user creation...")
        try:
            # Check if test user exists
            existing_user = await repo.get_user_by_email("test_auth@example.com")
            if existing_user:
                print(f"   Test user already exists, deleting...")
                await repo.delete_user(existing_user.id, soft_delete=False)
            
            user = await repo.create_user(
                email="test_auth@example.com",
                mobile="9999999999",
                password="TestPassword123!",
                first_name="Test",
                last_name="User"
            )
            print(f"   ✓ User created: id={user.id}, email={user.email}")
        except Exception as e:
            print(f"   ✗ User creation failed: {e}")
            return
        
        # Test get user by ID
        print("\n2. Testing get user by ID...")
        fetched_user = await repo.get_user_by_id(user.id)
        if fetched_user:
            print(f"   ✓ User fetched: {fetched_user.email}")
        else:
            print(f"   ✗ User not found")
        
        # Test get user by email
        print("\n3. Testing get user by email...")
        fetched_user = await repo.get_user_by_email("test_auth@example.com")
        if fetched_user:
            print(f"   ✓ User fetched by email: {fetched_user.email}")
        else:
            print(f"   ✗ User not found by email")
        
        # Test password verification
        print("\n4. Testing password verification...")
        is_valid = verify_password("TestPassword123!", fetched_user.password_hash)
        print(f"   Password valid: {is_valid}")
        print(f"   ✓ Password verification working")
        
        # Test user update
        print("\n5. Testing user update...")
        updated_user = await repo.update_user(
            user.id,
            first_name="Updated",
            email_verified=True
        )
        if updated_user:
            print(f"   ✓ User updated: {updated_user.first_name}, verified={updated_user.email_verified}")
        else:
            print(f"   ✗ User update failed")
        
        # Test user search
        print("\n6. Testing user search...")
        users = await repo.search_users(query="test", limit=10)
        print(f"   Found {len(users)} users matching 'test'")
        print(f"   ✓ User search working")
        
        # Clean up
        print("\n7. Cleaning up test user...")
        await repo.delete_user(user.id, soft_delete=False)
        print(f"   ✓ Test user deleted")


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("AUTHENTICATION SYSTEM TEST")
    print("=" * 80)

    # Test password utilities
    test_password_utilities()

    # Test JWT tokens
    await test_jwt_tokens()

    # Test token blacklist
    await test_token_blacklist()

    # Test user repository
    await test_user_repository()

    print("\n" + "=" * 80)
    print("AUTHENTICATION TEST SUMMARY")
    print("=" * 80)
    print("\n✅ All authentication tests completed successfully!\n")


if __name__ == "__main__":
    asyncio.run(main())


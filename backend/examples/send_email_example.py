"""
Email Sending Example

This script demonstrates how to use the email service to send emails
using Resend API.

Usage:
    python examples/send_email_example.py
"""

import asyncio
import sys
import os

# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.email import send_email
from src.utils.email_templates import (
    get_welcome_email_template,
    get_booking_confirmation_template,
    get_password_reset_template,
)


async def send_welcome_email_example():
    """Example: Send a welcome email to a new user."""
    print("\nSending welcome email...")

    # Get the email template
    template = get_welcome_email_template(
        user_name="John Doe",
        user_email="john.doe@example.com"
    )

    # Send the email
    result = await send_email(
        to=["john.doe@example.com"],
        subject=template["subject"],
        html_content=template["html"],
        text_content=template["text"],
    )

    if result["success"]:
        print(f"Welcome email sent successfully!")
        print(f"   Email ID: {result.get('email_id')}")
    else:
        print(f"Failed to send welcome email: {result['message']}")

    return result


async def send_booking_confirmation_example():
    """Example: Send a booking confirmation email."""
    print("\nSending booking confirmation email...")

    # Get the email template
    template = get_booking_confirmation_template(
        user_name="Jane Smith",
        booking_id="BK-2025-001",
        service_name="Home Cleaning Service",
        booking_date="January 15, 2025",
        booking_time="10:00 AM - 12:00 PM",
    )

    # Send the email
    result = await send_email(
        to=["jane.smith@example.com"],
        subject=template["subject"],
        html_content=template["html"],
        text_content=template["text"],
    )

    if result["success"]:
        print(f"Booking confirmation sent successfully!")
        print(f"   Email ID: {result.get('email_id')}")
    else:
        print(f"Failed to send booking confirmation: {result['message']}")

    return result


async def send_password_reset_example():
    """Example: Send a password reset email."""
    print("\nSending password reset email...")

    # Generate a mock reset token (in production, this would be a secure token)
    reset_token = "abc123def456ghi789"

    # Get the email template
    template = get_password_reset_template(
        user_name="Bob Johnson",
        reset_token=reset_token,
    )

    # Send the email
    result = await send_email(
        to=["bob.johnson@example.com"],
        subject=template["subject"],
        html_content=template["html"],
        text_content=template["text"],
    )

    if result["success"]:
        print(f"Password reset email sent successfully!")
        print(f"   Email ID: {result.get('email_id')}")
    else:
        print(f"Failed to send password reset email: {result['message']}")

    return result


async def send_simple_email_example():
    """Example: Send a simple plain text email."""
    print("\nSending simple email...")

    result = await send_email(
        to=["test@example.com"],
        subject="Test Email from ConvergeAI",
        text_content="This is a test email from ConvergeAI backend.",
        html_content="<h1>Test Email</h1><p>This is a test email from ConvergeAI backend.</p>",
    )

    if result["success"]:
        print(f"Simple email sent successfully!")
        print(f"   Email ID: {result.get('email_id')}")
    else:
        print(f"Failed to send simple email: {result['message']}")

    return result


async def main():
    """Run all email examples."""
    print("=" * 60)
    print("ConvergeAI Email Service Examples")
    print("=" * 60)

    # Check if Resend API key is configured
    resend_api_key = os.getenv("RESEND_API_KEY")
    if not resend_api_key:
        print("\nWARNING: RESEND_API_KEY not found in environment variables!")
        print("   Please set RESEND_API_KEY in your .env file to send emails.")
        print("\n   Example:")
        print("   RESEND_API_KEY=re_your_api_key_here")
        print("   OUTREACH_FROM=noreply@yourdomain.com")
        print("   OUTREACH_EMAIL_ENABLED=true")
        return

    print(f"\nResend API key found: {resend_api_key[:10]}...")
    
    # Run examples
    try:
        # Example 1: Welcome email
        await send_welcome_email_example()
        
        # Example 2: Booking confirmation
        await send_booking_confirmation_example()
        
        # Example 3: Password reset
        await send_password_reset_example()
        
        # Example 4: Simple email
        await send_simple_email_example()
        
        print("\n" + "=" * 60)
        print("All email examples completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the examples
    asyncio.run(main())


"""
Email Templates Module

This module provides pre-built email templates for common use cases.
"""

from typing import Dict, Any


def get_welcome_email_template(user_name: str, user_email: str) -> Dict[str, str]:
    """
    Get welcome email template for new users.
    
    Args:
        user_name: Name of the user
        user_email: Email of the user
        
    Returns:
        Dict with 'subject', 'html', and 'text' keys
    """
    subject = f"Welcome to ConvergeAI, {user_name}!"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 10px 10px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to ConvergeAI!</h1>
            </div>
            <div class="content">
                <p>Hi {user_name},</p>

                <p>Thank you for joining ConvergeAI! We're excited to have you on board.</p>

                <p>ConvergeAI is your intelligent customer service platform powered by advanced AI agents.
                Our multi-agent system is designed to handle all your customer service needs efficiently.</p>

                <h3>What you can do with ConvergeAI:</h3>
                <ul>
                    <li>Book services instantly</li>
                    <li>Cancel or modify bookings</li>
                    <li>File and track complaints</li>
                    <li>Get instant policy information</li>
                    <li>Chat with intelligent AI agents</li>
                </ul>
                
                <p>Get started by exploring our platform:</p>
                
                <a href="http://localhost:3000" class="button">Go to Dashboard</a>
                
                <p>If you have any questions, our AI agents are here to help 24/7!</p>
                
                <p>Best regards,<br>The ConvergeAI Team</p>
            </div>
            <div class="footer">
                <p>© 2025 ConvergeAI. All rights reserved.</p>
                <p>You received this email because you signed up for ConvergeAI.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text = f"""
    Welcome to ConvergeAI, {user_name}!
    
    Thank you for joining ConvergeAI! We're excited to have you on board.
    
    ConvergeAI is your intelligent customer service platform powered by advanced AI agents.
    
    What you can do with ConvergeAI:
    - Book services instantly
    - Cancel or modify bookings
    - File and track complaints
    - Get instant policy information
    - Chat with intelligent AI agents
    
    Get started: http://localhost:3000
    
    If you have any questions, our AI agents are here to help 24/7!
    
    Best regards,
    The ConvergeAI Team
    
    © 2025 ConvergeAI. All rights reserved.
    """
    
    return {
        "subject": subject,
        "html": html,
        "text": text,
    }


def get_booking_confirmation_template(
    user_name: str,
    booking_id: str,
    service_name: str,
    booking_date: str,
    booking_time: str,
) -> Dict[str, str]:
    """
    Get booking confirmation email template.
    
    Args:
        user_name: Name of the user
        booking_id: Booking ID
        service_name: Name of the service
        booking_date: Date of booking
        booking_time: Time of booking
        
    Returns:
        Dict with 'subject', 'html', and 'text' keys
    """
    subject = f"Booking Confirmed - {service_name}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: #10b981;
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 10px 10px;
            }}
            .booking-details {{
                background: white;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .detail-row {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: #10b981;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Booking Confirmed!</h1>
            </div>
            <div class="content">
                <p>Hi {user_name},</p>
                
                <p>Your booking has been confirmed. Here are the details:</p>
                
                <div class="booking-details">
                    <div class="detail-row">
                        <strong>Booking ID:</strong>
                        <span>{booking_id}</span>
                    </div>
                    <div class="detail-row">
                        <strong>Service:</strong>
                        <span>{service_name}</span>
                    </div>
                    <div class="detail-row">
                        <strong>Date:</strong>
                        <span>{booking_date}</span>
                    </div>
                    <div class="detail-row">
                        <strong>Time:</strong>
                        <span>{booking_time}</span>
                    </div>
                </div>
                
                <p>We'll send you a reminder 24 hours before your appointment.</p>
                
                <a href="http://localhost:3000/bookings/{booking_id}" class="button">View Booking</a>
                
                <p>Need to make changes? You can modify or cancel your booking anytime.</p>
                
                <p>Best regards,<br>The ConvergeAI Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text = f"""
    Booking Confirmed!
    
    Hi {user_name},
    
    Your booking has been confirmed. Here are the details:
    
    Booking ID: {booking_id}
    Service: {service_name}
    Date: {booking_date}
    Time: {booking_time}
    
    We'll send you a reminder 24 hours before your appointment.
    
    View your booking: http://localhost:3000/bookings/{booking_id}
    
    Need to make changes? You can modify or cancel your booking anytime.
    
    Best regards,
    The ConvergeAI Team
    """
    
    return {
        "subject": subject,
        "html": html,
        "text": text,
    }


def get_password_reset_template(user_name: str, reset_token: str) -> Dict[str, str]:
    """
    Get password reset email template.
    
    Args:
        user_name: Name of the user
        reset_token: Password reset token
        
    Returns:
        Dict with 'subject', 'html', and 'text' keys
    """
    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
    
    subject = "Reset Your ConvergeAI Password"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: #ef4444;
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 10px 10px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: #ef4444;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .warning {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 15px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <p>Hi {user_name},</p>

                <p>We received a request to reset your ConvergeAI password.</p>

                <p>Click the button below to reset your password:</p>

                <a href="{reset_link}" class="button">Reset Password</a>

                <div class="warning">
                    <strong>Security Notice:</strong><br>
                    This link will expire in 1 hour. If you didn't request this reset,
                    please ignore this email and your password will remain unchanged.
                </div>
                
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{reset_link}</p>
                
                <p>Best regards,<br>The ConvergeAI Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text = f"""
    Password Reset Request
    
    Hi {user_name},
    
    We received a request to reset your ConvergeAI password.
    
    Click this link to reset your password:
    {reset_link}
    
    ⚠️ Security Notice:
    This link will expire in 1 hour. If you didn't request this reset, 
    please ignore this email and your password will remain unchanged.
    
    Best regards,
    The ConvergeAI Team
    """
    
    return {
        "subject": subject,
        "html": html,
        "text": text,
    }


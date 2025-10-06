"""
Email Utility Module

This module provides email sending functionality using Resend API
and traditional SMTP as fallback.
"""

import os
from typing import List, Optional, Dict, Any
from enum import Enum

import resend
from loguru import logger


class EmailProvider(str, Enum):
    """Email provider types."""
    RESEND = "resend"
    SMTP = "smtp"


class EmailService:
    """
    Email service for sending emails via Resend API or SMTP.
    
    Attributes:
        provider: Email provider to use (resend or smtp)
        resend_api_key: Resend API key
        from_email: Default sender email address
        max_contacts: Maximum number of contacts per email
        enabled: Whether email sending is enabled
    """
    
    def __init__(
        self,
        provider: EmailProvider = EmailProvider.RESEND,
        resend_api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        max_contacts: int = 1,
        enabled: bool = True,
    ):
        """
        Initialize email service.
        
        Args:
            provider: Email provider to use
            resend_api_key: Resend API key (if using Resend)
            from_email: Default sender email address
            max_contacts: Maximum number of contacts per email
            enabled: Whether email sending is enabled
        """
        self.provider = provider
        self.enabled = enabled
        self.max_contacts = max_contacts
        self.from_email = from_email or os.getenv("OUTREACH_FROM", "noreply@convergeai.com")
        
        # Initialize Resend if using Resend provider
        if self.provider == EmailProvider.RESEND:
            self.resend_api_key = resend_api_key or os.getenv("RESEND_API_KEY")
            if self.resend_api_key:
                resend.api_key = self.resend_api_key
            else:
                logger.warning("Resend API key not provided. Email sending will be disabled.")
                self.enabled = False
    
    async def send_email(
        self,
        to: List[str],
        subject: str,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Send an email.
        
        Args:
            to: List of recipient email addresses
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content of the email
            from_email: Sender email address (overrides default)
            reply_to: Reply-to email address
            cc: List of CC email addresses
            bcc: List of BCC email addresses
            attachments: List of attachments
            
        Returns:
            Dict containing send result with 'success' and 'message' keys
            
        Raises:
            ValueError: If email sending is disabled or invalid parameters
        """
        if not self.enabled:
            logger.warning("Email sending is disabled")
            return {
                "success": False,
                "message": "Email sending is disabled",
            }
        
        # Validate recipients
        if not to or len(to) == 0:
            raise ValueError("At least one recipient email is required")
        
        if len(to) > self.max_contacts:
            raise ValueError(f"Maximum {self.max_contacts} recipients allowed per email")
        
        # Validate content
        if not html_content and not text_content:
            raise ValueError("Either html_content or text_content must be provided")
        
        sender = from_email or self.from_email
        
        try:
            if self.provider == EmailProvider.RESEND:
                return await self._send_via_resend(
                    to=to,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    from_email=sender,
                    reply_to=reply_to,
                    cc=cc,
                    bcc=bcc,
                    attachments=attachments,
                )
            elif self.provider == EmailProvider.SMTP:
                return await self._send_via_smtp(
                    to=to,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    from_email=sender,
                    reply_to=reply_to,
                    cc=cc,
                    bcc=bcc,
                    attachments=attachments,
                )
            else:
                raise ValueError(f"Unsupported email provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}",
                "error": str(e),
            }
    
    async def _send_via_resend(
        self,
        to: List[str],
        subject: str,
        html_content: Optional[str],
        text_content: Optional[str],
        from_email: str,
        reply_to: Optional[str],
        cc: Optional[List[str]],
        bcc: Optional[List[str]],
        attachments: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """
        Send email via Resend API.
        
        Args:
            Same as send_email method
            
        Returns:
            Dict containing send result
        """
        try:
            # Prepare email parameters
            params = {
                "from": from_email,
                "to": to,
                "subject": subject,
            }
            
            # Add content
            if html_content:
                params["html"] = html_content
            if text_content:
                params["text"] = text_content
            
            # Add optional fields
            if reply_to:
                params["reply_to"] = reply_to
            if cc:
                params["cc"] = cc
            if bcc:
                params["bcc"] = bcc
            if attachments:
                params["attachments"] = attachments
            
            # Send email
            response = resend.Emails.send(params)
            
            logger.info(f"Email sent successfully via Resend to {to}")
            
            return {
                "success": True,
                "message": "Email sent successfully",
                "provider": "resend",
                "email_id": response.get("id"),
                "response": response,
            }
            
        except Exception as e:
            logger.error(f"Resend API error: {str(e)}")
            raise
    
    async def _send_via_smtp(
        self,
        to: List[str],
        subject: str,
        html_content: Optional[str],
        text_content: Optional[str],
        from_email: str,
        reply_to: Optional[str],
        cc: Optional[List[str]],
        bcc: Optional[List[str]],
        attachments: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """
        Send email via SMTP.
        
        Args:
            Same as send_email method
            
        Returns:
            Dict containing send result
        """
        # TODO: Implement SMTP sending using emails library
        # This will be implemented when SMTP configuration is needed
        raise NotImplementedError("SMTP email sending not yet implemented")


# Global email service instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """
    Get or create the global email service instance.
    
    Returns:
        EmailService instance
    """
    global _email_service
    
    if _email_service is None:
        # Get configuration from environment
        enabled = os.getenv("OUTREACH_EMAIL_ENABLED", "true").lower() == "true"
        resend_api_key = os.getenv("RESEND_API_KEY")
        from_email = os.getenv("OUTREACH_FROM")
        max_contacts = int(os.getenv("OUTREACH_MAX_CONTACTS", "1"))
        
        _email_service = EmailService(
            provider=EmailProvider.RESEND,
            resend_api_key=resend_api_key,
            from_email=from_email,
            max_contacts=max_contacts,
            enabled=enabled,
        )
    
    return _email_service


async def send_email(
    to: List[str],
    subject: str,
    html_content: Optional[str] = None,
    text_content: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Convenience function to send an email using the global email service.
    
    Args:
        to: List of recipient email addresses
        subject: Email subject
        html_content: HTML content of the email
        text_content: Plain text content of the email
        **kwargs: Additional parameters passed to EmailService.send_email
        
    Returns:
        Dict containing send result
    """
    email_service = get_email_service()
    return await email_service.send_email(
        to=to,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        **kwargs,
    )


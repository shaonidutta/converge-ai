# Email Configuration Guide

This guide explains how to configure and use the email service in ConvergeAI backend.

## Overview

ConvergeAI supports two email providers:
1. **Resend API** (Recommended) - Modern, developer-friendly email API
2. **SMTP** (Traditional) - Standard SMTP protocol

## Quick Start with Resend

### 1. Get Resend API Key

1. Sign up at [resend.com](https://resend.com)
2. Verify your domain (or use their test domain for development)
3. Get your API key from the dashboard

### 2. Configure Environment Variables

Add these to your `.env` file:

```bash
# Resend Configuration
OUTREACH_EMAIL_ENABLED=true
RESEND_API_KEY=re_your_api_key_here
OUTREACH_FROM=noreply@yourdomain.com
OUTREACH_MAX_CONTACTS=1
```

### 3. Test Email Sending

Run the example script:

```bash
python examples/send_email_example.py
```

## Environment Variables

### Resend Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OUTREACH_EMAIL_ENABLED` | Enable/disable email sending | No | `true` |
| `RESEND_API_KEY` | Your Resend API key | Yes | - |
| `OUTREACH_FROM` | Default sender email address | Yes | `noreply@convergeai.com` |
| `OUTREACH_MAX_CONTACTS` | Max recipients per email | No | `1` |

### SMTP Configuration (Alternative)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SMTP_HOST` | SMTP server hostname | Yes | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | Yes | `587` |
| `EMAIL_USERNAME` | SMTP username | Yes | - |
| `EMAIL_PASSWORD` | SMTP password | Yes | - |

## Usage Examples

### Basic Email Sending

```python
from src.utils.email import send_email

# Send a simple email
result = await send_email(
    to=["user@example.com"],
    subject="Hello from ConvergeAI",
    html_content="<h1>Hello!</h1><p>This is a test email.</p>",
    text_content="Hello! This is a test email.",
)

if result["success"]:
    print(f"Email sent! ID: {result['email_id']}")
else:
    print(f"Failed: {result['message']}")
```

### Using Email Templates

```python
from src.utils.email import send_email
from src.utils.email_templates import get_welcome_email_template

# Get a pre-built template
template = get_welcome_email_template(
    user_name="John Doe",
    user_email="john@example.com"
)

# Send the email
result = await send_email(
    to=["john@example.com"],
    subject=template["subject"],
    html_content=template["html"],
    text_content=template["text"],
)
```

### Advanced Options

```python
from src.utils.email import send_email

result = await send_email(
    to=["user@example.com"],
    subject="Important Update",
    html_content="<p>Your booking is confirmed!</p>",
    text_content="Your booking is confirmed!",
    from_email="bookings@convergeai.com",  # Override default sender
    reply_to="support@convergeai.com",     # Set reply-to address
    cc=["manager@convergeai.com"],         # CC recipients
    bcc=["archive@convergeai.com"],        # BCC recipients
)
```

## Available Email Templates

### 1. Welcome Email

```python
from src.utils.email_templates import get_welcome_email_template

template = get_welcome_email_template(
    user_name="John Doe",
    user_email="john@example.com"
)
```

### 2. Booking Confirmation

```python
from src.utils.email_templates import get_booking_confirmation_template

template = get_booking_confirmation_template(
    user_name="Jane Smith",
    booking_id="BK-2025-001",
    service_name="Home Cleaning",
    booking_date="January 15, 2025",
    booking_time="10:00 AM - 12:00 PM",
)
```

### 3. Password Reset

```python
from src.utils.email_templates import get_password_reset_template

template = get_password_reset_template(
    user_name="Bob Johnson",
    reset_token="abc123def456",
)
```

## Creating Custom Templates

Create a new template function in `src/utils/email_templates.py`:

```python
def get_custom_template(param1: str, param2: str) -> Dict[str, str]:
    """
    Get custom email template.
    
    Args:
        param1: First parameter
        param2: Second parameter
        
    Returns:
        Dict with 'subject', 'html', and 'text' keys
    """
    subject = f"Custom Email - {param1}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Custom Email</h1>
        <p>Parameter 1: {param1}</p>
        <p>Parameter 2: {param2}</p>
    </body>
    </html>
    """
    
    text = f"""
    Custom Email
    
    Parameter 1: {param1}
    Parameter 2: {param2}
    """
    
    return {
        "subject": subject,
        "html": html,
        "text": text,
    }
```

## Email Template Best Practices

1. **Always provide both HTML and text versions**
   - Some email clients don't support HTML
   - Text version is used as fallback

2. **Use inline CSS for HTML emails**
   - Many email clients strip `<style>` tags
   - Inline styles are more reliable

3. **Keep it simple**
   - Avoid complex layouts
   - Use tables for layout (yes, really!)
   - Test in multiple email clients

4. **Include unsubscribe links** (for marketing emails)
   - Required by law in many countries
   - Good practice for user experience

5. **Optimize images**
   - Use absolute URLs for images
   - Provide alt text
   - Keep file sizes small

## Security Best Practices

1. **Never commit API keys**
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Validate email addresses**
   - Use email-validator library
   - Check for disposable email domains

3. **Rate limiting**
   - Respect Resend's rate limits
   - Implement your own rate limiting

4. **Monitor for abuse**
   - Track email sending patterns
   - Alert on unusual activity

## Troubleshooting

### Email not sending

1. **Check API key**
   ```bash
   echo $RESEND_API_KEY
   ```

2. **Check email is enabled**
   ```bash
   echo $OUTREACH_EMAIL_ENABLED
   ```

3. **Check logs**
   ```bash
   tail -f logs/app.log
   ```

### Domain not verified

- Resend requires domain verification for production
- Use their test domain for development: `onboarding@resend.dev`

### Rate limit exceeded

- Resend free tier: 100 emails/day
- Implement queuing for high-volume sending
- Consider upgrading plan

## Monitoring

### Track Email Metrics

```python
from src.utils.email import send_email

result = await send_email(...)

# Log the result
if result["success"]:
    logger.info(f"Email sent: {result['email_id']}")
    # Track in analytics
    analytics.track("email_sent", {
        "email_id": result["email_id"],
        "recipient": to[0],
        "template": "welcome",
    })
```

### Resend Dashboard

- View sent emails
- Check delivery status
- Monitor bounce rates
- Track open rates (if enabled)

## Production Checklist

- [ ] Domain verified in Resend
- [ ] API key stored securely
- [ ] Email templates tested
- [ ] Rate limiting implemented
- [ ] Error handling in place
- [ ] Monitoring configured
- [ ] Unsubscribe links added (if applicable)
- [ ] GDPR compliance checked
- [ ] Backup email provider configured

## Additional Resources

- [Resend Documentation](https://resend.com/docs)
- [Email Best Practices](https://www.campaignmonitor.com/resources/guides/email-marketing-best-practices/)
- [HTML Email Guide](https://www.campaignmonitor.com/css/)

## Support

For issues with:
- **Resend API**: Contact Resend support
- **ConvergeAI email service**: Open an issue on GitHub
- **Email templates**: Check `src/utils/email_templates.py`

---

**Happy Emailing! 📧**


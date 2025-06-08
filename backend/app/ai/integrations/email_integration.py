"""
Email Integration Module for Sales Agent.

This module provides functionality to send emails through various email service providers.
Currently supports SMTP with a base interface for other providers.
"""

import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Dict, List, Optional, Union, Any, BinaryIO
from pathlib import Path
from pydantic import BaseModel, EmailStr, Field
import aiosmtplib
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class EmailAttachment(BaseModel):
    """Email attachment model."""
    filename: str
    content: Union[bytes, str]
    content_type: str = "application/octet-stream"
    disposition: str = "attachment"  # or 'inline'

class EmailMessage(BaseModel):
    """Email message model."""
    to: List[EmailStr]
    subject: str
    body: str
    from_email: Optional[EmailStr] = None
    cc: List[EmailStr] = Field(default_factory=list)
    bcc: List[EmailStr] = Field(default_factory=list)
    reply_to: Optional[EmailStr] = None
    attachments: List[EmailAttachment] = Field(default_factory=list)
    html: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)

class EmailResponse(BaseModel):
    """Response from email sending operation."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None

class EmailIntegration:
    """Base class for email integrations."""
    
    def __init__(self, **kwargs):
        """Initialize the email integration."""
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for the integration."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def send_email(self, message: EmailMessage) -> EmailResponse:
        """Send an email.
        
        Args:
            message: Email message to send
            
        Returns:
            EmailResponse indicating success or failure
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def send_template_email(
        self,
        template_name: str,
        to: List[EmailStr],
        context: Dict[str, Any],
        **kwargs
    ) -> EmailResponse:
        """Send an email using a template.
        
        Args:
            template_name: Name of the template to use
            to: List of recipient email addresses
            context: Context variables for the template
            **kwargs: Additional arguments to pass to send_email
            
        Returns:
            EmailResponse indicating success or failure
        """
        raise NotImplementedError("Template-based email not implemented")

class SMTPEmailIntegration(EmailIntegration):
    """Email integration using SMTP."""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        use_ssl: bool = False,
        sender_name: Optional[str] = None,
        **kwargs
    ):
        """Initialize SMTP email integration.
        
        Args:
            smtp_server: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            use_tls: Whether to use TLS (default: True)
            use_ssl: Whether to use SSL (default: False)
            sender_name: Optional sender name to use in the From field
        """
        super().__init__(**kwargs)
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.sender_name = sender_name
        self.from_email = username  # Default from email is the username
    
    async def _create_message(self, email: EmailMessage) -> MIMEMultipart:
        """Create a MIME message from an EmailMessage."""
        msg = MIMEMultipart('alternative' if email.html else 'mixed')
        
        # Set basic headers
        msg['Subject'] = email.subject
        msg['From'] = email.from_email or self.from_email
        msg['To'] = ', '.join(email.to)
        
        if email.cc:
            msg['Cc'] = ', '.join(email.cc)
        if email.bcc:
            msg['Bcc'] = ', '.join(email.bcc)
        if email.reply_to:
            msg['Reply-To'] = email.reply_to
        
        # Add custom headers
        for key, value in email.headers.items():
            msg[key] = value
        
        # Add message body
        if email.html:
            part1 = MIMEText(email.body, 'plain')
            part2 = MIMEText(email.html, 'html')
            msg.attach(part1)
            msg.attach(part2)
        else:
            part = MIMEText(email.body, 'plain')
            msg.attach(part)
        
        # Add attachments
        for attachment in email.attachments:
            part = MIMEApplication(
                attachment.content,
                Name=attachment.filename
            )
            part['Content-Disposition'] = f'{attachment.disposition}; filename="{attachment.filename}"'
            part['Content-Type'] = attachment.content_type
            msg.attach(part)
        
        return msg
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def send_email(self, message: EmailMessage) -> EmailResponse:
        """Send an email using SMTP."""
        try:
            # Create the message
            msg = await self._create_message(message)
            
            # Connect to SMTP server
            if self.use_ssl:
                smtp = aiosmtplib.SMTP_SSL(
                    hostname=self.smtp_server,
                    port=self.smtp_port,
                    timeout=10
                )
            else:
                smtp = aiosmtplib.SMTP(
                    hostname=self.smtp_server,
                    port=self.smtp_port,
                    timeout=10
                )
            
            await smtp.connect()
            
            # Start TLS if needed
            if self.use_tls and not self.use_ssl:
                await smtp.starttls()
            
            # Authenticate if credentials are provided
            if self.username and self.password:
                await smtp.login(self.username, self.password)
            
            # Send the email
            recipients = message.to.copy()
            if message.cc:
                recipients.extend(message.cc)
            if message.bcc:
                recipients.extend(message.bcc)
            
            await smtp.send_message(
                msg,
                from_addr=message.from_email or self.from_email,
                to_addrs=recipients
            )
            
            await smtp.quit()
            
            return EmailResponse(
                success=True,
                message_id=msg['Message-ID'] if 'Message-ID' in msg else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}", exc_info=True)
            return EmailResponse(
                success=False,
                error=str(e)
            )

class SendGridEmailIntegration(EmailIntegration):
    """Email integration using SendGrid API."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize SendGrid integration.
        
        Args:
            api_key: SendGrid API key
        """
        super().__init__(**kwargs)
        self.api_key = api_key
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def send_email(self, message: EmailMessage) -> EmailResponse:
        """Send an email using SendGrid API."""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import (
                Mail, Attachment, FileContent, FileName, 
                FileType, Disposition, ContentId
            )
            
            sg = SendGridAPIClient(api_key=self.api_key)
            
            # Create SendGrid mail object
            mail = Mail(
                from_email=message.from_email,
                to_emails=message.to,
                subject=message.subject,
                plain_text_content=message.body,
                html_content=message.html
            )
            
            # Add CC and BCC
            if message.cc:
                for email in message.cc:
                    mail.add_cc(email)
            
            if message.bcc:
                for email in message.bcc:
                    mail.add_bcc(email)
            
            # Add reply-to
            if message.reply_to:
                mail.reply_to = message.reply_to
            
            # Add custom headers
            for key, value in message.headers.items():
                mail.add_header(key, value)
            
            # Add attachments
            for attachment in message.attachments:
                encoded = attachment.content
                if isinstance(encoded, str):
                    encoded = encoded.encode('utf-8')
                
                attached_file = Attachment()
                attached_file.file_content = FileContent(encoded)
                attached_file.file_type = FileType(attachment.content_type)
                attached_file.file_name = FileName(attachment.filename)
                attached_file.disposition = Disposition(attachment.disposition)
                
                if attachment.disposition == 'inline' and hasattr(attachment, 'content_id'):
                    attached_file.content_id = ContentId(attachment.content_id)
                
                mail.attachment = attached_file
            
            # Send the email
            response = await sg.client.mail.send.post(request_body=mail.get())
            
            if 200 <= response.status_code < 300:
                return EmailResponse(
                    success=True,
                    message_id=response.headers.get('X-Message-Id')
                )
            else:
                error_msg = f"SendGrid API error: {response.status_code} - {response.body}"
                self.logger.error(error_msg)
                return EmailResponse(
                    success=False,
                    error=error_msg
                )
                
        except Exception as e:
            self.logger.error(f"Failed to send email via SendGrid: {str(e)}", exc_info=True)
            return EmailResponse(
                success=False,
                error=str(e)
            )

# Factory function for creating the appropriate email integration
def create_email_integration(provider: str, **kwargs) -> EmailIntegration:
    """Create an email integration instance based on the provider.
    
    Args:
        provider: Email provider name ('smtp' or 'sendgrid')
        **kwargs: Provider-specific arguments
        
    Returns:
        An instance of the appropriate email integration class
    """
    provider = provider.lower()
    
    if provider == 'smtp':
        return SMTPEmailIntegration(**kwargs)
    elif provider == 'sendgrid':
        return SendGridEmailIntegration(**kwargs)
    else:
        raise ValueError(f"Unsupported email provider: {provider}")

"""
Notification System Module - Independent Notification and Alert Management

This module handles comprehensive notification management across multiple channels.
It can be developed, tested, and upgraded independently of other modules.
Includes email, SMS, Slack, webhook, and in-app notifications.

Features:
- Multi-channel notification support (Email, SMS, Slack, Webhooks, In-app)
- Template-based messaging with dynamic content
- Priority-based notification routing
- Delivery tracking and retry mechanisms
- Notification preferences and user management
- Rate limiting and throttling
- Notification analytics and reporting
- Integration with external services (SendGrid, Twilio, Slack, etc.)
"""

import asyncio
import logging
import json
import smtplib
import ssl
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import hashlib
import threading
from enum import Enum
import re
import time
from urllib.parse import urlencode
import tempfile
import os

# HTTP client for webhooks and API calls
try:
    import aiohttp
    import requests
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False

# Jinja2 for template rendering
try:
    from jinja2 import Environment, BaseLoader, Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class NotificationStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

class NotificationChannel(Enum):
    """Available notification channels"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    PUSH = "push"

@dataclass
class NotificationTemplate:
    """Notification template structure"""
    template_id: str
    name: str
    channel: NotificationChannel
    subject_template: str
    body_template: str
    variables: List[str] = field(default_factory=list)
    priority: NotificationPriority = NotificationPriority.NORMAL
    retry_count: int = 3
    retry_delay: int = 300  # seconds
    expiry_hours: int = 24
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationRecipient:
    """Notification recipient information"""
    recipient_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    slack_user_id: Optional[str] = None
    webhook_url: Optional[str] = None
    preferences: Dict[NotificationChannel, bool] = field(default_factory=dict)
    timezone: str = "UTC"
    language: str = "en"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationMessage:
    """Individual notification message"""
    message_id: str
    template_id: str
    recipient: NotificationRecipient
    channel: NotificationChannel
    priority: NotificationPriority
    subject: str
    body: str
    variables: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)
    scheduled_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    status: NotificationStatus = NotificationStatus.PENDING
    created_time: datetime = field(default_factory=datetime.now)
    sent_time: Optional[datetime] = None
    delivered_time: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    delivery_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationConfig:
    """Notification system configuration"""
    # Email configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    from_email: str = ""
    from_name: str = "RFP Automation System"
    
    # SMS configuration (Twilio)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    
    # Slack configuration
    slack_bot_token: str = ""
    slack_webhook_url: str = ""
    
    # Webhook configuration
    webhook_timeout: int = 30
    webhook_retry_count: int = 3
    
    # General settings
    max_concurrent_notifications: int = 10
    rate_limit_per_minute: int = 60
    enable_delivery_tracking: bool = True
    enable_analytics: bool = True
    default_retry_delay: int = 300
    default_expiry_hours: int = 24

class NotificationChannelInterface(ABC):
    """Abstract interface for notification channels"""
    
    @abstractmethod
    async def send_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send notification through this channel"""
        pass
    
    @abstractmethod
    def get_channel_name(self) -> str:
        """Return channel name"""
        pass
    
    @abstractmethod
    def validate_recipient(self, recipient: NotificationRecipient) -> bool:
        """Validate if recipient can receive notifications through this channel"""
        pass

class EmailNotificationChannel(NotificationChannelInterface):
    """Email notification channel"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self._validate_config()
    
    def _validate_config(self):
        """Validate email configuration"""
        required_fields = ['smtp_server', 'smtp_username', 'smtp_password', 'from_email']
        for field in required_fields:
            if not getattr(self.config, field):
                raise ValueError(f"Email configuration missing: {field}")
    
    async def send_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send email notification"""
        try:
            if not self.validate_recipient(message.recipient):
                raise ValueError("Recipient email address is required")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            msg['To'] = message.recipient.email
            msg['Subject'] = message.subject
            
            # Add body
            msg.attach(MIMEText(message.body, 'html' if '<' in message.body else 'plain'))
            
            # Add attachments
            for attachment_path in message.attachments:
                if os.path.exists(attachment_path):
                    with open(attachment_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(attachment_path)}'
                    )
                    msg.attach(part)
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.smtp_use_tls:
                    server.starttls(context=context)
                
                server.login(self.config.smtp_username, self.config.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {message.recipient.email}")
            return {
                'success': True,
                'channel': 'email',
                'recipient': message.recipient.email,
                'message_id': message.message_id
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {message.recipient.email}: {e}")
            return {
                'success': False,
                'channel': 'email',
                'error': str(e),
                'message_id': message.message_id
            }
    
    def get_channel_name(self) -> str:
        return "Email"
    
    def validate_recipient(self, recipient: NotificationRecipient) -> bool:
        """Validate email recipient"""
        if not recipient.email:
            return False
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, recipient.email) is not None

class SMSNotificationChannel(NotificationChannelInterface):
    """SMS notification channel using Twilio"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Twilio client"""
        try:
            if not all([self.config.twilio_account_sid, self.config.twilio_auth_token]):
                logger.warning("Twilio credentials not configured, SMS notifications disabled")
                return
            
            # Import Twilio (optional dependency)
            try:
                from twilio.rest import Client
                self.client = Client(self.config.twilio_account_sid, self.config.twilio_auth_token)
                logger.info("Twilio SMS client initialized")
            except ImportError:
                logger.warning("Twilio library not available, SMS notifications disabled")
                
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}")
    
    async def send_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            if not self.client:
                raise ValueError("SMS client not initialized")
            
            if not self.validate_recipient(message.recipient):
                raise ValueError("Recipient phone number is required")
            
            # Send SMS
            sms_message = self.client.messages.create(
                body=f"{message.subject}\n\n{message.body}",
                from_=self.config.twilio_from_number,
                to=message.recipient.phone
            )
            
            logger.info(f"SMS sent successfully to {message.recipient.phone}")
            return {
                'success': True,
                'channel': 'sms',
                'recipient': message.recipient.phone,
                'message_id': message.message_id,
                'provider_message_id': sms_message.sid
            }
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {message.recipient.phone}: {e}")
            return {
                'success': False,
                'channel': 'sms',
                'error': str(e),
                'message_id': message.message_id
            }
    
    def get_channel_name(self) -> str:
        return "SMS"
    
    def validate_recipient(self, recipient: NotificationRecipient) -> bool:
        """Validate SMS recipient"""
        if not recipient.phone:
            return False
        
        # Basic phone number validation (international format)
        phone_pattern = r'^\+[1-9]\d{1,14}$'
        return re.match(phone_pattern, recipient.phone) is not None

class SlackNotificationChannel(NotificationChannelInterface):
    """Slack notification channel"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Slack client"""
        try:
            if not self.config.slack_bot_token:
                logger.warning("Slack bot token not configured, Slack notifications disabled")
                return
            
            # Import Slack SDK (optional dependency)
            try:
                from slack_sdk.web.async_client import AsyncWebClient
                self.client = AsyncWebClient(token=self.config.slack_bot_token)
                logger.info("Slack client initialized")
            except ImportError:
                logger.warning("Slack SDK not available, Slack notifications disabled")
                
        except Exception as e:
            logger.error(f"Failed to initialize Slack client: {e}")
    
    async def send_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send Slack notification"""
        try:
            if not self.validate_recipient(message.recipient):
                raise ValueError("Recipient Slack user ID is required")
            
            # Prepare message blocks for rich formatting
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": message.subject
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message.body
                    }
                }
            ]
            
            # Add priority indicator
            if message.priority in [NotificationPriority.HIGH, NotificationPriority.URGENT, NotificationPriority.CRITICAL]:
                blocks.insert(0, {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":warning: *{message.priority.value.upper()} PRIORITY*"
                    }
                })
            
            if self.client:
                # Send via Slack API
                response = await self.client.chat_postMessage(
                    channel=message.recipient.slack_user_id,
                    blocks=blocks,
                    text=message.subject  # Fallback text
                )
                
                logger.info(f"Slack message sent successfully to {message.recipient.slack_user_id}")
                return {
                    'success': True,
                    'channel': 'slack',
                    'recipient': message.recipient.slack_user_id,
                    'message_id': message.message_id,
                    'slack_ts': response['ts']
                }
            
            elif self.config.slack_webhook_url:
                # Send via webhook
                if not HTTP_AVAILABLE:
                    raise ValueError("HTTP client not available for webhook")
                
                payload = {
                    "text": message.subject,
                    "blocks": blocks
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.config.slack_webhook_url,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self.config.webhook_timeout)
                    ) as response:
                        if response.status == 200:
                            logger.info("Slack webhook message sent successfully")
                            return {
                                'success': True,
                                'channel': 'slack',
                                'method': 'webhook',
                                'message_id': message.message_id
                            }
                        else:
                            raise ValueError(f"Slack webhook failed with status {response.status}")
            
            else:
                raise ValueError("Neither Slack client nor webhook URL configured")
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return {
                'success': False,
                'channel': 'slack',
                'error': str(e),
                'message_id': message.message_id
            }
    
    def get_channel_name(self) -> str:
        return "Slack"
    
    def validate_recipient(self, recipient: NotificationRecipient) -> bool:
        """Validate Slack recipient"""
        return bool(recipient.slack_user_id)

class WebhookNotificationChannel(NotificationChannelInterface):
    """Webhook notification channel"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
    
    async def send_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send webhook notification"""
        try:
            if not HTTP_AVAILABLE:
                raise ValueError("HTTP client not available for webhook")
            
            if not self.validate_recipient(message.recipient):
                raise ValueError("Recipient webhook URL is required")
            
            # Prepare webhook payload
            payload = {
                'message_id': message.message_id,
                'template_id': message.template_id,
                'recipient': {
                    'id': message.recipient.recipient_id,
                    'name': message.recipient.name
                },
                'channel': message.channel.value,
                'priority': message.priority.value,
                'subject': message.subject,
                'body': message.body,
                'variables': message.variables,
                'timestamp': message.created_time.isoformat(),
                'metadata': message.delivery_metadata
            }
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    message.recipient.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.webhook_timeout),
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    
                    response_text = await response.text()
                    
                    if response.status == 200:
                        logger.info(f"Webhook sent successfully to {message.recipient.webhook_url}")
                        return {
                            'success': True,
                            'channel': 'webhook',
                            'recipient': message.recipient.webhook_url,
                            'message_id': message.message_id,
                            'response_status': response.status,
                            'response_body': response_text
                        }
                    else:
                        raise ValueError(f"Webhook failed with status {response.status}: {response_text}")
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return {
                'success': False,
                'channel': 'webhook',
                'error': str(e),
                'message_id': message.message_id
            }
    
    def get_channel_name(self) -> str:
        return "Webhook"
    
    def validate_recipient(self, recipient: NotificationRecipient) -> bool:
        """Validate webhook recipient"""
        if not recipient.webhook_url:
            return False
        
        # Basic URL validation
        url_pattern = r'^https?://.+'
        return re.match(url_pattern, recipient.webhook_url) is not None

class InAppNotificationChannel(NotificationChannelInterface):
    """In-app notification channel (stores notifications for web interface)"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.notifications_store = {}  # In production, use database
        self.store_lock = threading.Lock()
    
    async def send_notification(self, message: NotificationMessage) -> Dict[str, Any]:
        """Store in-app notification"""
        try:
            # Store notification for user
            with self.store_lock:
                user_id = message.recipient.recipient_id
                if user_id not in self.notifications_store:
                    self.notifications_store[user_id] = []
                
                notification_data = {
                    'id': message.message_id,
                    'subject': message.subject,
                    'body': message.body,
                    'priority': message.priority.value,
                    'created_time': message.created_time.isoformat(),
                    'read': False,
                    'variables': message.variables,
                    'metadata': message.delivery_metadata
                }
                
                self.notifications_store[user_id].append(notification_data)
                
                # Keep only last 100 notifications per user
                if len(self.notifications_store[user_id]) > 100:
                    self.notifications_store[user_id] = self.notifications_store[user_id][-100:]
            
            logger.info(f"In-app notification stored for user {message.recipient.recipient_id}")
            return {
                'success': True,
                'channel': 'in_app',
                'recipient': message.recipient.recipient_id,
                'message_id': message.message_id
            }
            
        except Exception as e:
            logger.error(f"Failed to store in-app notification: {e}")
            return {
                'success': False,
                'channel': 'in_app',
                'error': str(e),
                'message_id': message.message_id
            }
    
    def get_channel_name(self) -> str:
        return "In-App"
    
    def validate_recipient(self, recipient: NotificationRecipient) -> bool:
        """Validate in-app recipient"""
        return bool(recipient.recipient_id)
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        with self.store_lock:
            user_notifications = self.notifications_store.get(user_id, [])
            
            if unread_only:
                return [n for n in user_notifications if not n['read']]
            
            return user_notifications.copy()
    
    def mark_notification_read(self, user_id: str, notification_id: str) -> bool:
        """Mark notification as read"""
        with self.store_lock:
            user_notifications = self.notifications_store.get(user_id, [])
            
            for notification in user_notifications:
                if notification['id'] == notification_id:
                    notification['read'] = True
                    return True
            
            return False
    
    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications"""
        with self.store_lock:
            user_notifications = self.notifications_store.get(user_id, [])
            return sum(1 for n in user_notifications if not n['read'])

class NotificationSystemModule:
    """Main Notification System Module - Orchestrates all notification channels"""
    
    def __init__(self, config: NotificationConfig = None):
        self.config = config or NotificationConfig()
        
        # Initialize notification channels
        self.channels = {}
        self._initialize_channels()
        
        # Template management
        self.templates = {}
        self._load_default_templates()
        
        # Message tracking
        self.messages = {}
        self.message_lock = threading.Lock()
        
        # Rate limiting
        self.rate_limiter = {}
        self.rate_lock = threading.Lock()
        
        # Analytics
        self.analytics = {
            'total_sent': 0,
            'total_delivered': 0,
            'total_failed': 0,
            'channel_stats': {},
            'priority_stats': {},
            'template_stats': {}
        }
        self.analytics_lock = threading.Lock()
        
        # Background task for processing notifications
        self.processing_queue = asyncio.Queue()
        self.processing_task = None
        self.shutdown_event = asyncio.Event()
        
        logger.info(f"Notification System Module initialized with {len(self.channels)} channels")
    
    def _initialize_channels(self):
        """Initialize notification channels"""
        try:
            # Email channel
            if self.config.smtp_username and self.config.smtp_password:
                self.channels[NotificationChannel.EMAIL] = EmailNotificationChannel(self.config)
            
            # SMS channel
            if self.config.twilio_account_sid and self.config.twilio_auth_token:
                self.channels[NotificationChannel.SMS] = SMSNotificationChannel(self.config)
            
            # Slack channel
            if self.config.slack_bot_token or self.config.slack_webhook_url:
                self.channels[NotificationChannel.SLACK] = SlackNotificationChannel(self.config)
            
            # Webhook channel (always available)
            self.channels[NotificationChannel.WEBHOOK] = WebhookNotificationChannel(self.config)
            
            # In-app channel (always available)
            self.channels[NotificationChannel.IN_APP] = InAppNotificationChannel(self.config)
            
            logger.info(f"Initialized channels: {list(self.channels.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to initialize notification channels: {e}")
    
    def _load_default_templates(self):
        """Load default notification templates"""
        default_templates = [
            NotificationTemplate(
                template_id="rfp_analysis_complete",
                name="RFP Analysis Complete",
                channel=NotificationChannel.EMAIL,
                subject_template="RFP Analysis Complete: {{organization_name}}",
                body_template="""
                <h2>RFP Analysis Complete</h2>
                <p>The analysis for <strong>{{organization_name}}</strong> has been completed.</p>
                
                <h3>Analysis Results:</h3>
                <ul>
                    <li><strong>Qualification Score:</strong> {{qualification_score}}/100</li>
                    <li><strong>Recommendation:</strong> {{recommendation}}</li>
                    <li><strong>Priority Level:</strong> {{priority_level}}</li>
                </ul>
                
                <h3>Key Findings:</h3>
                <p>{{key_findings}}</p>
                
                <h3>Next Steps:</h3>
                <p>{{next_steps}}</p>
                
                <p>View the full analysis report in the RFP Automation System.</p>
                """,
                variables=["organization_name", "qualification_score", "recommendation", "priority_level", "key_findings", "next_steps"],
                priority=NotificationPriority.NORMAL
            ),
            NotificationTemplate(
                template_id="high_priority_rfp",
                name="High Priority RFP Alert",
                channel=NotificationChannel.SLACK,
                subject_template="🚨 High Priority RFP: {{organization_name}}",
                body_template="""
                *High Priority RFP Detected*
                
                📋 *Organization:* {{organization_name}}
                🎯 *Score:* {{qualification_score}}/100
                ⏰ *Deadline:* {{deadline}}
                💰 *Budget:* {{budget}}
                
                *Green Flags:*
                {{green_flags}}
                
                *Action Required:* {{action_required}}
                """,
                variables=["organization_name", "qualification_score", "deadline", "budget", "green_flags", "action_required"],
                priority=NotificationPriority.HIGH
            ),
            NotificationTemplate(
                template_id="system_alert",
                name="System Alert",
                channel=NotificationChannel.EMAIL,
                subject_template="System Alert: {{alert_type}}",
                body_template="""
                <h2>System Alert</h2>
                <p><strong>Alert Type:</strong> {{alert_type}}</p>
                <p><strong>Severity:</strong> {{severity}}</p>
                <p><strong>Time:</strong> {{timestamp}}</p>
                
                <h3>Description:</h3>
                <p>{{description}}</p>
                
                <h3>Recommended Action:</h3>
                <p>{{recommended_action}}</p>
                """,
                variables=["alert_type", "severity", "timestamp", "description", "recommended_action"],
                priority=NotificationPriority.URGENT
            ),
            NotificationTemplate(
                template_id="approval_request",
                name="Approval Request",
                channel=NotificationChannel.EMAIL,
                subject_template="Approval Required: {{item_type}}",
                body_template="""
                <h2>Approval Request</h2>
                <p>An item requires your approval in the RFP Automation System.</p>
                
                <h3>Details:</h3>
                <ul>
                    <li><strong>Type:</strong> {{item_type}}</li>
                    <li><strong>Submitted by:</strong> {{submitted_by}}</li>
                    <li><strong>Submitted on:</strong> {{submitted_date}}</li>
                    <li><strong>Priority:</strong> {{priority}}</li>
                </ul>
                
                <h3>Description:</h3>
                <p>{{description}}</p>
                
                <p><a href="{{approval_url}}">Click here to review and approve</a></p>
                """,
                variables=["item_type", "submitted_by", "submitted_date", "priority", "description", "approval_url"],
                priority=NotificationPriority.NORMAL
            ),
            NotificationTemplate(
                template_id="weekly_summary",
                name="Weekly Summary Report",
                channel=NotificationChannel.EMAIL,
                subject_template="Weekly RFP Summary - {{week_ending}}",
                body_template="""
                <h2>Weekly RFP Summary</h2>
                <p><strong>Week Ending:</strong> {{week_ending}}</p>
                
                <h3>Summary Statistics:</h3>
                <ul>
                    <li><strong>RFPs Analyzed:</strong> {{rfps_analyzed}}</li>
                    <li><strong>High Priority:</strong> {{high_priority_count}}</li>
                    <li><strong>Proposals Generated:</strong> {{proposals_generated}}</li>
                    <li><strong>Success Rate:</strong> {{success_rate}}%</li>
                </ul>
                
                <h3>Top Organizations:</h3>
                {{top_organizations}}
                
                <h3>Upcoming Deadlines:</h3>
                {{upcoming_deadlines}}
                
                <p>View detailed analytics in the RFP Automation System dashboard.</p>
                """,
                variables=["week_ending", "rfps_analyzed", "high_priority_count", "proposals_generated", "success_rate", "top_organizations", "upcoming_deadlines"],
                priority=NotificationPriority.LOW
            )
        ]
        
        for template in default_templates:
            self.templates[template.template_id] = template
        
        logger.info(f"Loaded {len(default_templates)} default templates")
    
    def add_template(self, template: NotificationTemplate):
        """Add or update notification template"""
        self.templates[template.template_id] = template
        logger.info(f"Added/updated template: {template.template_id}")
    
    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Get notification template"""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[NotificationTemplate]:
        """List all notification templates"""
        return list(self.templates.values())
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template with variables"""
        try:
            if JINJA2_AVAILABLE:
                # Use Jinja2 for advanced templating
                jinja_template = Template(template)
                return jinja_template.render(**variables)
            else:
                # Simple string replacement
                rendered = template
                for key, value in variables.items():
                    rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
                return rendered
                
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return template
    
    def _check_rate_limit(self, recipient_id: str, channel: NotificationChannel) -> bool:
        """Check if recipient is within rate limits"""
        with self.rate_lock:
            now = time.time()
            key = f"{recipient_id}_{channel.value}"
            
            if key not in self.rate_limiter:
                self.rate_limiter[key] = []
            
            # Remove old entries (older than 1 minute)
            self.rate_limiter[key] = [
                timestamp for timestamp in self.rate_limiter[key]
                if now - timestamp < 60
            ]
            
            # Check if under limit
            if len(self.rate_limiter[key]) >= self.config.rate_limit_per_minute:
                return False
            
            # Add current timestamp
            self.rate_limiter[key].append(now)
            return True
    
    def _update_analytics(self, message: NotificationMessage, result: Dict[str, Any]):
        """Update notification analytics"""
        with self.analytics_lock:
            self.analytics['total_sent'] += 1
            
            if result['success']:
                self.analytics['total_delivered'] += 1
            else:
                self.analytics['total_failed'] += 1
            
            # Channel stats
            channel = message.channel.value
            if channel not in self.analytics['channel_stats']:
                self.analytics['channel_stats'][channel] = {'sent': 0, 'delivered': 0, 'failed': 0}
            
            self.analytics['channel_stats'][channel]['sent'] += 1
            if result['success']:
                self.analytics['channel_stats'][channel]['delivered'] += 1
            else:
                self.analytics['channel_stats'][channel]['failed'] += 1
            
            # Priority stats
            priority = message.priority.value
            if priority not in self.analytics['priority_stats']:
                self.analytics['priority_stats'][priority] = {'sent': 0, 'delivered': 0, 'failed': 0}
            
            self.analytics['priority_stats'][priority]['sent'] += 1
            if result['success']:
                self.analytics['priority_stats'][priority]['delivered'] += 1
            else:
                self.analytics['priority_stats'][priority]['failed'] += 1
            
            # Template stats
            template_id = message.template_id
            if template_id not in self.analytics['template_stats']:
                self.analytics['template_stats'][template_id] = {'sent': 0, 'delivered': 0, 'failed': 0}
            
            self.analytics['template_stats'][template_id]['sent'] += 1
            if result['success']:
                self.analytics['template_stats'][template_id]['delivered'] += 1
            else:
                self.analytics['template_stats'][template_id]['failed'] += 1
    
    async def send_notification(self, template_id: str, recipient: NotificationRecipient,
                              variables: Dict[str, Any] = None, 
                              channel: Optional[NotificationChannel] = None,
                              priority: Optional[NotificationPriority] = None,
                              scheduled_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Send notification using template"""
        try:
            # Get template
            template = self.get_template(template_id)
            if not template:
                raise ValueError(f"Template not found: {template_id}")
            
            # Use template channel if not specified
            if not channel:
                channel = template.channel
            
            # Use template priority if not specified
            if not priority:
                priority = template.priority
            
            # Check if channel is available
            if channel not in self.channels:
                raise ValueError(f"Channel not available: {channel}")
            
            # Check if recipient can receive notifications on this channel
            channel_handler = self.channels[channel]
            if not channel_handler.validate_recipient(recipient):
                raise ValueError(f"Recipient cannot receive notifications on {channel}")
            
            # Check recipient preferences
            if channel in recipient.preferences and not recipient.preferences[channel]:
                logger.info(f"Recipient {recipient.recipient_id} has disabled {channel} notifications")
                return {
                    'success': False,
                    'error': 'Recipient has disabled this notification channel',
                    'channel': channel.value
                }
            
            # Check rate limits
            if not self._check_rate_limit(recipient.recipient_id, channel):
                logger.warning(f"Rate limit exceeded for {recipient.recipient_id} on {channel}")
                return {
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'channel': channel.value
                }
            
            # Prepare variables
            template_variables = variables or {}
            
            # Render templates
            subject = self._render_template(template.subject_template, template_variables)
            body = self._render_template(template.body_template, template_variables)
            
            # Create message
            message_id = hashlib.md5(f"{template_id}_{recipient.recipient_id}_{datetime.now()}".encode()).hexdigest()[:12]
            
            message = NotificationMessage(
                message_id=message_id,
                template_id=template_id,
                recipient=recipient,
                channel=channel,
                priority=priority,
                subject=subject,
                body=body,
                variables=template_variables,
                scheduled_time=scheduled_time,
                expiry_time=datetime.now() + timedelta(hours=template.expiry_hours),
                max_retries=template.retry_count
            )
            
            # Store message
            with self.message_lock:
                self.messages[message_id] = message
            
            # Send immediately or schedule
            if scheduled_time and scheduled_time > datetime.now():
                message.status = NotificationStatus.PENDING
                logger.info(f"Notification scheduled for {scheduled_time}: {message_id}")
                return {
                    'success': True,
                    'message_id': message_id,
                    'status': 'scheduled',
                    'scheduled_time': scheduled_time.isoformat()
                }
            else:
                # Send immediately
                result = await self._send_message(message)
                return result
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _send_message(self, message: NotificationMessage) -> Dict[str, Any]:
        """Send individual message"""
        try:
            # Check if message has expired
            if message.expiry_time and datetime.now() > message.expiry_time:
                message.status = NotificationStatus.CANCELLED
                logger.warning(f"Message expired: {message.message_id}")
                return {
                    'success': False,
                    'message_id': message.message_id,
                    'error': 'Message expired'
                }
            
            # Get channel handler
            channel_handler = self.channels[message.channel]
            
            # Update message status
            message.status = NotificationStatus.SENT
            message.sent_time = datetime.now()
            
            # Send notification
            result = await channel_handler.send_notification(message)
            
            # Update message status based on result
            if result['success']:
                message.status = NotificationStatus.DELIVERED
                message.delivered_time = datetime.now()
            else:
                message.status = NotificationStatus.FAILED
                message.error_message = result.get('error', 'Unknown error')
            
            # Update analytics
            if self.config.enable_analytics:
                self._update_analytics(message, result)
            
            logger.info(f"Message {message.message_id} sent via {message.channel.value}: {result['success']}")
            
            return {
                'success': result['success'],
                'message_id': message.message_id,
                'channel': message.channel.value,
                'recipient': message.recipient.recipient_id,
                'sent_time': message.sent_time.isoformat() if message.sent_time else None,
                'delivered_time': message.delivered_time.isoformat() if message.delivered_time else None,
                'error': result.get('error')
            }
            
        except Exception as e:
            message.status = NotificationStatus.FAILED
            message.error_message = str(e)
            
            logger.error(f"Failed to send message {message.message_id}: {e}")
            return {
                'success': False,
                'message_id': message.message_id,
                'error': str(e)
            }
    
    async def send_bulk_notification(self, template_id: str, recipients: List[NotificationRecipient],
                                   variables: Dict[str, Any] = None,
                                   channel: Optional[NotificationChannel] = None,
                                   priority: Optional[NotificationPriority] = None) -> Dict[str, Any]:
        """Send notification to multiple recipients"""
        try:
            results = []
            
            # Send to each recipient
            for recipient in recipients:
                result = await self.send_notification(
                    template_id=template_id,
                    recipient=recipient,
                    variables=variables,
                    channel=channel,
                    priority=priority
                )
                results.append(result)
            
            # Summarize results
            successful = sum(1 for r in results if r['success'])
            failed = len(results) - successful
            
            logger.info(f"Bulk notification sent: {successful} successful, {failed} failed")
            
            return {
                'success': True,
                'total_recipients': len(recipients),
                'successful': successful,
                'failed': failed,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Bulk notification failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def retry_failed_notifications(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """Retry failed notifications"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            retry_results = []
            
            with self.message_lock:
                messages_to_retry = [
                    msg for msg in self.messages.values()
                    if (msg.status == NotificationStatus.FAILED and
                        msg.created_time > cutoff_time and
                        msg.retry_count < msg.max_retries)
                ]
            
            for message in messages_to_retry:
                try:
                    message.retry_count += 1
                    message.status = NotificationStatus.RETRYING
                    
                    result = await self._send_message(message)
                    retry_results.append(result)
                    
                except Exception as e:
                    logger.error(f"Retry failed for message {message.message_id}: {e}")
                    retry_results.append({
                        'success': False,
                        'message_id': message.message_id,
                        'error': str(e)
                    })
            
            successful_retries = sum(1 for r in retry_results if r['success'])
            
            logger.info(f"Retry completed: {successful_retries}/{len(retry_results)} successful")
            
            return {
                'success': True,
                'total_retried': len(retry_results),
                'successful': successful_retries,
                'results': retry_results
            }
            
        except Exception as e:
            logger.error(f"Retry operation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_message_status(self, message_id: str) -> Optional[NotificationMessage]:
        """Get message status"""
        with self.message_lock:
            return self.messages.get(message_id)
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get in-app notifications for user"""
        if NotificationChannel.IN_APP in self.channels:
            in_app_channel = self.channels[NotificationChannel.IN_APP]
            return in_app_channel.get_user_notifications(user_id, unread_only)
        return []
    
    def mark_notification_read(self, user_id: str, notification_id: str) -> bool:
        """Mark in-app notification as read"""
        if NotificationChannel.IN_APP in self.channels:
            in_app_channel = self.channels[NotificationChannel.IN_APP]
            return in_app_channel.mark_notification_read(user_id, notification_id)
        return False
    
    def get_unread_count(self, user_id: str) -> int:
        """Get unread notification count for user"""
        if NotificationChannel.IN_APP in self.channels:
            in_app_channel = self.channels[NotificationChannel.IN_APP]
            return in_app_channel.get_unread_count(user_id)
        return 0
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get notification analytics"""
        with self.analytics_lock:
            return self.analytics.copy()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get notification system status"""
        with self.message_lock:
            message_stats = {
                'total': len(self.messages),
                'pending': 0,
                'sent': 0,
                'delivered': 0,
                'failed': 0,
                'retrying': 0,
                'cancelled': 0
            }
            
            for message in self.messages.values():
                message_stats[message.status.value] += 1
        
        return {
            'channels': {
                channel.value: {
                    'name': handler.get_channel_name(),
                    'available': True
                }
                for channel, handler in self.channels.items()
            },
            'templates': {
                'total': len(self.templates),
                'templates': [
                    {
                        'id': t.template_id,
                        'name': t.name,
                        'channel': t.channel.value,
                        'priority': t.priority.value
                    }
                    for t in self.templates.values()
                ]
            },
            'messages': message_stats,
            'analytics': self.get_analytics() if self.config.enable_analytics else None,
            'configuration': {
                'max_concurrent': self.config.max_concurrent_notifications,
                'rate_limit_per_minute': self.config.rate_limit_per_minute,
                'delivery_tracking': self.config.enable_delivery_tracking,
                'analytics_enabled': self.config.enable_analytics
            }
        }
    
    async def test_channels(self) -> Dict[str, Any]:
        """Test all notification channels"""
        test_results = {}
        
        # Create test recipient
        test_recipient = NotificationRecipient(
            recipient_id="test_user",
            name="Test User",
            email="test@example.com",
            phone="+1234567890",
            slack_user_id="U1234567890",
            webhook_url="https://httpbin.org/post"
        )
        
        # Test each channel
        for channel, handler in self.channels.items():
            try:
                if not handler.validate_recipient(test_recipient):
                    test_results[channel.value] = {
                        'status': 'skipped',
                        'reason': 'Invalid recipient configuration'
                    }
                    continue
                
                # Create test message
                test_message = NotificationMessage(
                    message_id=f"test_{channel.value}_{int(time.time())}",
                    template_id="test",
                    recipient=test_recipient,
                    channel=channel,
                    priority=NotificationPriority.LOW,
                    subject="Test Notification",
                    body="This is a test notification from the RFP Automation System."
                )
                
                # Send test message
                start_time = time.time()
                result = await handler.send_notification(test_message)
                end_time = time.time()
                
                test_results[channel.value] = {
                    'status': 'success' if result['success'] else 'failed',
                    'response_time': end_time - start_time,
                    'result': result
                }
                
            except Exception as e:
                test_results[channel.value] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return test_results
    
    def cleanup_old_messages(self, older_than_days: int = 30):
        """Clean up old messages"""
        cutoff_time = datetime.now() - timedelta(days=older_than_days)
        
        with self.message_lock:
            to_remove = []
            for message_id, message in self.messages.items():
                if message.created_time < cutoff_time:
                    to_remove.append(message_id)
            
            for message_id in to_remove:
                del self.messages[message_id]
            
            logger.info(f"Cleaned up {len(to_remove)} old messages")
    
    def shutdown(self):
        """Shutdown notification system"""
        try:
            # Set shutdown event
            self.shutdown_event.set()
            
            # Clean up old messages
            self.cleanup_old_messages(0)  # Clean all
            
            logger.info("Notification System Module shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Example usage and testing
async def main():
    """Example usage of Notification System Module"""
    
    # Initialize notification system
    config = NotificationConfig(
        # Email configuration (replace with your settings)
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        smtp_username="your-email@gmail.com",
        smtp_password="your-app-password",
        from_email="your-email@gmail.com",
        from_name="RFP Automation System",
        
        # Rate limiting
        rate_limit_per_minute=10,
        max_concurrent_notifications=5,
        
        # Features
        enable_delivery_tracking=True,
        enable_analytics=True
    )
    
    notification_system = NotificationSystemModule(config)
    
    # Show system status
    print("Notification System Status:")
    status = notification_system.get_system_status()
    print(json.dumps(status, indent=2, default=str))
    
    # Test channels
    print("\nTesting notification channels...")
    test_results = await notification_system.test_channels()
    print(json.dumps(test_results, indent=2, default=str))
    
    # Create test recipients
    recipients = [
        NotificationRecipient(
            recipient_id="user1",
            name="John Doe",
            email="john@example.com",
            preferences={NotificationChannel.EMAIL: True, NotificationChannel.IN_APP: True}
        ),
        NotificationRecipient(
            recipient_id="user2",
            name="Jane Smith",
            email="jane@example.com",
            preferences={NotificationChannel.EMAIL: True, NotificationChannel.IN_APP: True}
        )
    ]
    
    # Send test notifications
    print("\nSending test notifications...")
    
    # RFP Analysis Complete notification
    for recipient in recipients:
        result = await notification_system.send_notification(
            template_id="rfp_analysis_complete",
            recipient=recipient,
            variables={
                "organization_name": "UNICEF",
                "qualification_score": "92",
                "recommendation": "High Priority",
                "priority_level": "High",
                "key_findings": "Strong alignment with our expertise in multimedia campaigns and environmental focus.",
                "next_steps": "Proceed with proposal development. Review detailed requirements and prepare initial concept."
            },
            channel=NotificationChannel.EMAIL
        )
        print(f"RFP Analysis notification to {recipient.name}: {result['success']}")
    
    # High Priority RFP alert
    result = await notification_system.send_notification(
        template_id="high_priority_rfp",
        recipient=recipients[0],
        variables={
            "organization_name": "UN Environment",
            "qualification_score": "95",
            "deadline": "2024-02-15",
            "budget": "$150,000",
            "green_flags": "• Environmental focus\n• Multimedia requirements\n• 5+ years experience needed",
            "action_required": "Review RFP details and begin proposal preparation immediately."
        },
        channel=NotificationChannel.IN_APP,
        priority=NotificationPriority.HIGH
    )
    print(f"High Priority alert: {result['success']}")
    
    # System alert
    result = await notification_system.send_notification(
        template_id="system_alert",
        recipient=recipients[0],
        variables={
            "alert_type": "Web Scraping Rate Limit",
            "severity": "Warning",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description": "The system has reached 80% of the daily rate limit for UNGM portal scraping.",
            "recommended_action": "Monitor scraping frequency and consider implementing additional delays between requests."
        },
        priority=NotificationPriority.URGENT
    )
    print(f"System alert: {result['success']}")
    
    # Bulk notification
    print("\nSending bulk notification...")
    bulk_result = await notification_system.send_bulk_notification(
        template_id="weekly_summary",
        recipients=recipients,
        variables={
            "week_ending": "2024-01-14",
            "rfps_analyzed": "23",
            "high_priority_count": "5",
            "proposals_generated": "3",
            "success_rate": "87",
            "top_organizations": "• UNICEF (3 RFPs)\n• UN Environment (2 RFPs)\n• World Bank (2 RFPs)",
            "upcoming_deadlines": "• UNICEF Campaign: Jan 20\n• UN Environment Video: Jan 25\n• World Bank Report: Feb 1"
        },
        channel=NotificationChannel.IN_APP
    )
    print(f"Bulk notification: {bulk_result['successful']}/{bulk_result['total_recipients']} successful")
    
    # Check in-app notifications
    print("\nIn-app notifications:")
    for recipient in recipients:
        notifications = notification_system.get_user_notifications(recipient.recipient_id)
        unread_count = notification_system.get_unread_count(recipient.recipient_id)
        print(f"{recipient.name}: {len(notifications)} total, {unread_count} unread")
        
        # Mark first notification as read
        if notifications:
            notification_system.mark_notification_read(recipient.recipient_id, notifications[0]['id'])
            print(f"  Marked notification {notifications[0]['id']} as read")
    
    # Show analytics
    print("\nNotification Analytics:")
    analytics = notification_system.get_analytics()
    print(json.dumps(analytics, indent=2, default=str))
    
    # Cleanup
    notification_system.cleanup_old_messages(0)  # Clean all for demo
    notification_system.shutdown()

if __name__ == "__main__":
    asyncio.run(main())

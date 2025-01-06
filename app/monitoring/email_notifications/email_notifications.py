import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import os
from flask import Blueprint, jsonify, request, render_template
from app.core.database import db
from app.core.base_service import BaseService
from app.core.config import Config
from app.core.error_handling.decorators import handle_errors
from app.core.database.models.notification_model import NotificationSettings, NotificationRule
from app.monitoring.notification_logic import NotificationTemplates
import logging

logger = logging.getLogger(__name__)

class EmailNotificationService(BaseService):
    """Service for managing and sending email notifications"""

    def __init__(self):
        super().__init__()
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.config = Config()
        self.templates = NotificationTemplates()

        if not all([self.smtp_username, self.smtp_password, self.sender_email]):
            logger.error("Email configuration missing required fields")
            raise ValueError("Email configuration incomplete")

    @handle_errors()
    def send_email(self, recipients: List[str], subject: str, body_text: str, body_html: Optional[str] = None) -> bool:
        """Send an email using configured SMTP settings"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = ', '.join(recipients)

        msg.attach(MIMEText(body_text, 'plain'))
        if body_html:
            msg.attach(MIMEText(body_html, 'html'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            logger.info(f"Email sent successfully to {recipients}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    @handle_errors()
    def send_notification(self, rule_id: int, data: dict) -> bool:
        """Send notification based on a specific rule"""
        rule = NotificationRule.query.get(rule_id)
        if not rule:
            logger.error(f"Notification rule {rule_id} not found")
            return False

        settings = NotificationSettings.query.first()
        if not settings:
            logger.error("Notification settings not found")
            return False

        message = self.templates.email_templates.format_error_notification(data)
        for channel in rule.channels:
            if channel == 'email' and settings.email_critical:
                self.send_email([settings.email_recipients], message['subject'], message['body'], message['html'])

        return True

    @handle_errors()
    def send_error_notification(self, error_data: Dict) -> bool:
        """Send error notification email"""
        subject = f"[{error_data['severity']}] Encoder Error: {error_data['encoder_name']}"
        body_text = self.templates.email_templates._generate_error_email_body(error_data)
        recipients = self._get_notification_recipients(error_data['severity'])
        return self.send_email(recipients, subject, body_text)

    def _get_notification_recipients(self, severity: str) -> List[str]:
        """Get notification recipients based on severity level"""
        return [os.getenv('DEFAULT_NOTIFICATION_EMAIL', 'admin@example.com')]

# API Blueprint for managing notifications
notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications/settings', methods=['GET'])
@handle_errors()
def notification_settings():
    """Render notification settings page"""
    settings = NotificationSettings.query.first()
    rules = NotificationRule.query.all()
    return render_template('notifications.html', settings=settings, notification_rules=rules)

@notifications_bp.route('/notifications/rules', methods=['POST'])
@handle_errors()
def create_rule():
    """Create new notification rule"""
    try:
        data = request.get_json()
        rule = NotificationRule(
            name=data['name'],
            condition=data['condition'],
            channels=data['channels'],
            priority=data['priority']
        )
        db.session.add(rule)
        db.session.commit()
        return jsonify({'status': 'success', 'rule_id': rule.id})
    except Exception as e:
        logger.error(f"Error creating notification rule: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@notifications_bp.route('/notifications/test', methods=['POST'])
@handle_errors()
def test_notification():
    """Test notification delivery"""
    channel = request.json.get('channel')
    if not channel:
        return jsonify({'status': 'error', 'message': 'Channel is required'}), 400

    service = EmailNotificationService()
    result = service.send_test_notification(channel)
    return jsonify({'status': 'success' if result else 'failed'})

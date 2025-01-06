from typing import Dict, List, Optional
import requests
import logging
from flask import Blueprint, jsonify, request, render_template
from app.core.database import db
from app.core.error_handling.decorators import handle_errors
from app.core.database.models.notification_model import NotificationSettings, NotificationRule
from app.monitoring.notification_logic import NotificationTemplates

logger = logging.getLogger(__name__)

class TelegramBot:
    """Handles sending notifications via Telegram Bot API"""

    def __init__(self):
        self.settings = NotificationSettings.query.first()
        if not self.settings:
            logger.error("No notification settings found")
            return

        self.token = self.settings.telegram_token
        self.chat_id = self.settings.telegram_chat_id
        self.api_base = f"https://api.telegram.org/bot{self.token}"
        self.templates = NotificationTemplates()

    @handle_errors()
    def send_message(self, message: Dict) -> bool:
        """Send notification message via Telegram"""
        if not self.token or not self.chat_id:
            logger.error("Telegram bot not configured - missing token or chat ID")
            return False

        text = self._format_message(message)

        try:
            response = requests.post(
                f"{self.api_base}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "HTML"
                }
            )
            response.raise_for_status()
            return True

        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False

    def _format_message(self, message: Dict) -> str:
        """Format notification message for Telegram with dynamic content"""
        severity_emoji = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️"
        }

        emoji = severity_emoji.get(message.get("severity", "info"), "ℹ️")

        # Example of using loc_key and loc_args for dynamic content
        loc_key = message.get('loc_key', 'Notification')
        loc_args = message.get('loc_args', [])

        text = f"""
{emoji} <b>{loc_key.format(*loc_args)}</b>

<b>Encoder:</b> {message.get('encoder_name', 'Unknown')}
<b>Status:</b> {message.get('status', 'Unknown')}
<b>Time:</b> {message.get('timestamp', 'Unknown')}

<b>Details:</b>
{message.get('error_message', 'No details provided')}

<b>Impact:</b>
• Service Impact: {message.get('service_impact', 'Unknown')}
• Affected Users: {message.get('affected_users', 'Unknown')}
• Est. Recovery: {message.get('recovery_time', 'Unknown')}

<b>Actions Taken:</b>
{message.get('automated_actions', 'None')}

<b>Recommended Actions:</b>
{message.get('recommended_actions', 'None')}

<a href="{message.get('dashboard_url', '#')}">View Dashboard</a> | <a href="{message.get('encoder_url', '#')}">Encoder Details</a>
"""
        return text

    @handle_errors()
    def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        try:
            response = requests.get(f"{self.api_base}/getMe")
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Telegram connection test failed: {str(e)}")
            return False

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

    bot = TelegramBot()
    result = bot.send_message({"subject": "Test Notification", "severity": "info"})
    return jsonify({'status': 'success' if result else 'failed'})

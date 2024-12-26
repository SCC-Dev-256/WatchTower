from ..database import db
from flask import Blueprint, jsonify, request, render_template
from ..models.notification import NotificationRule, NotificationSettings
from ..services.notification_service import NotificationService

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications/settings', methods=['GET'])
def notification_settings():
    """Render notification settings page"""
    settings = NotificationSettings.query.first()
    rules = NotificationRule.query.all()
    return render_template('notifications.html',
                         settings=settings,
                         notification_rules=rules)

@notifications_bp.route('/notifications/rules', methods=['POST'])
def create_rule():
    """Create new notification rule"""
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

@notifications_bp.route('/notifications/test', methods=['POST'])
def test_notification():
    """Test notification delivery"""
    channel = request.json['channel']
    service = NotificationService()
    
    result = service.send_test_notification(channel)
    return jsonify({'status': 'success' if result else 'failed'}) 
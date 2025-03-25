from app.core.database import db
from flask import Blueprint, jsonify, request, render_template
from app.core.database.models.notification_model import NotificationRule, NotificationSettings
from app.services.notification_service import NotificationService
from WatchTower.app.core.auth.auth import require_api_key, roles_required, error_handler
from pydantic import BaseModel, ValidationError, constr, conlist
from typing import List

notifications_bp = Blueprint('notifications', __name__)

class NotificationRuleModel(BaseModel):
    name: str = constr(min_length=1, max_length=100)
    condition: str = constr(min_length=1)
    channels: List[str] = conlist(str, min_items=1)
    priority: int

@notifications_bp.route('/notifications/settings', methods=['GET'])
@roles_required('admin', 'editor')
@require_api_key
@error_handler
def notification_settings():
    """Render notification settings page"""
    settings = NotificationSettings.query.first()
    rules = NotificationRule.query.all()
    return render_template('notifications.html',
                         settings=settings,
                         notification_rules=rules)

@notifications_bp.route('/notifications/rules', methods=['POST'])
@roles_required('admin', 'editor')
@require_api_key
@error_handler
def create_rule():
    """Create new notification rule"""
    try:
        data = request.get_json()
        rule_data = NotificationRuleModel(**data)
    except ValidationError as e:
        return jsonify({'status': 'error', 'errors': e.errors()}), 400

    rule = NotificationRule(
        name=rule_data.name,
        condition=rule_data.condition,
        channels=rule_data.channels,
        priority=rule_data.priority
    )
    db.session.add(rule)
    db.session.commit()
    return jsonify({'status': 'success', 'rule_id': rule.id})

@notifications_bp.route('/notifications/test', methods=['POST'])
@roles_required('admin', 'editor')
@require_api_key
@error_handler
def test_notification():
    """Test notification delivery"""
    channel = request.json.get('channel')
    if not channel:
        return jsonify({'status': 'error', 'message': 'Channel is required'}), 400

    service = NotificationService()
    result = service.send_test_notification(channel)
    return jsonify({'status': 'success' if result else 'failed'}) 
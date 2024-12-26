from typing import Dict, List
from datetime import datetime, timedelta
import redis
from collections import defaultdict, Counter

class NotificationManager:
    def __init__(self, app):
        self.app = app
        self.redis = redis.Redis.from_url(app.config['REDIS_URL'])
        self.rate_limits = {
            'critical': {'count': 5, 'window': 300},  # 5 per 5 minutes
            'warning': {'count': 3, 'window': 600},   # 3 per 10 minutes
            'info': {'count': 2, 'window': 1800}      # 2 per 30 minutes
        }
        self.grouping_window = 300  # 5 minutes
        
    def should_send_notification(self, notification_type: str, encoder_id: str) -> bool:
        """Check if notification should be sent based on rate limits"""
        key = f"notification_rate:{notification_type}:{encoder_id}"
        count = self.redis.get(key)
        
        if count is None:
            self.redis.setex(
                key, 
                self.rate_limits[notification_type]['window'],
                1
            )
            return True
            
        count = int(count)
        if count >= self.rate_limits[notification_type]['count']:
            return False
            
        self.redis.incr(key)
        return True
    
    def group_notifications(self, notifications: List[Dict]) -> List[Dict]:
        """Group similar notifications within time window"""
        groups = defaultdict(list)
        
        for notification in notifications:
            group_key = self._get_group_key(notification)
            groups[group_key].append(notification)
        
        return [
            self._merge_notifications(group)
            for group in groups.values()
            if len(group) > 0
        ]
    
    def _get_group_key(self, notification: Dict) -> str:
        """Generate more specific grouping key for notification"""
        components = [
            notification['error_type'],
            notification.get('category', 'general'),
            notification.get('severity', 'info')
        ]
        
        # Add location-based grouping
        if location := notification.get('location'):
            components.append(location)
        
        # Add service-based grouping
        if service := notification.get('service'):
            components.append(service)
        
        return ':'.join(components)
    
    def _merge_notifications(self, notifications: List[Dict]) -> Dict:
        """Enhanced notification merging with more context"""
        if len(notifications) == 1:
            return notifications[0]
        
        base = notifications[0].copy()
        base['count'] = len(notifications)
        base['merged'] = True
        
        # Group by encoder and location
        encoders_by_location = defaultdict(list)
        for n in notifications:
            encoders_by_location[n.get('location', 'unknown')].append(n['encoder_id'])
        
        base['affected_systems'] = {
            location: list(set(encoders))
            for location, encoders in encoders_by_location.items()
        }
        
        # Aggregate impact metrics
        base['aggregate_impact'] = self._calculate_aggregate_impact(notifications)
        
        # Track error progression
        base['error_progression'] = self._analyze_error_progression(notifications)
        
        # Summarize automated actions
        base['automated_actions_summary'] = self._summarize_automated_actions(notifications)
        
        return base
    
    def _calculate_aggregate_impact(self, notifications: List[Dict]) -> Dict:
        """Calculate aggregate impact of grouped notifications"""
        total_users_affected = sum(
            n.get('impact', {}).get('affected_users', 0) 
            for n in notifications
        )
        
        service_impacts = [
            n.get('impact', {}).get('service_impact', 'unknown')
            for n in notifications
        ]
        
        return {
            'total_users_affected': total_users_affected,
            'service_impacts': Counter(service_impacts),
            'severity_distribution': Counter(n.get('severity') for n in notifications)
        }
    
    def _analyze_error_progression(self, notifications: List[Dict]) -> Dict:
        """Analyze how errors have progressed over time"""
        sorted_notifications = sorted(
            notifications,
            key=lambda x: datetime.fromisoformat(x['timestamp'])
        )
        
        return {
            'first_occurrence': sorted_notifications[0]['timestamp'],
            'last_occurrence': sorted_notifications[-1]['timestamp'],
            'frequency': len(notifications) / (
                (datetime.fromisoformat(sorted_notifications[-1]['timestamp']) -
                 datetime.fromisoformat(sorted_notifications[0]['timestamp'])).total_seconds() / 3600
            ),  # errors per hour
            'is_accelerating': self._check_error_acceleration(sorted_notifications)
        }
    
    def send_grouped_notification(self, notification: Dict):
        """Send grouped notification"""
        if notification.get('merged', False):
            # Use special template for grouped notifications
            template = self.app.notification_templates.get_grouped_template(
                notification['error_type']
            )
        else:
            # Use standard template
            template = self.app.notification_templates.get_template(
                notification['error_type']
            )
            
        # Send to appropriate channels
        if notification['severity'] == 'critical':
            self.app.telegram_bot.send_message(
                template.format_critical_alert(notification)
            )
            
        self.app.email_sender.send_notification(
            template.format_error_notification(notification)
        ) 
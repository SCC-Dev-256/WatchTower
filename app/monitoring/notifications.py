from typing import Dict, List
from datetime import datetime
import json

class NotificationTemplates:
    def __init__(self):
        self.telegram_templates = TelegramTemplates()
        self.email_templates = EmailTemplates()

class EmailTemplates:
    def format_error_notification(self, error_data: Dict) -> Dict:
        """Format error notification for email"""
        return {
            'subject': f"[{error_data['severity']}] Encoder Error: {error_data['encoder_name']}",
            'body': self._generate_error_email_body(error_data),
            'html': self._generate_error_email_html(error_data)
        }
    
    def _generate_error_email_body(self, error_data: Dict) -> str:
        """Generate plain text email body"""
        template = """
ENCODER ERROR NOTIFICATION

Encoder: {encoder_name}
Status: {status}
Severity: {severity}
Time: {timestamp}

Error Details:
{error_message}

Impact Assessment:
- Service Impact: {service_impact}
- Affected Users: {affected_users}
- Estimated Recovery: {recovery_time}

Automated Actions Taken:
{automated_actions}

Recommended Actions:
{recommended_actions}

Historical Context:
- Similar Issues: {similar_issues}
- Last Occurrence: {last_occurrence}

Monitor Dashboard: {dashboard_url}
Encoder Details: {encoder_url}

---
This is an automated notification. Do not reply.
        """
        
        return template.format(
            encoder_name=error_data['encoder_name'],
            status=error_data['status'],
            severity=error_data['severity'],
            timestamp=error_data['timestamp'],
            error_message=error_data['message'],
            service_impact=error_data['impact_assessment']['service_impact'],
            affected_users=error_data['impact_assessment']['affected_users'],
            recovery_time=error_data['impact_assessment']['recovery_time_estimate'],
            automated_actions=self._format_actions(error_data['automated_actions']),
            recommended_actions=self._format_actions(error_data['recommended_actions']),
            similar_issues=error_data['historical_context']['similar_issues'],
            last_occurrence=error_data['historical_context']['last_occurrence'],
            dashboard_url=error_data['urls']['dashboard'],
            encoder_url=error_data['urls']['encoder']
        )

class TelegramTemplates:
    def format_critical_alert(self, alert_data: Dict) -> str:
        template = """
🚨 *CRITICAL ALERT - AJA HELO*

*Encoder:* {encoder_name}
*Location:* {location}
*Error Type:* {error_type}
*Time:* {timestamp}

*Current Status:*
• Video Input: {video_status}
• Audio Status: {audio_status}
• Storage: {storage_status}
• Network: {network_status}
• Stream Health: {stream_health}

*Impact Assessment:*
• Service Impact: {service_impact}
• Users Affected: {affected_users}
• Estimated Recovery: {recovery_time}

*Automated Actions Taken:*
{automated_actions}

*Required Manual Actions:*
{required_actions}

*Technical Details:*
• Last Known Config: {last_config}
• Error Code: {error_code}
• Related Events: {related_events}

*Resources:*
• [View Dashboard]({dashboard_url})
• [View Logs]({logs_url})
• [View Documentation]({docs_url})

*Contact:*
On-Call Engineer: {oncall_contact}
"""
        return template.format(**self._prepare_alert_data(alert_data))

    def format_warning_alert(self, alert_data: Dict) -> str:
        template = """
⚠️ *WARNING ALERT - AJA HELO*

*Encoder:* {encoder_name}
*Issue Type:* {issue_type}
*Status:* {current_status}
*Time:* {timestamp}

*Performance Metrics:*
• CPU Usage: {cpu_usage}%
• Memory: {memory_usage}%
• Network: {network_usage} Mbps
• Storage: {storage_usage}%

*Issue Details:*
{details}

*Historical Context:*
• Similar Issues: {similar_issues}
• Last Occurrence: {last_occurrence}
• Resolution Time: {avg_resolution_time}

*Suggested Actions:*
{suggested_actions}

*Monitoring:*
• [View Metrics]({metrics_url})
• [View Trends]({trends_url})
"""
        return template.format(**self._prepare_warning_data(alert_data))

    def format_multicast_alert(self, alert_data: Dict) -> str:
        template = """
📡 *MULTICAST STREAMING ALERT*

*Encoder:* {encoder_name}
*Location:* {location}
*Issue:* Multicast Stream Failure
*Time:* {timestamp}

*Network Details:*
• Multicast Group: {multicast_group}
• Network Interface: {interface}
• IGMP Version: {igmp_version}
• TTL: {ttl}

*Diagnostics:*
• Packet Loss: {packet_loss}%
• Jitter: {jitter}ms
• Network Load: {network_load}%

*Impact:*
• Affected Receivers: {affected_receivers}
• Stream Quality: {stream_quality}

*Actions Taken:*
{automated_actions}

*Required Actions:*
{manual_actions}

[View Network Diagnostics]({diagnostics_url})
"""
        return template.format(**self._prepare_multicast_data(alert_data))

    def format_storage_alert(self, alert_data: Dict) -> str:
        template = """
💾 *STORAGE ALERT*

*Encoder:* {encoder_name}
*Storage Device:* {storage_device}
*Issue:* {issue_type}
*Time:* {timestamp}

*Storage Status:*
• Total Space: {total_space}
• Used Space: {used_space}
• Free Space: {free_space}
• Health Status: {health_status}

*Recording Status:*
• Active Recordings: {active_recordings}
• Failed Recordings: {failed_recordings}
• Last Success: {last_successful_recording}

*SMART Data:*
{smart_data}

*Recommended Actions:*
{recommended_actions}

[View Storage Details]({storage_url})
"""
        return template.format(**self._prepare_storage_data(alert_data))

    def format_sync_loss_alert(self, alert_data: Dict) -> str:
        template = """
⚠️ *SYNC LOSS ALERT*

*Encoder:* {encoder_name}
*Issue:* {sync_type} Sync Loss
*Duration:* {duration}

*Signal Details:*
• Input Format: {input_format}
• Reference Source: {reference_source}
• Timecode Source: {timecode_source}
• Genlock Status: {genlock_status}

*Last Known Good:*
• Format: {last_good_format}
• Time: {last_good_time}
• Reference: {last_good_reference}

*Actions Available:*
{available_actions}

[View Sync Status]({sync_url})
"""
        return template.format(**self._prepare_sync_data(alert_data))
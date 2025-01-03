from datetime import datetime
from typing import Dict, List
import sqlite3
import json
from app.core.auth import require_api_key, roles_required
from app.core.error_handling import handle_errors

class AlertHistory:
    def __init__(self, db_path="alert_history.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    encoder_name TEXT,
                    alert_type TEXT,
                    severity TEXT,
                    description TEXT,
                    status TEXT,
                    resolved_at TEXT,
                    mitigation_steps TEXT
                )
            """)
    
    def record_alert(self, alert_data: Dict):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO alerts (
                    timestamp, encoder_name, alert_type, severity,
                    description, status, mitigation_steps
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                alert_data['encoder_name'],
                alert_data['alert_type'],
                alert_data['severity'],
                alert_data['description'],
                'active',
                json.dumps(alert_data.get('mitigation_steps', []))
            ))
    
    def resolve_alert(self, alert_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE alerts 
                SET status = 'resolved', resolved_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), alert_id))

    @roles_required('admin', 'editor', 'viewer')
    @require_api_key
    @handle_errors()
    def get_active_alerts(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM alerts 
                WHERE status = 'active' 
                ORDER BY timestamp DESC
            """)
            return [dict(row) for row in cursor.fetchall()] 
import json, time, logging, psycopg2, requests
from datetime import datetime
from typing import Dict, Any
from psycopg2.extras import DictCursor
from app.core.aja.aja_constants import AJAParameters, AJAStreamParams

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DBConnection:
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str):
        self.conn_params = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }

    def __enter__(self):
        self.conn = psycopg2.connect(**self.conn_params)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

class EncoderPoller:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.timeout = 5  # seconds

    def get_encoders(self) -> list:
        """Fetch all active encoders from database"""
        with DBConnection(**self.db_config) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT id, name, ip_address, port 
                    FROM encoders 
                    WHERE status != 'disabled'
                """)
                return cur.fetchall()

    def fetch_encoder_status(self, ip: str, port: int) -> Dict[str, Any]:
        """Fetch encoder status via AJA REST API"""
        try:
            # Fetch streaming status
            stream_url = f"http://{ip}:{port}/api/v1/status/streaming"
            stream_resp = requests.get(stream_url, timeout=self.timeout)
            stream_data = stream_resp.json()

            # Fetch system status
            system_url = f"http://{ip}:{port}/api/v1/status/system"
            system_resp = requests.get(system_url, timeout=self.timeout)
            system_data = system_resp.json()

            return {
                "level": "INFO" if stream_data.get("streaming") else "WARNING",
                "message": f"Stream status: {stream_data.get('status', 'Unknown')}",
                "raw_json": {
                    "stream": stream_data,
                    "system": system_data
                },
                "timestamp": datetime.now()
            }
        except requests.RequestException as e:
            return {
                "level": "ERROR",
                "message": f"Connection error: {str(e)}",
                "raw_json": {"error": str(e)},
                "timestamp": datetime.now()
            }

    def save_log(self, encoder_id: str, log_data: Dict[str, Any]):
        """Save encoder log to database"""
        with DBConnection(**self.db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO encoder_logs 
                    (encoder_id, level, message, raw_json, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    encoder_id,
                    log_data["level"],
                    log_data["message"],
                    json.dumps(log_data["raw_json"]),
                    log_data["timestamp"]
                ))
                conn.commit()

    def update_encoder_status(self, encoder_id: str, status: str):
        """Update encoder status in database"""
        with DBConnection(**self.db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE encoders 
                    SET status = %s, last_seen = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (status, encoder_id))
                conn.commit()

    def poll(self):
        """Main polling function"""
        encoders = self.get_encoders()
        for encoder in encoders:
            try:
                status = self.fetch_encoder_status(encoder['ip_address'], encoder['port'])
                self.save_log(encoder['id'], status)
                
                # Update encoder status
                new_status = 'online' if status['level'] == 'INFO' else 'error'
                self.update_encoder_status(encoder['id'], new_status)
                
                logger.info(f"Polled encoder {encoder['name']}: {status['message']}")
            except Exception as e:
                logger.error(f"Error polling encoder {encoder['name']}: {str(e)}")

def main():
    db_config = {
        "dbname": "your_db_name",
        "user": "your_user",
        "password": "your_password",
        "host": "your_host",
        "port": "your_port"
    }
    
    poller = EncoderPoller(db_config)
    
    while True:
        try:
            poller.poll()
            time.sleep(30)  # Poll every 30 seconds
        except KeyboardInterrupt:
            logger.info("Polling stopped by user")
            break
        except Exception as e:
            logger.error(f"Polling error: {str(e)}")
            time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    main()

from logging import LogRecord
import requests
from app.core.database import db

class AJADevice:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_param(self, paramid):
        url = f"{self.base_url}/config?action=get&paramid={paramid}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def set_param(self, paramid, value):
        url = f"{self.base_url}/config?action=set&paramid={paramid}&value={value}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def fetch_logs(self):
        url = f"{self.base_url}/logwatch.tmpl"
        response = requests.get(url)
        response.raise_for_status()
        logs = response.json()

        # Assuming logs is a list of log entries
        for log_entry in logs:
            log_record = LogRecord(
                timestamp=log_entry['timestamp'],
                level=log_entry['level'],
                message=log_entry['message'],
                encoder_name=log_entry['encoder_name']
            )
            db.session.add(log_record)
            db.session.commit()

def detect_bandwidth_anomalies(device):
    param = device.get_param("eParamID_BandwidthStatus")
    if int(param["value"]) < 100:  # Example threshold
        print("Bandwidth anomaly detected!")

import requests

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
        # Implement specific log-fetching logic based on your needs
        pass

def detect_bandwidth_anomalies(device):
    param = device.get_param("eParamID_BandwidthStatus")
    if int(param["value"]) < 100:  # Example threshold
        print("Bandwidth anomaly detected!")

# Monitoring Dashboard Configuration

## Grafana Setup

### 1. Data Sources

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
  
  - name: PostgreSQL
    type: postgres
    url: postgres:5432
    database: encoder_metrics
    user: ${DB_USER}
    secureJsonData:
      password: ${DB_PASSWORD}
```

### 2. Dashboard Definitions

```json
{
  "dashboard": {
    "id": null,
    "title": "Encoder Health Overview",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "helo_cpu_usage{job=\"encoders\"}",
            "legendFormat": "{{encoder_id}}"
          }
        ]
      },
      {
        "title": "Temperature",
        "type": "gauge",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "helo_temperature{job=\"encoders\"}",
            "legendFormat": "{{encoder_id}}"
          }
        ]
      }
    ]
  }
}
```

### 3. Alert Rules

```yaml
groups:
  - name: encoder_alerts
    rules:
      - alert: HighTemperature
        expr: helo_temperature > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High temperature on encoder {{ $labels.encoder_id }}
          
      - alert: StreamFailure
        expr: helo_stream_status == 0
        for: 1m
        labels:
          severity: critical
``` 
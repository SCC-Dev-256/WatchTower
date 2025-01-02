"SCC-Dev=256" 
**Encoder Manager System
A scalable REST API system for managing video encoders with automatic failover, load balancing, and real-time monitoring.

System Overview
mermaid graph TD Client[Client Applications] --> API[REST API Layer] API --> LB[Load Balancer] API --> WS[WebSocket Server] LB --> E1[Primary Encoder] LB --> E2[Backup Encoder] LB --> Monitor[Health Monitor] Monitor --> Prometheus[Prometheus] Prometheus --> Grafana[Grafana Dashboards] Monitor --> AutoFix[Auto Remediation] AutoFix --> E1 AutoFix --> E2 E1 --> Stream[Stream Output] E2 --> Stream WS --> Client

Core Features
Load Balancing: Intelligent distribution of encoding tasks
Automatic Failover: Seamless backup switching
Real-time Monitoring: Comprehensive health checks
Thermal Management: Proactive load management
Connection Health: Historical pattern analysis
WebSocket Integration: Live updates
Security: API key auth and SSL monitoring
Health Monitoring System
Direct API Monitoring
Real-time encoder metrics
CPU/Memory usage tracking
Temperature monitoring
Fan speed monitoring
Stream state validation
Connection Health Monitoring
Historical performance tracking
Pattern recognition
Predictive issue detection
Connection pool management
Thermal load balancing
Thermal Management
Proactive overload prevention
Connection temperature monitoring
Gradual cooling procedures
Load distribution optimization
Key Components
Certificate Monitor (app/monitoring/cert_monitor.py)
SSL certificate validation and renewal
Chain verification
Automatic remediation for certificate issues
Integration with Let's Encrypt/Certbot
Error Analysis (app/monitoring/error_analysis.py)
Pattern matching for known issues
Error correlation and impact assessment
Root cause analysis
Automated remediation suggestions
AJA Remediation (app/services/aja_remediation_service.py)
Device-specific error handling and automated fixes
Stream quality management and optimization
Connection monitoring and recovery
Storage management and optimization
Automatic issue resolution
Load Balancer (app/services/load_balancer.py)
Manages encoder distribution and health monitoring:

Assigns clients to optimal encoders based on load
Monitors encoder health metrics
Handles automatic failover when issues detected
Stream Validator (app/services/stream_validator.py)
Validates streaming configurations:

Resolution and FPS compatibility
Bitrate optimization
RTMP key validation
Performance Monitor (app/services/performance_monitor.py)
Tracks system performance:

Latency monitoring
Message rate tracking
Resource utilization metrics
WebSocket Security (app/services/websocket_security.py)
Handles secure WebSocket connections:

Connection authentication
Rate limiting
Message integrity verification
API Endpoints
Monitoring (app/api/routes/monitoring.py)
/api/monitoring/status: System metrics and health status
/api/monitoring/alerts: Active system alerts
Encoder Control (app/api/encoder_endpoints.py)
/encoders/<encoder_id>/control: Encoder control operations
/encoders/<encoder_id>/metrics: Real-time encoder metrics
Health Monitoring
GET /health/encoder/{encoder_id}
GET /health/detailed
Installation
Run the installer:
./encoder_manager_setup
Configure your environment:
cp .env.example .env
# Edit .env with your settings
Start the services:
docker-compose up -d
Configuration
The system is configured via installer-config.yml, which includes:

Dependencies and requirements
Directory structure
Database configuration
Monitoring ports
Security settings
Development
Testing
pytest app/tests/
Performance Testing
pytest app/tests/performance/
Monitoring
Prometheus metrics available on port 9090
Grafana dashboards on port 3000
Custom alerts configurable via Alert Manager
Security Considerations
API key authentication with automatic expiration
SSL certificate monitoring and auto-renewal
Rate limiting on all endpoints
Comprehensive error tracking and recovery
Error Handling
The system includes comprehensive error handling:

Automatic retry mechanisms
Graceful degradation
Detailed error logging
Alert generation for critical issues
Contributing
Fork the repository
Create a feature branch
Submit a pull request with detailed description
Ensure all tests pass
License
[Your License Here]

How It Works
1. Stream Initialization Flow
Client requests a streaming session via REST API
Load balancer:
Checks available encoders
Evaluates health metrics
Assigns optimal encoder
Configures backup encoder
System returns RTMP credentials to client
2. Active Stream Monitoring
Health monitor continuously checks:
CPU/Memory usage
Network bandwidth
Frame drops
Error rates
Real-time metrics available via WebSocket
Automated alerts for issues
3. Failover Process
When issues are detected:

System evaluates severity
Attempts auto-remediation
If unsuccessful:
Activates backup encoder
Transitions stream
Updates client connection
Logs incident
Usage Examples
Starting a Stream
# Initialize streaming session
response = requests.post(
    "http://your-server/api/streams/init",
    json={
        "resolution": "1920x1080",
        "bitrate": 5000000,
        "fps": 30
    },
    headers={"Authorization": "Bearer your-api-key"}
)

# Get RTMP credentials
rtmp_data = response.json()
print(f"Stream Key: {rtmp_data['stream_key']}")
print(f"RTMP URL: {rtmp_data['rtmp_url']}")
Monitoring Stream Health
# WebSocket connection for real-time updates
import socketio

sio = socketio.Client()

@sio.on('stream_health')
def on_health_update(data):
    print(f"CPU Usage: {data['cpu_usage']}%")
    print(f"Dropped Frames: {data['dropped_frames']}")
    print(f"Bitrate: {data['bitrate']} bps")

sio.connect('http://your-server')
sio.emit('subscribe', {'stream_id': 'your-stream-id'})
Component Details
Load Balancer
Purpose: Distributes encoding load and manages failover
Key Features:
Weighted load distribution
Health-based routing
Automatic failover
Configuration sync
Metrics Tracked:
Encoder CPU/Memory
Network bandwidth
Client count
Error rates
Stream Validator
Purpose: Ensures stream configuration quality
Validates:
Resolution compatibility
FPS settings
Bitrate optimization
RTMP key format
Provides:
Configuration recommendations
Warning for suboptimal settings
Performance Monitor
Purpose: Tracks system-wide performance
Metrics:
End-to-end latency
Message processing rates
Resource utilization
Error frequency
Features:
Historical tracking
Trend analysis
Performance forecasting
Automated Remediation
Purpose: Automatically fixes AJA encoder issues
Capabilities:
Stream setting adjustment and quality management
Resource reallocation and optimization
Connection monitoring and recovery
Storage management and optimization
API Reference
Stream Management
POST /api/streams/init
GET /api/streams/{stream_id}/health
PUT /api/streams/{stream_id}/config
DELETE /api/streams/{stream_id}
Monitoring
GET /api/monitoring/load-balancer
GET /api/monitoring/encoders/{encoder_id}/metrics
GET /api/monitoring/streams/health
WebSocket Events
// Subscribe to stream events
socket.emit('subscribe', {stream_id: 'xxx'})

// Health updates
socket.on('stream_health', (data) => {})

// Error events
socket.on('stream_error', (data) => {})
Common Issues & Solutions
Stream Quality Issues
Symptoms: Frame drops, quality degradation
Auto-fixes:
Bitrate adjustment
Resolution downscaling
FPS modification
Manual fixes:
Check network bandwidth
Verify encoder resources
Review stream settings
Failover Delays
Symptoms: Extended stream interruption
Solutions:
Adjust health check frequency
Lower failover thresholds
Optimize backup sync interval
Pre-warm backup encoders
Metrics Collection
GET /monitoring/streams/health
GET /monitoring/streams/config/{encoder_id}
Created by Andrew Schumacher

Integration Examples
Basic Health Check
response = await requests.get(
    f"http://your-server/health/encoder/{encoder_id}",
    headers={"Authorization": "Bearer your-api-key"}
)
health_data = response.json()
print(f"Encoder Status: {health_data['encoder']['device_status']}")
WebSocket Health Monitoring
@sio.on('health_update')
def on_health_update(data):
    print(f"CPU Usage: {data['device_status']['cpu_usage']}%")
    print(f"Temperature: {data['device_status']['temperature']}°C")
    print(f"Health Score: {data['connection_health']['health_score']}")
Monitoring Integration
Prometheus Metrics
Connection health scores
Thermal status metrics
Health check counters
Performance histograms
Grafana Dashboards
Real-time health visualization
Historical trends
Thermal management graphs
Connection pool status
Error Handling
Automatic retry mechanisms
Gradual degradation
Detailed error logging
Predictive maintenance
Thermal protection
Contributing
Fork the repository
Create a feature branch
Submit a pull request
Ensure all tests pass
License
[Your License Here]

Monitoring System
Thermal Management
The system implements sophisticated thermal monitoring and protection:

GET /api/monitoring/thermal/status
GET /api/monitoring/thermal/{encoder_id}/temperature
POST /api/monitoring/thermal/{encoder_id}/cooldown
Connection Temperature Monitoring

Real-time temperature scoring (0-100)
Automatic cooling periods when thresholds exceeded
Gradual cooldown with configurable steps
Integration with warmup management
Thresholds

Temperature High: 80°C
Load High: 75%
Burst Limit: 100 requests per cooling period
Cooling Period: 60 seconds
Gradual Cooldown: 5 steps
Metrics & Alerting
Core Metrics

CPU/Memory usage
Stream bitrate stability
Storage health
Connection load
Thermal status
Alert Categories

Video signal loss
Stream bitrate instability
Thermal warnings
NTP sync failures
Storage capacity alerts
API Endpoints
# Status Monitoring
GET /api/monitoring/status
GET /api/monitoring/alerts
GET /api/monitoring/metrics

# Encoder Operations
GET /api/encoders/{encoder_id}/metrics
GET /api/encoders/{encoder_id}/status
GET /api/encoders/system/status

# Load Balancer Monitoring
GET /api/monitoring/load-balancer
GET /api/monitoring/streams/health
GET /api/monitoring/streams/config/{encoder_id}
Error Tracking
Centralized error management
Error correlation analysis
Enhanced metrics collection
Automatic remediation for common issues
Historical error analysis
Storage Monitoring
Health checks for multiple storage devices
Automatic failover on storage issues
Reboot cycle detection
Storage optimization recommendations
Integration
Prometheus metrics export
Grafana dashboards
Alertmanager integration
Telegram notifications
Email alerts
from app.core.monitoring.system import MonitoringSystem
from app.core.logging.system import LoggingSystem

# Initialize systems
monitoring = MonitoringSystem(app)
logging = LoggingSystem(app)

# Monitor encoder health
status = await monitoring.monitor_encoder("encoder_123")
Configuration
# Monitoring Settings
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
MONITORING_INTERVAL=30

# Alert Thresholds
TEMP_HIGH_THRESHOLD=80
CPU_HIGH_THRESHOLD=85
MEMORY_HIGH_THRESHOLD=90
Contributing
Fork the repository
Create a feature branch
Submit a pull request
Ensure all tests pass**

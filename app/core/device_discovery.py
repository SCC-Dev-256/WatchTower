from typing import List, Dict, Optional
import ipaddress
import asyncio
import aiohttp
import logging
from datetime import datetime
from app.models.encoder import HeloEncoder
from app.core.endpoint_registry import EndpointRegistry
from dataclasses import dataclass
from enum import Enum
from app.core.security.rbac import roles_required

logger = logging.getLogger(__name__)

class StreamingState(Enum):
    IDLE = "idle"
    STREAMING = "streaming"
    RECORDING = "recording"
    ERROR = "error"
    RECONNECTING = "reconnecting"

@dataclass
class EncoderStatus:
    streaming: bool
    recording: bool
    state: StreamingState
    last_error: Optional[str]
    retry_count: int
    config_version: str

class HeloDiscovery:
    """Scanner for discovering AJA Helo encoders on the network"""
    
    def __init__(self, endpoint_registry: EndpointRegistry):
        self.endpoint_registry = endpoint_registry
        self.known_devices: Dict[str, datetime] = {}  # IP -> last_seen
        self.encoder_states: Dict[str, EncoderStatus] = {}
        self.HELO_PORT = 80  # Default HTTP port for Helo devices
        self.SCAN_TIMEOUT = 2  # Seconds to wait for response
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 5
        
    async def probe_device(self, ip: str) -> Optional[Dict]:
        """Probe a single IP address for AJA Helo device"""
        url = f"http://{ip}/config"  # AJA Helo config endpoint
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    timeout=self.SCAN_TIMEOUT
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Verify it's a Helo device by checking specific headers/response
                        if self._is_helo_device(data):
                            device_info = {
                                'ip': ip,
                                'serial': data.get('serial_number'),
                                'name': data.get('device_name', f'Helo-{ip}'),
                                'firmware': data.get('firmware_version'),
                                'last_seen': datetime.now()
                            }
                            # Check for configuration changes
                            await self._detect_config_changes(ip, data)
                            await self._update_device_state(ip, data)
                            return device_info
                            
        except Exception as e:
            logger.debug(f"Failed to probe {ip}: {str(e)}")
            await self._handle_connection_error(ip, str(e))
        return None

    def _is_helo_device(self, response_data: Dict) -> bool:
        """Verify if the response is from a Helo device"""
        # Add specific checks for Helo device identification
        required_keys = ['serial_number', 'device_type']
        return all(key in response_data for key in required_keys) and \
               response_data.get('device_type') == 'AJA_HELO'

    async def scan_network(self, network: str = "192.168.1.0/24") -> List[Dict]:
        """
        Scan network range for Helo devices
        
        Args:
            network: Network range in CIDR notation
        
        Returns:
            List of discovered Helo devices
        """
        network = ipaddress.ip_network(network)
        tasks = []
        
        # Create probe tasks for each IP in the network
        for ip in network.hosts():
            tasks.append(self.probe_device(str(ip)))
        
        # Run probes concurrently
        results = await asyncio.gather(*tasks)
        
        # Filter out None results and update known devices
        discovered_devices = [r for r in results if r is not None]
        
        for device in discovered_devices:
            self.known_devices[device['ip']] = device['last_seen']
            await self._register_device(device)
        
        return discovered_devices

    @roles_required('admin', 'editor')
    async def _register_device(self, device: Dict) -> None:
        """Register discovered device in the system"""
        try:
            # Create or update encoder in database
            encoder = HeloEncoder.query.filter_by(ip_address=device['ip']).first()
            
            if not encoder:
                encoder = HeloEncoder(
                    ip_address=device['ip'],
                    name=device['name'],
                    serial_number=device['serial'],
                    firmware_version=device['firmware']
                )
                # Add to database
                from flask import current_app
                with current_app.app_context():
                    current_app.db.session.add(encoder)
                    current_app.db.session.commit()
                
                logger.info(f"Registered new Helo device: {device['name']} ({device['ip']})")
            
            # Update last seen timestamp
            encoder.last_seen = device['last_seen']
            
        except Exception as e:
            logger.error(f"Failed to register device {device['ip']}: {str(e)}")

    @roles_required('viewer')
    async def monitor_devices(self, interval: int = 300) -> None:
        """
        Continuously monitor known devices
        
        Args:
            interval: Monitoring interval in seconds
        """
        while True:
            for ip in list(self.known_devices.keys()):
                result = await self.probe_device(ip)
                if result:
                    self.known_devices[ip] = datetime.now()
                    # Reset retry count on successful connection
                    if ip in self.encoder_states:
                        self.encoder_states[ip].retry_count = 0
                else:
                    # Device not responding, mark as offline
                    logger.warning(f"Device {ip} not responding")
                    
            await asyncio.sleep(interval) 

    async def _update_device_state(self, ip: str, data: Dict) -> None:
        """Update encoder state information"""
        try:
            state = StreamingState.IDLE
            if data.get('streaming_active'):
                state = StreamingState.STREAMING
            elif data.get('recording_active'):
                state = StreamingState.RECORDING
                
            self.encoder_states[ip] = EncoderStatus(
                streaming=data.get('streaming_active', False),
                recording=data.get('recording_active', False),
                state=state,
                last_error=None,
                retry_count=0,
                config_version=data.get('config_version', '0')
            )
            
            # Emit state change event
            await self._notify_state_change(ip)
            
        except Exception as e:
            logger.error(f"Failed to update device state for {ip}: {str(e)}")

    async def _handle_connection_error(self, ip: str, error: str) -> None:
        """Handle device connection errors with retry logic"""
        if ip in self.encoder_states:
            state = self.encoder_states[ip]
            state.last_error = error
            state.retry_count += 1
            
            if state.retry_count <= self.MAX_RETRIES:
                state.state = StreamingState.RECONNECTING
                await asyncio.sleep(self.RETRY_DELAY)
                # Attempt reconnection
                await self.probe_device(ip)
            else:
                state.state = StreamingState.ERROR
                await self._notify_state_change(ip)
                logger.error(f"Device {ip} failed after {self.MAX_RETRIES} retries")

    async def _notify_state_change(self, ip: str) -> None:
        """Emit state change event via WebSocket"""
        if hasattr(self.endpoint_registry, 'websocket'):
            await self.endpoint_registry.websocket.emit('encoder_state_change', {
                'ip': ip,
                'state': self.encoder_states[ip].__dict__
            })

    async def handle_failover(self, ip: str) -> bool:
        """Handle failover for a failed device"""
        try:
            if ip not in self.encoder_states:
                return False
                
            failed_state = self.encoder_states[ip]
            if failed_state.state != StreamingState.ERROR:
                return False
                
            # Find available backup device
            backup_ip = await self._find_backup_device()
            if not backup_ip:
                logger.error("No backup devices available for failover")
                return False
                
            # Copy configuration to backup device
            if not await self._copy_config(ip, backup_ip):
                logger.error("Failed to copy configuration to backup device")
                return False
                
            # Start streaming/recording on backup device
            if failed_state.streaming:
                await self._start_streaming(backup_ip)
            if failed_state.recording:
                await self._start_recording(backup_ip)
                
            logger.info(f"Failover successful from {ip} to {backup_ip}")
            return True
            
        except Exception as e:
            logger.error(f"Failover failed: {str(e)}")
            return False
            
    async def _find_backup_device(self) -> Optional[str]:
        """Find available backup device"""
        for ip, state in self.encoder_states.items():
            if state.state == StreamingState.IDLE:
                return ip
        return None
        
    async def _copy_config(self, source_ip: str, target_ip: str) -> bool:
        """Copy configuration from failed device to backup"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get config from source
                source_url = f"http://{source_ip}/config"
                async with session.get(source_url) as response:
                    if response.status != 200:
                        return False
                    config = await response.json()
                
                # Apply to target
                target_url = f"http://{target_ip}/config"
                async with session.post(target_url, json=config) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Config copy failed: {str(e)}")
            return False

    async def _detect_config_changes(self, ip: str, new_config: Dict) -> bool:
        """Detect and handle configuration changes"""
        try:
            if ip not in self.encoder_states:
                return False
                
            current_version = self.encoder_states[ip].config_version
            new_version = new_config.get('config_version', '0')
            
            if current_version != new_version:
                # Log configuration change
                logger.info(f"Configuration change detected for {ip}: {current_version} -> {new_version}")
                
                # Notify about config change
                if hasattr(self.endpoint_registry, 'websocket'):
                    await self.endpoint_registry.websocket.emit('config_change', {
                        'ip': ip,
                        'old_version': current_version,
                        'new_version': new_version,
                        'changes': self._diff_configs(new_config)
                    })
                    
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error detecting config changes: {str(e)}")
            return False
            
    def _diff_configs(self, new_config: Dict) -> Dict:
        """Compare configuration changes"""
        changes = {}
        if hasattr(self, '_last_config'):
            for key, value in new_config.items():
                if key not in self._last_config or self._last_config[key] != value:
                    changes[key] = {
                        'old': self._last_config.get(key),
                        'new': value
                    }
        self._last_config = new_config.copy()
        return changes

    async def _start_streaming(self, ip: str) -> bool:
        """Start streaming on device"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://{ip}/api/streaming/start"
                async with session.post(url) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to start streaming on {ip}: {str(e)}")
            return False

    async def _start_recording(self, ip: str) -> bool:
        """Start recording on device"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://{ip}/api/recording/start"
                async with session.post(url) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to start recording on {ip}: {str(e)}")
            return False
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import asyncio
from prometheus_client import Gauge, Counter, Histogram
from app.core.error_handling.errors import EnhancedErrorMetrics
from app.core.connection.prep_warmup_manager import HeloWarmupManager
from app.core.helo.helo_params import HeloDeviceParameters, VideoGeometry
from app.core.helo.helo_commands import HeloEncoder
from app.core.database import db
from app.core.error_handling.errors.exceptions import EncoderError

class ConnectionThermalMetrics:
    """Metrics for connection thermal management"""
    connection_temperature = Gauge('helo_connection_temperature', 
                                 'Connection temperature score', 
                                 ['encoder_id', 'connection_id'])
    cooling_events = Counter('helo_cooling_events_total', 
                           'Number of cooling events', 
                           ['encoder_id', 'reason'])
    connection_load = Gauge('helo_connection_load', 
                          'Connection load percentage', 
                          ['encoder_id'])
    cooling_duration = Histogram('helo_cooling_duration_seconds', 
                               'Cooling period duration')

class ConnectionThermalManager:
    """
    Manages connection cooling and thermal management for HELO encoders.
    
    This class implements sophisticated connection load management using a thermal model
    to prevent overload and ensure optimal performance. It works in conjunction with
    the warmup manager to maintain connection health.

    Attributes:
        warmup_manager (HeloWarmupManager): Manager for connection warmup
        metrics (EnhancedErrorMetrics): System-wide metrics tracking
        thresholds (Dict): Configuration thresholds for thermal management
        
    Example:
        ```python
        thermal_manager = ConnectionThermalManager(warmup_manager, metrics)
        
        # Check connection temperature
        if await thermal_manager.check_temperature('encoder_1', 'conn_123'):
            await thermal_manager.start_cooling('encoder_1', 'conn_123', 'high_load')
        ```
    """
    
    def __init__(self, 
                 warmup_manager: HeloWarmupManager,
                 metrics: EnhancedErrorMetrics):
        self.warmup_manager = warmup_manager
        self.metrics = metrics
        self.thermal_metrics = ConnectionThermalMetrics()
        
        # Thermal thresholds
        self.thresholds = {
            'temperature_high': 80,  # Connection temperature threshold
            'load_high': 75,         # Load percentage threshold
            'burst_limit': 100,      # Max requests per cooling period
            'cooling_period': 60,    # Cooling period in seconds
            'gradual_cooldown': 5    # Gradual cooldown steps
        }
        
        self._connection_stats: Dict[str, Dict] = {}
        self._cooling_tasks: Dict[str, asyncio.Task] = {}

    async def check_temperature(self, encoder_id: str, connection_id: str) -> bool:
        """
        Check if a connection needs cooling based on its current temperature.

        Args:
            encoder_id (str): The ID of the encoder to check
            connection_id (str): The specific connection ID to check

        Returns:
            bool: True if cooling is needed, False otherwise

        Example:
            ```python
            needs_cooling = await thermal_manager.check_temperature('encoder_1', 'conn_123')
            if needs_cooling:
                await thermal_manager.start_cooling('encoder_1', 'conn_123', 'preventive')
            ```
        """
        stats = self._connection_stats.get(connection_id, {})
        current_temp = self._calculate_temperature(stats)
        
        self.thermal_metrics.connection_temperature.labels(
            encoder_id, connection_id
        ).set(current_temp)
        
        return current_temp > self.thresholds['temperature_high']

    async def start_cooling(self, encoder_id: str, connection_id: str, reason: str):
        """
        Initiate a gradual cooling procedure for a connection.

        Implements a stepped cooling process to gracefully reduce connection load
        while maintaining service availability.

        Args:
            encoder_id (str): The ID of the encoder
            connection_id (str): The connection to cool
            reason (str): Reason for cooling (e.g., 'high_load', 'preventive')

        Example:
            ```python
            await thermal_manager.start_cooling(
                'encoder_1', 
                'conn_123', 
                'high_temperature'
            )
            ```
        """
        if connection_id not in self._cooling_tasks:
            self._cooling_tasks[connection_id] = asyncio.create_task(
                self._cooling_procedure(encoder_id, connection_id, reason)
            )
            
            self.thermal_metrics.cooling_events.labels(
                encoder_id, reason
            ).inc()

    async def _cooling_procedure(self, 
                               encoder_id: str, 
                               connection_id: str, 
                               reason: str):
        """
        Execute the gradual cooling procedure for a connection.

        Implements a multi-step cooling process that gradually reduces load while
        monitoring connection health.

        Args:
            encoder_id (str): The ID of the encoder
            connection_id (str): The connection being cooled
            reason (str): The reason for cooling

        Internal method used by start_cooling().
        """
        start_time = datetime.utcnow()
        
        try:
            # Gradual load reduction
            current_load = self._get_connection_load(connection_id)
            step_reduction = current_load / self.thresholds['gradual_cooldown']
            
            for step in range(self.thresholds['gradual_cooldown']):
                target_load = current_load - (step_reduction * (step + 1))
                await self._set_connection_load(encoder_id, connection_id, target_load)
                await asyncio.sleep(self.thresholds['cooling_period'] / self.thresholds['gradual_cooldown'])
            
            # Complete cooldown
            await self._complete_cooldown(encoder_id, connection_id)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.thermal_metrics.cooling_duration.observe(duration)
            
        except Exception as e:
            # Handle cooling failure
            await self._handle_cooling_failure(encoder_id, connection_id, str(e))
        
        finally:
            if connection_id in self._cooling_tasks:
                del self._cooling_tasks[connection_id]

    async def _set_connection_load(self, 
                                 encoder_id: str, 
                                 connection_id: str, 
                                 target_load: float):
        """Set connection load level"""
        self._connection_stats[connection_id] = {
            'target_load': target_load,
            'last_updated': datetime.utcnow()
        }
        
        self.thermal_metrics.connection_load.labels(encoder_id).set(target_load)

    async def _complete_cooldown(self, encoder_id: str, connection_id: str):
        """Complete cooldown and prepare for warmup"""
        # Reset connection stats
        self._connection_stats[connection_id] = {
            'temperature': 0,
            'load': 0,
            'request_count': 0,
            'last_reset': datetime.utcnow()
        }
        
        # Initiate warmup if needed
        await self.warmup_manager.schedule_warmup(encoder_id)

    def _calculate_temperature(self, stats: Dict) -> float:
        """Calculate connection temperature score"""
        if not stats:
            return 0.0
            
        factors = {
            'request_rate': 0.4,
            'error_rate': 0.3,
            'load_factor': 0.3
        }
        
        temperature = (
            (stats.get('request_rate', 0) * factors['request_rate']) +
            (stats.get('error_rate', 0) * factors['error_rate']) +
            (stats.get('load', 0) * factors['load_factor'])
        )
        
        return min(100.0, temperature)

    async def _handle_cooling_failure(self, 
                                    encoder_id: str, 
                                    connection_id: str, 
                                    error: str):
        """Handle cooling procedure failure"""
        # Force connection reset
        await self.warmup_manager.force_reset_connection(encoder_id, connection_id)
        
        # Update metrics
        self.metrics.record_error({
            'type': 'cooling_failure',
            'encoder_id': encoder_id,
            'connection_id': connection_id,
            'error': error
        }) 

    async def reduce_load(self, encoder_id: str):
        """
        Reduce the load on the encoder to manage temperature.
        
        Args:
            encoder_id (str): The ID of the encoder to adjust.
        """
        try:
            # Fetch the encoder's current parameters
            encoder = await HeloEncoder.query.get(encoder_id)
            if not encoder:
                raise ValueError(f"Encoder {encoder_id} not found")

            # Adjust parameters to reduce load
            encoder.device_parameters.width = 1280  # Reduce to 720p
            encoder.device_parameters.height = 720
            encoder.device_parameters.video_bit_rate = 5000  # Lower bitrate
            encoder.device_parameters.frame_rate = "Half"  # Reduce FPS
            encoder.device_parameters.video_geometry = VideoGeometry.MANUAL  # Ensure manual settings

            # Log the adjustment
            self.logger.info(f"Load reduced for encoder {encoder_id} to manage temperature.")
            
            # Optionally, update the encoder's settings in the database or device
            await self._apply_encoder_settings(encoder)

        except Exception as e:
            self.logger.error(f"Failed to reduce load for encoder {encoder_id}: {str(e)}")

    async def _apply_encoder_settings(self, encoder: HeloEncoder):
        """
        Apply the updated settings to the encoder.
        
        Args:
            encoder (HeloEncoder): The encoder with updated settings.
            
        Raises:
            EncoderError: If settings cannot be applied to the encoder.
        """
        try:
            # Get client for this encoder
            client = await self.encoder_service.get_client(encoder.id)
            
            # Build settings dict from device parameters
            settings = {
                'Video Bit Rate': encoder.device_parameters.video_bit_rate,
                'Frame Rate': encoder.device_parameters.frame_rate,
                'Video Geometry': encoder.device_parameters.video_geometry.value,
                'Width': encoder.device_parameters.width,
                'Height': encoder.device_parameters.height
            }

            # Update encoder settings through encoder service
            await self.encoder_service.update_encoder_settings(encoder.id, settings)

            # Update database record
            await db.session.commit()

            self.logger.info(f"Successfully applied thermal management settings to encoder {encoder.id}")

        except Exception as e:
            self.logger.error(f"Failed to apply settings to encoder {encoder.id}: {str(e)}")
            raise EncoderError(
                f"Failed to apply thermal settings: {str(e)}",
                encoder_id=encoder.id,
                error_type="settings_update"
            )
        pass 
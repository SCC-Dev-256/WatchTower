from typing import Dict, List, Optional
from app.core.base_service import BaseService
from app.core.error_handling.errors.exceptions import EncoderError
from app.core.database.models.encoder import HeloEncoder, EncoderMetrics
from app.core.enums import EncoderStatus, StreamingState
from app.core.database import db
from datetime import datetime, timedelta
from app.core.aja.aja_client import AJAHELOClient
from app.core.aja.aja_parameters import AJAParameterManager
from app.core.aja.aja_constants import AJAStreamParams
from app.core.error_handling.decorators import handle_errors
from app.core.error_handling.ErrorLogging import ErrorLogger
from app.core.error_handling.analysis import ErrorAnalyzer
from app.core.error_handling.performance_monitoring import PerformanceMonitor
from app.core.error_handling.helo_error_tracking import ErrorTracking
from app.core.error_handling.handlers import ErrorHandler


class EncoderService(BaseService):
    """Encoder management service"""

    def __init__(self):
        self.param_manager = AJAParameterManager()
        self._clients = {}  # Cache of AJA clients

    @handle_errors()
    async def _op_get_encoder(self, encoder_id: str) -> Dict:
        """Get encoder details"""
        encoder = await HeloEncoder.query.get(encoder_id)
        if not encoder:
            raise EncoderError(
                "Encoder not found",
                encoder_id=encoder_id
            )
        return encoder.to_dict()

    @handle_errors()
    async def _op_list_encoders(self) -> List[Dict]:
        """List all encoders"""
        encoders = await HeloEncoder.query.all()
        return [encoder.to_dict() for encoder in encoders]

    @handle_errors()
    async def _op_create_encoder(self, data: Dict) -> Dict:
        """Create new encoder"""
        await self._validate_params(data, ['name', 'ip_address', 'port'])
        
        existing = await HeloEncoder.query.filter_by(ip_address=data['ip_address']).first()
        if existing:
            raise EncoderError(
                "Encoder with this IP already exists",
                encoder_id=existing.id,
                error_type="duplicate"
            )

        encoder = HeloEncoder(
            name=data['name'],
            ip_address=data['ip_address'],
            port=data['port'],
            status=EncoderStatus.OFFLINE,
            streaming_state=StreamingState.STOPPED,
            created_at=datetime.utcnow()
        )
        
        db.session.add(encoder)
        await db.session.commit()
        
        return encoder.to_dict()

    async def _op_update_encoder(self, encoder_id: str, data: Dict) -> Dict:
        """Update encoder details"""
        encoder = await HeloEncoder.query.get(encoder_id)
        if not encoder:
            raise EncoderError(
                "Encoder not found",
                encoder_id=encoder_id
            )

        # Update allowed fields
        allowed_fields = ['name', 'status', 'streaming_state', 'config']
        for field in allowed_fields:
            if field in data:
                setattr(encoder, field, data[field])

        await db.session.commit()
        return encoder.to_dict()

    async def _op_start_stream(self, encoder_id: str, stream_config: Dict) -> Dict:
        """Start streaming"""
        await self._validate_params(stream_config, ['bitrate', 'resolution'])
        
        encoder = await HeloEncoder.query.get(encoder_id)
        if not encoder:
            raise EncoderError(
                "Encoder not found",
                encoder_id=encoder_id
            )

        if encoder.status != EncoderStatus.ONLINE:
            raise EncoderError(
                "Encoder is not online",
                encoder_id=encoder_id,
                error_type="invalid_state"
            )

        try:
            # Configure stream settings
            await self._configure_stream(encoder, stream_config)
            
            # Start the stream
            await encoder.start_stream()
            
            # Update encoder state
            encoder.streaming_state = StreamingState.STREAMING
            await db.session.commit()

            return {
                "status": "streaming",
                "stream_info": await self._get_stream_info(encoder)
            }
        except Exception as e:
            raise EncoderError(
                f"Failed to start stream: {str(e)}",
                encoder_id=encoder_id,
                error_type="stream_start"
            )

    async def _op_stop_stream(self, encoder_id: str) -> Dict:
        """Stop streaming"""
        encoder = await HeloEncoder.query.get(encoder_id)
        if not encoder:
            raise EncoderError(
                "Encoder not found",
                encoder_id=encoder_id
            )

        try:
            await encoder.stop_stream()
            encoder.streaming_state = StreamingState.STOPPED
            await db.session.commit()
            
            return {
                "status": "stopped",
                "encoder_id": encoder_id
            }
        except Exception as e:
            raise EncoderError(
                f"Failed to stop stream: {str(e)}",
                encoder_id=encoder_id,
                error_type="stream_stop"
            )

    async def _configure_stream(self, encoder: HeloEncoder, config: Dict) -> None:
        """Configure stream settings"""
        try:
            await encoder.configure_stream(
                bitrate=config['bitrate'],
                resolution=config['resolution'],
                fps=config.get('fps', 30),
                keyframe_interval=config.get('keyframe_interval', 2)
            )
        except Exception as e:
            raise EncoderError(
                f"Stream configuration failed: {str(e)}",
                encoder_id=encoder.id,
                error_type="configuration"
            )

    async def _get_stream_info(self, encoder: HeloEncoder) -> Dict:
        """Get current stream information"""
        return {
            "bitrate": encoder.current_bitrate,
            "resolution": encoder.current_resolution,
            "fps": encoder.current_fps,
            "uptime": encoder.stream_uptime,
            "status": encoder.streaming_state.value
        }

    async def _op_get_metrics(self, encoder_id: str, start_time: Optional[str] = None, 
                            end_time: Optional[str] = None) -> Dict:
        """Get encoder metrics"""
        encoder = await self._get_encoder_or_error(encoder_id)
        
        query = EncoderMetrics.query.filter(EncoderMetrics.encoder_id == encoder_id)
        if start_time:
            query = query.filter(EncoderMetrics.timestamp >= start_time)
        if end_time:
            query = query.filter(EncoderMetrics.timestamp <= end_time)
            
        metrics = await query.all()
        return {
            "encoder_id": encoder_id,
            "metrics": [metric.to_dict() for metric in metrics]
        }

    async def _op_get_status(self, encoder_id: str) -> Dict:
        """Get encoder status"""
        encoder = await self._get_encoder_or_error(encoder_id)
        
        # Get latest metrics
        latest_metrics = await EncoderMetrics.query.filter(
            EncoderMetrics.encoder_id == encoder_id
        ).order_by(EncoderMetrics.timestamp.desc()).first()
        
        return {
            "encoder_id": encoder_id,
            "status": encoder.status.value,
            "streaming_state": encoder.streaming_state.value,
            "last_checked": encoder.last_checked.isoformat(),
            "current_metrics": latest_metrics.to_dict() if latest_metrics else None
        }

    async def _op_get_system_status(self) -> Dict:
        """Get system-wide encoder status"""
        encoders = await HeloEncoder.query.all()
        
        summary = {
            "total": len(encoders),
            "online": sum(1 for e in encoders if e.status == EncoderStatus.ONLINE),
            "streaming": sum(1 for e in encoders if e.streaming_state == StreamingState.STREAMING),
            "offline": sum(1 for e in encoders if e.status == EncoderStatus.OFFLINE),
            "not_checked": sum(1 for e in encoders if 
                             e.last_checked < datetime.utcnow() - timedelta(minutes=5))
        }
        
        # Update Prometheus metrics if configured
        if self.config.get('PROMETHEUS_ENABLED'):
            self._update_prometheus_metrics(summary)
            
        return summary

    async def _get_encoder_or_error(self, encoder_id: str) -> HeloEncoder:
        """Helper to get encoder or raise error"""
        encoder = await HeloEncoder.query.get(encoder_id)
        if not encoder:
            raise EncoderError(
                "Encoder not found",
                encoder_id=encoder_id
            )
        return encoder

    async def update_encoder_settings(self, encoder_id: str, settings: Dict) -> Dict:
        """Update encoder settings with validation"""
        for param_name, value in settings.items():
            if not self.param_manager.validate_value(param_name, value):
                raise EncoderError(
                    f"Invalid value for parameter: {param_name}",
                    encoder_id=encoder_id,
                    error_type="invalid_parameter"
                )

        # Reference existing parameters from CSV
        if 'Video Bit Rate' in settings:
            await self._validate_bitrate(settings['Video Bit Rate'])
        
        if 'Frame Rate' in settings:
            await self._validate_framerate(settings['Frame Rate'])

        return await self._apply_settings(encoder_id, settings)

    async def get_client(self, encoder_id: str) -> AJAHELOClient:
        """Get or create AJA HELO client for encoder"""
        if encoder_id not in self._clients:
            encoder = await self.get_encoder(encoder_id)
            self._clients[encoder_id] = AJAHELOClient(encoder.ip_address)
        return self._clients[encoder_id]

    async def start_stream(self, encoder_id: str, config: Dict) -> Dict:
        """Start streaming on encoder with configuration"""
        async with await self.get_client(encoder_id) as client:
            # First configure the stream
            await client.configure_stream({
                AJAStreamParams.VIDEO_SOURCE: config.get('video_source', 'HDMI'),
                AJAStreamParams.AUDIO_SOURCE: config.get('audio_source', 'HDMI'),
                AJAStreamParams.VIDEO_BITRATE: config.get('bitrate', 5000000),
                AJAStreamParams.FRAME_RATE: config.get('fps', '29.97'),
                AJAStreamParams.STREAM_URL: config['stream_url']
            })
            
            # Then start streaming
            return await client.start_stream()

    async def get_encoder_status(self, encoder_id: str) -> Dict:
        """Get comprehensive encoder status"""
        async with await self.get_client(encoder_id) as client:
            return {
                'system': await client.get_system_status(),
                'stream': await client.get_stream_status(),
                'network': await client.get_network_stats(),
                'media': await client.get_media_status()
            }
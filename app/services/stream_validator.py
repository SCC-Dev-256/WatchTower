from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from .load_balancer import StreamingConfig
from app.core.aja.aja_parameters import AJAParameterManager
from app.core.aja.aja_constants import AJAStreamParams
from app.core.error_handling.decorators import handle_errors
from app.core.auth import require_api_key, roles_required

@dataclass
class StreamValidationResult:
    valid: bool
    issues: List[str]
    warnings: List[str]
    details: Dict

class StreamConfigValidator:
    """Validate streaming configuration parameters"""
    
    def __init__(self):
        self.valid_resolutions = [
            "1920x1080", "1280x720", "854x480", "640x360"
        ]
        self.valid_fps = [24, 25, 29.97, 30, 50, 59.94, 60]
        self.min_bitrate = 1_000_000  # 1 Mbps
        self.max_bitrate = 20_000_000  # 20 Mbps
        self.param_manager = AJAParameterManager()

    @handle_errors()
    @roles_required('admin', 'editor')
    @require_api_key
    def validate_config(self, config: StreamingConfig) -> StreamValidationResult:
        """Validate streaming configuration"""
        issues = []
        warnings = []
        details = {}

        # Validate Resolution
        if config.resolution not in self.valid_resolutions:
            issues.append(f"Invalid resolution: {config.resolution}")
        
        # Validate FPS
        if config.fps not in self.valid_fps:
            closest_fps = min(self.valid_fps, key=lambda x: abs(x - config.fps))
            warnings.append(f"Non-standard FPS: {config.fps}. Consider using {closest_fps}")
        
        # Validate Bitrate
        if config.bitrate < self.min_bitrate:
            issues.append(f"Bitrate too low: {config.bitrate/1_000_000}Mbps")
        elif config.bitrate > self.max_bitrate:
            issues.append(f"Bitrate too high: {config.bitrate/1_000_000}Mbps")
        
        # Calculate recommended bitrate for resolution
        recommended_bitrate = self._calculate_recommended_bitrate(
            config.resolution, config.fps
        )
        if abs(config.bitrate - recommended_bitrate) > recommended_bitrate * 0.3:
            warnings.append(
                f"Bitrate {config.bitrate/1_000_000}Mbps may not be optimal for "
                f"{config.resolution} at {config.fps}fps"
            )
        
        # Check RTMP key format
        if not self._validate_rtmp_key(config.rtmp_key):
            issues.append("Invalid RTMP stream key format")

        details = {
            'recommended_bitrate': recommended_bitrate,
            'bitrate_efficiency': config.bitrate / recommended_bitrate,
            'resolution_supported': config.resolution in self.valid_resolutions,
            'fps_supported': config.fps in self.valid_fps
        }

        return StreamValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            details=details
        )

    def _calculate_recommended_bitrate(self, resolution: str, fps: float) -> int:
        """Calculate recommended bitrate based on resolution and fps"""
        width, height = map(int, resolution.split('x'))
        pixels = width * height
        
        # Base bitrate calculation (based on resolution)
        if pixels <= 230400:  # 480p
            base_bitrate = 2_000_000
        elif pixels <= 921600:  # 720p
            base_bitrate = 4_500_000
        else:  # 1080p
            base_bitrate = 8_000_000
        
        # Adjust for frame rate
        if fps > 30:
            base_bitrate *= 1.5
        
        return int(base_bitrate)

    @handle_errors()
    @roles_required('admin', 'editor')
    @require_api_key
    def _validate_rtmp_key(self, key: str) -> bool:
        """Validate RTMP stream key format"""
        if not key or len(key) < 10:
            return False
        
        # Add your specific RTMP key validation rules here
        return True 

    @roles_required('admin', 'editor')
    @require_api_key    
    @handle_errors()
    async def validate_stream_config(self, config: Dict) -> Tuple[bool, List[str]]:
        """Validate stream configuration using AJA parameters"""
        errors = []
        
        # Validate each parameter against AJA specifications
        for param_name, value in config.items():
            if not self.param_manager.validate_value(param_name, value):
                errors.append(f"Invalid value for {param_name}: {value}")

        # Check required parameters
        required_params = [
            AJAStreamParams.VIDEO_SOURCE,
            AJAStreamParams.STREAM_FORMAT,
            AJAStreamParams.VIDEO_BITRATE
        ]
        
        for param in required_params:
            if param not in config:
                errors.append(f"Missing required parameter: {param}")

        return len(errors) == 0, errors
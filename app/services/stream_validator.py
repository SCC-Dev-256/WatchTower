from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from .encoder_backup_fail_over import StreamingConfig
from app.core.aja.aja_helo_parameter_service import AJAParameterManager
from app.core.aja.aja_constants import AJAStreamParams
from app.core.error_handling.decorators import handle_errors
from app.core.auth import require_api_key, roles_required
from abc import ABC, abstractmethod

@dataclass
class StreamValidationResult:
    valid: bool
    issues: List[str]
    warnings: List[str]
    details: Dict

class BaseValidator(ABC):
    @abstractmethod
    def validate(self, config: StreamingConfig) -> StreamValidationResult:
        pass

class ResolutionValidator(BaseValidator):
    def __init__(self, valid_resolutions):
        self.valid_resolutions = valid_resolutions

    def validate(self, config: StreamingConfig) -> StreamValidationResult:
        issues = []
        if config.resolution not in self.valid_resolutions:
            issues.append(f"Invalid resolution: {config.resolution}")
        return StreamValidationResult(valid=len(issues) == 0, issues=issues, warnings=[], details={})

class FPSValidator(BaseValidator):
    def __init__(self, valid_fps):
        self.valid_fps = valid_fps

    def validate(self, config: StreamingConfig) -> StreamValidationResult:
        warnings = []
        if config.fps not in self.valid_fps:
            closest_fps = min(self.valid_fps, key=lambda x: abs(x - config.fps))
            warnings.append(f"Non-standard FPS: {config.fps}. Consider using {closest_fps}")
        return StreamValidationResult(valid=True, issues=[], warnings=warnings, details={})

class BitrateValidator(BaseValidator):
    def __init__(self, min_bitrate, max_bitrate):
        self.min_bitrate = min_bitrate
        self.max_bitrate = max_bitrate

    def validate(self, config: StreamingConfig) -> StreamValidationResult:
        issues = []
        if config.bitrate < self.min_bitrate:
            issues.append(f"Bitrate too low: {config.bitrate/1_000_000}Mbps")
        elif config.bitrate > self.max_bitrate:
            issues.append(f"Bitrate too high: {config.bitrate/1_000_000}Mbps")
        return StreamValidationResult(valid=len(issues) == 0, issues=issues, warnings=[], details={})

class StreamConfigValidator:
    """Validate streaming configuration parameters"""
    
    def __init__(self):
        self.resolution_validator = ResolutionValidator([
            "1920x1080", "1280x720", "854x480", "640x360"
        ])
        self.fps_validator = FPSValidator([24, 25, 29.97, 30, 50, 59.94, 60])
        self.bitrate_validator = BitrateValidator(1_000_000, 20_000_000)
        self.param_manager = AJAParameterManager()

    @handle_errors()
    @roles_required('admin', 'editor')
    @require_api_key
    def validate_config(self, config: StreamingConfig) -> StreamValidationResult:
        """Validate streaming configuration"""
        results = [
            self.resolution_validator.validate(config),
            self.fps_validator.validate(config),
            self.bitrate_validator.validate(config)
        ]

        # Aggregate results
        valid = all(result.valid for result in results)
        issues = [issue for result in results for issue in result.issues]
        warnings = [warning for result in results for warning in result.warnings]
        details = {key: value for result in results for key, value in result.details.items()}

        return StreamValidationResult(valid=valid, issues=issues, warnings=warnings, details=details)

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
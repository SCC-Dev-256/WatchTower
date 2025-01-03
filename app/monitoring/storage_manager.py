from typing import List, Dict
from datetime import datetime
import logging
from app.core.security.rbac import roles_required

class StorageManager:
    def __init__(self, device):
        self.device = device
        self.logger = logging.getLogger(__name__)
        self.reboot_threshold = 3
        self.reboot_window = 300  # 5 minutes

    @roles_required('admin', 'editor')
    def check_storage_health(self) -> Dict:
        """Check health of both storage devices"""
        try:
            storage1 = self.device.get_param("eParamID_Storage1Status")
            storage2 = self.device.get_param("eParamID_Storage2Status")
            
            return {
                "storage1": {
                    "status": storage1["value"],
                    "healthy": self._is_storage_healthy(storage1)
                },
                "storage2": {
                    "status": storage2["value"],
                    "healthy": self._is_storage_healthy(storage2)
                }
            }
        except Exception as e:
            self.logger.error(f"Storage health check failed: {str(e)}")
            return {"error": str(e)}

    @roles_required('admin')
    def handle_reboot_cycle(self, reboot_history: List[datetime]) -> Dict:
        """Handle device stuck in reboot cycle"""
        if self._is_in_reboot_cycle(reboot_history):
            self.logger.warning("Reboot cycle detected, attempting storage mitigation")
            return self._mitigate_storage_issues()
        return {"status": "normal"}
    
    @roles_required('admin')
    def _mitigate_storage_issues(self) -> Dict:
        """Try disabling storage devices one at a time"""
        storage_status = self.check_storage_health()
        
        # Try disabling storage 1 first
        if not storage_status["storage1"]["healthy"]:
            self.logger.info("Attempting to disable Storage 1")
            try:
                self.device.set_param("eParamID_Storage1Enable", 0)
                return {"action": "disabled_storage1", "status": "waiting"}
            except Exception as e:
                self.logger.error(f"Failed to disable Storage 1: {str(e)}")
        
        # If still having issues, try disabling storage 2
        if not storage_status["storage2"]["healthy"]:
            self.logger.info("Attempting to disable Storage 2")
            try:
                self.device.set_param("eParamID_Storage2Enable", 0)
                return {"action": "disabled_storage2", "status": "waiting"}
            except Exception as e:
                self.logger.error(f"Failed to disable Storage 2: {str(e)}")
        
        return {"status": "critical", "message": "Unable to resolve storage issues"}
    
    @roles_required('admin')
    def _is_in_reboot_cycle(self, reboot_history: List[datetime]) -> bool:
        """Determine if device is in reboot cycle"""
        if len(reboot_history) < self.reboot_threshold:
            return False
            
        recent_reboots = [
            dt for dt in reboot_history 
            if (datetime.now() - dt).total_seconds() < self.reboot_window
        ]
        
        return len(recent_reboots) >= self.reboot_threshold 

    @roles_required('admin')
    def clear_storage(self, encoder_id: str):
        """Clear storage for a specific encoder."""
        # Implement storage clearing logic
        pass 
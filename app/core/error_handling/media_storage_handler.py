from typing import List
from app.core.error_handling.error_logging import ErrorLogger


class StorageHandler:
    def __init__(self):
        self.logger = ErrorLogger()
        self.storage_types = {
            'SD': 'SD Card Record Path',
            'USB': 'USB Record Path', 
            'SMB': 'SMB Network Record Path',
            'NFS': 'NFS Network Record Path'
        }
        self.restart_keywords = ["initialization", "assigning", "network access"]

    async def dismount_storage(self, encoder_id: str, path: str):
        """Safely dismount a storage path for an encoder"""
        try:
            mounted_param = f'{path} Mounted'
            await self._set_device_param(encoder_id, mounted_param, False)
            self.logger.info(f"Successfully dismounted {path} for encoder {encoder_id}")
            
            # Monitor for restart after dismount
            await self._monitor_restart_loop(encoder_id)
            
        except Exception as e:
            self.logger.error(f"Failed to dismount {path} for encoder {encoder_id}: {str(e)}")
            raise

    async def mount_storage(self, encoder_id: str, path: str) -> bool:
        """Attempt to mount storage path for an encoder"""
        try:
            mounted_param = f'{path} Mounted'
            await self._set_device_param(encoder_id, mounted_param, True)
            
            # Monitor for restart after mount attempt
            await self._monitor_restart_loop(encoder_id)
            
            if self.metrics['restart_count'].labels(encoder_id).get() > 2:
                self.logger.warning(f"Storage {path} causing restarts on {encoder_id}, dismounting")
                await self.dismount_storage(encoder_id, path)
                return False
                
            self.logger.info(f"Successfully mounted {path} for encoder {encoder_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to mount {path} for encoder {encoder_id}: {str(e)}")
            return False

    def get_storage_paths_from_config(self, encoder_id: str) -> List[str]:
        """Get configured storage paths for an encoder"""
        paths = []
        for storage_type in self.storage_types.values():
            if self._get_device_param(encoder_id, storage_type):
                paths.append(storage_type)
        return paths

    async def _monitor_restart_loop(self, encoder_id: str):
        """Monitor encoder logs for restart patterns"""
        log_data = await self._get_device_logs(encoder_id)
        log_lines = log_data.splitlines()
        
        if len(log_lines) <= 10:
            if any(keyword in line.lower() for line in log_lines for keyword in self.restart_keywords):
                self.logger.critical(
                    "Storage corrupt reboot cycle detected",
                    extra={
                        'encoder_id': encoder_id,
                        'anomaly_type': 'Storage Reboot Cycle'
                    }
                )
                self.metrics['storage_failures'].labels(encoder_id).inc()
                await self._handle_corrupted_storage(encoder_id)
                return

        restart_count = self.metrics['restart_count'].labels(encoder_id).inc()
        if restart_count > 3:
            self.logger.warning(f"Encoder {encoder_id} has restarted {restart_count} times")
            await self._take_preventive_action(encoder_id)
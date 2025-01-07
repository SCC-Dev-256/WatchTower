from typing import List
from app.core.error_handling.ErrorLogging import ErrorLogger
from app.core.error_handling.restart_monitor import RestartMonitor


class StorageHandler:
    def __init__(self):
        self.logger = ErrorLogger()
        self.storage_types = {
            'SD': 'SD Card Record Path',
            'USB': 'USB Record Path', 
            'SMB': 'SMB Network Record Path',
            'NFS': 'NFS Network Record Path'
        }

    async def dismount_storage(self, encoder_id: str, path: str):
        """Safely dismount a storage path for an encoder
        
        Args:
            encoder_id (str): ID of the encoder
            path (str): Storage path to dismount
        """
        try:
            # Set mounted parameter to False to dismount
            mounted_param = f'{path} Mounted'
            await self._set_device_param(encoder_id, mounted_param, False)
            self.logger.info(f"Successfully dismounted {path} for encoder {encoder_id}")
            
            # Monitor for restart after dismount
            restart_monitor = RestartMonitor()
            await restart_monitor.monitor_restart_loop(encoder_id)
            
        except Exception as e:
            self.logger.error(f"Failed to dismount {path} for encoder {encoder_id}: {str(e)}")
            raise

    async def mount_storage(self, encoder_id: str, path: str) -> bool:
        """Attempt to mount storage path for an encoder
        
        Args:
            encoder_id (str): ID of the encoder
            path (str): Storage path to mount
            
        Returns:
            bool: True if mount successful, False otherwise
        """
        try:
            # Set mounted parameter to True to mount
            mounted_param = f'{path} Mounted'
            await self._set_device_param(encoder_id, mounted_param, True)
            
            # Monitor for restart after mount attempt
            restart_monitor = RestartMonitor()
            await restart_monitor.monitor_restart_loop(encoder_id)
            
            # If we detect restarts, dismount the problematic drive
            if restart_monitor.metrics['restart_count'].labels(encoder_id).get() > 2:
                self.logger.warning(f"Storage {path} causing restarts on {encoder_id}, dismounting")
                await self.dismount_storage(encoder_id, path)
                return False
                
            self.logger.info(f"Successfully mounted {path} for encoder {encoder_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to mount {path} for encoder {encoder_id}: {str(e)}")
            return False

    def get_storage_paths_from_config(self, encoder_id: str) -> List[str]:
        """Get configured storage paths for an encoder
        
        Args:
            encoder_id (str): ID of the encoder
            
        Returns:
            List[str]: List of configured storage paths
        """
        paths = []
        for storage_type in self.storage_types.values():
            # Check if path is configured in encoder settings
            if self._get_device_param(encoder_id, storage_type):
                paths.append(storage_type)
        return paths
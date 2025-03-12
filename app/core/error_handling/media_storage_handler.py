from typing import List
from app.core.error_handling import ErrorLogger

# This file contains the StorageHandler class, which is used to handle storage operations for encoders.
# The StorageHandler class has the following methods:
# - dismount_storage: Dismounts a storage path for an encoder.
# - mount_storage: Mounts a storage path for an encoder.
# - get_storage_paths_from_config: Gets the storage paths for an encoder from the configuration.
# - monitor_restart_loop: Monitors the encoder logs for restart patterns.

# The following areas are blank and require input from the user:
# - Additional error handling logic for specific error types or logging requirements that are not yet defined.
# - Configuration details for retry logic, such as exponential backoff or jitter, that may need customization.
# - Any additional metrics or logging categories that the user might want to track.
# - Specific logic for handling different error types in the `dismount_storage` and `mount_storage` methods.
# - Detailed implementation for methods like `monitor_restart_loop` and `_handle_corrupted_storage`.

# Levels of abstraction that need to be made specific:
# 1. Error Handling Logic: Define specific logic for handling different types of errors (e.g., network, streaming, recording).
# 2. Retry Logic: Customize and add any additional retry mechanisms, such as exponential backoff or jitter.
# 3. Metrics: Customize and add any additional metrics that need to be tracked.
# 4. Logging: Configure log formatting and output destinations as per the application's requirements.
# 5. Error Analysis: Implement detailed logic for analyzing errors and providing insights.
# 6. Error Entry Creation: Ensure the error data captures all necessary details for each error type.
# 7. Error Processing: Define the specific steps to process and handle each error type in the `dismount_storage` and `mount_storage` methods.



class StorageHandler:
    """
    A class to handle storage operations for encoders, including mounting,
    dismounting, and monitoring for restart patterns.

    This class provides methods to manage storage paths, monitor encoder logs
    for restart patterns, and log any issues encountered during storage operations.
    """

    def __init__(self):
        """
        Initialize the StorageHandler with a logger and predefined storage types.
        """
        self.logger = ErrorLogger()
        self.storage_types = {
            'SD': 'SD Card Record Path',
            'USB': 'USB Record Path', 
            'SMB': 'SMB Network Record Path',
            'NFS': 'NFS Network Record Path'
        }
        self.restart_keywords = ["initialization", "assigning", "network access"]

    async def dismount_storage(self, encoder_id: str, path: str):
        """
        Safely dismount a storage path for an encoder.

        Args:
            encoder_id (str): The ID of the encoder.
            path (str): The storage path to dismount.

        Raises:
            Exception: If dismounting fails.
        """
        try:
            mounted_param = f'{path} Mounted'
            await self._set_device_param(encoder_id, mounted_param, False)
            self.logger.info(f"Successfully dismounted {path} for encoder {encoder_id}")
            
            # Monitor for restart after dismount
            await self.monitor_restart_loop(encoder_id)
            
        except Exception as e:
            self.logger.error(f"Failed to dismount {path} for encoder {encoder_id}: {str(e)}")
            raise

    async def mount_storage(self, encoder_id: str, path: str) -> bool:
        """
        Attempt to mount a storage path for an encoder.

        Args:
            encoder_id (str): The ID of the encoder.
            path (str): The storage path to mount.

        Returns:
            bool: True if mounting is successful, False otherwise.
        """
        try:
            mounted_param = f'{path} Mounted'
            await self._set_device_param(encoder_id, mounted_param, True)
            
            # Monitor for restart after mount attempt
            await self.monitor_restart_loop(encoder_id)
            
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
        """
        Get configured storage paths for an encoder.

        Args:
            encoder_id (str): The ID of the encoder.

        Returns:
            List[str]: A list of storage paths configured for the encoder.
        """
        paths = []
        for storage_type in self.storage_types.values():
            if self._get_device_param(encoder_id, storage_type):
                paths.append(storage_type)
        return paths

    async def monitor_restart_loop(self, encoder_id: str):
        """
        Monitor encoder logs for restart patterns.

        Args:
            encoder_id (str): The ID of the encoder.

        Raises:
            Exception: If a storage corruption reboot cycle is detected.
        """
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
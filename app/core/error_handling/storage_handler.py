from typing import List
from app.core.error_handling.ErrorLogging import ErrorLogger

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
        except Exception as e:
            self.logger.error(f"Failed to dismount {path} for encoder {encoder_id}: {str(e)}")
            raise

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
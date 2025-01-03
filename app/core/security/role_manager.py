import json
import os
from typing import Dict, List

class RoleManager:
    def __init__(self, config_path: str = 'app/core/security/roles_config.json'):
        self.config_path = config_path
        self.roles = self._load_roles()

    def _load_roles(self) -> Dict[str, List[str]]:
        """Load roles and permissions from the configuration file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Role configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as file:
            config = json.load(file)
            return config.get('roles', {})

    def get_permissions(self, role: str) -> List[str]:
        """Get permissions for a given role."""
        return self.roles.get(role, [])

    def refresh_roles(self):
        """Refresh roles from the configuration file."""
        self.roles = self._load_roles()

    def has_permission(self, user_roles: List[str], permission: str) -> bool:
        """Check if any of the user's roles have the specified permission."""
        for role in user_roles:
            if permission in self.get_permissions(role):
                return True
        return False 
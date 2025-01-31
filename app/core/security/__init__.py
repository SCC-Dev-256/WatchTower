# config/__init__.py
from .models import Role, Permission
from .rbac import roles_required, permission_required, get_user_roles_and_permissions
from .role_manager import RoleManager
from .security_logger import SecurityEventLogger
from .security_manager import SecurityManager
from .ssl_config import SSLConfig, configure_ssl

def read_nginx_conf():
    """Read the nginx.conf file and return its content."""
    try:
        with open('app/core/security/nginx/nginx.conf', 'r') as file:
            nginx_config_content = file.read()
        return nginx_config_content
    except FileNotFoundError:
        raise FileNotFoundError("nginx.conf file not found in the specified path.")
    except Exception as e:
        raise Exception(f"Error reading nginx.conf: {str(e)}")

__all__ = [
    'Role',
    'Permission',
    'roles_required',
    'permission_required',
    'get_user_roles_and_permissions',
    'RoleManager',
    'SecurityEventLogger',
    'SecurityManager',
    'SSLConfig',
    'configure_ssl',
    'read_nginx_conf'
]
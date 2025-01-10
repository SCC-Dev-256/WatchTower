import logging

# Configure audit logger
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)
handler = logging.FileHandler('audit.log')
formatter = logging.Formatter('%(asctime)s - %(user_id)s - %(action)s - %(resource)s - %(status)s')
handler.setFormatter(formatter)
audit_logger.addHandler(handler)

def log_audit(user_id, action, resource, status):
    """Log an audit entry."""
    audit_logger.info('', extra={
        'user_id': user_id,
        'action': action,
        'resource': resource,
        'status': status
    }) 

def log_role_change(user_id, action, role_name, status):
    """Log role changes."""
    audit_logger.info('', extra={
        'user_id': user_id,
        'action': action,
        'role_name': role_name,
        'status': status
    }) 
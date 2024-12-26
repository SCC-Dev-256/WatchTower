from typing import Any, Dict, Optional
from flask import jsonify
from datetime import datetime

class APIResponse:
    @staticmethod
    def success(data: Any = None, message: str = None, status_code: int = 200) -> tuple:
        response = {
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
        }
        if data is not None:
            response['data'] = data
        if message:
            response['message'] = message
            
        return jsonify(response), status_code

    @staticmethod
    def error(message: str, code: int = 400, details: Optional[Dict] = None) -> tuple:
        response = {
            'success': False,
            'timestamp': datetime.utcnow().isoformat(),
            'error': {
                'message': message,
                'code': code
            }
        }
        if details:
            response['error']['details'] = details
            
        return jsonify(response), code 
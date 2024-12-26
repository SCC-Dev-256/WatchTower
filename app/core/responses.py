from typing import Any, Dict, Optional
from flask import jsonify

class APIResponse:
    @staticmethod
    def success(data: Any = None, message: str = None) -> Dict:
        response = {'success': True}
        if data is not None:
            response['data'] = data
        if message:
            response['message'] = message
        return jsonify(response)

    @staticmethod
    def error(message: str, code: int = 400, details: Optional[Dict] = None) -> Dict:
        response = {
            'success': False,
            'error': {
                'message': message,
                'code': code
            }
        }
        if details:
            response['error']['details'] = details
        return jsonify(response), code 
from typing import Any, Dict, Optional
from flask import jsonify
from datetime import datetime

class APIResponse:
    """
    A utility class for generating standardized API responses in JSON format.

    This class provides static methods to create success and error responses
    that can be used throughout the application to ensure consistency in
    response structure.
    """

    @staticmethod
    def success(data: Any = None, message: str = None, status_code: int = 200) -> tuple:
        """
        Generate a success response.

        Args:
            data (Any, optional): The data to include in the response. Defaults to None.
            message (str, optional): An optional message to include in the response. Defaults to None.
            status_code (int, optional): The HTTP status code for the response. Defaults to 200.

        Returns:
            tuple: A tuple containing the JSON response and the status code.
        """
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
        """
        Generate an error response.

        Args:
            message (str): The error message to include in the response.
            code (int, optional): The HTTP status code for the error. Defaults to 400.
            details (Optional[Dict], optional): Additional details about the error. Defaults to None.

        Returns:
            tuple: A tuple containing the JSON response and the status code.
        """
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
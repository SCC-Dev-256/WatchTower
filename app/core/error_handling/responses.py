from typing import Any, Dict, Optional
from flask import jsonify
from datetime import datetime

# This file contains the APIResponse class, which is used to generate standardized API responses in JSON format.
# The APIResponse class has the following methods:
# - success: Generates a success response.
# - error: Generates an error response.

# The following areas are blank and require input from the user:
# - Additional error handling logic for specific error types or logging requirements that are not yet defined.
# - Configuration details for retry logic, such as exponential backoff or jitter, that may need customization.
# - Any additional metrics or logging categories that the user might want to track.
# - Specific logic for handling different error types in the `success` and `error` methods.
# - Detailed implementation for methods like `success` and `error`.


# Levels of abstraction that need to be made specific:
# 1. Error Handling Logic: Define specific logic for handling different types of errors (e.g., network, streaming, recording).
# 2. Retry Logic: Customize and add any additional retry mechanisms, such as exponential backoff or jitter.
# 3. Metrics: Customize and add any additional metrics that need to be tracked.
# 4. Logging: Configure log formatting and output destinations as per the application's requirements.
# 5. Error Analysis: Implement detailed logic for analyzing errors and providing insights.
# 6. Error Entry Creation: Ensure the error data captures all necessary details for each error type.
# 7. Error Processing: Define the specific steps to process and handle each error type in the `success` and `error` methods.


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
from flask import Blueprint, jsonify, request, current_app
from flask_pydantic import validate
from pydantic import BaseModel
from typing import List

encoder_ops_bp = Blueprint('encoder_ops', __name__)

class BulkOperationRequest(BaseModel):
    encoder_ids: List[int]
    operation: str
    parameters: dict = {}

@encoder_ops_bp.route('/encoders/bulk', methods=['POST'])
@validate()
def bulk_operation(body: BulkOperationRequest):
    """Execute bulk operations on encoders"""
    results = {}
    
    for encoder_id in body.encoder_ids:
        try:
            result = current_app.encoder_manager.execute_operation(
                encoder_id,
                body.operation,
                body.parameters
            )
            results[encoder_id] = {'status': 'success', 'result': result}
        except Exception as e:
            results[encoder_id] = {'status': 'error', 'error': str(e)}
    
    return jsonify(results) 
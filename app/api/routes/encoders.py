from flask import Blueprint, jsonify, request
from app.core.error_handling import handle_errors
from app.models.encoder import HeloEncoder
from app.core.auth import require_api_key
from app.services.encoder_service import EncoderService
from app.core.security.rbac import roles_required, permission_required

encoder_bp = Blueprint('encoders', __name__, url_prefix='/api/encoders')
encoder_service = EncoderService()

@encoder_bp.route('/', methods=['GET'])
@roles_required('admin', 'user')
def list_encoders():
    encoders = HeloEncoder.query.all()
    return jsonify([e.to_dict() for e in encoders])

@encoder_bp.route('/<encoder_id>', methods=['GET'])
@require_api_key
@handle_errors()
async def get_encoder(encoder_id: str):
    """Get encoder details"""
    return await encoder_service.execute('get_encoder', encoder_id=encoder_id)

@encoder_bp.route('/', methods=['POST'])
@require_api_key
@handle_errors()
async def create_encoder():
    """Create new encoder"""
    return await encoder_service.execute('create_encoder', data=request.json)

@encoder_bp.route('/<encoder_id>', methods=['PUT'])
@require_api_key
@handle_errors()
async def update_encoder(encoder_id: str):
    """Update encoder details"""
    return await encoder_service.execute('update_encoder', 
                                       encoder_id=encoder_id, 
                                       data=request.json)

@encoder_bp.route('/<encoder_id>/stream', methods=['POST'])
@require_api_key
@handle_errors()
async def start_stream(encoder_id: str):
    """Start streaming"""
    return await encoder_service.execute('start_stream',
                                       encoder_id=encoder_id,
                                       stream_config=request.json)

@encoder_bp.route('/<encoder_id>/stream', methods=['DELETE'])
@require_api_key
@handle_errors()
async def stop_stream(encoder_id: str):
    """Stop streaming"""
    return await encoder_service.execute('stop_stream', encoder_id=encoder_id)

@encoder_bp.route('/<encoder_id>/metrics', methods=['GET'])
@require_api_key
@handle_errors()
async def get_metrics(encoder_id: str):
    """Get encoder metrics"""
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    return await encoder_service.execute('get_metrics',
                                       encoder_id=encoder_id,
                                       start_time=start_time,
                                       end_time=end_time)

@encoder_bp.route('/<encoder_id>/status', methods=['GET'])
@require_api_key
@handle_errors()
async def get_status(encoder_id: str):
    """Get encoder status"""
    return await encoder_service.execute('get_status', encoder_id=encoder_id)

@encoder_bp.route('/system/status', methods=['GET'])
@require_api_key
@handle_errors()
async def get_system_status():
    """Get system-wide encoder status"""
    return await encoder_service.execute('get_system_status')

@encoder_bp.route('/encoders/<int:encoder_id>', methods=['DELETE'])
@permission_required('delete_encoder')
def delete_encoder(encoder_id):
    # Function implementation
    return jsonify({"message": f"Encoder {encoder_id} deleted"})
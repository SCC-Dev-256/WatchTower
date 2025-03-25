from fastapi import APIRouter, Depends, HTTPException
from app.core.live_transcription.handler_whisper_online import LiveCaptioningService
from app.services.encoder_service import EncoderService
from app.core.auth.auth import require_api_key
from typing import Dict

router = APIRouter()

@router.post("/{encoder_id}/start")
@require_api_key
async def start_transcription(
    encoder_id: str,
    encoder_service: EncoderService = Depends()
):
    """Start transcription for an encoder stream"""
    return await encoder_service.start_transcription(encoder_id)

@router.post("/{encoder_id}/stop")
@require_api_key
async def stop_transcription(
    encoder_id: str,
    encoder_service: EncoderService = Depends()
):
    """Stop transcription for an encoder stream"""
    return await encoder_service.stop_transcription(encoder_id)

@router.get("/{encoder_id}/status")
@require_api_key
async def get_transcription_status(
    encoder_id: str,
    encoder_service: EncoderService = Depends()
):
    """Get transcription status for an encoder"""
    return await encoder_service.get_transcription_status(encoder_id)

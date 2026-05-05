import httpx
from fastapi import APIRouter
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("")
async def get_ai_health():
    """
    Check the health of the AI inference engine.
    If using local Ollama, verify connectivity.
    """
    if not settings.USE_CUSTOM_AI:
        return {
            "status": "connected", 
            "provider": "external", 
            "model": "Groq Llama-3-70B (Fallback)",
            "message": "Connected to Neural Cloud"
        }
    
    try:
        # Ollama API base is usually CUSTOM_AI_URL minus '/v1'
        ollama_base = settings.CUSTOM_AI_URL.replace("/v1", "")
        async with httpx.AsyncClient() as client:
            # Check if Ollama is running
            response = await client.get(ollama_base, timeout=1.0)
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "provider": "local",
                    "model": settings.CUSTOM_AI_MODEL,
                    "message": f"Engine Active: {settings.CUSTOM_AI_MODEL}"
                }
    except Exception as e:
        logger.warning(f"AI Health Check failed: {str(e)}")
        
    return {
        "status": "offline",
        "provider": "local",
        "model": settings.CUSTOM_AI_MODEL,
        "message": "Neural Engine Offline",
        "error": "Ensure Ollama is running and the model is loaded."
    }

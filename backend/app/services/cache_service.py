import json
import hashlib
import logging
from typing import Any, Optional
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger("neuroplan.cache")

class CacheService:
    """
    Asynchronous Redis Cache Service.
    Handles AI response caching and temporary session state.
    """
    def __init__(self):
        self.enabled = settings.REDIS_ENABLED
        self.redis_url = settings.REDIS_URL
        self._client: Optional[redis.Redis] = None

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        return self._client

    def _generate_key(self, prefix: str, data: str) -> str:
        """Generate a deterministic cache key using SHA-256."""
        hash_val = hashlib.sha256(data.encode()).hexdigest()
        return f"neuroplan:{prefix}:{hash_val}"

    async def get_ai_response(self, prompt: str, system_msg: str) -> Optional[Any]:
        if not self.enabled:
            return None
            
        try:
            client = await self._get_client()
            key = self._generate_key("ai", prompt + system_msg)
            cached = await client.get(key)
            
            if cached:
                logger.info("Cache HIT: AI response retrieved from Redis")
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Cache GET error: {e}")
        
        return None

    async def set_ai_response(self, prompt: str, system_msg: str, response: Any, ttl: int = None):
        if not self.enabled:
            return
            
        try:
            client = await self._get_client()
            key = self._generate_key("ai", prompt + system_msg)
            ttl = ttl or settings.AI_CACHE_TTL
            
            await client.set(key, json.dumps(response), ex=ttl)
            logger.info(f"Cache SET: AI response stored with TTL {ttl}s")
        except Exception as e:
            logger.error(f"Cache SET error: {e}")

    async def invalidate_prefix(self, prefix: str):
        """Clear all keys with a certain prefix."""
        if not self.enabled:
            return
        try:
            client = await self._get_client()
            keys = await client.keys(f"neuroplan:{prefix}:*")
            if keys:
                await client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache INVALIDATE error: {e}")

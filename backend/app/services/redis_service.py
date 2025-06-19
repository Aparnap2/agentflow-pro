import json
import asyncio
import redis.asyncio as redis
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from ...core.config import settings, PlanType

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
        self.rate_limit_windows = {
            PlanType.STARTER: 60,  # 1 minute window for starter
            PlanType.PRO: 30,      # 30 second window for pro
            PlanType.ENTERPRISE: 10  # 10 second window for enterprise
        }
        self.api_call_limits = {
            PlanType.STARTER: settings.STARTER_PLAN_API_CALLS,
            PlanType.PRO: settings.PRO_PLAN_API_CALLS,
            PlanType.ENTERPRISE: settings.ENTERPRISE_PLAN_API_CALLS
        }
        self.token_limits = {
            PlanType.STARTER: settings.STARTER_PLAN_LLM_TOKENS,
            PlanType.PRO: settings.PRO_PLAN_LLM_TOKENS,
            PlanType.ENTERPRISE: settings.ENTERPRISE_PLAN_LLM_TOKENS
        }

    async def set_cache(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cache with TTL"""
        try:
            serialized = json.dumps(value)
            return await self.redis.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    async def get_cache(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            cached = await self.redis.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            logger.error(f"Error getting cache: {e}")
            return None

    async def check_rate_limit(self, tenant_id: str, tenant_plan: PlanType) -> Dict[str, Any]:
        """
        Check rate limit using token bucket algorithm
        Returns dict with allowed status and remaining tokens
        """
        now = datetime.utcnow()
        window = self.rate_limit_windows[tenant_plan]
        max_tokens = self.api_call_limits[tenant_plan]
        
        # Create a unique key for this tenant's rate limit bucket
        bucket_key = f"rate_limit:{tenant_id}"
        
        # Get the current bucket state
        pipe = self.redis.pipeline()
        pipe.hgetall(bucket_key)
        pipe.pttl(bucket_key)
        result = await pipe.execute()
        
        current = result[0] or {}
        ttl = result[1] // 1000  # Convert to seconds
        
        last_update = datetime.fromisoformat(current.get('last_update', now.isoformat()))
        tokens = float(current.get('tokens', max_tokens))
        
        # Calculate how many tokens to add based on time passed
        time_passed = (now - last_update).total_seconds()
        tokens_to_add = (time_passed * max_tokens) / (window * 60)  # Tokens per second
        
        # Update token count, but don't exceed max
        new_tokens = min(tokens + tokens_to_add, max_tokens)
        
        # Check if request is allowed
        allowed = new_tokens >= 1
        
        if allowed:
            # Consume a token
            new_tokens -= 1
            last_update = now
            # Update the bucket
            pipe = self.redis.pipeline()
            pipe.hmset(bucket_key, {
                'tokens': str(new_tokens),
                'last_update': last_update.isoformat()
            })
            # Set TTL if this is a new key
            if not current:
                pipe.expire(bucket_key, window * 60)  # Convert minutes to seconds
            await pipe.execute()
        
        return {
            'allowed': allowed,
            'tokens_remaining': int(new_tokens),
            'max_tokens': max_tokens,
            'reset_in': window * 60 - time_passed if allowed else 0
        }

    async def increment_usage(self, tenant_id: str, api_calls: int = 1, llm_tokens: int = 0) -> None:
        """Increment usage counters for a tenant"""
        now = datetime.utcnow()
        day_key = f"usage:{tenant_id}:{now.strftime('%Y-%m-%d')}"
        
        pipe = self.redis.pipeline()
        pipe.hincrby(day_key, 'api_calls', api_calls)
        pipe.hincrby(day_key, 'llm_tokens', llm_tokens)
        pipe.expire(day_key, 7 * 24 * 3600)  # Keep for 7 days
        await pipe.execute()

    async def get_daily_usage(self, tenant_id: str, date: Optional[datetime] = None) -> Dict[str, int]:
        """Get daily usage for a tenant"""
        if date is None:
            date = datetime.utcnow()
        day_key = f"usage:{tenant_id}:{date.strftime('%Y-%m-%d')}"
        
        usage = await self.redis.hgetall(day_key)
        return {
            'api_calls': int(usage.get(b'api_calls', 0)),
            'llm_tokens': int(usage.get(b'llm_tokens', 0))
        }

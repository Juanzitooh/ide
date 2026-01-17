import json
from typing import Optional

import redis
from flask import current_app

_CLIENT = None


def _client() -> redis.Redis:
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT
    config = current_app.config
    _CLIENT = redis.Redis(
        host=config.get("REDIS_HOST"),
        port=config.get("REDIS_PORT"),
        db=config.get("REDIS_DB"),
        decode_responses=True,
    )
    return _CLIENT


def cache_get(key: str) -> Optional[dict]:
    client = _client()
    raw = client.get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def cache_set(key: str, value: dict, ttl: int) -> None:
    client = _client()
    client.setex(key, ttl, json.dumps(value))


def cache_delete(*keys: str) -> None:
    client = _client()
    if keys:
        client.delete(*keys)

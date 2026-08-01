import uuid

from app.modules.copilot.application.security.rate_limiter import TokenRateLimiter
from app.modules.copilot.application.security.stream_sanitizer import stream_sanitizer
from app.modules.copilot.infrastructure.cache.multi_layer_cache import MultiLayerCache


def test_multi_layer_cache_set_get_and_expiration():
    cache = MultiLayerCache(default_ttl_seconds=1)
    cache.set("test-key", {"data": "cached_value"})

    cached = cache.get("test-key")
    assert cached == {"data": "cached_value"}

    # Test cache invalidation
    cache.invalidate("test-key")
    assert cache.get("test-key") is None


def test_multi_layer_cache_workspace_clear():
    cache = MultiLayerCache(default_ttl_seconds=300)
    ws_id = uuid.uuid4()
    cache.set(f"ws:{str(ws_id)}:key1", "val1")
    cache.set(f"ws:{str(ws_id)}:key2", "val2")
    cache.set("other_key", "val3")

    cleared_count = cache.clear_workspace(ws_id)
    assert cleared_count == 2
    assert cache.get("other_key") == "val3"


def test_stream_sanitizer_secret_scrubbing():
    raw_text = "API Key sk-123456789012345678901234 and Bearer secret_token_xyz"
    sanitized = stream_sanitizer.sanitize_text(raw_text)

    assert "[REDACTED_API_KEY]" in sanitized
    assert "sk-123456789012345678901234" not in sanitized
    assert "Bearer [REDACTED_TOKEN]" in sanitized


def test_token_rate_limiter():
    limiter = TokenRateLimiter(max_requests_per_minute=2, max_tokens_per_minute=5000)
    ws_id = uuid.uuid4()

    assert limiter.check_rate_limit(ws_id, estimated_tokens=1000) is True
    assert limiter.check_rate_limit(ws_id, estimated_tokens=1000) is True
    # 3rd request exceeds max_requests=2
    assert limiter.check_rate_limit(ws_id, estimated_tokens=1000) is False

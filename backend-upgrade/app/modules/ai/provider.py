from __future__ import annotations

"""
LLM provider abstraction.

Business logic depends on the `LLMProvider` interface only. To add a provider:
implement `LLMProvider`, register it in `_PROVIDER_REGISTRY`, and set
`AI_PROVIDER` in the environment. No service, route, schema or API contract
changes.

Providers return parsed JSON objects. Vendor-specific transport concerns
(retries, timeouts, rate-limit classification, markdown fence stripping) are
handled here so the service layer sees only domain exceptions.
"""

import json
import re
from abc import ABC, abstractmethod
from typing import Any

try:
    from google import genai
    from google.genai import errors as genai_errors
except ImportError:
    genai = None
    genai_errors = None


from app.core.config import settings
from app.core.exceptions import LLMError, RateLimitError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Models occasionally wrap JSON in markdown fences despite instructions.
_JSON_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.MULTILINE)


class ProviderUnavailableError(LLMError):
    """The configured provider is not usable (missing credentials, unknown name)."""

    def __init__(self, message: str):
        super().__init__(message)
        self.code = "provider_unavailable"


class InvalidAIResponseError(LLMError):
    """The provider replied, but the payload was not usable JSON."""

    def __init__(self, message: str):
        super().__init__(message)
        self.code = "invalid_ai_response"


def _strip_json_fences(text: str) -> str:
    """Remove markdown code fences a model may have wrapped around JSON."""
    return _JSON_FENCE_RE.sub("", text).strip()


def _extract_json_object(text: str) -> str:
    """
    Return the outermost JSON object in `text`.

    Models sometimes prepend a sentence before the JSON. Rather than fail, we
    locate the first balanced top-level object. Raises if none is found.
    """
    cleaned = _strip_json_fences(text)
    start = cleaned.find("{")
    if start == -1:
        raise InvalidAIResponseError("AI response contained no JSON object")

    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(cleaned)):
        char = cleaned[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return cleaned[start : index + 1]
    raise InvalidAIResponseError("AI response contained an unterminated JSON object")


def _google_sdk_error_types() -> tuple[type[BaseException], ...]:
    """Return available Google GenAI SDK exception classes."""
    return tuple(
        error_type
        for name in ("APIError", "ClientError", "ServerError")
        if isinstance((error_type := getattr(genai_errors, name, None)), type)
    )


def _google_error_status_code(exc: BaseException) -> int | None:
    """Best-effort status code extraction from Google GenAI SDK errors."""
    for attr in ("status_code", "code"):
        val = getattr(exc, attr, None)
        if isinstance(val, int):
            return val
        if isinstance(val, str) and val.isdigit():
            return int(val)

    msg = str(exc).lower()
    if "404" in msg or "not_found" in msg or "not found" in msg or "no longer available" in msg:
        return 404
    if "429" in msg or "resource_exhausted" in msg or "quota" in msg or "too many requests" in msg:
        return 429
    if "503" in msg or "unavailable" in msg or "high demand" in msg:
        return 503
    if "401" in msg or "unauthenticated" in msg:
        return 401
    if "403" in msg or "permission_denied" in msg:
        return 403

    return None


def _is_quota_exhausted(exc: BaseException) -> bool:
    """Detect permanent API quota exhaustion vs transient rate limits."""
    msg = str(exc).lower()
    return "exceeded your current quota" in msg or "quota exceeded" in msg or "check your plan and billing" in msg


def _is_transient_error(exc: BaseException, status_code: int | None) -> bool:
    """True for transient errors that warrant retry and fallback."""
    if status_code in (408, 503) or (status_code is not None and status_code >= 500):

        return True
    msg = str(exc).lower()
    return "503" in msg or "unavailable" in msg or "high demand" in msg or "temporarily unavailable" in msg


def _extract_retry_delay(exc: BaseException) -> float | None:
    msg = str(exc)
    match = re.search(r"retry in ([0-9\.]+)s", msg, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    match_delay = re.search(r"retryDelay': '([0-9]+)s'", msg, re.IGNORECASE)
    if match_delay:
        try:
            return float(match_delay.group(1))
        except ValueError:
            pass
    return None


def _is_google_sdk_error(exc: BaseException) -> bool:
    error_types = _google_sdk_error_types()
    return bool(error_types) and isinstance(exc, error_types)


def _key_fingerprint(key: str) -> str:
    """Return a safe fingerprint of the API key (never the full key)."""
    if not key:
        return "NONE"
    cleaned = key.strip()
    if len(cleaned) <= 8:
        return cleaned[:2] + "..." + cleaned[-2:]
    return cleaned[:4] + "..." + cleaned[-4:]


class LLMProvider(ABC):
    """Interface every LLM provider must satisfy."""

    #: Stable identifier persisted to company_ai_research.model_provider
    name: str

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Concrete model identifier, persisted for reproducibility."""

    @abstractmethod
    def is_available(self) -> bool:
        """True when this provider has everything it needs to run."""

    @abstractmethod
    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """
        Generate a JSON object from the model.

        Raises:
            ProviderUnavailableError: provider not configured or temporarily unavailable.
            RateLimitError: provider rate limit hit or quota exceeded.
            InvalidAIResponseError: response was not parseable JSON.
            LLMError: any other generation failure (incl. timeout).
        """


import concurrent.futures
import threading


class GeminiProvider(LLMProvider):
    """Google Gemini via the official Google GenAI SDK."""

    name = "gemini"

    def __init__(self) -> None:
        self._client: Any = None
        self._in_flight: dict[str, concurrent.futures.Future] = {}
        self._lock = threading.Lock()

    @property
    def model_version(self) -> str:
        return settings.GEMINI_MODEL

    def is_available(self) -> bool:
        return settings.has_gemini and genai is not None

    def _get_client(self) -> Any:
        if not self.is_available():
            raise ProviderUnavailableError("Gemini API key not configured")

        if self._client is None and genai:
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)

        return self._client


    def _handle_google_error(self, exc: BaseException) -> None:
        import traceback
        status_code = _google_error_status_code(exc)
        original_error_str = str(exc)
        tb = traceback.format_exc()
        key_fp = _key_fingerprint(settings.GEMINI_API_KEY)

        logger.error(
            "gemini_sdk_original_exception",
            provider=self.name,
            model=self.model_version,
            key_fingerprint=key_fp,
            status_code=status_code,
            exception_type=type(exc).__name__,
            error_body=original_error_str,
            traceback=tb,
        )

        if status_code == 429:
            if _is_quota_exhausted(exc):
                raise RateLimitError(
                    service="gemini",
                    message="Gemini API quota exceeded. Please wait for quota reset or enable billing.",
                ) from exc
            raise RateLimitError(
                service="gemini",
                message=f"Gemini API error ({status_code} RESOURCE_EXHAUSTED): {original_error_str}",
            ) from exc

        if status_code in {401, 403}:
            raise ProviderUnavailableError(
                f"Gemini API error ({status_code} AUTHENTICATION_ERROR): {original_error_str}"
            ) from exc

        if status_code == 404:
            raise ProviderUnavailableError(
                f"Gemini API error (404 NOT_FOUND): {original_error_str}"
            ) from exc

        if status_code == 503:
            raise ProviderUnavailableError(
                f"Gemini API error (503 UNAVAILABLE): {original_error_str}"
            ) from exc

        raise LLMError(f"Gemini API error ({status_code or 'UNKNOWN'}): {original_error_str}") from exc

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        import hashlib
        prompt_key = hashlib.sha256(f"{system_prompt}:{user_prompt}".encode("utf-8")).hexdigest()

        with self._lock:
            if prompt_key in self._in_flight:
                logger.info("gemini_in_flight_request_deduplicated", prompt_key=prompt_key[:12])
                future = self._in_flight[prompt_key]
                return future.result(timeout=120)

            future = concurrent.futures.Future()
            self._in_flight[prompt_key] = future

        try:
            res = self._execute_generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            future.set_result(res)
            return res
        except Exception as exc:
            future.set_exception(exc)
            raise
        finally:
            with self._lock:
                self._in_flight.pop(prompt_key, None)

    def _execute_generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        import time
        import traceback
        client = self._get_client()
        key_fp = _key_fingerprint(settings.GEMINI_API_KEY)

        candidate_models: list[str] = []
        primary_model = settings.GEMINI_MODEL or "gemini-2.0-flash"
        if primary_model:
            candidate_models.append(primary_model)
        for fallback in ["gemini-flash-latest", "gemini-2.0-flash-lite"]:
            if fallback not in candidate_models:
                candidate_models.append(fallback)

        backoff_delays = [2.0, 5.0, 10.0]
        last_error: BaseException | None = None
        last_status_code: int | None = None
        request_count = 0

        prompt_content = f"""
System:
{system_prompt}

User:
{user_prompt}
"""
        prompt_length = len(prompt_content)
        prompt_token_estimate = prompt_length // 4

        for model_name in candidate_models:
            for attempt, delay in enumerate([0.0] + backoff_delays, start=1):
                request_count += 1
                if delay > 0:
                    logger.info(
                        "gemini_retry_backoff_sleep",
                        model=model_name,
                        key_fingerprint=key_fp,
                        attempt=attempt,
                        request_count=request_count,
                        retry_count=attempt - 1,
                        wait_seconds=delay,
                    )
                    time.sleep(delay)

                start_time = time.perf_counter()
                try:
                    logger.info(
                        "calling_gemini_model",
                        model=model_name,
                        key_fingerprint=key_fp,
                        attempt=attempt,
                        request_count=request_count,
                        prompt_length=prompt_length,
                        prompt_token_estimate=prompt_token_estimate,
                    )
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt_content,
                    )
                    latency_ms = int((time.perf_counter() - start_time) * 1000)
                    content = response.text
                    if not content:
                        raise InvalidAIResponseError("AI response content was empty")

                    parsed = json.loads(_extract_json_object(content))
                    if not isinstance(parsed, dict):
                        raise InvalidAIResponseError("AI response JSON was not an object")

                    usage = getattr(response, "usage_metadata", None)
                    input_tokens = getattr(usage, "prompt_token_count", None) if usage else None
                    output_tokens = getattr(usage, "candidates_token_count", None) if usage else None

                    logger.info(
                        "gemini_request_success",
                        model=model_name,
                        key_fingerprint=key_fp,
                        attempt=attempt,
                        request_count=request_count,
                        status_code=200,
                        latency_ms=latency_ms,
                        prompt_length=prompt_length,
                        prompt_token_estimate=prompt_token_estimate,
                        actual_input_tokens=input_tokens,
                        actual_output_tokens=output_tokens,
                    )
                    return parsed

                except InvalidAIResponseError:
                    raise
                except json.JSONDecodeError as exc:
                    latency_ms = int((time.perf_counter() - start_time) * 1000)
                    logger.warning(
                        "ai_response_not_json",
                        provider=self.name,
                        model=model_name,
                        key_fingerprint=key_fp,
                        request_count=request_count,
                        latency_ms=latency_ms,
                        error=str(exc),
                    )
                    raise InvalidAIResponseError(f"AI response was not valid JSON: {exc}") from exc
                except Exception as exc:
                    latency_ms = int((time.perf_counter() - start_time) * 1000)
                    status_code = _google_error_status_code(exc)
                    last_error = exc
                    last_status_code = status_code
                    tb = traceback.format_exc()

                    logger.warning(
                        "gemini_model_request_failed",
                        provider=self.name,
                        model=model_name,
                        key_fingerprint=key_fp,
                        attempt=attempt,
                        request_count=request_count,
                        retry_count=attempt - 1,
                        status_code=status_code,
                        latency_ms=latency_ms,
                        prompt_token_estimate=prompt_token_estimate,
                        error=str(exc),
                        traceback=tb,
                    )

                    # 1. 404 NOT_FOUND: Do NOT retry 404
                    if status_code == 404:
                        logger.warning(
                            "gemini_model_not_found_skipping",
                            model=model_name,
                            key_fingerprint=key_fp,
                            status_code=404,
                        )
                        break

                    # 2. 429 RESOURCE_EXHAUSTED / Quota
                    if status_code == 429:
                        if _is_quota_exhausted(exc):
                            logger.warning(
                                "gemini_model_quota_exhausted_trying_fallback",
                                model=model_name,
                                key_fingerprint=key_fp,
                                status_code=429,
                            )
                            break
                        else:
                            retry_delay = _extract_retry_delay(exc)
                            if retry_delay and retry_delay > 0:
                                logger.info(
                                    "gemini_respecting_retry_info_delay",
                                    model=model_name,
                                    retry_delay_seconds=retry_delay,
                                )
                                time.sleep(min(retry_delay, 15.0))
                            if attempt <= len(backoff_delays):
                                continue
                            else:
                                logger.warning(
                                    "gemini_model_rate_limit_retries_exhausted_trying_fallback",
                                    model=model_name,
                                    key_fingerprint=key_fp,
                                )
                                break

                    # 3. 503 UNAVAILABLE
                    if status_code == 503:
                        if attempt <= len(backoff_delays):
                            continue
                        else:
                            logger.warning(
                                "gemini_model_503_retries_exhausted_trying_fallback",
                                model=model_name,
                                key_fingerprint=key_fp,
                            )
                            break

                    # 4. Non-transient errors
                    if status_code in (401, 403):
                        self._handle_google_error(exc)
                    else:
                        break

        if last_error is not None:
            self._handle_google_error(last_error)
        raise ProviderUnavailableError("Gemini API call failed with no exception raised.")


# Registry
# Future providers register here. Nothing in the service layer changes when
# this dict grows.

_PROVIDER_REGISTRY: dict[str, type[LLMProvider]] = {
    GeminiProvider.name: GeminiProvider,
}

_PROVIDER_INSTANCES: dict[str, LLMProvider] = {}


def get_provider(name: str | None = None) -> LLMProvider:
    """
    Resolve the active LLM provider. Used as a FastAPI/Celery dependency so
    callers can inject a fake in tests.
    """
    provider_name = (name or settings.AI_PROVIDER).strip().lower()

    provider_cls = _PROVIDER_REGISTRY.get(provider_name)
    if provider_cls is None:
        raise ProviderUnavailableError(
            f"Unknown AI provider '{provider_name}'. "
            f"Registered: {', '.join(sorted(_PROVIDER_REGISTRY))}"
        )

    if provider_name not in _PROVIDER_INSTANCES:
        _PROVIDER_INSTANCES[provider_name] = provider_cls()
    return _PROVIDER_INSTANCES[provider_name]


def register_provider(provider_cls: type[LLMProvider]) -> None:
    """Register an additional provider implementation at import time."""
    _PROVIDER_REGISTRY[provider_cls.name] = provider_cls
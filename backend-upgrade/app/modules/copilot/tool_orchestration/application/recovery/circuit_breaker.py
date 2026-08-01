"""
Circuit Breaker (Phase 5.5.3)
Provides per-tool circuit breaker protection (Closed, Open, Half-Open).
"""
import enum
import time
from typing import Dict


class CircuitState(str, enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_interval_seconds: float = 10.0,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_interval_seconds = recovery_interval_seconds
        
        self._failures: Dict[str, int] = {}
        self._last_failure_time: Dict[str, float] = {}
        self._states: Dict[str, CircuitState] = {}

    def get_state(self, tool_name: str) -> CircuitState:
        state = self._states.get(tool_name, CircuitState.CLOSED)
        if state == CircuitState.OPEN:
            last_fail = self._last_failure_time.get(tool_name, 0.0)
            if time.time() - last_fail > self.recovery_interval_seconds:
                self._states[tool_name] = CircuitState.HALF_OPEN
                return CircuitState.HALF_OPEN
        return state

    def allow_execution(self, tool_name: str) -> bool:
        return self.get_state(tool_name) != CircuitState.OPEN

    def record_success(self, tool_name: str) -> None:
        self._failures[tool_name] = 0
        self._states[tool_name] = CircuitState.CLOSED

    def record_failure(self, tool_name: str) -> None:
        count = self._failures.get(tool_name, 0) + 1
        self._failures[tool_name] = count
        self._last_failure_time[tool_name] = time.time()

        if count >= self.failure_threshold:
            self._states[tool_name] = CircuitState.OPEN


circuit_breaker = CircuitBreaker()

"""
Устойчивость к ошибкам: Retry + Circuit Breaker (аналог Polly)
"""
import time
import functools
import logging
from enum import Enum
from typing import Callable, Any, Type, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import threading

logger = logging.getLogger('Resilience')

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 3
    timeout_seconds: int = 30
    success_threshold: int = 2

class CircuitBreaker:
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    logger.info(f"[CB:{self.name}] OPEN -> HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise Exception(f"Circuit breaker '{self.name}' is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e
    
    def _on_success(self):
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    logger.info(f"[CB:{self.name}] HALF_OPEN -> CLOSED")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0
    
    def _on_failure(self):
        with self.lock:
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitState.CLOSED:
                self.failure_count += 1
                if self.failure_count >= self.config.failure_threshold:
                    logger.warning(f"[CB:{self.name}] CLOSED -> OPEN")
                    self.state = CircuitState.OPEN
            
            elif self.state == CircuitState.HALF_OPEN:
                logger.warning(f"[CB:{self.name}] HALF_OPEN -> OPEN")
                self.state = CircuitState.OPEN
                self.failure_count = self.config.failure_threshold
    
    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return True
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.config.timeout_seconds
    
    def get_state(self) -> str:
        return self.state.value


def retry(max_attempts: int = 3, delay_seconds: float = 1.0, 
          backoff_multiplier: float = 2.0, exceptions: Tuple[Type[Exception], ...] = (Exception,)):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay_seconds
            
            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        logger.info(f"Retry successful on attempt {attempt}")
                    return result
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(f"Attempt {attempt}/{max_attempts} failed: {e}")
                        time.sleep(current_delay)
                        current_delay *= backoff_multiplier
                    else:
                        logger.error(f"All {max_attempts} attempts failed")
            
            raise last_exception
        return wrapper
    return decorator


class ResilienceService:
    def __init__(self, name: str):
        self.name = name
        self.circuit_breaker = CircuitBreaker(name)
    
    def call_with_resilience(self, func: Callable, max_retries: int = 3, *args, **kwargs) -> Any:
        @retry(max_attempts=max_retries)
        def call_with_cb():
            return self.circuit_breaker.call(func, *args, **kwargs)
        
        return call_with_cb()


if __name__ == "__main__":
    import random
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    
    print("\n" + "=" * 60)
    print("Resilience Patterns Demo: Retry + Circuit Breaker")
    print("=" * 60)
    
    class UnstableService:
        def __init__(self, fail_count: int = 2):
            self.call_count = 0
            self.fail_count = fail_count
        
        def call(self, data: str) -> str:
            self.call_count += 1
            if self.call_count <= self.fail_count:
                raise ConnectionError(f"Service unavailable (attempt {self.call_count})")
            return f"Success! Got: {data}"
    
    print("\n1. Retry Pattern Demo")
    print("-" * 40)
    
    unstable = UnstableService(fail_count=2)
    
    @retry(max_attempts=3, delay_seconds=0.5)
    def unreliable_call():
        return unstable.call("test data")
    
    try:
        result = unreliable_call()
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Failed: {e}")
    
    print("\n2. Circuit Breaker Demo")
    print("-" * 40)
    
    failing_service = UnstableService(fail_count=100)
    resilience = ResilienceService("test-service")
    
    for i in range(1, 6):
        try:
            result = resilience.call_with_resilience(failing_service.call, max_retries=2, data=f"req-{i}")
            print(f"   Request {i}: Success")
        except Exception as e:
            print(f"   Request {i}: Failed - {e}")
        print(f"   Circuit state: {resilience.circuit_breaker.get_state()}")
    
    print("\nDemo completed!")

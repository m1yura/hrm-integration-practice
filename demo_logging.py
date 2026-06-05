"""
Демонстрация работы логирования и обработки ошибок
"""
import time
import random
import sys
from logger_config import setup_logging, log_with_props
from resilience import ResilienceService, retry, CircuitBreaker

# Инициализация логгера
logger = setup_logging("DemoSystem", "DEBUG")

def simulate_unstable_service():
    """Симуляция нестабильного сервиса"""
    rnd = random.random()
    if rnd < 0.4:
        return {"status": "success", "data": "Operation completed"}
    elif rnd < 0.7:
        raise ConnectionError("Temporary network error")
    else:
        raise ValueError("Business validation failed")

@retry(max_attempts=3, delay_seconds=0.5)
def call_with_retry():
    """Вызов с Retry"""
    return simulate_unstable_service()

def demo_logging_levels():
    """Демонстрация разных уровней логирования"""
    print("\n" + "=" * 60)
    print("1. Different Logging Levels Demo")
    print("=" * 60)
    
    logger.debug("This is DEBUG message - detailed diagnostic")
    logger.info("This is INFO message - normal operation")
    logger.warning("This is WARNING message - something suspicious")
    logger.error("This is ERROR message - operation failed")
    
    log_with_props(logger, "info", "Business event with properties", 
                  {'user_id': 123, 'action': 'login', 'ip': '192.168.1.1'})

def demo_retry_pattern():
    """Демонстрация Retry pattern"""
    print("\n" + "=" * 60)
    print("2. Retry Pattern Demo")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i in range(5):
        try:
            logger.info(f"Attempt {i+1}: Calling unstable service")
            result = call_with_retry()
            logger.info(f"[OK] Success: {result}")
            success_count += 1
        except Exception as e:
            logger.error(f"[FAIL] Failed after retries: {e}")
            fail_count += 1
        
        time.sleep(0.5)
    
    logger.info(f"Stats: Success={success_count}, Failures={fail_count}")

def demo_circuit_breaker():
    """Демонстрация Circuit Breaker"""
    print("\n" + "=" * 60)
    print("3. Circuit Breaker Demo")
    print("=" * 60)
    
    cb = CircuitBreaker("payment-service")
    fail_count = 0
    
    for i in range(10):
        try:
            logger.info(f"Request {i+1}: Checking circuit state: {cb.get_state()}")
            
            def risky_call():
                if random.random() < 0.7:
                    raise Exception("Service unavailable")
                return "Payment processed"
            
            result = cb.call(risky_call)
            logger.info(f"[OK] Request {i+1} succeeded: {result}")
            
        except Exception as e:
            logger.error(f"[FAIL] Request {i+1} failed: {e}")
            fail_count += 1
        
        time.sleep(1)
    
    logger.info(f"Total failures: {fail_count}, Final circuit state: {cb.get_state()}")

def demo_error_logging():
    """Демонстрация логирования ошибок с полным стеком"""
    print("\n" + "=" * 60)
    print("4. Error Logging with Stack Trace Demo")
    print("=" * 60)
    
    def nested_function():
        raise ValueError("Critical business error in nested call")
    
    def middle_function():
        try:
            nested_function()
        except Exception as e:
            logger.error(f"Error in middle function", exc_info=True)
            raise
    
    try:
        middle_function()
    except Exception as e:
        logger.critical(f"System error: {e}", exc_info=True)

def demo_structured_logging():
    """Демонстрация структурированного логирования в JSON"""
    print("\n" + "=" * 60)
    print("5. Structured Logging (JSON) Demo")
    print("=" * 60)
    
    events = [
        {'event': 'user_login', 'user_id': 1001, 'timestamp': time.time()},
        {'event': 'application_submit', 'application_id': 5001, 'vacancy_id': 200},
        {'event': 'payment_processed', 'amount': 15000, 'currency': 'RUB'}
    ]
    
    for event in events:
        log_with_props(logger, "info", f"Event: {event['event']}", event)
        time.sleep(0.1)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("LOGGING, MONITORING & ERROR HANDLING DEMO")
    print("=" * 70)
    
    demo_logging_levels()
    demo_retry_pattern()
    demo_circuit_breaker()
    demo_error_logging()
    demo_structured_logging()
    
    print("\n" + "=" * 70)
    print("All demos completed!")
    print("\nCheck logs in 'logs' directory:")
    print("   - DemoSystem.json.log (structured JSON format)")
    print("   - DemoSystem.log (plain text format)")
    print("\nLog features demonstrated:")
    print("   - Different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    print("   - Structured logging with properties")
    print("   - Retry pattern with exponential backoff")
    print("   - Circuit Breaker pattern (OPEN -> HALF_OPEN -> CLOSED)")
    print("   - Full stack trace on errors")
    print("   - JSON format for machine parsing")
    print("=" * 70)

"""
Пример модуля с интегрированным логированием и устойчивостью
"""
import requests
from logger_config import setup_logging, log_with_props
from resilience import ResilienceService, retry
import time

# Инициализация логирования
logger = setup_logging("HRM_Integration", "DEBUG")

# Сервис устойчивости
resilience = ResilienceService("API_Gateway")

class HRMIntegrationClient:
    """Клиент для интеграции с устойчивостью к ошибкам"""
    
    def __init__(self):
        self.base_urls = {
            'employees': 'http://127.0.0.1:5001',
            'vacancies': 'http://127.0.0.1:5002',
            'applications': 'http://127.0.0.1:8000'
        }
    
    @retry(max_attempts=3, delay_seconds=0.5, exceptions=(requests.RequestException,))
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Выполнение HTTP запроса с Retry"""
        log_with_props(logger, "debug", f"Making {method} request to {url}", 
                      {'method': method, 'url': url})
        
        response = requests.request(method, url, timeout=5, **kwargs)
        
        if response.status_code >= 400:
            raise requests.HTTPError(f"HTTP {response.status_code}: {response.text}")
        
        return response
    
    def call_with_circuit_breaker(self, service: str, endpoint: str, method: str = 'GET', data=None):
        """Вызов API с Circuit Breaker защитой"""
        url = f"{self.base_urls[service]}/{endpoint}"
        
        def api_call():
            return self._make_request(method, url, json=data)
        
        return resilience.call_with_resilience(api_call, max_retries=2)
    
    def get_employee(self, employee_id: int):
        """Получение сотрудника с логированием и устойчивостью"""
        start_time = time.time()
        
        try:
            log_with_props(logger, "info", f"Fetching employee {employee_id}", 
                          {'employee_id': employee_id, 'action': 'get_employee'})
            
            response = self.call_with_circuit_breaker('employees', f'employees/{employee_id}')
            
            elapsed = time.time() - start_time
            log_with_props(logger, "info", f"Employee {employee_id} fetched successfully", 
                          {'employee_id': employee_id, 'duration_ms': round(elapsed * 1000, 2)})
            
            return response.json()
            
        except Exception as e:
            elapsed = time.time() - start_time
            log_with_props(logger, "error", f"Failed to fetch employee {employee_id}", 
                          {'employee_id': employee_id, 'error': str(e), 'duration_ms': round(elapsed * 1000, 2)})
            raise
    
    def create_application(self, employee_id: int, vacancy_id: int, comment: str = ""):
        """Создание заявки с полным логированием"""
        start_time = time.time()
        application_id = None
        
        try:
            log_with_props(logger, "info", "Starting application creation flow",
                          {'employee_id': employee_id, 'vacancy_id': vacancy_id})
            
            # Шаг 1: Проверка сотрудника
            logger.info(f"Step 1/3: Validating employee {employee_id}")
            employee = self.get_employee(employee_id)
            log_with_props(logger, "debug", "Employee validation passed",
                          {'employee': employee})
            
            # Шаг 2: Проверка вакансии
            logger.info(f"Step 2/3: Validating vacancy {vacancy_id}")
            vacancy = self.call_with_circuit_breaker('vacancies', f'vacancies/{vacancy_id}')
            log_with_props(logger, "debug", "Vacancy validation passed",
                          {'vacancy': vacancy.json()})
            
            # Шаг 3: Создание заявки
            logger.info(f"Step 3/3: Creating application")
            application_data = {
                'employee_id': employee_id,
                'vacancy_id': vacancy_id,
                'comment': f"{comment} (Integration flow)"
            }
            response = self.call_with_circuit_breaker('applications', 'applications', 'POST', application_data)
            
            application_id = response.json().get('id')
            elapsed = time.time() - start_time
            
            log_with_props(logger, "info", "Application created successfully",
                          {
                              'application_id': application_id,
                              'employee_id': employee_id,
                              'vacancy_id': vacancy_id,
                              'duration_ms': round(elapsed * 1000, 2)
                          })
            
            return response.json()
            
        except Exception as e:
            elapsed = time.time() - start_time
            log_with_props(logger, "error", "Application creation failed",
                          {
                              'employee_id': employee_id,
                              'vacancy_id': vacancy_id,
                              'application_id': application_id,
                              'error': str(e),
                              'error_type': type(e).__name__,
                              'duration_ms': round(elapsed * 1000, 2)
                          })
            raise


def demo_integration_with_logging():
    """Демонстрация интеграции с логированием и устойчивостью"""
    print("\n" + "=" * 70)
    print("HRM Integration with Logging & Resilience")
    print("=" * 70)
    
    client = HRMIntegrationClient()
    
    # Успешный сценарий
    print("\n📌 1. Successful scenario")
    print("-" * 40)
    try:
        result = client.create_application(1, 2, "Demo integration")
        print(f"   ✅ Application created: {result}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Сценарий с ошибкой (несуществующий сотрудник)
    print("\n📌 2. Error scenario (invalid employee)")
    print("-" * 40)
    try:
        result = client.create_application(999, 2, "Should fail")
        print(f"   Unexpected success: {result}")
    except Exception as e:
        print(f"   ✅ Correctly failed: {e}")
    
    print("\n📁 Logs saved to: logs/ directory")
    print("   - HRM_Integration.json.log (structured JSON)")
    print("   - HRM_Integration.log (plain text)")
    print("   - Also console output with colors")

if __name__ == "__main__":
    demo_integration_with_logging()

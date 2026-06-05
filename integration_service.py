import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('IntegrationService')

# DTO классы
@dataclass
class EmployeeDTO:
    id: int
    name: str
    position: str

@dataclass
class VacancyDTO:
    id: int
    title: str
    department: str
    salary: int

@dataclass
class ApplicationResponseDTO:
    id: int
    employee_id: int
    vacancy_id: int
    comment: str
    status: str
    created_at: str

# Адаптеры
class EmployeeAdapter:
    @staticmethod
    def to_dto(data: Dict) -> Optional[EmployeeDTO]:
        try:
            return EmployeeDTO(
                id=data.get('id'),
                name=data.get('name'),
                position=data.get('position')
            )
        except Exception as e:
            logger.error(f"EmployeeAdapter error: {e}")
            return None

class VacancyAdapter:
    @staticmethod
    def to_dto(data: Dict) -> Optional[VacancyDTO]:
        try:
            return VacancyDTO(
                id=data.get('id'),
                title=data.get('title'),
                department=data.get('department'),
                salary=data.get('salary')
            )
        except Exception as e:
            logger.error(f"VacancyAdapter error: {e}")
            return None

class ApplicationAdapter:
    @staticmethod
    def to_response(data: Dict) -> ApplicationResponseDTO:
        return ApplicationResponseDTO(
            id=data.get('id'),
            employee_id=data.get('employee_id'),
            vacancy_id=data.get('vacancy_id'),
            comment=data.get('comment', ''),
            status=data.get('status', 'pending'),
            created_at=data.get('created_at', datetime.now().isoformat())
        )

# Интеграционный сервис
class HRMIntegrationService:
    def __init__(self, employees_url: str, vacancies_url: str, applications_url: str):
        self.employees_url = employees_url
        self.vacancies_url = vacancies_url
        self.applications_url = applications_url
        self.employee_adapter = EmployeeAdapter()
        self.vacancy_adapter = VacancyAdapter()
        self.application_adapter = ApplicationAdapter()
        logger.info("Integration Service initialized")

    def get_employee(self, employee_id: int) -> Optional[EmployeeDTO]:
        try:
            response = requests.get(f"{self.employees_url}/{employee_id}", timeout=3)
            if response.status_code == 200:
                return self.employee_adapter.to_dto(response.json())
            return None
        except Exception as e:
            logger.error(f"Error getting employee: {e}")
            return None

    def get_vacancy(self, vacancy_id: int) -> Optional[VacancyDTO]:
        try:
            response = requests.get(f"{self.vacancies_url}/{vacancy_id}", timeout=3)
            if response.status_code == 200:
                return self.vacancy_adapter.to_dto(response.json())
            return None
        except Exception as e:
            logger.error(f"Error getting vacancy: {e}")
            return None

    def create_application(self, employee_id: int, vacancy_id: int, comment: str = "") -> Optional[ApplicationResponseDTO]:
        logger.info(f"Integration flow: Employee {employee_id} -> Vacancy {vacancy_id}")
        
        employee = self.get_employee(employee_id)
        if not employee:
            logger.error(f"Employee {employee_id} not found")
            return None
        logger.info(f"Employee found: {employee.name}")
        
        vacancy = self.get_vacancy(vacancy_id)
        if not vacancy:
            logger.error(f"Vacancy {vacancy_id} not found")
            return None
        logger.info(f"Vacancy found: {vacancy.title}")
        
        try:
            application_data = {
                "employee_id": employee_id,
                "vacancy_id": vacancy_id,
                "comment": f"{comment} (Employee: {employee.name}, Vacancy: {vacancy.title})"
            }
            response = requests.post(self.applications_url, json=application_data, timeout=5)
            if response.status_code == 201:
                application = self.application_adapter.to_response(response.json())
                logger.info(f"Application created successfully! ID: {application.id}")
                return application
            else:
                logger.error(f"Failed to create application: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error creating application: {e}")
            return None

    def get_all_applications(self) -> List[ApplicationResponseDTO]:
        try:
            response = requests.get(self.applications_url, timeout=3)
            if response.status_code == 200:
                apps_data = response.json()
                return [self.application_adapter.to_response(app) for app in apps_data]
            return []
        except Exception as e:
            logger.error(f"Error getting applications: {e}")
            return []

def demo():
    print("\n" + "=" * 60)
    print("HRM INTEGRATION SERVICE DEMO")
    print("=" * 60)
    
    integration = HRMIntegrationService(
        employees_url="http://127.0.0.1:5001/employees",
        vacancies_url="http://127.0.0.1:5002/vacancies",
        applications_url="http://127.0.0.1:8000/applications"
    )
    
    print("\nCreating application for Employee 1 -> Vacancy 2...")
    result = integration.create_application(1, 2, "Test from integration service")
    
    if result:
        print(f"\n✅ SUCCESS!")
        print(f"   Application ID: {result.id}")
        print(f"   Status: {result.status}")
    else:
        print("\n❌ FAILED!")
    
    print("\nAll applications:")
    for app in integration.get_all_applications():
        print(f"   - App #{app.id}: Employee {app.employee_id} -> Vacancy {app.vacancy_id} [{app.status}]")

if __name__ == "__main__":
    print("\nMake sure all modules are running:")
    print("  python module_a_employees.py")
    print("  python module_b_vacancies.py")
    print("  python module_c_applications.py")
    print()
    
    response = input("Are all modules running? (y/n): ")
    if response.lower() == 'y':
        demo()
    else:
        print("Please start all modules first!")

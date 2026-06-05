"""
Saga Pattern (аналог MassTransit Saga)
Компенсационные транзакции при ошибках
"""
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger('SagaOrchestrator')

class SagaStepStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"

@dataclass
class SagaStep:
    """Шаг саги"""
    name: str
    action: Callable
    compensation: Callable
    status: SagaStepStatus = SagaStepStatus.PENDING
    result: Any = None
    error: str = None

class SagaOrchestrator:
    """
    Оркестратор саги для сквозного процесса "Приём сотрудника"
    
    Шаги:
    1. Создание заявки
    2. Проверка вакансии
    3. Проверка сотрудника
    4. Одобрение HR
    5. Создание приказа
    6. Отправка уведомления
    """
    
    def __init__(self, saga_id: str):
        self.saga_id = saga_id
        self.steps: List[SagaStep] = []
        self.context: Dict = {}
        self.start_time = None
        self.end_time = None
        
    def add_step(self, name: str, action: Callable, compensation: Callable = None):
        """Добавление шага в сагу"""
        self.steps.append(SagaStep(name=name, action=action, compensation=compensation))
        return self
    
    def execute(self, initial_context: Dict) -> Dict:
        """Выполнение саги с компенсацией при ошибке"""
        self.start_time = datetime.now()
        self.context = initial_context.copy()
        
        logger.info(f"🚀 Starting Saga {self.saga_id}")
        logger.info(f"   Steps: {[s.name for s in self.steps]}")
        
        for i, step in enumerate(self.steps):
            logger.info(f"📍 Executing step {i+1}/{len(self.steps)}: {step.name}")
            
            try:
                result = step.action(self.context)
                step.status = SagaStepStatus.COMPLETED
                step.result = result
                
                # Обновляем контекст результатом шага
                if isinstance(result, dict):
                    self.context.update(result)
                    
                logger.info(f"   ✅ Step '{step.name}' completed")
                
            except Exception as e:
                step.status = SagaStepStatus.FAILED
                step.error = str(e)
                logger.error(f"   ❌ Step '{step.name}' failed: {e}")
                
                # Запускаем компенсацию для выполненных шагов
                self._compensate(i)
                raise Exception(f"Saga failed at step '{step.name}': {e}")
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"🏁 Saga {self.saga_id} completed successfully in {duration:.2f}s")
        
        return self.context
    
    def _compensate(self, failed_step_index: int):
        """Компенсация выполненных шагов (откат)"""
        logger.warning(f"🔄 Starting compensation for {failed_step_index} steps")
        
        for i in range(failed_step_index - 1, -1, -1):
            step = self.steps[i]
            if step.compensation:
                try:
                    step.compensation(self.context)
                    step.status = SagaStepStatus.COMPENSATED
                    logger.info(f"   🔄 Compensated step: {step.name}")
                except Exception as e:
                    logger.error(f"   ❌ Compensation failed for {step.name}: {e}")
            else:
                logger.warning(f"   ⚠️ No compensation for step: {step.name}")


# Пример саги для HRM
class HRMHiringSaga:
    """Сага найма сотрудника"""
    
    @staticmethod
    def create_application(context: Dict) -> Dict:
        """Шаг 1: Создание заявки"""
        # Имитация создания заявки
        application_id = context.get('application_id', 1)
        logger.info(f"      Creating application #{application_id}")
        return {"application_created": True, "application_status": "draft"}
    
    @staticmethod
    def check_vacancy(context: Dict) -> Dict:
        """Шаг 2: Проверка вакансии"""
        vacancy_id = context.get('vacancy_id', 2)
        # Имитация проверки остатков (аналог CheckStock)
        if vacancy_id <= 0:
            raise Exception("Invalid vacancy ID")
        logger.info(f"      Vacancy #{vacancy_id} is active and available")
        return {"vacancy_valid": True}
    
    @staticmethod
    def check_employee(context: Dict) -> Dict:
        """Шаг 3: Проверка сотрудника"""
        employee_id = context.get('employee_id', 1)
        # Проверка, не уволен ли сотрудник и т.д.
        if employee_id <= 0:
            raise Exception("Invalid employee ID")
        logger.info(f"      Employee #{employee_id} is eligible for hiring")
        return {"employee_valid": True}
    
    @staticmethod
    def hr_approval(context: Dict) -> Dict:
        """Шаг 4: Одобрение HR"""
        # Имитация одобрения
        logger.info(f"      HR approval granted")
        return {"hr_approved": True, "approval_date": datetime.now().isoformat()}
    
    @staticmethod
    def create_order(context: Dict) -> Dict:
        """Шаг 5: Создание приказа о приёме"""
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        logger.info(f"      Hiring order created: {order_number}")
        return {"order_number": order_number}
    
    @staticmethod
    def send_notification(context: Dict) -> Dict:
        """Шаг 6: Отправка уведомления"""
        logger.info(f"      Notification sent to employee and HR")
        return {"notification_sent": True}
    
    # Компенсации
    @staticmethod
    def compensate_application(context: Dict):
        """Отмена заявки"""
        logger.info(f"      Compensating: Deleting application...")
    
    @staticmethod
    def compensate_order(context: Dict):
        """Отмена приказа"""
        logger.info(f"      Compensating: Cancelling order...")


def run_hiring_saga(employee_id: int, vacancy_id: int, application_id: int = 1):
    """Запуск полного сквозного процесса найма"""
    
    saga = SagaOrchestrator(f"HIRING-{application_id}")
    
    saga.add_step(
        "Create Application",
        HRMHiringSaga.create_application,
        HRMHiringSaga.compensate_application
    )
    saga.add_step(
        "Check Vacancy",
        HRMHiringSaga.check_vacancy
    )
    saga.add_step(
        "Check Employee",
        HRMHiringSaga.check_employee
    )
    saga.add_step(
        "HR Approval",
        HRMHiringSaga.hr_approval
    )
    saga.add_step(
        "Create Order",
        HRMHiringSaga.create_order,
        HRMHiringSaga.compensate_order
    )
    saga.add_step(
        "Send Notification",
        HRMHiringSaga.send_notification
    )
    
    context = {
        "employee_id": employee_id,
        "vacancy_id": vacancy_id,
        "application_id": application_id,
        "vacancy_active": True,
        "hr_available": True,
        "contract_ready": True
    }
    
    result = saga.execute(context)
    return result

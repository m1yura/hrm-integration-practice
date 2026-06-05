"""
End-to-End сценарий: Приём сотрудника на работу
Соответствует BPMN диаграмме
"""
import logging
import sys
from datetime import datetime
from state_machine import ApplicationStateMachine, ApplicationEvent, STATE_MACHINE_DIAGRAM
from saga_orchestrator import run_hiring_saga, SagaOrchestrator, HRMHiringSaga

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('E2EScenario')

def print_separator(title: str):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def demo_state_machine():
    """Демонстрация State Machine"""
    print_separator("📊 PART 1: UML State Machine Demo")
    
    print(STATE_MACHINE_DIAGRAM)
    
    # Создаём конечный автомат для заявки
    context = {
        "employee_id": 1,
        "vacancy_id": 2,
        "hr_available": True,
        "vacancy_active": True,
        "contract_ready": True
    }
    
    sm = ApplicationStateMachine(application_id=100, context=context)
    
    print(f"\nInitial state: {sm.get_state()}")
    
    # Проходим все состояния
    events = [
        (ApplicationEvent.SUBMIT, "Подача заявки"),
        (ApplicationEvent.START_REVIEW, "Начало рассмотрения"),
        (ApplicationEvent.APPROVE, "Одобрение"),
        (ApplicationEvent.SIGN_CONTRACT, "Подписание приказа"),
        (ApplicationEvent.COMPLETE, "Завершение")
    ]
    
    for event, description in events:
        print(f"\n▶ Event: {description} ({event.value})")
        success = sm.fire(event)
        if success:
            print(f"   New state: {sm.get_state()}")
        else:
            print(f"   ❌ Transition failed!")
            break
    
    print(f"\n📜 State transition history:")
    for h in sm.get_history():
        print(f"   {h['from']} → {h['to']} at {h['timestamp']}")
    
    return sm

def demo_saga_success():
    """Демонстрация успешной саги"""
    print_separator("🔄 PART 2: Saga Pattern Demo (Successful Flow)")
    
    try:
        result = run_hiring_saga(employee_id=1, vacancy_id=2, application_id=200)
        
        print("\n✅ Saga completed successfully!")
        print(f"   Context: {result}")
        return True
    except Exception as e:
        print(f"\n❌ Saga failed: {e}")
        return False

def demo_saga_with_compensation():
    """Демонстрация саги с компенсацией при ошибке"""
    print_separator("🔄 PART 3: Saga Pattern Demo (With Compensation)")
    
    # Создаём сагу, которая упадёт на шаге Check Employee
    saga = SagaOrchestrator("FAILING-SAGA-001")
    
    saga.add_step("Step 1 - Create App", HRMHiringSaga.create_application)
    saga.add_step("Step 2 - Check Vacancy", 
                  lambda ctx: HRMHiringSaga.check_vacancy(ctx))
    saga.add_step("Step 3 - Check Employee (will fail)", 
                  lambda ctx: (_ for _ in ()).throw(Exception("Employee validation failed")))
    saga.add_step("Step 4 - HR Approval", HRMHiringSaga.hr_approval)
    
    context = {"employee_id": 1, "vacancy_id": 2, "application_id": 301}
    
    try:
        result = saga.execute(context)
        print("\n✅ Saga completed (unexpected!)")
        return False
    except Exception as e:
        print(f"\n✅ Saga failed as expected, compensation executed!")
        print(f"   Error: {e}")
        return True

def demo_full_e2e():
    """Полный End-to-End сценарий"""
    print_separator("🎯 PART 4: Complete End-to-End Hiring Process")
    
    logger.info("Starting E2E Scenario: HIRE EMPLOYEE")
    
    # Шаг 1: Пользователь подаёт заявку
    logger.info("Step 1: Employee submits application for vacancy")
    
    # Шаг 2: State Machine обрабатывает переходы
    logger.info("Step 2: State machine processes transitions")
    context = {
        "employee_id": 1,
        "vacancy_id": 2,
        "hr_available": True,
        "vacancy_active": True,
        "contract_ready": True
    }
    sm = ApplicationStateMachine(application_id=500, context=context)
    
    # Проходим все состояния
    for event in [ApplicationEvent.SUBMIT, 
                  ApplicationEvent.START_REVIEW,
                  ApplicationEvent.APPROVE,
                  ApplicationEvent.SIGN_CONTRACT,
                  ApplicationEvent.COMPLETE]:
        sm.fire(event)
    
    # Шаг 3: Saga выполняет транзакционные шаги
    logger.info("Step 3: Saga orchestrates transactional steps")
    saga_result = run_hiring_saga(employee_id=1, vacancy_id=2, application_id=500)
    
    # Шаг 4: Финальный результат
    logger.info("Step 4: Process completed")
    
    print("\n" + "=" * 70)
    print(" 🎉 END-TO-END SCENARIO COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"   Final State: {sm.get_state()}")
    print(f"   Order Number: {saga_result.get('order_number', 'N/A')}")
    print(f"   Approval Date: {saga_result.get('approval_date', 'N/A')}")
    print("=" * 70)
    
    return sm, saga_result

if __name__ == "__main__":
    print("\n" + "█" * 70)
    print("█ HRM SYSTEM - END TO END SCENARIO (HIRING PROCESS)")
    print("█" * 70)
    
    # Часть 1: State Machine
    sm = demo_state_machine()
    
    # Часть 2: Успешная Saga
    demo_saga_success()
    
    # Часть 3: Saga с компенсацией
    demo_saga_with_compensation()
    
    # Часть 4: Полный E2E сценарий
    demo_full_e2e()
    
    print("\n✅ All demos completed successfully!")
    print("\n📋 For report:")
    print("   1. UML State Machine Diagram (see above)")
    print("   2. Logs - saved to console")
    print("   3. Screenshots of this output")
    print("   4. Link to repository")

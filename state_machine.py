"""
UML State Machine для заявки (Application)
Статусы: 
- DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED → CONTRACT_SIGNED → COMPLETED
                                         ↓
                                      REJECTED
"""
from enum import Enum
from typing import Dict, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger('StateMachine')

class ApplicationState(Enum):
    """Статусы заявки"""
    DRAFT = "draft"                    # Черновик
    SUBMITTED = "submitted"            # Подана
    UNDER_REVIEW = "under_review"      # На рассмотрении
    APPROVED = "approved"              # Одобрена
    REJECTED = "rejected"              # Отклонена
    CONTRACT_SIGNED = "contract_signed" # Приказ подписан
    COMPLETED = "completed"            # Завершена

class ApplicationEvent(Enum):
    """События, изменяющие статус"""
    SUBMIT = "submit"                  # Подать заявку
    START_REVIEW = "start_review"      # Начать рассмотрение
    APPROVE = "approve"                # Одобрить
    REJECT = "reject"                  # Отклонить
    SIGN_CONTRACT = "sign_contract"    # Подписать приказ
    COMPLETE = "complete"              # Завершить

@dataclass
class StateTransition:
    """Переход между состояниями"""
    from_state: ApplicationState
    to_state: ApplicationState
    event: ApplicationEvent
    condition: Callable = None
    action: Callable = None

class ApplicationStateMachine:
    """Конечный автомат для заявки"""
    
    def __init__(self, application_id: int, context: Dict = None):
        self.application_id = application_id
        self.current_state = ApplicationState.DRAFT
        self.context = context or {}
        self.history = []
        self._transitions = self._build_transitions()
        
    def _build_transitions(self) -> Dict[ApplicationEvent, StateTransition]:
        """Построение всех разрешённых переходов"""
        return {
            ApplicationEvent.SUBMIT: StateTransition(
                from_state=ApplicationState.DRAFT,
                to_state=ApplicationState.SUBMITTED,
                event=ApplicationEvent.SUBMIT,
                condition=self._can_submit,
                action=self._on_submit
            ),
            ApplicationEvent.START_REVIEW: StateTransition(
                from_state=ApplicationState.SUBMITTED,
                to_state=ApplicationState.UNDER_REVIEW,
                event=ApplicationEvent.START_REVIEW,
                condition=self._can_start_review,
                action=self._on_start_review
            ),
            ApplicationEvent.APPROVE: StateTransition(
                from_state=ApplicationState.UNDER_REVIEW,
                to_state=ApplicationState.APPROVED,
                event=ApplicationEvent.APPROVE,
                condition=self._can_approve,
                action=self._on_approve
            ),
            ApplicationEvent.REJECT: StateTransition(
                from_state=ApplicationState.UNDER_REVIEW,
                to_state=ApplicationState.REJECTED,
                event=ApplicationEvent.REJECT,
                condition=self._can_reject,
                action=self._on_reject
            ),
            ApplicationEvent.SIGN_CONTRACT: StateTransition(
                from_state=ApplicationState.APPROVED,
                to_state=ApplicationState.CONTRACT_SIGNED,
                event=ApplicationEvent.SIGN_CONTRACT,
                condition=self._can_sign_contract,
                action=self._on_sign_contract
            ),
            ApplicationEvent.COMPLETE: StateTransition(
                from_state=ApplicationState.CONTRACT_SIGNED,
                to_state=ApplicationState.COMPLETED,
                event=ApplicationEvent.COMPLETE,
                condition=self._can_complete,
                action=self._on_complete
            ),
        }
    
    # Условия для переходов (проверки)
    def _can_submit(self) -> bool:
        return self.context.get('employee_id') is not None and self.context.get('vacancy_id') is not None
    
    def _can_start_review(self) -> bool:
        return self.context.get('hr_available', True)
    
    def _can_approve(self) -> bool:
        # Проверка: вакансия ещё открыта?
        return self.context.get('vacancy_active', True)
    
    def _can_reject(self) -> bool:
        return True
    
    def _can_sign_contract(self) -> bool:
        # Проверка: договор готов?
        return self.context.get('contract_ready', True)
    
    def _can_complete(self) -> bool:
        return True
    
    # Действия при переходах
    def _on_submit(self):
        logger.info(f"📝 Application {self.application_id} submitted")
        self._log_state_change(ApplicationState.DRAFT, ApplicationState.SUBMITTED)
    
    def _on_start_review(self):
        logger.info(f"🔍 Application {self.application_id} under review by HR")
        self._log_state_change(ApplicationState.SUBMITTED, ApplicationState.UNDER_REVIEW)
    
    def _on_approve(self):
        logger.info(f"✅ Application {self.application_id} approved!")
        self._log_state_change(ApplicationState.UNDER_REVIEW, ApplicationState.APPROVED)
    
    def _on_reject(self):
        logger.info(f"❌ Application {self.application_id} rejected")
        self._log_state_change(ApplicationState.UNDER_REVIEW, ApplicationState.REJECTED)
    
    def _on_sign_contract(self):
        logger.info(f"📄 Contract signed for application {self.application_id}")
        self._log_state_change(ApplicationState.APPROVED, ApplicationState.CONTRACT_SIGNED)
    
    def _on_complete(self):
        logger.info(f"🎉 Application {self.application_id} completed! Employee hired!")
        self._log_state_change(ApplicationState.CONTRACT_SIGNED, ApplicationState.COMPLETED)
    
    def _log_state_change(self, from_state: ApplicationState, to_state: ApplicationState):
        self.history.append({
            "from": from_state.value,
            "to": to_state.value,
            "timestamp": datetime.now().isoformat()
        })
    
    def fire(self, event: ApplicationEvent) -> bool:
        """Выполнение перехода по событию"""
        if event not in self._transitions:
            logger.error(f"Unknown event: {event.value}")
            return False
        
        transition = self._transitions[event]
        
        if self.current_state != transition.from_state:
            logger.error(f"Cannot apply {event.value} from state {self.current_state.value}")
            return False
        
        if transition.condition and not transition.condition():
            logger.error(f"Condition failed for event {event.value}")
            return False
        
        # Выполняем переход
        self.current_state = transition.to_state
        
        if transition.action:
            transition.action()
        
        return True
    
    def get_state(self) -> str:
        return self.current_state.value
    
    def get_history(self) -> list:
        return self.history
    
    def can_fire(self, event: ApplicationEvent) -> bool:
        """Проверка, можно ли выполнить событие"""
        if event not in self._transitions:
            return False
        transition = self._transitions[event]
        if self.current_state != transition.from_state:
            return False
        if transition.condition and not transition.condition():
            return False
        return True


# Диаграмма для отчёта (текстовая версия)
STATE_MACHINE_DIAGRAM = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                        UML State Machine - Application                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌───────┐    submit    ┌──────────┐   start_review   ┌──────────────┐     │
│   │ DRAFT │ ───────────> │ SUBMITTED│ ───────────────> │ UNDER_REVIEW │     │
│   └───────┘              └──────────┘                  └──────────────┘     │
│                                                             │               │
│                                                    ┌────────┴────────┐      │
│                                                    │                 │      │
│                                                  approve           reject   │
│                                                    │                 │      │
│                                                    ▼                 ▼      │
│                                              ┌──────────┐      ┌──────────┐  │
│                                              │ APPROVED │      │ REJECTED │  │
│                                              └──────────┘      └──────────┘  │
│                                                    │                          │
│                                              sign_contract                    │
│                                                    │                          │
│                                                    ▼                          │
│                                            ┌──────────────┐                   │
│                                            │CONTRACT_SIGNED│                  │
│                                            └──────────────┘                   │
│                                                    │                          │
│                                                 complete                      │
│                                                    │                          │
│                                                    ▼                          │
│                                            ┌───────────┐                      │
│                                            │ COMPLETED │                      │
│                                            └───────────┘                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
"""

"""
Простая шина событий (аналог MassTransit)
Для синхронизации между модулями
"""
import threading
from typing import Dict, List, Callable
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger('EventBus')

@dataclass
class Event:
    """Базовое событие"""
    event_type: str
    data: Dict
    created_at: datetime = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()

class EventBus:
    """Шина событий для межмодульного взаимодействия"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._subscribers = {}
        return cls._instance
    
    def subscribe(self, event_type: str, callback: Callable):
        """Подписка на событие"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.info(f"Subscribed to event: {event_type}")
    
    def publish(self, event: Event):
        """Публикация события"""
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in callback for {event.event_type}: {e}")
            logger.info(f"Event {event.event_type} published to {len(self._subscribers[event.event_type])} subscribers")
        else:
            logger.info(f"Event {event.event_type} published (no subscribers)")

# Глобальный экземпляр шины событий
event_bus = EventBus()

# События HRM системы
EMPLOYEE_CREATED = "employee.created"
EMPLOYEE_UPDATED = "employee.updated"
VACANCY_CREATED = "vacancy.created"
APPLICATION_CREATED = "application.created"
APPLICATION_STATUS_CHANGED = "application.status_changed"

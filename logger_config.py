"""
Структурированное логирование (аналог Serilog)
"""
import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import traceback

# Создаём директорию для логов
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

class JSONFormatter(logging.Formatter):
    """JSON форматтер для структурированного логирования"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        if hasattr(record, 'props'):
            log_entry["props"] = record.props
        
        return json.dumps(log_entry, ensure_ascii=False)

class ConsoleFormatter(logging.Formatter):
    """Форматтер для консоли (без эмодзи)"""
    
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        return f"{timestamp} [{record.levelname}] {record.name} - {record.getMessage()}"

def setup_logging(service_name: str, log_level: str = "INFO"):
    """Настройка логирования для сервиса"""
    
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    logger.handlers.clear()
    
    # JSON логгер для файла
    json_handler = logging.FileHandler(LOG_DIR / f"{service_name}.json.log", encoding='utf-8')
    json_handler.setFormatter(JSONFormatter())
    logger.addHandler(json_handler)
    
    # Текстовый логгер для файла
    text_handler = logging.FileHandler(LOG_DIR / f"{service_name}.log", encoding='utf-8')
    text_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s'))
    logger.addHandler(text_handler)
    
    # Вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ConsoleFormatter())
    logger.addHandler(console_handler)
    
    return logger

def log_with_props(logger, level: str, message: str, props: Dict[str, Any] = None):
    """Логирование с дополнительными свойствами"""
    if props:
        extra = {'props': props}
    else:
        extra = {}
    
    getattr(logger, level)(message, extra=extra)

if __name__ == "__main__":
    logger = setup_logging("test_service", "DEBUG")
    
    logger.info("Service started")
    logger.warning("Low disk space", extra={'props': {'free_space_mb': 100}})
    
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.error("Something went wrong", exc_info=True)
    
    print("\nLogging configured!")
    print(f"   Logs directory: {LOG_DIR.absolute()}")

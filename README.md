# HRM Integration Practice

Учебный проект с несколькими HRM-сервисами и простым веб-интерфейсом:

| Компонент | Технология | Порт | Назначение |
| --- | --- | --- | --- |
| Employees | Flask | 5001 | Сотрудники |
| Vacancies | FastAPI + Uvicorn | 5002 | Вакансии |
| Applications | Flask | 8000 | Заявки на вакансии |
| UI | Flask + static HTML | 8080 | Веб-интерфейс и API-прокси |

Базовая версия работает на данных в памяти и не требует Docker или базы данных.

## Требования

- Python 3.10 или новее
- pip
- Docker Desktop, только если нужен PostgreSQL из `docker-compose.db.yml`

Проверить, что Python доступен:

```bash
python --version
```

Если Windows пишет, что `python` не найден, установите Python с сайта [python.org](https://www.python.org/downloads/) и включите опцию `Add python.exe to PATH` при установке. Если у вас работает команда `py`, ее можно использовать вместо `python`, например `py -m venv .venv`.

## Быстрый запуск

### 1. Создать и активировать виртуальное окружение

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Запустить сервисы

Откройте три отдельных терминала из корня проекта и активируйте виртуальное окружение в каждом.

Терминал 1:

```bash
python module_a_employees.py
```

Терминал 2:

```bash
python module_b_vacancies.py
```

Терминал 3:

```bash
python module_c_applications.py
```

После запуска будут доступны API:

- Employees: http://127.0.0.1:5001/employees
- Vacancies: http://127.0.0.1:5002/vacancies
- Applications: http://127.0.0.1:8000/applications

### 4. Запустить веб-интерфейс

Откройте четвертый терминал, активируйте виртуальное окружение и выполните:

```bash
python ui_server.py
```

Откройте в браузере:

```text
http://127.0.0.1:8080
```

## Автоматическая проверка запуска

Скрипт `run_tests.py` сам запускает три API-сервиса, проверяет основные сценарии и затем останавливает процессы:

```bash
python run_tests.py
```

Это самый простой способ убедиться, что зависимости установлены корректно.

## Ручная проверка API

Windows PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:5001/employees
Invoke-RestMethod http://127.0.0.1:5002/vacancies
Invoke-RestMethod http://127.0.0.1:8000/applications
```

macOS/Linux:

```bash
curl http://127.0.0.1:5001/employees
curl http://127.0.0.1:5002/vacancies
curl http://127.0.0.1:8000/applications
```

Создать заявку:

```bash
curl -X POST http://127.0.0.1:8000/applications \
  -H "Content-Type: application/json" \
  -d '{"employee_id": 1, "vacancy_id": 2, "comment": "Test application"}'
```

## Тесты

Юнит-тесты:

```bash
python -m unittest tests.unit.test_adapters
```

Интеграционные и E2E-тесты требуют запущенных сервисов на портах `5001`, `5002` и `8000`:

```bash
python -m unittest tests.integration.test_integration
python -m unittest tests.e2e.test_e2e
```

## Демо интеграционного сервиса

Сначала запустите три API-сервиса, затем выполните:

```bash
python integration_service.py
```

Скрипт попросит подтвердить, что сервисы уже запущены, и создаст заявку через интеграционный слой.

## Опционально: база данных

В проекте есть отдельные файлы для экспериментов с базой данных:

- `docker-compose.db.yml` запускает PostgreSQL в Docker
- `models.py` использует SQLite-файл `hrm.db`
- `module_a_db.py` показывает вариант модуля Employees с SQLAlchemy
- `test_db.py` проверяет SQLite-модели

Запуск PostgreSQL:

```bash
docker compose -f docker-compose.db.yml up -d
```

Для SQLite-демо установите SQLAlchemy:

```bash
pip install sqlalchemy
python test_db.py
```

## Частые проблемы

### Порт уже занят

Остановите старый процесс или измените порт в соответствующем файле:

- `module_a_employees.py` - порт `5001`
- `module_b_vacancies.py` - порт `5002`
- `module_c_applications.py` - порт `8000`
- `ui_server.py` - порт `8080`

### UI показывает пустые данные

Проверьте, что перед запуском `ui_server.py` уже работают все три API-сервиса:

```bash
python module_a_employees.py
python module_b_vacancies.py
python module_c_applications.py
```

### PowerShell не активирует виртуальное окружение

Если команда активации заблокирована политикой выполнения скриптов, запустите PowerShell от имени обычного пользователя и выполните:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

После этого повторите:

```powershell
.\.venv\Scripts\Activate.ps1
```

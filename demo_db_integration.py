import requests
import time
import json

BASE_URL_EMPLOYEES = "http://localhost:5001"
BASE_URL_VACANCIES = "http://localhost:5002"
BASE_URL_APPLICATIONS = "http://localhost:8000"

print("=" * 60)
print("HRM Database Integration Demo")
print("PostgreSQL + SQLAlchemy + Event Bus")
print("=" * 60)

# 1. Создаём сотрудника через API
print("\n1. Creating new employee via API...")
new_employee = {
    "name": "Тестовый Сотрудник",
    "position": "Стажёр",
    "email": "test@example.com",
    "phone": "+7-999-123-45-67"
}
response = requests.post(f"{BASE_URL_EMPLOYEES}/employees", json=new_employee)
if response.status_code == 201:
    employee = response.json()
    print(f"   ✅ Employee created: {employee['name']} (ID: {employee['id']})")
else:
    print(f"   ❌ Failed: {response.text}")
    exit(1)

# 2. Создаём вакансию
print("\n2. Creating new vacancy...")
new_vacancy = {
    "title": "Junior Python Developer",
    "department": "IT",
    "salary": 90000,
    "description": "Ищем стажёра в команду разработки"
}
response = requests.post(f"{BASE_URL_VACANCIES}/vacancies", json=new_vacancy)
if response.status_code == 201:
    vacancy = response.json()
    print(f"   ✅ Vacancy created: {vacancy['title']} (ID: {vacancy['id']})")
else:
    print(f"   ❌ Failed: {response.text}")

# 3. Создаём заявку
print("\n3. Creating application...")
application_data = {
    "employee_id": employee['id'],
    "vacancy_id": vacancy['id'],
    "comment": "Хочу попробовать свои силы!"
}
response = requests.post(f"{BASE_URL_APPLICATIONS}/applications", json=application_data)
if response.status_code == 201:
    application = response.json()
    print(f"   ✅ Application created: ID {application['id']} - Status: {application['status']}")
else:
    print(f"   ❌ Failed: {response.text}")

# 4. Проверяем синхронизацию через общую БД
print("\n4. Checking data persistence in PostgreSQL...")
time.sleep(1)

response = requests.get(f"{BASE_URL_APPLICATIONS}/applications")
if response.status_code == 200:
    apps = response.json()
    print(f"   ✅ Total applications in DB: {len(apps)}")
    for app in apps:
        if app.get('employee_name'):
            print(f"      - Application #{app['id']}: {app['employee_name']} -> {app.get('vacancy_title', 'N/A')} [{app['status']}]")

print("\n" + "=" * 60)
print("✅ Database integration demo completed!")
print("   - PostgreSQL stores all data")
print("   - SQLAlchemy ORM used for models")
print("   - Event bus for synchronization")
print("=" * 60)

from models import init_db, SessionLocal, Employee, Vacancy, Application

print("Testing SQLite database...")

# Инициализация БД
init_db()

db = SessionLocal()

# Создаём сотрудника
emp = Employee(name="Тестовый Сотрудник", position="Разработчик", email="test@example.com")
db.add(emp)
db.commit()
print(f"✅ Employee created: {emp.name} (ID: {emp.id})")

# Создаём вакансию
vac = Vacancy(title="Python Developer", department="IT", salary=100000)
db.add(vac)
db.commit()
print(f"✅ Vacancy created: {vac.title} (ID: {vac.id})")

# Создаём заявку
app = Application(employee_id=emp.id, vacancy_id=vac.id, comment="Хочу работать!")
db.add(app)
db.commit()
print(f"✅ Application created: ID {app.id}")

# Проверяем данные
print("\n--- All Employees ---")
for e in db.query(Employee).all():
    print(f"  {e.id}: {e.name} - {e.position}")

print("\n--- All Vacancies ---")
for v in db.query(Vacancy).all():
    print(f"  {v.id}: {v.title} - {v.department} (${v.salary})")

print("\n--- All Applications ---")
for a in db.query(Application).all():
    emp_name = a.employee.name if a.employee else "Unknown"
    vac_title = a.vacancy.title if a.vacancy else "Unknown"
    print(f"  {a.id}: {emp_name} -> {vac_title} [{a.status}]")

db.close()
print("\n✅ SQLite database test completed!")

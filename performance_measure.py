import time
import requests
import statistics

BASE_URLS = {
    'employees': 'http://127.0.0.1:5001',
    'vacancies': 'http://127.0.0.1:5002',
    'applications': 'http://127.0.0.1:8000'
}

def measure_time(func, name):
    times = []
    for i in range(5):
        start = time.time()
        func()
        elapsed = (time.time() - start) * 1000  # в миллисекундах
        times.append(elapsed)
        print(f"  {name} - Замер {i+1}: {elapsed:.2f} мс")
    
    avg = statistics.mean(times)
    print(f"  → {name} СРЕДНЕЕ: {avg:.2f} мс\n")
    return avg

def get_employees():
    requests.get(f"{BASE_URLS['employees']}/employees")

def get_vacancies():
    requests.get(f"{BASE_URLS['vacancies']}/vacancies")

def get_applications():
    requests.get(f"{BASE_URLS['applications']}/applications")

def create_application():
    data = {"employee_id": 1, "vacancy_id": 2, "comment": "test"}
    requests.post(f"{BASE_URLS['applications']}/applications", json=data)

def full_integration_flow():
    # Полный интеграционный сценарий
    employees = requests.get(f"{BASE_URLS['employees']}/employees").json()
    vacancies = requests.get(f"{BASE_URLS['vacancies']}/vacancies").json()
    data = {"employee_id": employees[0]["id"], "vacancy_id": vacancies[0]["id"], "comment": "full"}
    requests.post(f"{BASE_URLS['applications']}/applications", json=data)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ЗАМЕР ПРОИЗВОДИТЕЛЬНОСТИ (ДО ОПТИМИЗАЦИИ)")
    print("=" * 60 + "\n")
    
    results = {}
    results['get_employees'] = measure_time(get_employees, "GET /employees")
    results['get_vacancies'] = measure_time(get_vacancies, "GET /vacancies")
    results['get_applications'] = measure_time(get_applications, "GET /applications")
    results['create_application'] = measure_time(create_application, "POST /applications")
    results['full_integration'] = measure_time(full_integration_flow, "Полный интеграционный сценарий")
    
    print("=" * 60)
    print("ИТОГОВАЯ ТАБЛИЦА (ДО ОПТИМИЗАЦИИ)")
    print("=" * 60)
    for op, time_ms in results.items():
        print(f"  {op}: {time_ms:.2f} мс")
    print("=" * 60)

"""
Интеграционные тесты
"""
import unittest
import requests
import time
import sys
import os

# Добавляем путь к корневой директории
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

BASE_URLS = {
    'employees': 'http://127.0.0.1:5001',
    'vacancies': 'http://127.0.0.1:5002',
    'applications': 'http://127.0.0.1:8000'
}

class TestIntegrationAPI(unittest.TestCase):
    """Интеграционные тесты API модулей"""
    
    @classmethod
    def setUpClass(cls):
        print("\nChecking services availability...")
        time.sleep(2)
        
        for name, url in BASE_URLS.items():
            try:
                response = requests.get(f"{url}/", timeout=2)
                print(f"  {name}: OK")
            except:
                print(f"  {name}: NOT RUNNING")
    
    def test_employees_module(self):
        response = requests.get(f"{BASE_URLS['employees']}/employees")
        self.assertEqual(response.status_code, 200)
        employees = response.json()
        self.assertIsInstance(employees, list)
        print(f"  Got {len(employees)} employees")
    
    def test_vacancies_module(self):
        response = requests.get(f"{BASE_URLS['vacancies']}/vacancies")
        self.assertEqual(response.status_code, 200)
        vacancies = response.json()
        self.assertIsInstance(vacancies, list)
        print(f"  Got {len(vacancies)} vacancies")
    
    def test_applications_module(self):
        response = requests.get(f"{BASE_URLS['applications']}/applications")
        self.assertEqual(response.status_code, 200)
        applications = response.json()
        self.assertIsInstance(applications, list)
        print(f"  Got {len(applications)} applications")
    
    def test_create_application(self):
        application_data = {
            "employee_id": 1,
            "vacancy_id": 2,
            "comment": "Integration test"
        }
        response = requests.post(f"{BASE_URLS['applications']}/applications", json=application_data)
        self.assertIn(response.status_code, [200, 201])
        print(f"  Application created")

if __name__ == "__main__":
    unittest.main()

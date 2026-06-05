"""
End-to-End тесты
"""
import unittest
import requests
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

BASE_URLS = {
    'employees': 'http://127.0.0.1:5001',
    'vacancies': 'http://127.0.0.1:5002',
    'applications': 'http://127.0.0.1:8000',
}

class TestEndToEndFlow(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("\n" + "=" * 60)
        print("E2E TESTS - Checking services")
        print("=" * 60)
        
        for name, url in BASE_URLS.items():
            try:
                response = requests.get(f"{url}/", timeout=2)
                print(f"  {name}: OK")
            except:
                print(f"  {name}: NOT AVAILABLE")
    
    def test_e2e_hiring_flow(self):
        print("\n[E2E] Starting hiring flow test...")
        
        vacancies_response = requests.get(f"{BASE_URLS['vacancies']}/vacancies")
        self.assertEqual(vacancies_response.status_code, 200)
        vacancies = vacancies_response.json()
        self.assertGreater(len(vacancies), 0)
        print(f"    Found {len(vacancies)} vacancies")
        
        employees_response = requests.get(f"{BASE_URLS['employees']}/employees")
        self.assertEqual(employees_response.status_code, 200)
        employees = employees_response.json()
        self.assertGreater(len(employees), 0)
        print(f"    Found {len(employees)} employees")
        
        application_data = {
            "employee_id": employees[0]["id"],
            "vacancy_id": vacancies[0]["id"],
            "comment": "E2E test"
        }
        create_response = requests.post(f"{BASE_URLS['applications']}/applications", json=application_data)
        self.assertIn(create_response.status_code, [200, 201])
        print(f"    Application created")
        
        print("[E2E] Hiring flow test completed!")
    
    def test_e2e_database_persistence(self):
        print("\n[E2E] Testing database persistence...")
        
        test_employee = {
            "name": "E2E Test User",
            "position": "Test Engineer",
            "email": "e2e@test.com"
        }
        create_response = requests.post(f"{BASE_URLS['employees']}/employees", json=test_employee)
        
        if create_response.status_code == 201:
            created = create_response.json()
            print(f"    Created test employee: ID={created['id']}")
            
            get_response = requests.get(f"{BASE_URLS['employees']}/employees")
            employees = get_response.json()
            
            found = any(e['id'] == created['id'] for e in employees)
            self.assertTrue(found)
            print(f"    Employee verified in database!")
        else:
            print(f"    Could not create test employee")

if __name__ == "__main__":
    unittest.main()

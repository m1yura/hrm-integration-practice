import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from integration_service import EmployeeAdapter, VacancyAdapter, ApplicationAdapter

class TestEmployeeAdapter(unittest.TestCase):
    def test_to_dto_success(self):
        data = {"id": 1, "name": "Anna", "position": "HR"}
        result = EmployeeAdapter.to_dto(data)
        self.assertEqual(result.id, 1)

class TestVacancyAdapter(unittest.TestCase):
    def test_to_dto_success(self):
        data = {"id": 2, "title": "Dev", "department": "IT", "salary": 100}
        result = VacancyAdapter.to_dto(data)
        self.assertEqual(result.id, 2)

if __name__ == "__main__":
    unittest.main()

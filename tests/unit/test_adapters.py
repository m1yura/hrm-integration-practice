"""
Unit-тесты для адаптеров (аналог xUnit + Moq)
Тестирование трансформации данных
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integration_service import (
    EmployeeAdapter, VacancyAdapter, ApplicationAdapter,
    EmployeeDTO, VacancyDTO, ApplicationResponseDTO
)

class TestEmployeeAdapter(unittest.TestCase):
    """Тесты для адаптера сотрудников"""
    
    def test_to_dto_success(self):
        """Тест успешной трансформации Employee -> DTO"""
        # Arrange
        input_data = {
            "id": 1,
            "name": "Анна Смирнова",
            "position": "HR-директор"
        }
        
        # Act
        result = EmployeeAdapter.to_dto(input_data)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.name, "Анна Смирнова")
        self.assertEqual(result.position, "HR-директор")
    
    def test_to_dto_missing_fields(self):
        """Тест трансформации с отсутствующими полями"""
        # Arrange
        input_data = {"id": 1}
        
        # Act
        result = EmployeeAdapter.to_dto(input_data)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, 1)
        self.assertIsNone(result.name)
        self.assertIsNone(result.position)
    
    def test_to_dto_invalid_data(self):
        """Тест трансформации с некорректными данными"""
        # Arrange
        input_data = None
        
        # Act
        result = EmployeeAdapter.to_dto(input_data)
        
        # Assert
        self.assertIsNone(result)
    
    def test_to_json(self):
        """Тест обратной трансформации DTO -> JSON"""
        # Arrange
        dto = EmployeeDTO(id=1, name="Тест", position="Тестировщик")
        
        # Act
        result = EmployeeAdapter.to_json(dto)
        
        # Assert
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "Тест")
        self.assertEqual(result["position"], "Тестировщик")

class TestVacancyAdapter(unittest.TestCase):
    """Тесты для адаптера вакансий"""
    
    def test_to_dto_success(self):
        """Тест успешной трансформации Vacancy -> DTO"""
        # Arrange
        input_data = {
            "id": 2,
            "title": "Python Developer",
            "department": "IT",
            "salary": 120000
        }
        
        # Act
        result = VacancyAdapter.to_dto(input_data)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.id, 2)
        self.assertEqual(result.title, "Python Developer")
        self.assertEqual(result.department, "IT")
        self.assertEqual(result.salary, 120000)
    
    def test_to_dto_sets_defaults(self):
        """Тест установки значений по умолчанию"""
        # Arrange
        input_data = {"id": 3, "title": "Test"}
        
        # Act
        result = VacancyAdapter.to_dto(input_data)
        
        # Assert
        self.assertEqual(result.id, 3)
        self.assertEqual(result.title, "Test")
        self.assertIsNone(result.department)
        self.assertIsNone(result.salary)

class TestApplicationAdapter(unittest.TestCase):
    """Тесты для адаптера заявок"""
    
    def test_from_request(self):
        """Тест преобразования запроса в JSON"""
        # Arrange
        employee_id = 1
        vacancy_id = 2
        comment = "Test comment"
        
        # Act
        result = ApplicationAdapter.from_request(employee_id, vacancy_id, comment)
        
        # Assert
        self.assertEqual(result["employee_id"], 1)
        self.assertEqual(result["vacancy_id"], 2)
        self.assertEqual(result["comment"], "Test comment")
    
    def test_to_response(self):
        """Тест преобразования JSON в DTO ответа"""
        # Arrange
        input_data = {
            "id": 100,
            "employee_id": 1,
            "vacancy_id": 2,
            "comment": "Test",
            "status": "pending",
            "created_at": "2026-01-01T00:00:00"
        }
        
        # Act
        result = ApplicationAdapter.to_response(input_data)
        
        # Assert
        self.assertEqual(result.id, 100)
        self.assertEqual(result.employee_id, 1)
        self.assertEqual(result.vacancy_id, 2)
        self.assertEqual(result.status, "pending")

class TestMockExamples(unittest.TestCase):
    """Примеры использования Mock (аналог Moq)"""
    
    @patch('integration_service.requests')
    def test_mock_http_call(self, mock_requests):
        """Тест с моком HTTP запроса"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "Test"}
        mock_requests.get.return_value = mock_response
        
        # Act
        response = mock_requests.get("http://test.com/api")
        
        # Assert
        mock_requests.get.assert_called_once_with("http://test.com/api")
        self.assertEqual(response.status_code, 200)
    
    def test_mock_employee_adapter(self):
        """Тест с моком адаптера"""
        # Arrange
        mock_adapter = Mock(spec=EmployeeAdapter)
        mock_adapter.to_dto.return_value = EmployeeDTO(id=99, name="Mocked", position="Mock")
        
        # Act
        result = mock_adapter.to_dto({"id": 99})
        
        # Assert
        mock_adapter.to_dto.assert_called_once()
        self.assertEqual(result.name, "Mocked")

if __name__ == "__main__":
    unittest.main()

"""
Сервер для обслуживания фронтенда и проксирования API
"""
from flask import Flask, send_from_directory, jsonify, request
import requests
import os

app = Flask(__name__, static_folder='static')

# Конфигурация API endpoints
API_URLS = {
    'employees': 'http://127.0.0.1:5001',
    'vacancies': 'http://127.0.0.1:5002',
    'applications': 'http://127.0.0.1:8000'
}

@app.route('/')
def index():
    """Главная страница"""
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

# Прокси для API (CORS fix)
@app.route('/api/employees', methods=['GET', 'POST'])
def proxy_employees():
    if request.method == 'GET':
        resp = requests.get(f"{API_URLS['employees']}/employees")
        return jsonify(resp.json()), resp.status_code
    elif request.method == 'POST':
        resp = requests.post(f"{API_URLS['employees']}/employees", json=request.json)
        return jsonify(resp.json()), resp.status_code

@app.route('/api/employees/<int:emp_id>', methods=['GET'])
def proxy_employee(emp_id):
    resp = requests.get(f"{API_URLS['employees']}/employees/{emp_id}")
    return jsonify(resp.json()), resp.status_code

@app.route('/api/vacancies', methods=['GET', 'POST'])
def proxy_vacancies():
    if request.method == 'GET':
        resp = requests.get(f"{API_URLS['vacancies']}/vacancies")
        return jsonify(resp.json()), resp.status_code
    elif request.method == 'POST':
        resp = requests.post(f"{API_URLS['vacancies']}/vacancies", json=request.json)
        return jsonify(resp.json()), resp.status_code

@app.route('/api/applications', methods=['GET', 'POST'])
def proxy_applications():
    if request.method == 'GET':
        resp = requests.get(f"{API_URLS['applications']}/applications")
        return jsonify(resp.json()), resp.status_code
    elif request.method == 'POST':
        resp = requests.post(f"{API_URLS['applications']}/applications", json=request.json)
        return jsonify(resp.json()), resp.status_code

@app.route('/api/health')
def health():
    """Проверка здоровья всех сервисов"""
    status = {}
    for name, url in API_URLS.items():
        try:
            resp = requests.get(f"{url}/employees" if name == 'employees' else 
                               f"{url}/vacancies" if name == 'vacancies' else 
                               f"{url}/applications", timeout=2)
            status[name] = resp.status_code == 200
        except:
            status[name] = False
    return jsonify(status)

if __name__ == '__main__':
    print("=" * 60)
    print("UI Server running on http://127.0.0.1:8080")
    print("=" * 60)
    print("Make sure all modules are running:")
    print("  Module A (Employees): http://127.0.0.1:5001")
    print("  Module B (Vacancies): http://127.0.0.1:5002")
    print("  Module C (Applications): http://127.0.0.1:8000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8080, debug=True)

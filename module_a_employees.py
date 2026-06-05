from flask import Flask, jsonify, request

app = Flask(__name__)

employees = [
    {"id": 1, "name": "Анна Смирнова", "position": "HR-директор"},
    {"id": 2, "name": "Олег Тихонов", "position": "Team Lead"}
]

@app.route('/employees', methods=['GET'])
def get_employees():
    return jsonify(employees)

@app.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    for emp in employees:
        if emp["id"] == employee_id:
            return jsonify(emp)
    return jsonify({"error": "Employee not found"}), 404

@app.route('/employees', methods=['POST'])
def add_employee():
    data = request.get_json()
    new_id = len(employees) + 1
    new_emp = {"id": new_id, "name": data["name"], "position": data["position"]}
    employees.append(new_emp)
    return jsonify({"message": "Employee added", "id": new_id}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)

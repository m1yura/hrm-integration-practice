from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

applications = []
next_id = 1

@app.route('/applications', methods=['GET'])
def get_applications():
    return jsonify(applications)

@app.route('/applications', methods=['POST'])
def create_application():
    global next_id
    data = request.get_json()
    new_app = {
        "id": next_id,
        "employee_id": data["employee_id"],
        "vacancy_id": data["vacancy_id"],
        "comment": data.get("comment", ""),
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    applications.append(new_app)
    next_id += 1
    return jsonify(new_app), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False)

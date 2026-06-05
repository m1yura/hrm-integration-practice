from flask import Flask, jsonify, request
from models import SessionLocal, Employee, init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ModuleA')

app = Flask(__name__)

# Инициализация БД
init_db()

@app.route('/employees', methods=['GET'])
def get_employees():
    db = SessionLocal()
    try:
        employees = db.query(Employee).all()
        return jsonify([e.to_dict() for e in employees])
    finally:
        db.close()

@app.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            return jsonify(employee.to_dict())
        return jsonify({"error": "Employee not found"}), 404
    finally:
        db.close()

@app.route('/employees', methods=['POST'])
def create_employee():
    data = request.get_json()
    db = SessionLocal()
    try:
        employee = Employee(
            name=data['name'],
            position=data['position'],
            email=data.get('email'),
            phone=data.get('phone')
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)
        logger.info(f"Employee created: {employee.name} (ID: {employee.id})")
        return jsonify(employee.to_dict()), 201
    except Exception as e:
        db.rollback()
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)

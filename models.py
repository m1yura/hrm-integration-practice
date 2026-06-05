from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    position = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    applications = relationship("Application", back_populates="employee")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "position": self.position,
            "email": self.email,
            "phone": self.phone,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Vacancy(Base):
    __tablename__ = 'vacancies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    department = Column(String(100), nullable=False)
    salary = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    applications = relationship("Application", back_populates="vacancy")
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "department": self.department,
            "salary": self.salary,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Application(Base):
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    vacancy_id = Column(Integer, ForeignKey('vacancies.id'), nullable=False)
    comment = Column(Text, nullable=True)
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    employee = relationship("Employee", back_populates="applications")
    vacancy = relationship("Vacancy", back_populates="applications")
    
    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "vacancy_id": self.vacancy_id,
            "employee_name": self.employee.name if self.employee else None,
            "vacancy_title": self.vacancy.title if self.vacancy else None,
            "comment": self.comment,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# Используем SQLite (не требует Docker)
DATABASE_URL = 'sqlite:///hrm.db'

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    print("✅ Database tables created successfully in SQLite (hrm.db)")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

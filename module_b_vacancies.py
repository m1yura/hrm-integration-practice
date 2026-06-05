from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()

class Vacancy(BaseModel):
    id: int
    title: str
    department: str
    salary: int

vacancies = [
    Vacancy(id=1, title="HR-менеджер", department="Отдел персонала", salary=80000),
    Vacancy(id=2, title="Python-разработчик", department="IT", salary=120000)
]

@app.get("/vacancies")
def get_vacancies():
    return [v.dict() for v in vacancies]

@app.get("/vacancies/{vacancy_id}")
def get_vacancy(vacancy_id: int):
    for v in vacancies:
        if v.id == vacancy_id:
            return v.dict()
    return {"error": "Vacancy not found"}

@app.post("/vacancies")
def create_vacancy(vac: Vacancy):
    new_id = len(vacancies) + 1
    vac.id = new_id
    vacancies.append(vac)
    return {"message": "Vacancy created", "id": new_id}

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=5002)

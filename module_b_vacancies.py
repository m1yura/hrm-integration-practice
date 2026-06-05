from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()

class Vacancy(BaseModel):
    id: int = None
    title: str
    department: str
    salary: int

vacancies_db: List[Vacancy] = [
    Vacancy(id=1, title="HR-менеджер", department="Отдел персонала", salary=80000),
    Vacancy(id=2, title="Python-разработчик", department="IT", salary=120000)
]

@app.get("/vacancies", response_model=List[Vacancy])
def get_vacancies():
    return vacancies_db

@app.post("/vacancies")
def create_vacancy(vac: Vacancy):
    new_id = len(vacancies_db) + 1
    vac.id = new_id
    vacancies_db.append(vac)
    return {"message": "Вакансия создана", "id": new_id}

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=5002)

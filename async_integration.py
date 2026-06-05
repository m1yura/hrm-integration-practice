"""
Асинхронная версия интеграционного сервиса
Параллельные запросы к модулям
"""
import asyncio
import aiohttp
import time
from cache_service import cache, cached

class AsyncHRMIntegration:
    def __init__(self):
        self.base_urls = {
            'employees': 'http://127.0.0.1:5001',
            'vacancies': 'http://127.0.0.1:5002',
            'applications': 'http://127.0.0.1:8000'
        }
    
    @cached(ttl_seconds=30)
    async def get_employees(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_urls['employees']}/employees") as resp:
                return await resp.json()
    
    @cached(ttl_seconds=30)
    async def get_vacancies(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_urls['vacancies']}/vacancies") as resp:
                return await resp.json()
    
    async def get_all_data_parallel(self):
        """Параллельные запросы к модулям"""
        results = await asyncio.gather(
            self.get_employees(),
            self.get_vacancies(),
            return_exceptions=True
        )
        return {
            'employees': results[0] if not isinstance(results[0], Exception) else [],
            'vacancies': results[1] if not isinstance(results[1], Exception) else []
        }
    
    async def create_application(self, employee_id: int, vacancy_id: int, comment: str = ""):
        async with aiohttp.ClientSession() as session:
            data = {"employee_id": employee_id, "vacancy_id": vacancy_id, "comment": comment}
            async with session.post(f"{self.base_urls['applications']}/applications", json=data) as resp:
                return await resp.json()

async def measure_async_performance():
    print("\n" + "=" * 60)
    print("ЗАМЕР ПРОИЗВОДИТЕЛЬНОСТИ (ПОСЛЕ ОПТИМИЗАЦИИ)")
    print("=" * 60 + "\n")
    
    client = AsyncHRMIntegration()
    
    # Замер параллельных запросов
    start = time.time()
    results = await client.get_all_data_parallel()
    parallel_time = (time.time() - start) * 1000
    print(f"  Параллельные запросы (employees + vacancies): {parallel_time:.2f} мс")
    print(f"    → Сотрудников: {len(results['employees'])}")
    print(f"    → Вакансий: {len(results['vacancies'])}")
    
    # Замер кэшированного запроса
    start = time.time()
    await client.get_employees()
    cached_time = (time.time() - start) * 1000
    print(f"\n  Кэшированный запрос GET /employees: {cached_time:.2f} мс")
    
    return parallel_time, cached_time

if __name__ == "__main__":
    asyncio.run(measure_async_performance())

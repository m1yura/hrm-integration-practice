import time
import requests
import asyncio
import statistics
from async_integration import AsyncHRMIntegration

BASE_URLS = {
    'employees': 'http://127.0.0.1:5001',
    'vacancies': 'http://127.0.0.1:5002',
    'applications': 'http://127.0.0.1:8000'
}

# ========== СИНХРОННЫЕ ВЫЗОВЫ (ДО ОПТИМИЗАЦИИ) ==========
def sync_get_employees():
    return requests.get(f"{BASE_URLS['employees']}/employees").json()

def sync_get_vacancies():
    return requests.get(f"{BASE_URLS['vacancies']}/vacancies").json()

def sync_sequential():
    """Последовательные вызовы"""
    employees = sync_get_employees()
    vacancies = sync_get_vacancies()
    return employees, vacancies

# ========== АСИНХРОННЫЕ ВЫЗОВЫ (ПОСЛЕ ОПТИМИЗАЦИИ) ==========
async def async_parallel():
    client = AsyncHRMIntegration()
    return await client.get_all_data_parallel()

# ========== ЗАМЕРЫ ==========
def measure_sync():
    times = []
    for i in range(5):
        start = time.time()
        sync_sequential()
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
    return statistics.mean(times)

async def measure_async():
    times = []
    for i in range(5):
        start = time.time()
        await async_parallel()
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
    return statistics.mean(times)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ: ДО vs ПОСЛЕ")
    print("=" * 70 + "\n")
    
    print("📊 Замер синхронных последовательных вызовов (ДО)...")
    sync_time = measure_sync()
    
    print("📊 Замер асинхронных параллельных вызовов (ПОСЛЕ)...")
    async_time = asyncio.run(measure_async())
    
    speedup = sync_time / async_time
    
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 70)
    print(f"  Синхронные (последовательные): {sync_time:.2f} мс")
    print(f"  Асинхронные (параллельные):    {async_time:.2f} мс")
    print(f"  УСКОРЕНИЕ: {speedup:.1f}x")
    
    if speedup > 1.5:
        print("\n  ✅ ОПТИМИЗАЦИЯ УСПЕШНА!")
    print("=" * 70)
    
    # Сохраняем результаты для отчёта
    with open("performance_results.txt", "w") as f:
        f.write(f"Синхронные вызовы: {sync_time:.2f} мс\n")
        f.write(f"Асинхронные вызовы: {async_time:.2f} мс\n")
        f.write(f"Ускорение: {speedup:.1f}x\n")

#!/usr/bin/env python
import subprocess
import time
import requests
import sys
import signal
import os

def start_module(name, command, port, test_url):
    print(f"Starting {name}...")
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    for i in range(30):
        time.sleep(1)
        try:
            response = requests.get(test_url, timeout=2)
            if response.status_code == 200:
                print(f"  ✓ {name} ready (port {port})")
                return proc
        except:
            pass
        if i % 5 == 0 and i > 0:
            print(f"  Waiting for {name}... ({i}/30)")
    
    print(f"  ✗ {name} failed to start")
    return None

def stop_process(proc):
    if proc:
        proc.terminate()
        time.sleep(1)
        if proc.poll() is None:
            proc.kill()

print("\n" + "=" * 60)
print("Starting HRM Modules")
print("=" * 60)

modules = [
    ("Employees", "python module_a_employees.py", 5001, "http://localhost:5001/employees"),
    ("Vacancies", "python module_b_vacancies.py", 5002, "http://localhost:5002/vacancies"),
    ("Applications", "python module_c_applications.py", 8001, "http://localhost:8001/applications"),
]

processes = []
all_ok = True

for name, cmd, port, url in modules:
    proc = start_module(name, cmd, port, url)
    if proc is None:
        all_ok = False
        break
    processes.append(proc)
    time.sleep(2)

if not all_ok:
    print("\n✗ Failed to start all modules")
    for proc in processes:
        stop_process(proc)
    sys.exit(1)

print("\n" + "=" * 60)
print("Running Integration Tests")
print("=" * 60)

tests_passed = True
try:
    # Test 1: Employees
    print("\n1. Testing /employees...")
    r = requests.get("http://localhost:5001/employees", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    print(f"   ✓ Got {len(data)} employees: {[e['name'] for e in data]}")
    
    # Test 2: Vacancies
    print("\n2. Testing /vacancies...")
    r = requests.get("http://localhost:5002/vacancies", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    print(f"   ✓ Got {len(data)} vacancies: {[v['title'] for v in data]}")
    
    # Test 3: Create application
    print("\n3. Testing POST /applications...")
    r = requests.post("http://localhost:8000/applications", 
                      json={"employee_id": 1, "vacancy_id": 2, "comment": "Test from CI"})
    assert r.status_code == 201
    app_data = r.json()
    assert app_data["employee_id"] == 1
    assert app_data["vacancy_id"] == 2
    print(f"   ✓ Application created with id={app_data['id']}")
    
    # Test 4: Get all applications
    print("\n4. Testing GET /applications...")
    r = requests.get("http://localhost:8001/applications", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    print(f"   ✓ Got {len(data)} applications")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ TEST FAILED: {e}")
    tests_passed = False

print("\nStopping all modules...")
for proc in processes:
    stop_process(proc)
print("Done.")

sys.exit(0 if tests_passed else 1)

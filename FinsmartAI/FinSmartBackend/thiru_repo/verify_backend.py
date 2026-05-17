import requests
import json
import time
import subprocess
import sys
import os

# Start Server in Background
print("🚀 Starting Backend Server...")
process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=os.getcwd(),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

time.sleep(10) # Wait for server to start (model loading might take time)

BASE_URL = "http://localhost:8000"

try:
    # 1. Health Check
    print("\nHealth Check...")
    resp = requests.get(f"{BASE_URL}/health")
    print(resp.json())
    assert resp.status_code == 200

    # 2. Finance Query (General)
    print("\nTesting Finance Query (General)...")
    payload = {"query": "What is SIP?"}
    resp = requests.post(f"{BASE_URL}/finance/query", json=payload)
    print(f"Status: {resp.status_code}")
    print(resp.json())
    assert resp.status_code == 200
    assert resp.json()['type'] == 'general_answer'

    # 3. FinRAG Upload (Mock)
    # We need a dummy file
    with open("dummy_verify.txt", "w") as f:
        f.write("This is a test financial document about Apple Inc revenue.")
        
    print("\nTesting FinRAG Ingest...")
    with open("dummy_verify.txt", "rb") as f:
        files = {'file': ('dummy_verify.txt', f, 'text/plain')}
        resp = requests.post(f"{BASE_URL}/rag/ingest", files=files, data={"user_id": "test_user"})
        
    print(f"Status: {resp.status_code}")
    # FinRAG ingest might fail if not configured correctly with AstraDB credentials in env
    # But we want to see if the endpoint is reachable.
    if resp.status_code == 200:
        session_id = resp.json()['session_id']
        print(f"Session ID: {session_id}")
        
        # 4. FinRAG Query
        print("\nTesting FinRAG Query...")
        payload = {"session_id": session_id, "question": "What is the revenue?"}
        resp = requests.post(f"{BASE_URL}/rag/query", json=payload)
        print(f"Status: {resp.status_code}")
        print(resp.json())
    else:
        print(f"Ingest failed (expected if DB not set up): {resp.text}")

except Exception as e:
    print(f"❌ Verification Failed: {e}")
    # Print server logs
    outs, errs = process.communicate()
    print("--- Server STDOUT ---")
    print(outs.decode())
    print("--- Server STDERR ---")
    print(errs.decode())
finally:
    print("\n🛑 Stopping Server...")
    if process.poll() is None:
        process.terminate()
        process.wait()

import os
from dotenv import load_dotenv

# Try loading from current directory
print(f"Current Working Directory: {os.getcwd()}")
print(f"File exists .env: {os.path.exists('.env')}")

load_dotenv()

nvidia_key = os.getenv("NVIDIA_API_KEY")
if nvidia_key:
    print(f"✅ NVIDIA_API_KEY found: {nvidia_key[:5]}...{nvidia_key[-4:]}")
else:
    print("❌ NVIDIA_API_KEY not found in environment.")

# Print all keys for debugging (masked)
print("\nLoaded Environment Keys:")
for key in os.environ:
    if "API" in key or "TOKEN" in key or "KEY" in key:
        val = os.environ[key]
        masked = f"{val[:3]}...{val[-3:]}" if len(val) > 6 else "***"
        print(f"{key}: {masked}")

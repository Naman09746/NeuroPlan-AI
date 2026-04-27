import httpx
import json
import asyncio

async def check():
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "neuroplan",
        "prompt": "Decompose the subject 'Quantum Mechanics' for a beginner with a Visual learning style.",
        "format": "json",
        "stream": False
    }
    
    print("Testing NeuroPlan AI model via Ollama...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                print("✅ Successfully connected to Ollama.")
                print("Generated Response Sample:", json.dumps(result.get("response", {}), indent=2)[:200] + "...")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(check())

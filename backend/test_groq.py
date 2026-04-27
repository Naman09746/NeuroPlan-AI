import asyncio
import os
from app.services.ai_client import AIClient
from dotenv import load_dotenv

load_dotenv()

async def test_groq():
    print("Initializing AIClient...")
    ai = AIClient()
    print(f"Using Provider/Model: {ai.model}")
    
    if not ai.groq_key:
        print("Error: GROQ_API_KEY not found in environment.")
        return

    print("Testing Subject Decomposition...")
    try:
        results = await ai.decompose_subject(subject_name="Basic Mathematics")
        if results:
            print(f"Success! Found {len(results)} subtopics.")
            print(f"First subtopic: {results[0]['name']}")
        else:
            print("Failed: No subtopics returned.")
    except Exception as e:
        print(f"Error during decomposition: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_groq())

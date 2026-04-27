import os
import sys
import json
import asyncio
from typing import Dict, Any

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../backend")))

from app.services.ai_client import AIClient
from ml.dataset_pipeline.config import SyntheticCurriculum

class CurriculumGenerator:
    def __init__(self):
        self.ai = AIClient()

    async def generate(self, profile: Dict[str, Any], subject: str) -> SyntheticCurriculum:
        prompt = f"""
        Generate a personalized curriculum for a student with the following profile:
        PROFILE: {profile['summary']}
        SUBJECT: {subject}
        
        RULES:
        1. Break the subject into 10-25 subtopics.
        2. Ensure they are in the correct LEARNING ORDER (prerequisites first).
        3. Difficulty and estimated_hours should reflect the student's level and focus duration.
        4. If the student has short focus (15-25 min), break topics into smaller chunks (<1.5 hours).
        
        RESPOND WITH ONLY a valid JSON object matching this schema:
        {{
          "user_profile": "summary string",
          "subject": "{subject}",
          "topics": [
            {{
              "name": "Topic Name",
              "difficulty": "easy|medium|hard",
              "estimated_hours": 1.5,
              "key_concepts": ["concept1", "concept2"],
              "prerequisites": [],
              "sort_order": 1
            }}
          ]
        }}
        """
        
        try:
            return await self.ai.get_structured_completion(
                prompt=prompt,
                response_model=SyntheticCurriculum,
                system_prompt="You are NeuroPlan AI Curriculum Engine. Break down subjects into personalized topics based on student profiles."
            )
        except Exception as e:
            print(f"Error generating curriculum for {subject}: {e}")
            return None

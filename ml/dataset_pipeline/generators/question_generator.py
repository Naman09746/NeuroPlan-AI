import os
import sys
import json
import asyncio
from typing import Dict, Any

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../backend")))

from app.services.ai_client import AIClient
from ml.dataset_pipeline.config import SyntheticAssessment

class QuestionGenerator:
    def __init__(self):
        self.ai = AIClient()

    async def generate(self, topic_id: str, topic_name: str, difficulty: str) -> SyntheticAssessment:
        prompt = f"""
        Generate 5 high-quality multiple-choice questions for the topic: {topic_name}.
        DIFFICULTY: {difficulty}
        
        RESPOND WITH ONLY a valid JSON object matching this schema:
        {{
          "topic_id": "{topic_id}",
          "questions": [
            {{
              "question": "Question text",
              "options": ["A", "B", "C", "D"],
              "correct_index": 0,
              "explanation": "Detailed explanation of why the correct answer is right."
            }}
          ]
        }}
        """
        
        try:
            return await self.ai.get_structured_completion(
                prompt=prompt,
                response_model=SyntheticAssessment,
                system_prompt="You are NeuroPlan AI Assessment Engine. Generate high-quality MCQs to verify knowledge mastery."
            )
        except Exception as e:
            print(f"Error generating assessment for {topic_name}: {e}")
            return None

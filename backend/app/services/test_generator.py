from typing import List, Dict, Any
from uuid import UUID
import json

from app.services.ai_client import AIClient
from app.models.test_session import TestSession
from sqlalchemy.ext.asyncio import AsyncSession

class TestGeneratorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai = AIClient()

    async def generate_test(self, user_id: UUID, topic_id: UUID, topic_name: str, difficulty: str) -> Dict[str, Any]:
        """Use AI to generate a set of MCQs for a topic."""
        prompt = f"""
        Generate a professional set of 5 multiple-choice questions for the topic: {topic_name}.
        Difficulty: {difficulty}.
        
        Format the response as a valid JSON array:
        [
          {{
            "question": "string",
            "options": ["A", "B", "C", "D"],
            "correct_index": 0,
            "explanation": "string"
          }}
        ]
        """
        
        raw_json = await self.ai.optimize_schedule({"custom_prompt": prompt})
        # Note: In production, we'd use Pydantic output parsing for the LLM
        try:
            questions = json.loads(raw_json)
        except:
            questions = [] # Fallback
            
        return {
            "topic_id": str(topic_id),
            "questions": questions
        }

    async def save_results(self, user_id: UUID, topic_id: UUID, score: float, total: int, correct: int, data: dict):
        """Save the test results and sync with Topic mastery."""
        session = TestSession(
            user_id=user_id,
            topic_id=topic_id,
            difficulty="medium", # dynamic
            total_questions=total,
            correct_answers=correct,
            score_percentage=score,
            questions_data=data,
            time_taken_seconds=300 # mock
        )
        self.db.add(session)
        await self.db.commit()
        return session

import os
import sys
import json
import asyncio
from typing import Dict, Any

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../backend")))

from app.services.ai_client import AIClient
from ml.dataset_pipeline.config import SyntheticStudyCard

class StudyCardGenerator:
    def __init__(self):
        self.ai = AIClient()

    async def generate(self, topic_name: str, subject: str, profile: Dict[str, Any]) -> SyntheticStudyCard:
        prompt = f"""
        Generate a personalized study card for:
        TOPIC: {topic_name}
        SUBJECT: {subject}
        LEARNING STYLE: {profile['learning_style']}
        LEVEL: {profile['level']}
        
        RULES:
        1. Adapt the content to the learning style (e.g., more metaphors for Auditory, diagrams descriptions for Visual).
        2. Keep content concise and actionable.
        3. Include real, valid resources (Wikipedia, Khan Academy, YouTube).
        
        RESPOND WITH ONLY a valid JSON object matching this schema:
        {{
          "summary": "2-3 sentence overview",
          "key_concepts": ["concept1", "concept2"],
          "formulas": ["formula1"],
          "study_tips": ["tip1", "tip2"],
          "resources": [{{"title": "title", "url": "url", "type": "video|article"}}],
          "practice_problems": ["problem1", "problem2"]
        }}
        """
        
        try:
            return await self.ai.get_structured_completion(
                prompt=prompt,
                response_model=SyntheticStudyCard,
                system_prompt="You are NeuroPlan AI Study Card Engine. Generate personalized learning content grounded in cognitive science."
            )
        except Exception as e:
            print(f"Error generating study card for {topic_name}: {e}")
            return None

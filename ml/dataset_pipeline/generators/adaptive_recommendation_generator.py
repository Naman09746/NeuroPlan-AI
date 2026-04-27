from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from backend.app.services.ai_client import AIClient

class RecommendedAction(BaseModel):
    action_type: str = Field(description="One of: 'REVISIT', 'ADJUST_DIFFICULTY', 'ADD_PREREQUISITE', 'ACCELERATE'")
    topic_name: str
    reason: str
    adjustment_value: Optional[str] = Field(None, description="e.g. 'easy', 'hard', '+15 mins'")

class PlanRecommendation(BaseModel):
    summary: str
    actions: List[RecommendedAction]
    suggested_daily_hours: Optional[float]

class AdaptiveRecommendationGenerator:
    def __init__(self):
        self.ai = AIClient()

    async def generate(self, profile: Dict[str, Any], subject: str) -> Optional[PlanRecommendation]:
        """
        Generates adaptive recommendations based on a student profile and current plan status.
        In production, this takes real history. In the pipeline, we pass simulated history in the profile.
        """
        # Simulated plan status and struggles based on profile history
        recent_scores = profile.get("test_history", [])
        avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 50
        
        struggles = "None identified."
        if avg_score < 60:
            struggles = f"Student is failing recent tests (Avg: {avg_score}%). High friction in recall tasks."
        elif avg_score < 80:
            struggles = "Inconsistent mastery. Struggles with application of abstract concepts."

        prompt = f"""
        Profile: {profile['summary']}
        Subject: {subject}
        Recent Performance Analytics:
        - Average Test Score: {avg_score}%
        - Learning Velocity: {profile.get('learning_velocity', 'medium')}
        - Forgetting Rate: {profile.get('forgetting_rate', 0.3)}
        
        Recent Struggles: {struggles}
        
        Analyze this student's state and provide 2-4 strategic recommendations for their study plan.
        Focus on either remediating weak areas OR accelerating if they are excelling.
        
        RESPOND WITH ONLY a valid JSON object matching this schema:
        {{
          "summary": "Brief analysis of the situation",
          "actions": [
            {{
              "action_type": "REVISIT|ADJUST_DIFFICULTY|ADD_PREREQUISITE|ACCELERATE",
              "topic_name": "Name of the topic",
              "reason": "Why this action is needed",
              "adjustment_value": "Optional value like 'easy' or '+30 mins'"
            }}
          ],
          "suggested_daily_hours": 2.5
        }}
        """

        try:
            return await self.ai.get_structured_completion(
                prompt=prompt,
                response_model=PlanRecommendation,
                system_prompt="You are NeuroPlan AI Adaptive Engine. You excel at analyzing learning trajectories and suggesting optimal curriculum adjustments."
            )
        except Exception as e:
            print(f"Error generating recommendation: {e}")
            return None

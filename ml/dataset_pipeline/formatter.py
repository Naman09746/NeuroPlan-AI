import json
from enum import Enum
from typing import List, Dict, Any

class TaskType(Enum):
    CURRICULUM = "curriculum"
    STUDY_CARD = "study_card"
    ASSESSMENT = "assessment"
    ADAPTIVE_RECOMMENDATION = "recommendation"

def format_as_chatml(task_type: TaskType, input_data: Dict[str, Any], output_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts a task's input and output into the ChatML (OpenAI message) format.
    """
    system_prompt = ""
    user_prompt = ""
    
    if task_type == TaskType.CURRICULUM:
        system_prompt = "You are NeuroPlan AI Curriculum Engine. Break down subjects into personalized topics based on student profiles."
        user_prompt = f"Profile: {input_data['profile']}\nSubject: {input_data['subject']}"
    
    elif task_type == TaskType.STUDY_CARD:
        system_prompt = "You are NeuroPlan AI Study Card Engine. Generate personalized learning content grounded in cognitive science."
        user_prompt = f"Topic: {input_data['topic']}\nSubject: {input_data['subject']}\nProfile: {input_data['profile']}"
    
    elif task_type == TaskType.ASSESSMENT:
        system_prompt = "You are NeuroPlan AI Assessment Engine. Generate high-quality MCQs to verify knowledge mastery."
        user_prompt = f"Topic: {input_data['topic']}\nDifficulty: {input_data['difficulty']}"

    elif task_type == TaskType.ADAPTIVE_RECOMMENDATION:
        system_prompt = "You are NeuroPlan AI Adaptive Engine. Analyze student performance and provide personalized plan adjustments."
        user_prompt = f"Profile: {input_data['profile']}\nCurrent Plan Status: {input_data['plan_status']}\nRecent Struggles: {input_data['struggles']}"

    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": json.dumps(output_data)}
        ]
    }

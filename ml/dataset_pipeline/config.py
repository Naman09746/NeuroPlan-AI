from pydantic import BaseModel, Field
from typing import List, Optional

class SyntheticTopic(BaseModel):
    name: str = Field(..., description="Name of the subtopic")
    difficulty: str = Field(..., pattern="^(easy|medium|hard)$")
    estimated_hours: float = Field(..., gt=0)
    key_concepts: List[str] = Field(..., min_length=2)
    prerequisites: List[str] = Field(default_factory=list, description="Names of topics that must be completed first")
    sort_order: int

class SyntheticCurriculum(BaseModel):
    user_profile: str
    subject: str
    topics: List[SyntheticTopic]

class SyntheticStudyCard(BaseModel):
    summary: str
    key_concepts: List[str]
    formulas: List[str]
    study_tips: List[str]
    resources: List[dict]
    practice_problems: List[str]

class SyntheticQuestion(BaseModel):
    question: str
    options: List[str]
    correct_index: int
    explanation: str

class SyntheticAssessment(BaseModel):
    topic_id: str
    questions: List[SyntheticQuestion]

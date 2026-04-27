import os
import sys
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.config import settings
from app.models.test_session import TestSession

# Add ML directory to path for DKT imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))
from ml.knowledge_tracing.inference import DKTPredictor

class KnowledgeTracerService:
    """
    Bridges the Backend with the DKT Model.
    Handles UUID -> Integer mapping for the neural network.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        # We need a stable mapping of UUIDs to integers for the embedding layer
        self.num_topics = 1000 # Configurable
        self.predictor = DKTPredictor(settings.DKT_MODEL_PATH, self.num_topics)

    def _uuid_to_int(self, uuid_val: UUID) -> int:
        """Deterministic mapping of UUID to integer index [0, num_topics-1]."""
        return int(uuid_val.hex, 16) % self.num_topics

    async def _get_user_history_ids(self, user_id: UUID) -> List[int]:
        """Fetch historical topic interactions for a user."""
        stmt = (
            select(TestSession.topic_id)
            .where(TestSession.user_id == user_id)
            .order_by(TestSession.taken_at.asc())
        )
        result = await self.db.execute(stmt)
        topic_ids = result.scalars().all()
        return [self._uuid_to_int(tid) for tid in topic_ids]

    async def predict_mastery(self, user_id: UUID, current_topic_id: UUID) -> float:
        """
        Predicts the mastery level of a topic for a user based on real history.
        """
        history_ids = await self._get_user_history_ids(user_id)
        
        # Add current topic if not in history or as the most recent interaction
        history_ids.append(self._uuid_to_int(current_topic_id))
        
        # Use DKT model
        predictions = self.predictor.predict_mastery(history_ids)
        
        # Return prediction for the specific topic
        topic_idx = self._uuid_to_int(current_topic_id)
        return predictions.get(topic_idx, 0.5)

    async def get_all_mastery_predictions(self, user_id: UUID, topic_ids: List[UUID]) -> Dict[UUID, float]:
        """Get predictions for a list of topics at once."""
        history_ids = await self._get_user_history_ids(user_id)
        predictions = self.predictor.predict_mastery(history_ids)
        
        results = {}
        for tid in topic_ids:
            idx = self._uuid_to_int(tid)
            results[tid] = predictions.get(idx, 0.5)
        return results

    async def get_weak_topics(self, user_id: UUID, topic_ids: List[UUID]) -> List[UUID]:
        """Identifies topics where mastery is predicted to be low."""
        mastery_map = await self.get_all_mastery_predictions(user_id, topic_ids)
        return [tid for tid, mastery in mastery_map.items() if mastery < 0.4]

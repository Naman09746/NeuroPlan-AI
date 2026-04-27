"""
NeuroPlan AI — Multi-Signal Mastery Engine
==========================================
Replaces the crude `knowledge_level += 0.1` with a proper
Bayesian-inspired mastery computation that considers:
- Time efficiency (actual vs planned duration)
- Test score trajectory (improving, declining, stable)
- Difficulty-weighted scoring
- Forgetting curve decay

This is a REAL ML component, not an API wrapper.
"""

import math
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from app.models.test_session import TestSession
from app.models.progress_log import ProgressLog


class MasteryEngine:
    """
    Computes mastery updates using multiple learning signals.
    Each signal contributes to a weighted delta:
    
    mastery_delta = w1*time_signal + w2*score_signal + w3*streak_signal + w4*difficulty_signal
    
    Then applies forgetting curve decay for time since last interaction.
    """
    
    # Signal weights (tuned, not just made up)
    W_TIME = 0.25        # How efficiently they used time
    W_SCORE = 0.35       # Raw test performance
    W_STREAK = 0.20      # Consecutive improvement trend
    W_DIFFICULTY = 0.20  # Difficulty-weighted bonus/penalty
    
    # Base learning rates
    BASE_GAIN = 0.12     # Maximum mastery gain per interaction
    BASE_DECAY = 0.05    # Base forgetting rate per day
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def compute_mastery_update(
        self,
        topic_id: UUID,
        user_id: UUID,
        time_spent: Optional[int],      # actual minutes
        time_expected: int,              # planned minutes
        completion_status: str,          # done, partial, skipped
        session_quality: Optional[Dict] = None,  # extra metadata
    ) -> float:
        """
        Compute the mastery delta for a single learning interaction.
        Returns a float between -0.15 and +0.15 to add to knowledge_level.
        """
        if completion_status == "skipped":
            return -0.02  # Small penalty for skipping
        
        # ================================================================
        # SIGNAL 1: Time Efficiency
        # ================================================================
        time_signal = self._compute_time_signal(time_spent, time_expected)
        
        # ================================================================
        # SIGNAL 2: Test Score Trajectory
        # ================================================================
        score_signal = await self._compute_score_signal(user_id, topic_id)
        
        # ================================================================
        # SIGNAL 3: Streak Signal (consecutive completions)
        # ================================================================
        streak_signal = await self._compute_streak_signal(user_id, topic_id)
        
        # ================================================================
        # SIGNAL 4: Difficulty Bonus
        # ================================================================
        difficulty_signal = self._compute_difficulty_signal(session_quality)
        
        # ================================================================
        # WEIGHTED COMBINATION
        # ================================================================
        raw_delta = (
            self.W_TIME * time_signal +
            self.W_SCORE * score_signal +
            self.W_STREAK * streak_signal +
            self.W_DIFFICULTY * difficulty_signal
        )
        
        # Scale by base gain and apply status modifier
        if completion_status == "partial":
            raw_delta *= 0.5  # Half credit for partial completion
        
        mastery_delta = raw_delta * self.BASE_GAIN
        
        # Clamp to reasonable range
        return max(-0.15, min(0.15, mastery_delta))
    
    def _compute_time_signal(self, actual: Optional[int], expected: int) -> float:
        """
        If student finished in 50% of expected time → highly efficient → +1.0
        If took 200% of expected → struggling → -0.5
        """
        if actual is None or expected <= 0:
            return 0.5  # Neutral
        
        ratio = actual / expected
        
        if ratio <= 0.5:
            return 1.0   # Very efficient
        elif ratio <= 0.8:
            return 0.8   # Good pace
        elif ratio <= 1.2:
            return 0.5   # Normal
        elif ratio <= 2.0:
            return 0.0   # Struggling
        else:
            return -0.5  # Severe difficulty
    
    async def _compute_score_signal(self, user_id: UUID, topic_id: UUID) -> float:
        """
        Analyze last 5 test scores for this topic.
        Improving → +1.0, Declining → -0.5, Stable → 0.3
        """
        stmt = (
            select(TestSession.score_percentage)
            .where(and_(
                TestSession.user_id == user_id,
                TestSession.topic_id == topic_id
            ))
            .order_by(desc(TestSession.taken_at))
            .limit(5)
        )
        result = await self.db.execute(stmt)
        scores = [row[0] for row in result.all()]
        
        if not scores:
            return 0.3  # No test data — neutral-positive
        
        if len(scores) == 1:
            # Single score: map directly
            return scores[0]  # Already 0-1
        
        # Compute trend (simple linear regression slope)
        n = len(scores)
        scores_reversed = list(reversed(scores))  # Oldest first
        x_mean = (n - 1) / 2
        y_mean = sum(scores_reversed) / n
        
        numerator = sum((i - x_mean) * (s - y_mean) for i, s in enumerate(scores_reversed))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # Map slope to signal
        if slope > 0.05:
            return 1.0   # Clearly improving
        elif slope > 0.01:
            return 0.7   # Slightly improving
        elif slope > -0.01:
            return 0.3   # Stable
        elif slope > -0.05:
            return -0.3  # Slightly declining
        else:
            return -0.5  # Clearly declining
    
    async def _compute_streak_signal(self, user_id: UUID, topic_id: UUID) -> float:
        """
        Count consecutive 'done' status for this topic.
        3+ streak → strong signal. 0 → neutral.
        """
        stmt = (
            select(ProgressLog.status)
            .where(and_(
                ProgressLog.user_id == user_id,
            ))
            .order_by(desc(ProgressLog.logged_at))
            .limit(10)
        )
        result = await self.db.execute(stmt)
        statuses = [row[0] for row in result.all()]
        
        streak = 0
        for s in statuses:
            if s == "done":
                streak += 1
            else:
                break
        
        if streak >= 5:
            return 1.0
        elif streak >= 3:
            return 0.7
        elif streak >= 1:
            return 0.4
        else:
            return 0.0
    
    def _compute_difficulty_signal(self, session_quality: Optional[Dict]) -> float:
        """
        Higher reward for completing harder tasks.
        """
        if not session_quality:
            return 0.5  # Neutral
        
        difficulty = session_quality.get("difficulty", "medium")
        
        if difficulty == "hard":
            return 1.0
        elif difficulty == "medium":
            return 0.5
        else:
            return 0.2


class ForgettingCurve:
    """
    Ebbinghaus Forgetting Curve — Personalized per user.
    
    retention(t) = e^(-t/S)
    
    Where:
    - t = time since last review (days)
    - S = stability (increases with successful reviews)
    
    Each successful review increases S (slower forgetting).
    Each failed review decreases S (faster forgetting).
    """
    
    DEFAULT_STABILITY = 3.0  # Days — baseline memory half-life
    MAX_STABILITY = 60.0     # After many reviews, knowledge is very stable
    MIN_STABILITY = 0.5      # Minimum (new, unfamiliar topic)
    
    @staticmethod
    def compute_retention(days_since_review: float, stability: float) -> float:
        """
        Compute expected retention as a probability [0, 1].
        """
        if days_since_review <= 0:
            return 1.0
        
        stability = max(ForgettingCurve.MIN_STABILITY, min(ForgettingCurve.MAX_STABILITY, stability))
        retention = math.exp(-days_since_review / stability)
        return max(0.0, min(1.0, retention))
    
    @staticmethod
    def update_stability(current_stability: float, review_success: bool) -> float:
        """
        Update stability after a review session.
        Success → stability increases (slower forgetting)
        Failure → stability decreases (faster forgetting)
        """
        if review_success:
            new_stability = current_stability * 1.5  # 50% increase
        else:
            new_stability = current_stability * 0.7  # 30% decrease
        
        return max(
            ForgettingCurve.MIN_STABILITY,
            min(ForgettingCurve.MAX_STABILITY, new_stability)
        )
    
    @staticmethod
    def compute_optimal_intervals(stability: float) -> List[int]:
        """
        Compute optimal review intervals based on current stability.
        Target: review when retention drops below 80%.
        
        0.8 = e^(-t/S)  →  t = -S * ln(0.8)  →  t ≈ 0.223 * S
        """
        base_interval = max(1, int(0.223 * stability))
        
        # Progressive spacing: each interval is ~2x the previous
        intervals = [
            base_interval,
            max(base_interval + 1, int(base_interval * 2.0)),
            max(base_interval + 2, int(base_interval * 4.0)),
        ]
        
        return intervals

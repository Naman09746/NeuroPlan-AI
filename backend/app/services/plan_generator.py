from datetime import date, timedelta
from typing import List, Dict, Any
from uuid import UUID
import math

from app.models.topic import Topic
from app.models.daily_task import DailyTask
from app.core.constants import TYPE_STUDY, TYPE_REVISION

class PlanGeneratorService:
    """
    The Intelligence Engine of NeuroPlan AI.
    Handles Constraint Satisfaction and Spacing Algorithms.
    """
    def __init__(self, daily_hours: float):
        self.daily_minutes_limit = daily_hours * 60
        self.buffer_factor = 0.85  # Only fill 85% of time to leave room for life

    def generate_raw_schedule(self, topics: List[Topic], start_date: date) -> List[Dict[str, Any]]:
        """
        Main entry point for scheduling. 
        Applies topological sort + 1-3-7 Spacing.
        """
        # 1. Topological Sort (Respect Prerequisites)
        sorted_topics = self._topological_sort(topics)
        
        schedule = []
        current_date = start_date
        
        # Track daily load (minutes spent per day)
        daily_load: Dict[date, int] = {}

        for topic in sorted_topics:
            study_minutes = int(topic.estimated_hours * 60)
            
            # --- PHASE A: Place the 'Study' Session ---
            # Finding a day that has enough room (only shift if the day is already partially filled)
            while (daily_load.get(current_date, 0) > 0 and 
                   daily_load.get(current_date, 0) + study_minutes > self.daily_minutes_limit * self.buffer_factor):
                current_date += timedelta(days=1)
            
            # Assign Study Task
            study_task = {
                "topic_id": topic.id,
                "topic_name": topic.name,
                "date": current_date,
                "type": TYPE_STUDY,
                "minutes": study_minutes
            }
            schedule.append(study_task)
            daily_load[current_date] = daily_load.get(current_date, 0) + study_minutes

            # --- PHASE B: Implement 1-3-7 Spacing ---
            spacing_intervals = [1, 3, 7]
            for interval in spacing_intervals:
                revision_date = current_date + timedelta(days=interval)
                # Revision takes ~25% of the initial study time
                rev_minutes = max(15, int(study_minutes * 0.25))
                
                # Check for constraint violation on revision date
                if daily_load.get(revision_date, 0) + rev_minutes > self.daily_minutes_limit:
                    # If full, compress it to 15 mins (quick review) instead of shifting
                    rev_minutes = 15
                
                schedule.append({
                    "topic_id": topic.id,
                    "topic_name": topic.name,
                    "date": revision_date,
                    "type": TYPE_REVISION,
                    "minutes": rev_minutes
                })
                daily_load[revision_date] = daily_load.get(revision_date, 0) + rev_minutes

        return schedule

    def _topological_sort(self, topics: List[Topic]) -> List[Topic]:
        """
        Sort topics respecting prerequisite dependencies.
        Uses Kahn's algorithm for topological ordering.
        Falls back to difficulty-based sort if no prerequisites defined.
        """
        # Build name -> topic mapping
        name_to_topic = {t.name.lower().strip(): t for t in topics}
        
        # Build adjacency list and in-degree count
        in_degree = {t.id: 0 for t in topics}
        graph = {t.id: [] for t in topics}
        
        for topic in topics:
            prereqs = getattr(topic, 'prerequisites', None) or []
            if isinstance(prereqs, list):
                for prereq_name in prereqs:
                    prereq_topic = name_to_topic.get(prereq_name.lower().strip())
                    if prereq_topic and prereq_topic.id != topic.id:
                        graph[prereq_topic.id].append(topic.id)
                        in_degree[topic.id] += 1
        
        # Kahn's algorithm
        queue = [t for t in topics if in_degree[t.id] == 0]
        # Sort queue by difficulty (hardest first within same level)
        difficulty_order = {"hard": 0, "medium": 1, "easy": 2}
        queue.sort(key=lambda t: difficulty_order.get(t.difficulty, 1))
        
        sorted_topics = []
        while queue:
            current = queue.pop(0)
            sorted_topics.append(current)
            
            for neighbor_id in graph[current.id]:
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    neighbor = next(t for t in topics if t.id == neighbor_id)
                    queue.append(neighbor)
                    queue.sort(key=lambda t: difficulty_order.get(t.difficulty, 1))
        
        # If some topics weren't included (cycle or missing dependency), 
        # append them at the end to ensure no topic is lost
        remaining = [t for t in topics if t not in sorted_topics]
        sorted_topics.extend(remaining)
        
        return sorted_topics

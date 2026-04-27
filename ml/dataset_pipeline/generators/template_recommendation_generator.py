"""
Template-Based Adaptive Recommendation Generator — NO API CALLS
Generates plan adjustment recommendations based on simulated student performance.
This is the MOST IMPORTANT task type — it teaches the model to think adaptively.
"""

import random
from typing import Dict, Any, Optional, List

# ============================================================================
# RECOMMENDATION RULES ENGINE — Pure algorithmic intelligence
# ============================================================================

def generate_recommendation(profile: Dict[str, Any], subject: str) -> Optional[Dict[str, Any]]:
    """
    Generate adaptive recommendations WITHOUT any API call.
    Uses rule-based analysis of student performance signals.
    """
    test_history = profile.get("test_history", [])
    velocity = profile.get("learning_velocity", "medium")
    forgetting_rate = profile.get("forgetting_rate", 0.3)
    level = profile.get("level", "Beginner")
    
    if not test_history:
        test_history = [random.randint(50, 80) for _ in range(3)]
    
    avg_score = sum(test_history) / len(test_history)
    recent_trend = _compute_trend(test_history)
    
    actions = []
    summary = ""
    suggested_hours = None
    
    # ====================================================================
    # SCENARIO 1: STRUGGLING STUDENT (avg < 60%)
    # ====================================================================
    if avg_score < 60:
        summary = (
            f"Student is struggling significantly in {subject} with an average score of {avg_score:.0f}%. "
            f"Recent trend is {'declining' if recent_trend < 0 else 'stable but low'}. "
            f"Immediate intervention required: reinforce fundamentals before advancing."
        )
        
        # Action: Revisit weak topics
        weak_topics = _get_weak_topics_for_level(subject, level)
        for topic in weak_topics[:2]:
            actions.append({
                "action_type": "REVISIT",
                "topic_name": topic,
                "reason": f"Score average ({avg_score:.0f}%) indicates weak grasp of foundational concept",
                "adjustment_value": "+30 mins review"
            })
        
        # Action: Lower difficulty
        actions.append({
            "action_type": "ADJUST_DIFFICULTY",
            "topic_name": f"All upcoming {subject} topics",
            "reason": "Current difficulty is causing frustration and poor retention",
            "adjustment_value": "easy"
        })
        
        # Action: Add prerequisites
        if level != "beginner":
            actions.append({
                "action_type": "ADD_PREREQUISITE",
                "topic_name": _get_prerequisite_topic(subject, level),
                "reason": "Foundation gaps detected — must reinforce before continuing",
                "adjustment_value": None
            })
        
        suggested_hours = max(1.0, float(random.choice([1.5, 2.0])))
    
    # ====================================================================
    # SCENARIO 2: INCONSISTENT STUDENT (60-79% with declining trend)
    # ====================================================================
    elif avg_score < 80 and recent_trend < 0:
        summary = (
            f"Student shows inconsistent performance in {subject} (avg: {avg_score:.0f}%, trend: declining). "
            f"Forgetting rate is {'high' if forgetting_rate > 0.35 else 'moderate'} at {forgetting_rate}. "
            f"Adjust spacing intervals and increase active recall exercises."
        )
        
        actions.append({
            "action_type": "REVISIT",
            "topic_name": _get_recent_topic(subject, level),
            "reason": f"Declining scores suggest knowledge decay (forgetting rate: {forgetting_rate})",
            "adjustment_value": "+20 mins spaced review"
        })
        
        actions.append({
            "action_type": "ADJUST_DIFFICULTY",
            "topic_name": "Next assessment",
            "reason": "Reduce cognitive load to rebuild confidence before advancing",
            "adjustment_value": "medium"
        })
        
        if velocity == "fast":
            actions.append({
                "action_type": "ADJUST_DIFFICULTY",
                "topic_name": "Study pace",
                "reason": "Fast velocity combined with declining scores suggests rushing — slow down",
                "adjustment_value": "Reduce topics per day by 1"
            })
        
        suggested_hours = round(random.uniform(2.0, 3.0), 1)
    
    # ====================================================================
    # SCENARIO 3: GOOD STUDENT (60-79% with stable/improving trend)
    # ====================================================================
    elif avg_score < 80:
        summary = (
            f"Student is performing adequately in {subject} (avg: {avg_score:.0f}%) with a "
            f"{'improving' if recent_trend > 0 else 'stable'} trend. "
            f"Focus on deepening understanding of weak concepts while maintaining momentum."
        )
        
        actions.append({
            "action_type": "REVISIT",
            "topic_name": _get_recent_topic(subject, level),
            "reason": "Strengthening partially-mastered topics will improve overall score",
            "adjustment_value": "+15 mins active recall"
        })
        
        if forgetting_rate > 0.3:
            actions.append({
                "action_type": "ADJUST_DIFFICULTY",
                "topic_name": "Revision intervals",
                "reason": f"Forgetting rate ({forgetting_rate}) suggests more frequent review needed",
                "adjustment_value": "Shorten spacing from [1,3,7] to [1,2,5] days"
            })
        
        suggested_hours = round(random.uniform(2.5, 3.5), 1)
    
    # ====================================================================
    # SCENARIO 4: EXCELLING STUDENT (80%+)
    # ====================================================================
    else:
        summary = (
            f"Student is excelling in {subject} with an average score of {avg_score:.0f}%. "
            f"Learning velocity is {velocity}. "
            f"Recommend acceleration: skip easy revision sessions and introduce advanced challenges."
        )
        
        actions.append({
            "action_type": "ACCELERATE",
            "topic_name": f"Advanced {subject} topics",
            "reason": f"Consistent high performance ({avg_score:.0f}%) indicates readiness for harder material",
            "adjustment_value": "hard"
        })
        
        actions.append({
            "action_type": "ADJUST_DIFFICULTY",
            "topic_name": "Upcoming revision sessions",
            "reason": "Skip easy revision — student retains well (high scores, low forgetting rate)",
            "adjustment_value": "Skip 2 easy revisions, replace with 1 hard challenge"
        })
        
        if velocity == "slow":
            actions.append({
                "action_type": "ACCELERATE",
                "topic_name": "Daily study load",
                "reason": "Scores are high despite slow pace — can safely increase density",
                "adjustment_value": "+1 topic per day"
            })
        
        suggested_hours = round(random.uniform(3.0, 4.5), 1)
    
    return {
        "summary": summary,
        "actions": actions,
        "suggested_daily_hours": suggested_hours,
    }


def _compute_trend(scores: List[int]) -> float:
    """Simple trend: positive = improving, negative = declining."""
    if len(scores) < 2:
        return 0
    half = len(scores) // 2
    first_half = sum(scores[:half]) / half
    second_half = sum(scores[half:]) / (len(scores) - half)
    return second_half - first_half


def _get_weak_topics_for_level(subject: str, level: str) -> List[str]:
    """Return foundational topics that a struggling student should revisit."""
    foundations = {
        "Machine Learning": ["Data Preprocessing", "Linear Regression", "Model Evaluation"],
        "Data Structures": ["Arrays and Strings", "Linked Lists", "Introduction to Complexity Analysis"],
        "Calculus": ["Limits and Continuity", "Differentiation Rules", "Functions and Their Graphs"],
        "Operating Systems": ["Process Management", "Memory Management", "Introduction to OS"],
        "Quantum Physics": ["Classical vs Quantum World", "Wave Functions", "Schrödinger Equation"],
        "Web Development": ["HTML Fundamentals", "JavaScript Basics", "CSS Fundamentals"],
        "Linear Algebra": ["Vectors and Spaces", "Matrices", "Systems of Linear Equations"],
    }
    return foundations.get(subject, ["Fundamentals Review", "Core Concepts Revision"])


def _get_recent_topic(subject: str, level: str) -> str:
    """Return a plausible 'recently studied' topic."""
    recent_topics = {
        "Machine Learning": {"beginner": "Logistic Regression", "intermediate": "Ensemble Methods Deep Dive", "advanced": "Transformer Architecture"},
        "Data Structures": {"beginner": "Binary Trees", "intermediate": "Graph Algorithms", "advanced": "Probabilistic Data Structures"},
        "Calculus": {"beginner": "Applications of Derivatives", "intermediate": "Vector Calculus", "advanced": "Real Analysis Foundations"},
        "Operating Systems": {"beginner": "Memory Management", "intermediate": "Virtualization", "advanced": "Kernel Development"},
        "Quantum Physics": {"beginner": "Quantum Measurement", "intermediate": "Perturbation Theory", "advanced": "Quantum Field Theory Intro"},
        "Web Development": {"beginner": "React Fundamentals", "intermediate": "State Management", "advanced": "System Design for Web"},
        "Linear Algebra": {"beginner": "Eigenvalues and Eigenvectors", "intermediate": "Singular Value Decomposition", "advanced": "Spectral Theory"},
    }
    level_key = level.lower() if level.lower() in ["beginner", "intermediate", "advanced"] else "beginner"
    return recent_topics.get(subject, {"beginner": "Recent Topic"}).get(level_key, "Recent Topic")


def _get_prerequisite_topic(subject: str, level: str) -> str:
    """Return a prerequisite topic to add."""
    prereqs = {
        "Machine Learning": "Python for ML — Review NumPy and Data Handling",
        "Data Structures": "Introduction to Complexity Analysis — Re-derive Big-O",
        "Calculus": "Functions and Their Graphs — Rebuild intuition",
        "Operating Systems": "Process Management — Review PCB and scheduling basics",
        "Quantum Physics": "Classical vs Quantum World — Strengthen intuition about dual nature",
        "Web Development": "JavaScript Basics — Solidify DOM and event handling",
        "Linear Algebra": "Vectors and Spaces — Review span and linear independence",
    }
    return prereqs.get(subject, "Fundamentals Prerequisite Module")

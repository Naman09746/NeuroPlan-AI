import random

LEARNING_STYLES = ["Visual", "Auditory", "Reading/Writing", "Kinesthetic"]
FOCUS_DURATIONS = ["15 min (Micro-learning)", "25 min (Pomodoro)", "50 min", "90 min deep work"]
KNOWLEDGE_LEVELS = ["Beginner", "Intermediate", "Advanced"]
SUBJECTS = [
    "Machine Learning", "Calculus", "World History", "Organic Chemistry", 
    "Economics", "Psychology", "Linear Algebra", "Data Structures",
    "Microbiology", "Macroeconomics", "Quantum Physics", "Shakespearean Literature",
    "Discrete Mathematics", "Neuroscience", "Financial Accounting"
]

def generate_random_profile():
    style = random.choice(LEARNING_STYLES)
    focus = random.choice(FOCUS_DURATIONS)
    level = random.choice(KNOWLEDGE_LEVELS)
    
    # Simulated metrics for adaptive intelligence
    velocity = random.choice(["slow", "medium", "fast"])
    forgetting_rate = random.uniform(0.1, 0.5) # Decay factor
    
    past_performance = ""
    test_history = []
    
    if level == "Beginner":
        past_performance = random.choice([
            "Strong theoretical interest but struggles with practical application.",
            "Weak in prerequisite math, needs clear foundational blocks.",
            "Highly motivated, prefers step-by-step guidance."
        ])
        test_history = [random.randint(40, 75) for _ in range(random.randint(2, 5))]
    elif level == "Intermediate":
        past_performance = random.choice([
            "Good grasp of basics, needs help with complex problem-solving.",
            "Inconsistent performance in recent assessments.",
            "Strong in visual concepts, struggles with abstract formulas."
        ])
        test_history = [random.randint(60, 90) for _ in range(random.randint(3, 7))]
    else:
        past_performance = random.choice([
            "Strong foundation, looking for advanced research applications.",
            "Expert in related fields, needs fast-paced technical deep-dives.",
            "Interested in optimization and architectural nuances."
        ])
        test_history = [random.randint(80, 100) for _ in range(random.randint(5, 10))]

    return {
        "learning_style": style,
        "focus_duration": focus,
        "level": level,
        "learning_velocity": velocity,
        "forgetting_rate": round(forgetting_rate, 2),
        "test_history": test_history,
        "context": past_performance,
        "summary": (
            f"Style: {style}, Focus: {focus}, Level: {level}, "
            f"Velocity: {velocity}, Forgetting Rate: {round(forgetting_rate, 2)}, "
            f"Recent Scores: {test_history}, Background: {past_performance}"
        )
    }

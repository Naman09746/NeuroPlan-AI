"""
Synthetic Interaction Data Generator for DKT Training
=====================================================
Generates realistic student interaction sequences for training
the Deep Knowledge Tracing (DKT) LSTM model.

This simulates how students interact with topics over time:
- Fast learners get more correct answers
- Prerequisite knowledge affects correctness probability
- Forgetting curve makes older topics decay

Usage:
    python3 -m ml.knowledge_tracing.generate_interactions --students 500 --output ml/data/interactions.json
"""

import json
import random
import math
import argparse
from typing import Dict, List


def generate_synthetic_interactions(
    num_students: int = 500,
    num_topics: int = 100,
    min_interactions: int = 15,
    max_interactions: int = 80,
) -> Dict[str, List[Dict]]:
    """
    Generate realistic student interaction sequences.
    
    Each student has a simulated:
    - Ability level (affects base correctness probability)
    - Learning rate (how fast mastery improves with practice)
    - Forgetting rate (how fast mastery decays without practice)
    """
    all_data = {}
    
    for student_idx in range(num_students):
        student_id = f"student_{student_idx}"
        
        # Student attributes
        ability = random.gauss(0.5, 0.15)  # Normal distribution centered at 0.5
        ability = max(0.1, min(0.9, ability))
        learning_rate = random.uniform(0.05, 0.2)
        forgetting_rate = random.uniform(0.01, 0.08)
        
        # Track per-topic mastery
        mastery = {t: random.uniform(0.0, 0.3) for t in range(num_topics)}
        last_practice = {t: -100 for t in range(num_topics)}  # Timestep of last practice
        
        # Choose topics this student interacts with (not all 100)
        active_topics = random.sample(range(num_topics), random.randint(5, 25))
        
        num_interactions = random.randint(min_interactions, max_interactions)
        interactions = []
        
        for timestep in range(num_interactions):
            # Pick a topic (weighted toward ones with lower mastery — adaptive system)
            topic_weights = []
            for t in active_topics:
                # Lower mastery = higher chance of being scheduled
                weight = max(0.1, 1.0 - mastery[t])
                topic_weights.append(weight)
            
            topic_id = random.choices(active_topics, weights=topic_weights, k=1)[0]
            
            # Apply forgetting curve since last practice
            time_since = timestep - last_practice[topic_id]
            decay = math.exp(-forgetting_rate * time_since)
            effective_mastery = mastery[topic_id] * decay
            
            # Probability of correct answer
            p_correct = 0.2 + 0.6 * effective_mastery + 0.2 * ability
            p_correct = max(0.05, min(0.95, p_correct))  # Clamp
            
            correct = 1 if random.random() < p_correct else 0
            
            interactions.append({
                "topic_id": topic_id,
                "correct": correct,
            })
            
            # Update mastery based on outcome
            if correct:
                mastery[topic_id] = min(1.0, mastery[topic_id] + learning_rate * (1 - mastery[topic_id]))
            else:
                mastery[topic_id] = max(0.0, mastery[topic_id] - learning_rate * 0.3)
            
            last_practice[topic_id] = timestep
        
        all_data[student_id] = interactions
    
    return all_data


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic interaction data for DKT training")
    parser.add_argument("--students", type=int, default=500, help="Number of students to simulate")
    parser.add_argument("--topics", type=int, default=100, help="Number of topics")
    parser.add_argument("--output", type=str, default="ml/data/interactions.json", help="Output file path")
    args = parser.parse_args()
    
    print(f"🧠 Generating {args.students} synthetic student interaction histories...")
    print(f"   Topics: {args.topics}")
    
    data = generate_synthetic_interactions(
        num_students=args.students,
        num_topics=args.topics,
    )
    
    import os
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    with open(args.output, "w") as f:
        json.dump(data, f, indent=2)
    
    # Stats
    total_interactions = sum(len(v) for v in data.values())
    avg_interactions = total_interactions / len(data)
    
    print(f"\n✅ Generated {len(data)} students with {total_interactions} total interactions")
    print(f"   Average interactions per student: {avg_interactions:.1f}")
    print(f"   Saved to: {args.output}")
    print(f"   File size: {os.path.getsize(args.output) / 1024:.1f} KB")


if __name__ == "__main__":
    main()

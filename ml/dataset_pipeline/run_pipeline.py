"""
NeuroPlan AI — Synthetic Training Data Pipeline
================================================
Generates training data for fine-tuning using ZERO API calls.
All data comes from curated domain knowledge + algorithmic rules.

This is NOT an API wrapper. This is a proper ML data pipeline.

Usage:
    python3 -m ml.dataset_pipeline.run_pipeline --count 1500 --output ml/data/training_data.jsonl
"""

import os
import json
import random
import argparse

from ml.dataset_pipeline.profiles import generate_random_profile
from ml.dataset_pipeline.formatter import format_as_chatml, TaskType

# Template-based generators — NO API dependency
from ml.dataset_pipeline.generators.template_curriculum_generator import (
    generate_curriculum, AVAILABLE_SUBJECTS
)
from ml.dataset_pipeline.generators.template_study_card_generator import (
    generate_study_card
)
from ml.dataset_pipeline.generators.template_assessment_generator import (
    generate_assessment
)
from ml.dataset_pipeline.generators.template_recommendation_generator import (
    generate_recommendation
)


def run_pipeline(count: int, output_file: str):
    """
    Generate `count` training samples using template-based generation.
    No network calls. No API keys. Pure algorithmic data.
    """
    print(f"🧠 NeuroPlan AI — Synthetic Data Pipeline (Template Mode)")
    print(f"📊 Generating {count} training examples...")
    print(f"📁 Output: {output_file}")
    print(f"🔑 API Keys Required: NONE\n")
    
    # Distribution: 30% curriculum, 30% study cards, 20% assessments, 20% recommendations
    num_curriculums = int(count * 0.30)
    num_cards = int(count * 0.30)
    num_assessments = int(count * 0.20)
    num_recommendations = count - num_curriculums - num_cards - num_assessments
    
    all_samples = []
    stats = {"curriculum": 0, "study_card": 0, "assessment": 0, "recommendation": 0, "failed": 0}
    
    # ================================================================
    # 1. CURRICULUM GENERATION
    # ================================================================
    print(f"\n[1/4] Generating {num_curriculums} curriculum samples...")
    for i in range(num_curriculums):
        profile = generate_random_profile()
        subject = random.choice(AVAILABLE_SUBJECTS)
        
        result = generate_curriculum(profile, subject)
        if result:
            chatml = format_as_chatml(
                TaskType.CURRICULUM,
                {"profile": profile["summary"], "subject": subject},
                result
            )
            all_samples.append(chatml)
            stats["curriculum"] += 1
        else:
            stats["failed"] += 1
        
        if (i + 1) % 100 == 0:
            print(f"   ✓ {i + 1}/{num_curriculums} curriculum samples generated")
    
    print(f"   ✅ {stats['curriculum']} curriculum samples generated")
    
    # ================================================================
    # 2. STUDY CARD GENERATION
    # ================================================================
    print(f"\n[2/4] Generating {num_cards} study card samples...")
    for i in range(num_cards):
        profile = generate_random_profile()
        subject = random.choice(AVAILABLE_SUBJECTS)
        
        # Get a real topic name from the curriculum
        curriculum = generate_curriculum(profile, subject)
        if curriculum and curriculum["topics"]:
            topic = random.choice(curriculum["topics"])
            topic_name = topic["name"]
            profile["key_concepts"] = topic.get("key_concepts", [])
        else:
            topic_name = f"Introduction to {subject}"
            profile["key_concepts"] = ["core concepts", "fundamentals"]
        
        result = generate_study_card(topic_name, subject, profile)
        if result:
            chatml = format_as_chatml(
                TaskType.STUDY_CARD,
                {"profile": profile["summary"], "subject": subject, "topic": topic_name},
                result
            )
            all_samples.append(chatml)
            stats["study_card"] += 1
        else:
            stats["failed"] += 1
        
        if (i + 1) % 100 == 0:
            print(f"   ✓ {i + 1}/{num_cards} study card samples generated")
    
    print(f"   ✅ {stats['study_card']} study card samples generated")
    
    # ================================================================
    # 3. ASSESSMENT GENERATION
    # ================================================================
    print(f"\n[3/4] Generating {num_assessments} assessment samples...")
    for i in range(num_assessments):
        subject = random.choice(AVAILABLE_SUBJECTS)
        difficulty = random.choice(["easy", "medium", "hard"])
        
        # Get a real topic name
        profile = generate_random_profile()
        curriculum = generate_curriculum(profile, subject)
        if curriculum and curriculum["topics"]:
            topic = random.choice(curriculum["topics"])
            topic_name = topic["name"]
        else:
            topic_name = f"Introduction to {subject}"
        
        result = generate_assessment(topic_name, subject, difficulty)
        if result:
            chatml = format_as_chatml(
                TaskType.ASSESSMENT,
                {"topic": topic_name, "difficulty": difficulty},
                result
            )
            all_samples.append(chatml)
            stats["assessment"] += 1
        else:
            stats["failed"] += 1
        
        if (i + 1) % 100 == 0:
            print(f"   ✓ {i + 1}/{num_assessments} assessment samples generated")
    
    print(f"   ✅ {stats['assessment']} assessment samples generated")
    
    # ================================================================
    # 4. ADAPTIVE RECOMMENDATION GENERATION
    # ================================================================
    print(f"\n[4/4] Generating {num_recommendations} adaptive recommendation samples...")
    for i in range(num_recommendations):
        profile = generate_random_profile()
        subject = random.choice(AVAILABLE_SUBJECTS)
        
        result = generate_recommendation(profile, subject)
        if result:
            avg_score = sum(profile.get("test_history", [])) / len(profile.get("test_history", [])) if profile.get("test_history") else 50
            plan_status = f"Average Score: {avg_score:.0f}%, Velocity: {profile.get('learning_velocity')}"
            struggles = "Failing scores" if avg_score < 60 else ("Declining trend" if avg_score < 75 else "None")
            
            chatml = format_as_chatml(
                TaskType.ADAPTIVE_RECOMMENDATION,
                {"profile": profile["summary"], "plan_status": plan_status, "struggles": struggles},
                result
            )
            all_samples.append(chatml)
            stats["recommendation"] += 1
        else:
            stats["failed"] += 1
        
        if (i + 1) % 100 == 0:
            print(f"   ✓ {i + 1}/{num_recommendations} recommendation samples generated")
    
    print(f"   ✅ {stats['recommendation']} recommendation samples generated")
    
    # ================================================================
    # SHUFFLE & WRITE
    # ================================================================
    random.shuffle(all_samples)
    
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_file, "w") as f:
        for sample in all_samples:
            f.write(json.dumps(sample) + "\n")
    
    # ================================================================
    # SUMMARY
    # ================================================================
    total = sum(v for k, v in stats.items() if k != "failed")
    print(f"\n{'='*60}")
    print(f"🎯 PIPELINE COMPLETE")
    print(f"{'='*60}")
    print(f"   Total samples:      {total}")
    print(f"   ├─ Curriculum:       {stats['curriculum']}")
    print(f"   ├─ Study Cards:      {stats['study_card']}")
    print(f"   ├─ Assessments:      {stats['assessment']}")
    print(f"   ├─ Recommendations:  {stats['recommendation']}")
    print(f"   └─ Failed:           {stats['failed']}")
    print(f"\n   📁 Saved to: {output_file}")
    print(f"   📏 File size: {os.path.getsize(output_file) / 1024:.1f} KB")
    print(f"   🔑 API calls made: 0")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NeuroPlan AI — Synthetic Training Data Pipeline")
    parser.add_argument("--count", type=int, default=1500, help="Number of training samples to generate")
    parser.add_argument("--output", type=str, default="ml/data/training_data.jsonl", help="Output file path")
    args = parser.parse_args()
    
    run_pipeline(args.count, args.output)

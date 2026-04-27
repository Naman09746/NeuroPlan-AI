"""
NeuroPlan AI — Model Evaluation Framework
==========================================
Evaluates the fine-tuned model on held-out test data.
Measures JSON validity, schema conformance, and output quality.

Usage:
    python3 -m ml.eval.evaluate_model --model neuroplan --data ml/data/training_data.jsonl --samples 50
"""

import json
import argparse
import random
import os
from typing import Dict, Any, List


def load_test_samples(data_path: str, num_samples: int) -> List[Dict]:
    """Load random samples from training data for evaluation."""
    with open(data_path, "r") as f:
        all_samples = [json.loads(line) for line in f if line.strip()]
    
    random.shuffle(all_samples)
    return all_samples[:num_samples]


def evaluate_json_validity(response: str) -> bool:
    """Check if the response is valid JSON."""
    try:
        json.loads(response)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def evaluate_schema_conformance(response: str, task_type: str) -> Dict[str, bool]:
    """Check if the JSON response conforms to the expected schema."""
    try:
        data = json.loads(response)
    except (json.JSONDecodeError, TypeError):
        return {"valid_json": False, "has_required_fields": False, "correct_types": False}
    
    results = {"valid_json": True, "has_required_fields": False, "correct_types": False}
    
    if task_type == "curriculum":
        required = ["user_profile", "subject", "topics"]
        results["has_required_fields"] = all(k in data for k in required)
        if results["has_required_fields"]:
            results["correct_types"] = (
                isinstance(data.get("topics"), list) and
                len(data.get("topics", [])) > 0 and
                all("name" in t and "difficulty" in t for t in data.get("topics", []))
            )
    
    elif task_type == "study_card":
        required = ["summary", "key_concepts", "study_tips"]
        results["has_required_fields"] = all(k in data for k in required)
        if results["has_required_fields"]:
            results["correct_types"] = (
                isinstance(data.get("key_concepts"), list) and
                isinstance(data.get("study_tips"), list) and
                len(data.get("summary", "")) > 10
            )
    
    elif task_type == "assessment":
        required = ["topic_id", "questions"]
        results["has_required_fields"] = all(k in data for k in required)
        if results["has_required_fields"]:
            results["correct_types"] = (
                isinstance(data.get("questions"), list) and
                len(data.get("questions", [])) > 0 and
                all("question" in q and "options" in q for q in data.get("questions", []))
            )
    
    elif task_type == "recommendation":
        required = ["summary", "actions"]
        results["has_required_fields"] = all(k in data for k in required)
        if results["has_required_fields"]:
            results["correct_types"] = (
                isinstance(data.get("actions"), list) and
                len(data.get("actions", [])) > 0 and
                all("action_type" in a and "topic_name" in a for a in data.get("actions", []))
            )
    
    return results


def detect_task_type(sample: Dict) -> str:
    """Detect the task type from the system message."""
    system_msg = sample.get("messages", [{}])[0].get("content", "")
    if "Curriculum" in system_msg:
        return "curriculum"
    elif "Study Card" in system_msg:
        return "study_card"
    elif "Assessment" in system_msg:
        return "assessment"
    elif "Adaptive" in system_msg:
        return "recommendation"
    return "unknown"


def evaluate_training_data(data_path: str, num_samples: int = 50):
    """
    Evaluate the TRAINING DATA quality itself.
    This is what you run BEFORE uploading to Kaggle.
    """
    print(f"🔬 NeuroPlan AI — Training Data Quality Evaluation")
    print(f"{'='*60}")
    
    samples = load_test_samples(data_path, num_samples)
    
    metrics = {
        "total": len(samples),
        "json_valid": 0,
        "schema_conformant": 0,
        "has_required_fields": 0,
        "correct_types": 0,
        "by_type": {},
    }
    
    for sample in samples:
        task_type = detect_task_type(sample)
        if task_type not in metrics["by_type"]:
            metrics["by_type"][task_type] = {"total": 0, "valid": 0, "conformant": 0}
        
        metrics["by_type"][task_type]["total"] += 1
        
        # Get the assistant's response (this is the "label" the model learns)
        messages = sample.get("messages", [])
        if len(messages) >= 3:
            response = messages[2].get("content", "")
        else:
            continue
        
        # Check JSON validity
        if evaluate_json_validity(response):
            metrics["json_valid"] += 1
            metrics["by_type"][task_type]["valid"] += 1
            
            # Check schema conformance
            schema_results = evaluate_schema_conformance(response, task_type)
            if schema_results.get("has_required_fields"):
                metrics["has_required_fields"] += 1
            if schema_results.get("correct_types"):
                metrics["schema_conformant"] += 1
                metrics["by_type"][task_type]["conformant"] += 1
    
    # Report
    print(f"\n📊 Results ({metrics['total']} samples evaluated):")
    print(f"   ├─ JSON Validity:        {metrics['json_valid']}/{metrics['total']} ({metrics['json_valid']/max(1,metrics['total'])*100:.1f}%)")
    print(f"   ├─ Required Fields:      {metrics['has_required_fields']}/{metrics['total']} ({metrics['has_required_fields']/max(1,metrics['total'])*100:.1f}%)")
    print(f"   └─ Schema Conformance:   {metrics['schema_conformant']}/{metrics['total']} ({metrics['schema_conformant']/max(1,metrics['total'])*100:.1f}%)")
    
    print(f"\n📋 By Task Type:")
    for task_type, type_metrics in metrics["by_type"].items():
        total = type_metrics["total"]
        valid = type_metrics["valid"]
        conformant = type_metrics["conformant"]
        print(f"   {task_type:20s} | {total:3d} samples | {valid/max(1,total)*100:.0f}% valid JSON | {conformant/max(1,total)*100:.0f}% schema conformant")
    
    # Pass/Fail threshold
    validity_rate = metrics['json_valid'] / max(1, metrics['total']) * 100
    conformance_rate = metrics['schema_conformant'] / max(1, metrics['total']) * 100
    
    print(f"\n{'='*60}")
    if validity_rate >= 95 and conformance_rate >= 85:
        print(f"✅ PASS — Data quality is sufficient for training")
    elif validity_rate >= 85:
        print(f"⚠️  MARGINAL — Consider regenerating low-quality samples")
    else:
        print(f"❌ FAIL — Data quality too low. Fix generators before training")
    print(f"{'='*60}")
    
    return metrics


def evaluate_model_inference(model_name: str = "neuroplan", base_url: str = "http://localhost:11434"):
    """
    Evaluate a trained model served via Ollama.
    Sends test prompts and evaluates response quality.
    """
    try:
        import httpx
    except ImportError:
        print("❌ httpx not installed. Run: pip3 install httpx")
        return
    
    import asyncio
    
    test_prompts = [
        {
            "system": "You are NeuroPlan AI Curriculum Engine. Break down subjects into personalized topics based on student profiles. Please respond with valid JSON.",
            "user": "Profile: Style: Visual, Focus: 50 min, Level: Beginner, Velocity: medium\nSubject: Machine Learning",
            "expected_type": "curriculum",
        },
        {
            "system": "You are NeuroPlan AI Study Card Engine. Generate personalized learning content grounded in cognitive science. Please respond with valid JSON.",
            "user": "Topic: Linear Regression\nSubject: Machine Learning\nProfile: Style: Kinesthetic, Focus: 25 min, Level: Beginner",
            "expected_type": "study_card",
        },
        {
            "system": "You are NeuroPlan AI Adaptive Engine. Analyze student performance and provide personalized plan adjustments. Please respond with valid JSON.",
            "user": "Profile: Style: Auditory, Focus: 50 min, Level: Intermediate, Velocity: slow, Recent Scores: [55, 48, 62]\nPlan Status: Average Score: 55%, Declining trend\nStruggles: Failing assessments on advanced topics",
            "expected_type": "recommendation",
        },
    ]
    
    async def run_tests():
        print(f"\n🤖 Testing model: {model_name} at {base_url}")
        print(f"{'='*60}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            for i, test in enumerate(test_prompts):
                print(f"\n--- Test {i+1}: {test['expected_type']} ---")
                
                try:
                    response = await client.post(
                        f"{base_url}/api/chat",
                        json={
                            "model": model_name,
                            "messages": [
                                {"role": "system", "content": test["system"]},
                                {"role": "user", "content": test["user"]},
                            ],
                            "format": "json",
                            "stream": False,
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        content = result.get("message", {}).get("content", "")
                        
                        # Evaluate
                        is_valid = evaluate_json_validity(content)
                        schema = evaluate_schema_conformance(content, test["expected_type"])
                        
                        print(f"   JSON Valid:     {'✅' if is_valid else '❌'}")
                        print(f"   Schema Match:   {'✅' if schema.get('correct_types') else '❌'}")
                        print(f"   Response (first 200 chars): {content[:200]}...")
                    else:
                        print(f"   ❌ HTTP {response.status_code}: {response.text[:200]}")
                
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    print(f"   (Is Ollama running? Start with: ollama serve)")
    
    asyncio.run(run_tests())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NeuroPlan AI — Model Evaluation")
    parser.add_argument("--data", type=str, default="ml/data/training_data.jsonl", help="Training data path")
    parser.add_argument("--samples", type=int, default=100, help="Number of samples to evaluate")
    parser.add_argument("--mode", type=str, choices=["data", "model"], default="data", help="Evaluate data or live model")
    parser.add_argument("--model", type=str, default="neuroplan", help="Model name in Ollama")
    args = parser.parse_args()
    
    if args.mode == "data":
        evaluate_training_data(args.data, args.samples)
    else:
        evaluate_model_inference(args.model)

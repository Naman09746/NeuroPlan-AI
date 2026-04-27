"""
NeuroPlan AI — Kaggle Fine-Tuning Script
=========================================
Fine-tunes Llama-3.1-8B-Instruct on NeuroPlan's synthetic dataset
using QLoRA (4-bit) via Unsloth for free Kaggle T4 GPUs.

STEP-BY-STEP INSTRUCTIONS FOR KAGGLE:
1. Create a new Kaggle notebook
2. Go to Settings → Accelerator → GPU T4 x2
3. Upload ml/data/training_data.jsonl as a Kaggle Dataset named "neuroplan-training-data"
4. Copy this entire file into a notebook cell
5. Run the cell (~45 minutes)
6. Download the output GGUF file from Kaggle Output

The resulting model replaces ALL API calls in NeuroPlan AI.
No OpenAI. No Groq. Your own model.
"""

# ============================================================================
# CELL 1: INSTALL DEPENDENCIES
# ============================================================================
# !pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
# !pip install --no-deps trl peft accelerate bitsandbytes

# ============================================================================
# CELL 2: IMPORTS & CONFIG
# ============================================================================
import json
import os
from datasets import Dataset

# Training configuration — optimized for Kaggle T4 x2
CONFIG = {
    "base_model": "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit",
    "max_seq_length": 4096,
    "lora_r": 32,
    "lora_alpha": 32,
    "lora_dropout": 0.05,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    "learning_rate": 2e-4,
    "epochs": 3,
    "batch_size": 4,
    "gradient_accumulation_steps": 2,  # Effective batch = 8
    "warmup_ratio": 0.05,
    "weight_decay": 0.01,
    "output_dir": "/kaggle/working/neuroplan-model",
    "dataset_path": "/kaggle/input/neuroplan-training-data/training_data.jsonl",
}


# ============================================================================
# CELL 3: LOAD MODEL WITH UNSLOTH (4-BIT QUANTIZED)
# ============================================================================
def load_model():
    from unsloth import FastLanguageModel
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=CONFIG["base_model"],
        max_seq_length=CONFIG["max_seq_length"],
        dtype=None,  # Auto-detect
        load_in_4bit=True,
    )
    
    # Apply LoRA adapters
    model = FastLanguageModel.get_peft_model(
        model,
        r=CONFIG["lora_r"],
        lora_alpha=CONFIG["lora_alpha"],
        lora_dropout=CONFIG["lora_dropout"],
        target_modules=CONFIG["target_modules"],
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )
    
    print(f"✅ Model loaded: {CONFIG['base_model']}")
    print(f"   Trainable parameters: {model.print_trainable_parameters()}")
    
    return model, tokenizer


# ============================================================================
# CELL 4: LOAD & FORMAT DATASET
# ============================================================================
def load_dataset(tokenizer):
    """Load JSONL and convert to Llama-3.1 chat template format."""
    
    samples = []
    with open(CONFIG["dataset_path"], "r") as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))
    
    print(f"📊 Loaded {len(samples)} training samples")
    
    # Convert messages to Llama 3.1 chat format
    formatted = []
    for sample in samples:
        messages = sample.get("messages", [])
        if len(messages) >= 3:
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False
            )
            formatted.append({"text": text})
    
    print(f"   Formatted: {len(formatted)} samples")
    
    # Split into train/eval
    dataset = Dataset.from_list(formatted)
    split = dataset.train_test_split(test_size=0.1, seed=42)
    
    print(f"   Train: {len(split['train'])}, Eval: {len(split['test'])}")
    
    return split


# ============================================================================
# CELL 5: TRAIN
# ============================================================================
def train(model, tokenizer, dataset):
    from trl import SFTTrainer
    from transformers import TrainingArguments
    from unsloth import is_bfloat16_supported
    
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        dataset_text_field="text",
        max_seq_length=CONFIG["max_seq_length"],
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            output_dir=CONFIG["output_dir"],
            per_device_train_batch_size=CONFIG["batch_size"],
            gradient_accumulation_steps=CONFIG["gradient_accumulation_steps"],
            warmup_ratio=CONFIG["warmup_ratio"],
            num_train_epochs=CONFIG["epochs"],
            learning_rate=CONFIG["learning_rate"],
            fp16=not is_bfloat16_supported(),
            bf16=is_bfloat16_supported(),
            logging_steps=10,
            eval_strategy="steps",
            eval_steps=50,
            save_strategy="steps",
            save_steps=100,
            weight_decay=CONFIG["weight_decay"],
            lr_scheduler_type="cosine",
            seed=42,
            report_to="none",  # No wandb on Kaggle
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
        ),
    )
    
    print("🚀 Starting training...")
    print(f"   Epochs: {CONFIG['epochs']}")
    print(f"   Effective batch size: {CONFIG['batch_size'] * CONFIG['gradient_accumulation_steps']}")
    print(f"   Learning rate: {CONFIG['learning_rate']}")
    
    trainer_stats = trainer.train()
    
    print(f"\n✅ Training complete!")
    print(f"   Total steps: {trainer_stats.global_step}")
    print(f"   Final train loss: {trainer_stats.training_loss:.4f}")
    
    return trainer


# ============================================================================
# CELL 6: EVALUATE ON HELD-OUT SET
# ============================================================================
def evaluate(model, tokenizer, dataset):
    """Run inference on eval samples and check JSON quality."""
    from unsloth import FastLanguageModel
    FastLanguageModel.for_inference(model)
    
    eval_samples = dataset["test"].select(range(min(20, len(dataset["test"]))))
    
    json_valid = 0
    total = 0
    
    print("\n🔬 Evaluating on held-out samples...")
    
    for sample in eval_samples:
        text = sample["text"]
        
        # Extract just the prompt (everything before assistant's response)
        # Split at the last assistant header
        if "<|start_header_id|>assistant<|end_header_id|>" in text:
            prompt = text.split("<|start_header_id|>assistant<|end_header_id|>")[0] + "<|start_header_id|>assistant<|end_header_id|>\n\n"
        else:
            continue
        
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        outputs = model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.3,
            do_sample=True,
        )
        
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        total += 1
        try:
            json.loads(response.strip())
            json_valid += 1
        except json.JSONDecodeError:
            pass
    
    print(f"   JSON validity: {json_valid}/{total} ({json_valid/max(1,total)*100:.1f}%)")
    return json_valid / max(1, total)


# ============================================================================
# CELL 7: EXPORT TO GGUF FOR OLLAMA
# ============================================================================
def export_gguf(model, tokenizer):
    """Export to GGUF Q4_K_M format for Ollama serving."""
    
    output_path = "/kaggle/working/neuroplan-llama-3.1-8b-gguf"
    
    print(f"\n📦 Exporting to GGUF (Q4_K_M)...")
    print(f"   Output: {output_path}")
    
    model.save_pretrained_gguf(
        output_path,
        tokenizer,
        quantization_method="q4_k_m",
    )
    
    # List output files
    for f in os.listdir(output_path):
        size = os.path.getsize(os.path.join(output_path, f))
        print(f"   {f}: {size / (1024*1024):.1f} MB")
    
    print(f"\n✅ GGUF export complete!")
    print(f"   Download from Kaggle Output and place in: ml/models/")
    print(f"   Then run: ollama create neuroplan -f ml/serving/Modelfile")


# ============================================================================
# MAIN EXECUTION — Copy this entire file into a Kaggle notebook cell
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🧠 NeuroPlan AI — Fine-Tuning Pipeline")
    print("=" * 60)
    print(f"Base Model: {CONFIG['base_model']}")
    print(f"Dataset: {CONFIG['dataset_path']}")
    print(f"Output: {CONFIG['output_dir']}")
    print("=" * 60)
    
    # Step 1: Load model
    model, tokenizer = load_model()
    
    # Step 2: Load dataset
    dataset = load_dataset(tokenizer)
    
    # Step 3: Train
    trainer = train(model, tokenizer, dataset)
    
    # Step 4: Evaluate
    json_rate = evaluate(model, tokenizer, dataset)
    
    # Step 5: Export
    export_gguf(model, tokenizer)
    
    print("\n" + "=" * 60)
    print("🎯 PIPELINE COMPLETE")
    print("=" * 60)
    print("NEXT STEPS:")
    print("1. Download the GGUF file from Kaggle Output")
    print("2. Place it in: ml/models/neuroplan-llama-3.1-8b-gguf/")
    print("3. Run: ollama create neuroplan -f ml/serving/Modelfile")
    print("4. Test: python3 -m ml.serving.health_check")
    print("5. Set USE_CUSTOM_AI=true in backend/.env")
    print("=" * 60)

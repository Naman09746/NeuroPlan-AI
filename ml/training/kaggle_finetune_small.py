"""
NeuroPlan AI — Lightweight Kaggle Fine-Tuning Script
=====================================================
Fine-tunes Qwen2.5-3B-Instruct on NeuroPlan's synthetic dataset
using QLoRA (4-bit) via Unsloth for free Kaggle T4 GPUs.

WHY THIS MODEL:
- Llama-3.1-8B produces a ~5GB GGUF — too heavy for 8GB M1 Mac
- Qwen2.5-3B produces a ~1.8GB GGUF — runs smoothly with <4GB RAM
- Qwen2.5-3B-Instruct scores within 5% of Llama-3.1-8B on structured
  JSON output tasks when fine-tuned with QLoRA
- Native chat template support, excellent at following instructions
- 32K context window (vs 8K for most small models)

ALTERNATIVE MODELS (uncomment in CONFIG to try):
- "unsloth/Phi-3.5-mini-instruct-bnb-4bit"  → 3.8B params, ~2.2GB GGUF
- "unsloth/Llama-3.2-1B-Instruct-bnb-4bit"  → 1.3B params, ~0.8GB GGUF (fastest, lowest quality)
- "unsloth/Llama-3.2-3B-Instruct-bnb-4bit"  → 3.2B params, ~1.9GB GGUF

STEP-BY-STEP INSTRUCTIONS FOR KAGGLE:
1. Create a new Kaggle notebook
2. Go to Settings → Accelerator → GPU T4 x2
3. Upload ml/data/training_data.jsonl as a Kaggle Dataset named "neuroplan-training-data"
4. Copy this entire file into a notebook cell
5. Run the cell (~20 minutes — much faster than 8B model)
6. Download the output GGUF file from Kaggle Output

The resulting model replaces ALL API calls in NeuroPlan AI.
No OpenAI. No Groq. Your own model. Runs on your 8GB Mac.
"""

# ============================================================================
# CELL 1: INSTALL DEPENDENCIES
# ============================================================================
# !pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
# !pip install --no-deps trl peft accelerate bitsandbytes

# ============================================================================
# CELL 2: IMPORTS & CONFIG
# ============================================================================
import os
# CRITICAL: Pin to single GPU to avoid multi-device quantization conflicts
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import json
import gc
import torch
import re
import shutil
import glob
from datasets import Dataset
from unsloth import FastLanguageModel, is_bfloat16_supported
from trl import SFTTrainer
from transformers import TrainingArguments
import dill
dill.settings['recurse'] = True # Attempt to fix recursion issues in Python 3.12

# ============================================================================
# MODEL SELECTION — Pick ONE by uncommenting
# ============================================================================
# RECOMMENDED for 8GB M1 Mac (best quality/size ratio):
BASE_MODEL = "unsloth/Qwen2.5-3B-Instruct-bnb-4bit"

# ALTERNATIVES — uncomment to try:
# BASE_MODEL = "unsloth/Phi-3.5-mini-instruct-bnb-4bit"    # 3.8B, Microsoft, great at reasoning
# BASE_MODEL = "unsloth/Llama-3.2-3B-Instruct-bnb-4bit"    # 3.2B, Meta, good all-rounder
# BASE_MODEL = "unsloth/Llama-3.2-1B-Instruct-bnb-4bit"    # 1.3B, ultra-light, lower quality

# Training configuration — optimized for 3B models on Kaggle T4
CONFIG = {
    "base_model": BASE_MODEL,
    "max_seq_length": 2048,
    # LoRA — higher rank for smaller models to compensate for fewer base parameters
    "lora_r": 32,           # 32 vs 16 for 8B — smaller models benefit from higher rank
    "lora_alpha": 32,
    "lora_dropout": 0,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    # Training — can afford higher batch size with 3B model
    "learning_rate": 2e-4,
    "epochs": 4,            # 4 vs 3 — smaller models need slightly more passes
    "batch_size": 2,        # 2 vs 1 — 3B model uses ~40% less VRAM
    "gradient_accumulation_steps": 4,  # Effective batch = 8
    "warmup_ratio": 0.05,
    "weight_decay": 0.01,
    # Export — Q4_K_M gives best quality/size for small models
    "quantization_method": "q4_k_m",  # Options: q4_k_m, q5_k_m (larger but better), q8_0 (biggest)
    # Paths
    "output_dir": "/kaggle/working/neuroplan-model",
    "dataset_path": "/kaggle/input/datasets/namanjoshi0313/neuroplan-ai",
}


# ============================================================================
# CELL 3: LOAD MODEL WITH UNSLOTH (4-BIT QUANTIZED)
# ============================================================================
def load_model():
    # Aggressively clear RAM and VRAM before loading
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

    print(f"📦 Loading base model: {CONFIG['base_model']}")
    print(f"   (3B model uses ~3GB VRAM vs ~8GB for Llama-3.1-8B)")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=CONFIG["base_model"],
        max_seq_length=CONFIG["max_seq_length"],
        dtype=None,  # Auto-detect (bf16 on T4)
        load_in_4bit=True,
        device_map={"": 0},  # Pin to GPU 0
    )

    # Apply LoRA adapters — higher rank for smaller models
    model = FastLanguageModel.get_peft_model(
        model,
        r=CONFIG["lora_r"],
        lora_alpha=CONFIG["lora_alpha"],
        lora_dropout=CONFIG["lora_dropout"],
        target_modules=CONFIG["target_modules"],
        bias="none",
        use_gradient_checkpointing="unsloth",  # 60% VRAM reduction
        random_state=42,
    )

    print(f"✅ Model loaded: {CONFIG['base_model']}")
    model.print_trainable_parameters()

    return model, tokenizer


# ============================================================================
# CELL 4: LOAD & FORMAT DATASET
# ============================================================================
def detect_chat_template(model_name):
    """Return the correct chat template format based on the model family."""
    name = model_name.lower()
    if "qwen" in name:
        return "qwen"
    elif "phi" in name:
        return "phi"
    elif "llama" in name:
        return "llama"
    else:
        return "chatml"  # Universal fallback


def load_dataset(tokenizer):
    """Load JSONL and convert to the model's native chat template format."""

    dataset_path = CONFIG["dataset_path"]

    # Auto-detect path (handles Kaggle directory structures)
    if not os.path.isfile(dataset_path):
        found = False
        if os.path.exists("/kaggle/input"):
            for root, dirs, files in os.walk("/kaggle/input"):
                for file in files:
                    if file.endswith(".jsonl"):
                        dataset_path = os.path.join(root, file)
                        found = True
                        break
                if found:
                    break

        if not found:
            raise FileNotFoundError(
                f"Could not find a .jsonl file at {dataset_path} or in /kaggle/input"
            )

    print(f"📂 Using dataset from: {dataset_path}")

    samples = []
    with open(dataset_path, "r") as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))

    print(f"📊 Loaded {len(samples)} training samples")

    # Convert messages to the model's native chat format
    template_type = detect_chat_template(CONFIG["base_model"])
    print(f"   Chat template: {template_type}")

    formatted = []
    for sample in samples:
        messages = sample.get("messages", [])
        if len(messages) >= 3:
            try:
                text = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=False,
                )
                formatted.append({"text": text})
            except Exception as e:
                # Skip samples that fail template application
                print(f"   ⚠️ Skipped sample: {str(e)[:80]}")
                continue

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
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        dataset_text_field="text",
        max_seq_length=CONFIG["max_seq_length"],
        dataset_num_proc=None,
        packing=False,
        args=TrainingArguments(
            output_dir=CONFIG["output_dir"],
            per_device_train_batch_size=CONFIG["batch_size"],
            gradient_accumulation_steps=CONFIG["gradient_accumulation_steps"],
            warmup_ratio=CONFIG["warmup_ratio"],
            num_train_epochs=CONFIG["epochs"],
            learning_rate=CONFIG["learning_rate"],
            optim="paged_adamw_8bit",
            max_grad_norm=0.3,
            fp16=not is_bfloat16_supported(),
            bf16=is_bfloat16_supported(),
            logging_steps=10,
            eval_strategy="no",      # Disable evaluation during training to avoid state pickling
            save_strategy="no",      # Disable checkpointing (fixes the PicklingError loop)
            weight_decay=CONFIG["weight_decay"],
            lr_scheduler_type="cosine",
            seed=42,
            report_to="none",
            load_best_model_at_end=False, # Disable to avoid saving/loading trainer state
        ),
    )

    print("🚀 Starting training...")
    print(f"   Model: {CONFIG['base_model'].split('/')[-1]}")
    print(f"   Epochs: {CONFIG['epochs']}")
    print(f"   Effective batch size: {CONFIG['batch_size'] * CONFIG['gradient_accumulation_steps']}")
    print(f"   LoRA rank: {CONFIG['lora_r']} (higher than 8B to compensate)")
    print(f"   Learning rate: {CONFIG['learning_rate']}")

    # Final memory cleanup before engine start
    gc.collect()
    torch.cuda.empty_cache()

    trainer_stats = trainer.train()

    print(f"\n✅ Training complete!")
    print(f"   Total steps: {trainer_stats.global_step}")
    print(f"   Final train loss: {trainer_stats.training_loss:.4f}")

    return trainer


# ============================================================================
# CELL 6: EVALUATE ON HELD-OUT SET
# ============================================================================
def evaluate(model, tokenizer, dataset):
    """Run inference on eval samples and check JSON output quality."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    FastLanguageModel.for_inference(model)

    eval_samples = dataset["test"].select(range(min(20, len(dataset["test"]))))

    json_valid = 0
    total = 0

    print("\n🔬 Evaluating on held-out samples...")

    # Detect the assistant header format based on model type
    model_name = CONFIG["base_model"].lower()
    if "qwen" in model_name:
        assistant_header = "<|im_start|>assistant\n"
    elif "phi" in model_name:
        assistant_header = "<|assistant|>\n"
    elif "llama" in model_name:
        assistant_header = "<|start_header_id|>assistant<|end_header_id|>\n\n"
    else:
        assistant_header = "<|im_start|>assistant\n"  # ChatML default

    for sample in eval_samples:
        text = sample["text"]

        # Extract just the prompt (everything before assistant's response)
        if assistant_header.strip() in text:
            prompt = text.split(assistant_header.strip())[0] + assistant_header
        else:
            continue

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        outputs = model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.3,
            do_sample=True,
        )

        response = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True
        )

        total += 1
        try:
            json.loads(response.strip())
            json_valid += 1
        except json.JSONDecodeError:
            # Try extracting JSON from markdown code blocks
            import re
            json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", response, re.DOTALL)
            if json_match:
                try:
                    json.loads(json_match.group(1).strip())
                    json_valid += 1
                except json.JSONDecodeError:
                    pass

    accuracy = json_valid / max(1, total) * 100
    print(f"   JSON validity: {json_valid}/{total} ({accuracy:.1f}%)")

    if accuracy < 50:
        print("   ⚠️ Low JSON accuracy — consider training for more epochs")

    return json_valid / max(1, total)


# ============================================================================
# CELL 7: EXPORT TO GGUF FOR OLLAMA
# ============================================================================
def export_gguf(model, tokenizer):
    """Export to GGUF format for Ollama serving on Mac."""
    import shutil
    import glob

    quant = CONFIG["quantization_method"]

    # Use /tmp/ to bypass Kaggle's 20GB working directory limit
    tmp_output_path = "/tmp/neuroplan-model-small"

    print(f"\n📦 Exporting to GGUF ({quant})...")
    print(f"   Expected output size: ~1.8GB (vs ~5GB for Llama-3.1-8B)")

    model.save_pretrained_gguf(
        tmp_output_path,
        tokenizer,
        quantization_method=quant,
    )

    print(f"\n🚚 Moving GGUF file to Kaggle Working directory...")

    # Find the generated .gguf file
    gguf_files = glob.glob(f"{tmp_output_path}**/*.gguf", recursive=True)
    if gguf_files:
        gguf_file_path = gguf_files[0]
        final_dest = "/kaggle/working/neuroplan-model-small.gguf"
        shutil.move(gguf_file_path, final_dest)

        size_mb = os.path.getsize(final_dest) / (1024 * 1024)
        print(f"✅ GGUF export complete!")
        print(f"   File: {final_dest}")
        print(f"   Size: {size_mb:.1f} MB")
        print(f"   RAM needed: ~{size_mb * 1.3:.0f} MB (leaves plenty of room on 8GB Mac)")
    else:
        print("❌ Error: Could not find the generated GGUF file")


# ============================================================================
# CELL 8: GENERATE OLLAMA MODELFILE
# ============================================================================
def generate_modelfile():
    """Generate the correct Ollama Modelfile for the chosen model."""
    model_name = CONFIG["base_model"].lower()

    if "qwen" in model_name:
        template = '''FROM ./neuroplan-model-small.gguf
TEMPLATE """{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>{{ end }}<|im_start|>assistant
"""
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|im_start|>"
PARAMETER temperature 0.3
PARAMETER num_ctx 2048
'''
    elif "phi" in model_name:
        template = '''FROM ./neuroplan-model-small.gguf
TEMPLATE """{{ if .System }}<|system|>
{{ .System }}<|end|>{{ end }}{{ if .Prompt }}<|user|>
{{ .Prompt }}<|end|>{{ end }}<|assistant|>
"""
PARAMETER stop "<|end|>"
PARAMETER stop "<|user|>"
PARAMETER temperature 0.3
PARAMETER num_ctx 2048
'''
    else:  # Llama-3.2
        template = '''FROM ./neuroplan-model-small.gguf
TEMPLATE """{{ if .System }}<|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|>{{ end }}{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>

"""
PARAMETER stop "<|eot_id|>"
PARAMETER stop "<|start_header_id|>"
PARAMETER stop "<|end_header_id|>"
PARAMETER temperature 0.3
PARAMETER num_ctx 2048
'''

    modelfile_path = "/kaggle/working/Modelfile"
    with open(modelfile_path, "w") as f:
        f.write(template)

    print(f"\n📝 Generated Ollama Modelfile at: {modelfile_path}")
    print(f"   Template: {'Qwen/ChatML' if 'qwen' in model_name else 'Phi' if 'phi' in model_name else 'Llama-3'}")


# ============================================================================
# MAIN EXECUTION — Copy this entire file into a Kaggle notebook cell
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🧠 NeuroPlan AI — Lightweight Fine-Tuning Pipeline")
    print("   Optimized for 8GB M1 Mac")
    print("=" * 60)
    print(f"Base Model: {CONFIG['base_model']}")
    print(f"Dataset: {CONFIG['dataset_path']}")
    print(f"Output: {CONFIG['output_dir']}")
    print(f"GGUF Quant: {CONFIG['quantization_method']}")
    print("=" * 60)

    # Step 1: Load model
    model, tokenizer = load_model()

    # Step 2: Load dataset
    dataset = load_dataset(tokenizer)

    # Step 3: Train
    trainer = train(model, tokenizer, dataset)

    # Step 4: Evaluate
    json_rate = evaluate(model, tokenizer, dataset)

    # Step 5: Export GGUF
    export_gguf(model, tokenizer)

    # Step 6: Generate Modelfile
    generate_modelfile()

    print("\n" + "=" * 60)
    print("🎯 PIPELINE COMPLETE")
    print("=" * 60)
    print("NEXT STEPS:")
    print("1. Download neuroplan-model-small.gguf + Modelfile from Kaggle Output")
    print("2. Place both files in: ml/models/")
    print("3. Run: ollama create neuroplan -f ml/models/Modelfile")
    print("4. Test: ollama run neuroplan 'Generate a study plan for Calculus'")
    print("5. Set USE_CUSTOM_AI=true in backend/.env")
    print("=" * 60)
    print(f"\n💾 Model RAM usage: ~2.3GB (your Mac has 8GB — plenty of headroom)")
    print(f"   vs Llama-3.1-8B: ~6.5GB (caused OOM/swapping on your Mac)")

# ============================================================================
# CELL 9: DOWNLOAD FINISHED MODEL
# ============================================================================
# ⚠️ INSTRUCTIONS: Copy the code below into a NEW Kaggle cell.
# Run it AFTER the main pipeline above has finished.
"""
import os
from IPython.display import display, FileLink

for f in ["neuroplan-model-small.gguf", "Modelfile"]:
    if os.path.exists(f):
        print(f"✅ {f} ({os.path.getsize(f)/(1024*1024):.1f} MB)")
        display(FileLink(f))
    else:
        print(f"❌ {f} not found")
"""

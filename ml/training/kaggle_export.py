# NOTE: Run this in a separate Kaggle session or after training to merge and export to GGUF.
# GPU required for merging.

from unsloth import FastLanguageModel
import torch

# 1. Load the trained LoRA adapter
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "neuroplan-lora-adapter", # Path relative to /kaggle/working/
    max_seq_length = 4096,
    dtype = None,
    load_in_4bit = True,
)

# 2. Merge and Save to GGUF
# We use Q4_K_M for a good balance of size and performance
print("📦 Merging and exporting to GGUF Q4_K_M...")
model.save_pretrained_gguf(
    "neuroplan-llama-3.1-8b-gguf", 
    tokenizer, 
    quantization_method = "q4_k_m"
)

print("✅ Model exported to neuroplan-llama-3.1-8b-gguf directory.")
print("Now download the .gguf file from this directory and use it with Ollama.")

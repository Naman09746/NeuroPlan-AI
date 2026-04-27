# ml/training/config.py
# Optimized for Kaggle T4 x2 (16GB VRAM each)

BASE_MODEL = "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit"
LORA_R = 32          # Higher rank for multi-tasking (curriculum, cards, questions)
LORA_ALPHA = 32      
LORA_DROPOUT = 0.05  
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
MAX_SEQ_LENGTH = 4096  # Increased context for complex JSON outputs
LEARNING_RATE = 2e-4
EPOCHS = 3
BATCH_SIZE = 4        
GRAD_ACCUM = 2        # Effective batch size = 8
KAGGLE_DATASET = "/kaggle/input/neuroplan-training-data"  # Mount point for Kaggle Dataset
KAGGLE_OUTPUT = "/kaggle/working"
ADAPTER_NAME = "neuroplan-lora-adapter"
FINAL_MODEL_NAME = "neuroplan-llama-3.1-8b-gguf"

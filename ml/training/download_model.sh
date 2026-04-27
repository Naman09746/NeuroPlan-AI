#!/bin/bash
# ml/training/download_model.sh

USER_NAME=$1
KERNEL_SLUG="neuroplan-export"

if [ -z "$USER_NAME" ]; then
    echo "❌ Usage: ./ml/training/download_model.sh <your-kaggle-username>"
    exit 1
fi

echo "📥 Downloading GGUF model from Kaggle output..."
mkdir -p ml/models
kaggle kernels output $USER_NAME/$KERNEL_SLUG -p ml/models/

echo "✅ Download complete. Check ml/models/ for the .gguf file."

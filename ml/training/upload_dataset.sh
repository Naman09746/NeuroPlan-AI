#!/bin/bash
# ml/training/upload_dataset.sh

# Requirements: kaggle CLI installed and configured (~/.kaggle/kaggle.json)

if [ ! -f "ml/data/train.jsonl" ]; then
    echo "❌ Error: ml/data/train.jsonl not found. Run the dataset pipeline first."
    exit 1
fi

echo "📦 Preparing Kaggle Dataset..."
# Create metadata if not exists
if [ ! -f "ml/data/dataset-metadata.json" ]; then
    kaggle datasets init -p ml/data/
    # Modify the slug in the generated file
    sed -i '' 's/INSERT_TITLE_HERE/neuroplan-training-data/g' ml/data/dataset-metadata.json
    sed -i '' 's/INSERT_SLUG_HERE/neuroplan-training-data/g' ml/data/dataset-metadata.json
fi

echo "🚀 Uploading to Kaggle..."
kaggle datasets create -p ml/data/ || kaggle datasets version -p ml/data/ -m "Updated training data"

echo "✅ Dataset uploaded successfully."

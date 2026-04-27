import torch
import os
from ml.knowledge_tracing.model import DKTModel

class DKTPredictor:
    def __init__(self, checkpoint_path, num_topics):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.num_topics = num_topics
        self.model = DKTModel(num_topics).to(self.device)
        
        if os.path.exists(checkpoint_path):
            self.model.load_state_dict(torch.load(checkpoint_path, map_location=self.device))
            self.model.eval()
            print("✅ DKT Model loaded successfully.")
        else:
            print(f"⚠️ DKT Checkpoint not found at {checkpoint_path}. Using untrained model.")

    def predict_mastery(self, interaction_history: list) -> dict:
        """
        Input: list of topic IDs the student has interacted with in order.
        Output: dict of {topic_id: mastery_probability} for all topics.
        """
        if not interaction_history:
            return {i: 0.5 for i in range(self.num_topics)}
            
        # Pad and tensorize
        seq = torch.tensor(interaction_history, dtype=torch.long).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            # Get predictions for the last state
            preds = self.model(seq)
            last_pred = preds[0, -1, :].cpu().numpy()
            
        return {i: float(last_pred[i]) for i in range(self.num_topics)}

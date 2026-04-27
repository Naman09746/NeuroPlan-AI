import torch
from torch.utils.data import Dataset
import json

class InteractionDataset(Dataset):
    def __init__(self, data_path, num_topics, max_len=100):
        self.max_len = max_len
        self.num_topics = num_topics
        
        # Expecting JSON format: {"student_id": [interaction1, interaction2, ...]}
        # where interaction is {"topic_id": int, "correct": 0/1}
        with open(data_path, "r") as f:
            self.data = json.load(f)
        self.student_ids = list(self.data.keys())

    def __len__(self):
        return len(self.student_ids)

    def __getitem__(self, idx):
        student_id = self.student_ids[idx]
        interactions = self.data[student_id]
        
        # Truncate or pad to max_len
        interactions = interactions[-self.max_len:]
        
        # Prepare input and target
        # Input (q_seq): topic_id + correct * num_topics for interaction info
        # Target (r_seq): correctness of the interaction
        q_seq = []
        r_seq = []
        target_topic_seq = []
        
        for inter in interactions:
            topic_id = inter["topic_id"]
            correct = inter["correct"]
            q_seq.append(topic_id) # Simplify for now: just embed the topic
            r_seq.append(float(correct))
            target_topic_seq.append(topic_id)

        # Padding
        actual_len = len(q_seq)
        if actual_len < self.max_len:
            pad_len = self.max_len - actual_len
            q_seq += [0] * pad_len
            r_seq += [0] * pad_len
            target_topic_seq += [0] * pad_len
            
        return {
            "q_seq": torch.tensor(q_seq, dtype=torch.long),
            "r_seq": torch.tensor(r_seq, dtype=torch.float),
            "target_topic_seq": torch.tensor(target_topic_seq, dtype=torch.long),
            "actual_len": actual_len
        }

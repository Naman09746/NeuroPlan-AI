import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from ml.knowledge_tracing.model import DKTModel
from ml.knowledge_tracing.dataset import InteractionDataset
import os

def train(dataset_path, num_topics, epochs=20, lr=0.001):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training DKT on {device}...")
    
    dataset = InteractionDataset(dataset_path, num_topics)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    model = DKTModel(num_topics).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCELoss()
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for batch in loader:
            q = batch["q_seq"].to(device)
            r = batch["r_seq"].to(device)
            target_topics = batch["target_topic_seq"].to(device)
            actual_lens = batch["actual_len"]
            
            optimizer.zero_grad()
            
            # Forward pass: shape (batch, seq, num_topics)
            preds = model(q)
            
            # Filter predictions for the specific target topics
            # This is slow but clear for demonstration
            loss = 0
            for b in range(preds.size(0)):
                # Only take up to actual length
                b_len = actual_lens[b]
                if b_len > 1:
                    # Predict interaction i+1 from state i
                    p = preds[b, :b_len-1, :]
                    targets = r[b, 1:b_len]
                    topics = target_topics[b, 1:b_len]
                    
                    # Gather the probability of the specific topic that was answered next
                    p_target = p.gather(1, topics.view(-1, 1)).squeeze()
                    loss += criterion(p_target, targets)
            
            loss = loss / preds.size(0)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(loader):.4f}")
    
    os.makedirs("ml/models", exist_ok=True)
    torch.save(model.state_dict(), "ml/models/dkt_checkpoint.pt")
    print("✅ DKT Model saved to ml/models/dkt_checkpoint.pt")

if __name__ == "__main__":
    # Placeholder for running
    # train("ml/data/interactions.json", num_topics=100)
    pass

import torch
import torch.nn as nn

class DKTModel(nn.Module):
    """
    Deep Knowledge Tracing Model using an LSTM.
    Input: Sequence of interaction objects (topic_id, correctness)
    Output: Predicted probability of answering correctly on any topic.
    """
    def __init__(self, num_topics, embedding_dim=64, hidden_dim=128, num_layers=2):
        super(DKTModel, self).__init__()
        self.num_topics = num_topics
        
        # Topic ID embedding
        self.embedding = nn.Embedding(num_topics, embedding_dim)
        
        # Interaction input: One-hot topic_id * correctness
        # We simplify: if correct, input = topic_id + num_topics
        # if incorrect, input = topic_id
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True)
        
        # Output: Predicted mastery for each topic
        self.fc = nn.Linear(hidden_dim, num_topics)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x shape: (batch_size, seq_len) topic IDs with interaction bit
        # embedding
        embeds = self.embedding(x)
        
        # LSTM
        lstm_out, _ = self.lstm(embeds)
        
        # Predicting mastery for all topics
        logits = self.fc(lstm_out)
        return self.sigmoid(logits)

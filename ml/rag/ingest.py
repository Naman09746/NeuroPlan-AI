import chromadb
from chromadb.utils import embedding_functions
import os

class KnowledgeIngestor:
    def __init__(self, db_path="./data/chromadb"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.tokenizer = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="study_content",
            embedding_function=self.tokenizer
        )

    def ingest_text(self, text, metadata):
        """Metadata should include 'topic', 'subject', 'source'."""
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[f"{metadata['subject']}_{metadata['topic']}_{hash(text)}"]
        )
        print(f"✅ Ingested content for {metadata['topic']}")

    def ingest_directory(self, directory_path, subject):
        """Ingests all .txt files in a directory for a given subject."""
        for filename in os.listdir(directory_path):
            if filename.endswith(".txt"):
                topic = filename.replace(".txt", "")
                with open(os.path.join(directory_path, filename), "r") as f:
                    content = f.read()
                    self.ingest_text(content, {"topic": topic, "subject": subject, "source": filename})

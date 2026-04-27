import chromadb
from chromadb.utils import embedding_functions

class StudyContentRetriever:
    def __init__(self, db_path="./data/chromadb"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.tokenizer = embedding_functions.DefaultEmbeddingFunction()
        try:
            self.collection = self.client.get_collection(
                name="study_content",
                embedding_function=self.tokenizer
            )
        except:
            self.collection = None

    def retrieve_context(self, topic_name, subject_name, k=3):
        """Retrieves top-k relevant chunks for a topic."""
        if not self.collection:
            return ""
            
        query = f"Key concepts, formulas, and study material for {topic_name} in {subject_name}"
        
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            where={"subject": subject_name}
        )
        
        documents = results.get("documents", [[]])[0]
        return "\n---\n".join(documents)

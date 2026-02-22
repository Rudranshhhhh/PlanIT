"""RAG Pipeline for PlanIT.

Retrieves relevant travel information to augment LLM responses.
Uses ChromaDB for vector storage and sentence-transformers for embeddings.
"""

import os
from typing import List, Dict, Optional, Any
from pathlib import Path

# Lazy imports to avoid loading heavy dependencies at startup
_embedder = None
_chroma_client = None


def get_embedder():
    """Lazy load the sentence transformer model."""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedder


def get_chroma_client():
    """Lazy load the ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        import chromadb
        db_path = Path(__file__).parent / "chroma_db"
        db_path.mkdir(exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=str(db_path))
    return _chroma_client


class RAGPipeline:
    """RAG pipeline using ChromaDB and sentence-transformers.
    
    This pipeline:
    1. Stores documents as vector embeddings
    2. Retrieves relevant documents for queries
    3. Augments prompts with retrieved context
    
    Example:
        >>> rag = RAGPipeline()
        >>> rag.add_documents([
        ...     {"id": "1", "text": "Paris is great in spring", "metadata": {"source": "travel_guide"}}
        ... ])
        >>> context = rag.augment_prompt("When should I visit Paris?")
    """
    
    def __init__(self, collection_name: str = "travel_docs"):
        """Initialize the RAG pipeline.
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.collection_name = collection_name
        self._collection = None
    
    @property
    def collection(self):
        """Get or create the ChromaDB collection."""
        if self._collection is None:
            client = get_chroma_client()
            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """Add documents to the vector store.
        
        Args:
            documents: List of documents, each with:
                - id (str): Unique document ID
                - text (str): Document content
                - metadata (dict, optional): Additional metadata
        
        Returns:
            Number of documents added
        """
        if not documents:
            return 0
        
        embedder = get_embedder()
        
        ids = [doc["id"] for doc in documents]
        texts = [doc["text"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        
        # Generate embeddings
        embeddings = embedder.encode(texts).tolist()
        
        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        return len(documents)
    
    def add_text(self, text: str, doc_id: Optional[str] = None, 
                 metadata: Optional[Dict] = None) -> str:
        """Convenience method to add a single text document.
        
        Args:
            text: Document text
            doc_id: Optional ID (auto-generated if not provided)
            metadata: Optional metadata
            
        Returns:
            Document ID
        """
        import uuid
        doc_id = doc_id or str(uuid.uuid4())
        self.add_documents([{
            "id": doc_id,
            "text": text,
            "metadata": metadata or {}
        }])
        return doc_id
    
    def retrieve(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of documents with text, metadata, and similarity score
        """
        if self.collection.count() == 0:
            return []
        
        embedder = get_embedder()
        query_embedding = embedder.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(k, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        documents = []
        for i in range(len(results["documents"][0])):
            documents.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "score": 1 - results["distances"][0][i]  # Convert distance to similarity
            })
        
        return documents
    
    def augment_prompt(self, query: str, k: int = 3) -> str:
        """Augment a query with retrieved context.
        
        Args:
            query: User's question
            k: Number of documents to retrieve
            
        Returns:
            Augmented prompt with context prepended
        """
        docs = self.retrieve(query, k)
        
        if not docs:
            return query
        
        # Build context section
        context_parts = []
        for doc in docs:
            source = doc.get("metadata", {}).get("source", "Knowledge Base")
            context_parts.append(f"[Source: {source}]\n{doc['text']}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        return f"""Use the following context to help answer the question. If the context doesn't contain relevant information, use your general knowledge.

CONTEXT:
{context}

---

QUESTION: {query}"""
    
    def clear(self) -> None:
        """Clear all documents from the collection."""
        client = get_chroma_client()
        client.delete_collection(self.collection_name)
        self._collection = None
    
    def count(self) -> int:
        """Return the number of documents in the collection."""
        return self.collection.count()


# Global pipeline instance
_rag_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline(collection_name: str = "travel_docs") -> RAGPipeline:
    """Get or create the global RAG pipeline instance."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline(collection_name)
    return _rag_pipeline


# Seed data for travel planning
SEED_DOCUMENTS = [
    {
        "id": "paris_spring",
        "text": "Paris is best visited in spring (April-June) when the weather is mild and the gardens are in bloom. The Jardin du Luxembourg and Tuileries are particularly beautiful. Expect temperatures around 15-20°C.",
        "metadata": {"source": "Travel Guide", "destination": "Paris", "topic": "best_time"}
    },
    {
        "id": "paris_budget",
        "text": "Budget travelers in Paris should expect to spend around €100-150 per day including accommodation, food, and transportation. Hostels cost €30-50/night, and a meal at a casual restaurant is €15-25. The Paris Museum Pass (€52 for 2 days) offers great value.",
        "metadata": {"source": "Budget Guide", "destination": "Paris", "topic": "budget"}
    },
    {
        "id": "tokyo_tips",
        "text": "Tokyo is expensive but offers great value for quality. Cherry blossom season (late March - early April) is magical but crowded. The JR Pass saves money on transportation. Ryokans offer authentic Japanese experiences.",
        "metadata": {"source": "Travel Guide", "destination": "Tokyo", "topic": "tips"}
    },
    {
        "id": "travel_packing",
        "text": "Essential packing tips: Roll clothes to save space, bring a universal power adapter, carry-on only saves time and money, pack layers for variable weather, and always have a basic first-aid kit.",
        "metadata": {"source": "Travel Tips", "topic": "packing"}
    },
    {
        "id": "bali_beaches",
        "text": "Bali's best beaches include Seminyak for sunset views and beach clubs, Nusa Dua for calm waters and luxury resorts, and Uluwatu for surfing. The dry season (April-October) offers the best beach weather.",
        "metadata": {"source": "Beach Guide", "destination": "Bali", "topic": "beaches"}
    }
]


def seed_travel_data() -> int:
    """Add seed travel data to the RAG pipeline.
    
    Returns:
        Number of documents added
    """
    pipeline = get_rag_pipeline()
    
    # Only seed if collection is empty
    if pipeline.count() == 0:
        return pipeline.add_documents(SEED_DOCUMENTS)
    
    return 0


if __name__ == "__main__":
    # Demo usage
    print("Initializing RAG Pipeline...")
    rag = get_rag_pipeline()
    
    # Seed with travel data
    added = seed_travel_data()
    print(f"Added {added} seed documents")
    print(f"Total documents: {rag.count()}")
    
    # Test retrieval
    test_query = "When is the best time to visit Paris?"
    print(f"\nQuery: {test_query}")
    print("\nRetrieved documents:")
    for doc in rag.retrieve(test_query, k=2):
        print(f"  - [{doc['score']:.3f}] {doc['text'][:100]}...")
    
    print("\nAugmented prompt:")
    print(rag.augment_prompt(test_query)[:500] + "...")

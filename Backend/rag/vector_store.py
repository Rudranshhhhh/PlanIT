"""Vector store wrapper for RAG components.

This is a minimal placeholder for storing and querying vectors.
"""

from typing import List, Any


class VectorStore:
    """In-memory toy vector store (stub)."""

    def __init__(self):
        self._items = []  # list of (id, vector, metadata)

    def add(self, id: str, vector: List[float], metadata: Any = None) -> None:
        self._items.append((id, vector, metadata))

    def search(self, query_vector: List[float], k: int = 5):
        """Return up to k nearest items (naive linear scan stub)."""
        # Placeholder: just return first k items
        return self._items[:k]


if __name__ == "__main__":
    vs = VectorStore()
    vs.add("doc1", [0.1, 0.2], {"title": "Doc 1"})
    print(vs.search([0.1, 0.2]))

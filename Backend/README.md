# Backend

This folder contains backend components for PlanIT:

- `agents/`: planner, budget, and geo agents (stubs)
- `rag/`: vector store helper for RAG
- `mcp/`: minimal MCP server stub
- `api/`: Flask application entrypoint

How to run (example):

1. Create a virtual environment and install dependencies:

   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt

2. Run the API server:

   python api\main.py

3. Run the MCP server:

   python mcp\server.py

These are minimal stubs to be expanded with real logic and tests.

from duckduckgo_search import DDGS
import json

print("Testing simple search with backend='html'...")
try:
    with DDGS() as ddgs:
        results = list(ddgs.text("python programming", max_results=3, backend="html"))
    print("\nResult count:", len(results))
    print(json.dumps(results, indent=2))
except Exception as e:
    print("\nERROR:")
    print(e)

from duckduckgo_search import DDGS
import json

queries = [
    "Mysore travel guide",
    "top places to visit in Mysore",
    "Mysore 2 day itinerary",
    "Mysore trip budget"
]

print("Testing DuckDuckGo Search for Mysore...")

for q in queries:
    print(f"\nQUERY: {q}")
    try:
        with DDGS() as ddgs:
            # excessive wait time might be due to retries or timeouts
            # Checking 'html' backend behavior
            results = list(ddgs.text(q, max_results=4, backend="html", region="in-en"))
            
        print(f"Count: {len(results)}")
        for i, r in enumerate(results):
            print(f"  [{i+1}] {r['title']}")
            print(f"      {r['body'][:100]}...")
            print(f"      URL: {r['href']}")
            
    except Exception as e:
        print(f"ERROR: {e}")

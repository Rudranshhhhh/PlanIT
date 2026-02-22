from duckduckgo_search import DDGS
import json

def is_mostly_english(text):
    if not text: return False
    # Calculate percentage of ascii characters
    ascii_count = sum(1 for c in text if ord(c) < 128)
    return (ascii_count / len(text)) > 0.8

print("Testing Search variants for Mysore...")

def test_query(query, backend="html", region="in-en"):
    print(f"\n--- Testing: '{query}' [backend={backend}, region={region}] ---")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5, backend=backend, region=region))
        
        valid_results = []
        for r in results:
            if is_mostly_english(r.get("title", "")) and is_mostly_english(r.get("body", "")):
                valid_results.append(r)
            else:
                print(f"Skipping non-English result: {r.get('title')[:30]}...")
                
        print(f"Found {len(results)} total, {len(valid_results)} valid.")
        if valid_results:
            print("Top Valid Result:")
            print(json.dumps(valid_results[0], indent=2))
        else:
            print("NO VALID RESULTS.")
            
    except Exception as e:
        print(f"Error: {e}")

# Test 1: Current setup
test_query("Mysore 2 day itinerary", backend="html", region="in-en")

# Test 2: Adding 'India' to query
test_query("Mysore India 2 day itinerary", backend="html", region="in-en")

# Test 3: Lite backend (often cleaner/faster)
test_query("Mysore 2 day itinerary", backend="lite", region="in-en")

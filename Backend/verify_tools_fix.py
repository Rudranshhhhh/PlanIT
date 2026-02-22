try:
    from duckduckgo_search import DDGS
except ImportError:
    print("Failed to import DDGS from duckduckgo_search. Trying 'from ddgs import DDGS'...")
    try: 
        from ddgs import DDGS
    except ImportError:
        print("CRITICAL: plain 'ddgs' import also failed.")
        raise

import json

# Define helper before use to avoid NameError
def is_mostly_english(text):
    if not text: return False
    ascii_count = sum(1 for c in text if ord(c) < 128)
    return (ascii_count / len(text)) > 0.8

print("Verifying DDGS with 'in-en' region...")
query = "Mysore 2 day itinerary"

try:
    with DDGS() as ddgs:
        # Testing the exact logic we want to use in tools.py
        results = list(ddgs.text(query, max_results=5, backend="html", region="in-en"))

    print(f"\nResults count: {len(results)}")
    
    valid_count = 0
    for i, r in enumerate(results):
        title = r.get("title", "")
        body = r.get("body", "")
        print(f"\nResult {i+1}: {title[:50]}...")
        
        if is_mostly_english(title) and is_mostly_english(body):
            print("  [VALID ENGLISH]")
            valid_count += 1
        else:
            print("  [INVALID/NON-ENGLISH]")

    if valid_count > 0:
        print("\nSUCCESS: Found valid English results.")
    else:
        print("\nFAILURE: No valid English results found.")

except Exception as e:
    print(f"CRASH: {e}")

def unused_symbol(): pass


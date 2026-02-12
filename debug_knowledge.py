from knowledge import KnowledgeBase
import logging

# Configure logging to show errors
logging.basicConfig(level=logging.ERROR)

def test_knowledge():
    kb = KnowledgeBase()
    
    print("Testing DDG...")
    res = kb.ask_general_question("Elon Musk")
    print(f"DDG Result: {res}")
    
    print("\nTesting Wikipedia...")
    res = kb.ask_wikipedia("Elon Musk")
    print(f"Wiki Result: {res}")

    print("\nTesting Full Flow...")
    res = kb.get_answer("who is Elon Musk")
    print(f"Full Answer: {res}")

def check_ssl():
    import requests
    try:
        requests.get("https://www.google.com")
        print("SSL Check: OK")
    except Exception as e:
        print(f"SSL Check Failed: {e}")

if __name__ == "__main__":
    check_ssl()
    test_knowledge()

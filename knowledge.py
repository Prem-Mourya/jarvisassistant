import logging

# Track what's available
DDGS_AVAILABLE = True # Assume available, handle import error in method
WIKIPEDIA_AVAILABLE = True # Assume available, handle import error in method

class KnowledgeBase:
    def __init__(self):
        # Lazy initialization
        self.ddgs = None
        
    def _get_ddgs(self):
        global DDGS_AVAILABLE
        if not self.ddgs and DDGS_AVAILABLE:
            try:
                from ddgs import DDGS
                self.ddgs = DDGS()
            except ImportError:
                logging.error("ddgs not installed. Run 'pip install ddgs'")
                DDGS_AVAILABLE = False
                return None
            except Exception as e:
                logging.error(f"Error initializing DDGS: {e}")
                return None
        return self.ddgs

    def ask_general_question(self, query):
        """
        Ask a general question using DuckDuckGo Instant Answers or Text Search.
        Returns a summary string.
        """
        # DDG has TLS protocol issues with LibreSSL on some systems
        # Disabled for now, using Wikipedia as primary source
        return None
        
        # ddgs = self._get_ddgs()
        # if not ddgs:
        #     return "Knowledge modules are missing."
        #     
        # try:
        #     # 1. Try DuckDuckGo Chat/Answer (using text search for now as it's more reliable for snippets)
        #     # We fetch 1 result to get a quick answer
        #     results = ddgs.text(query, max_results=1)
        #     if results:
        #         return results[0]['body']
        # except Exception as e:
        #     logging.error(f"DDG Error: {e}")
        #     
        # return None

    def ask_wikipedia(self, query):
        """
        Search Wikipedia for a summary.
        """
        try:
            import wikipedia
            wikipedia.set_lang("en")
        except ImportError:
            logging.error("wikipedia not installed. Run 'pip install wikipedia'")
            return "Wikipedia module missing."
            
        try:
            # Clean up the query - remove common question words
            clean_query = query.lower()
            for phrase in ["who is ", "what is ", "tell me about "]:
                clean_query = clean_query.replace(phrase, "")
            clean_query = clean_query.strip()
            
            # Get summary, limit to 2 sentences
            summary = wikipedia.summary(clean_query, sentences=2)
            return summary
        except wikipedia.exceptions.DisambiguationError as e:
            # If ambiguous, try the first option
            try:
                summary = wikipedia.summary(e.options[0], sentences=2)
                return f"It might be {e.options[0]}. {summary}"
            except:
                return "The query is too ambiguous."
        except wikipedia.exceptions.PageError:
            return "I couldn't find a Wikipedia page for that."
        except Exception as e:
            return f"Wikipedia error: {e}"

    def get_answer(self, query):
        """Smart routing: Use Wikipedia as primary source."""
        logging.info(f"Asking KnowledgeBase: {query}")
        
        # Check if this is an unsuitable question for Wikipedia
        unsuitable_keywords = [
            "price", "cost", "how much", "buy", "purchase",  # Pricing
            "review", "opinion", "recommend", "best", "worst",  # Opinions
            "latest", "current", "today", "now", "recent",  # Current events
            "my", "your", "i ", "you ",  # Personal questions
        ]
        
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in unsuitable_keywords):
            # Question is not suitable for Wikipedia - suggest web search
            if any(word in query_lower for word in ["price", "cost", "how much", "buy"]):
                return "I'll search Google for pricing information. search Google instead"
            elif any(word in query_lower for word in ["latest", "current", "today", "now", "recent"]):
                return "I'll search Google for the latest information. search Google instead"
            elif any(word in query_lower for word in ["review", "opinion", "best", "worst"]):
                return "I'll search Google for reviews and opinions. search Google instead"
            elif any(word in query_lower for word in ["my", "your", "i ", "you "]):
                return "I can only answer factual questions about topics, not personal questions."
            else:
                return "I'll search Google for that. search Google instead"
        
        # Wikipedia is more reliable for factual queries
        answer = self.ask_wikipedia(query)
        if answer and "couldn't find" not in answer.lower():
            return answer
            
        # DDG disabled due to TLS issues
        # answer = self.ask_general_question(query)
        # if answer:
        #     return answer
            
        return None

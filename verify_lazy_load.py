import sys
import logging

# Mock logging to avoid clutter
logging.basicConfig(level=logging.ERROR)

print("Initial modules:", "wikipedia" in sys.modules, "ddgs" in sys.modules)

import knowledge
print("After importing knowledge:", "wikipedia" in sys.modules, "ddgs" in sys.modules)

kb = knowledge.KnowledgeBase()
print("After initializing KnowledgeBase:", "wikipedia" in sys.modules, "ddgs" in sys.modules)

# Now trigger the import
print("Triggering Wikipedia import...")
# We won't actually call the API to avoid network/key errors, just check if the method *would* trigger it
# But since the import is inside the method, we must call it or inspect it.
# Let's just call it with a dummy query that might return missing module or something, 
# but effectively we want to see if `sys.modules` changes *only* when we call it.

# Actually, I can just check if the modules are present. If they are NOT present now, then lazy loading is working.

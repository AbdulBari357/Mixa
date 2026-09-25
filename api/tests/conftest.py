import os

# Tests must never call real LLM APIs: they'd be slow, flaky and spend quota.
os.environ["GEMINI_API_KEY"] = ""
os.environ["GROQ_API_KEY"] = ""

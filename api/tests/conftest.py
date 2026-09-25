import os

# Tests must never call Gemini: they'd be slow, flaky and spend quota.
os.environ["GEMINI_API_KEY"] = ""

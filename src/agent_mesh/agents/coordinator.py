import os
from ceylonai_next import LlmAgent

# Ensure GOOGLE_API_KEY is set from environment
# This is required for google::gemini-* models
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError(
        "GOOGLE_API_KEY environment variable is not set. "
        "Please set it in your .env file or environment. "
        "Get your API key from: https://makersuite.google.com/app/apikey"
    )

coordinator = LlmAgent("Coordinator", "google::gemini-2.5-flash")
coordinator.with_system_prompt(
    "You are a helpful coordinator. and we need output as a simple text"
)
coordinator.build()

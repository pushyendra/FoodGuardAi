"""Entry point for the Food Inspector ADK agent.

Loads environment variables from .env before any ADK imports
so that GOOGLE_API_KEY and GOOGLE_GENAI_USE_VERTEXAI are available
at runtime.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (same directory as this file)
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Verify key env vars are set
assert os.getenv("GOOGLE_API_KEY"), "GOOGLE_API_KEY not found in .env"
assert os.getenv("GOOGLE_GENAI_USE_VERTEXAI") == "FALSE", (
    "GOOGLE_GENAI_USE_VERTEXAI must be set to FALSE for Google AI Studio auth"
)

# Import the agent after env is loaded
from food_inspector.agent import root_agent  # noqa: E402

if __name__ == "__main__":
    print(f"✔ GOOGLE_GENAI_USE_VERTEXAI = {os.getenv('GOOGLE_GENAI_USE_VERTEXAI')}")
    print(f"✔ GOOGLE_API_KEY            = {os.getenv('GOOGLE_API_KEY')[:10]}...")
    print(f"✔ Agent '{root_agent.name}' loaded successfully.")

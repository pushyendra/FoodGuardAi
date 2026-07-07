"""Food Inspector ADK Agent package.

Loads .env on import so that GOOGLE_API_KEY and GOOGLE_GENAI_USE_VERTEXAI
are available before ADK initialises the model backend.
"""

from pathlib import Path
from dotenv import load_dotenv

# Load .env from this package's directory
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_env_path)

from . import agent  # noqa: E402

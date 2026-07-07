"""Food Analyzer ADK Agent package.

Loads .env on import so that GOOGLE_API_KEY and GOOGLE_GENAI_USE_VERTEXAI
are available before ADK initialises the model backend.
"""

from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (one level up from this package)
_project_root = Path(__file__).resolve().parent.parent
_env_path = _project_root / "food_inspector" / ".env"

# Fall back to a .env in this package's own directory
if not _env_path.exists():
    _env_path = _project_root / ".env"

load_dotenv(dotenv_path=_env_path)

# ── Monkey-patch ADK to strip Markdown from Gemma JSON output ──
import google.adk.utils._schema_utils as adk_schema_utils
import google.adk.workflow._llm_agent_wrapper as llm_wrapper

_original_validate_schema = adk_schema_utils.validate_schema

def _patched_validate_schema(schema, json_text):
    if isinstance(json_text, str):
        # aggressively strip markdown ticks
        json_text = json_text.strip()
        if json_text.startswith("```json"):
            json_text = json_text[7:]
        elif json_text.startswith("```"):
            json_text = json_text[3:]
        
        if json_text.endswith("```"):
            json_text = json_text[:-3]
            
        json_text = json_text.strip()
    return _original_validate_schema(schema, json_text)

adk_schema_utils.validate_schema = _patched_validate_schema
llm_wrapper.validate_schema = _patched_validate_schema

from . import agent  # noqa: E402

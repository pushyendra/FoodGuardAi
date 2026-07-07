"""Centralised configuration for the Food Analyzer agent.

All tunables (model name, danger scoring thresholds, etc.) live here
so they can be changed in one place without touching node logic.
"""

# ── LLM Model ────────────────────────────────────────────────────────
MODEL_NAME: str = "gemini-2.0-flash"

# ── Danger Scoring ───────────────────────────────────────────────────
# Maps the safety category string (as returned by the LLM) to an
# integer score used in the ranking stage.
DANGER_SCORES: dict[str, int] = {
    "safe": 1,
    "moderate": 2,
    "dangerous": 3,
}

# Overall product rating thresholds (applied to average danger score)
# avg >= HIGH_THRESHOLD  → AVOID
# avg >= MED_THRESHOLD   → CAUTION
# else                   → SAFE
RATING_HIGH_THRESHOLD: float = 2.5
RATING_MED_THRESHOLD: float = 1.5

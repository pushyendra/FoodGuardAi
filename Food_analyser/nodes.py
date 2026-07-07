"""Graph nodes for the Food Analyzer pipeline.

Each function here becomes a node in the ADK Workflow graph.
The Workflow engine automatically wires Event.output → typed input
between consecutive nodes.

Pipeline:
  START → extract_ingredients → analyse_safety → rank_ingredients → generate_verdict
         (LLM)                  (LLM)            (pure Python)      (LLM)
"""

from __future__ import annotations


from google.adk import Agent, Event

from .config import DANGER_SCORES, MODEL_NAME
from .schemas import (
    IngredientSafety,
    IngredientsResult,
    ProductVerdict,
    RankedIngredient,
    RankedResult,
    SafetyAnalysisResult,
)

# ─────────────────────────────────────────────────────────────────────
# Stage 1 — Ingredient Extraction (LLM Agent)
# ─────────────────────────────────────────────────────────────────────

extract_ingredients_agent = Agent(
    name="extract_ingredients_agent",
    model=MODEL_NAME,
    description="Extracts the real-world ingredient list for a given food product.",
    instruction="""\
You are a food-science and regulatory expert. Given a food product name, return its
**COMPREHENSIVE, IN-DEPTH ingredient list** as it would appear on the full product
packaging label, including all sub-ingredients, additives, and chemicals.

Rules:
- DO NOT just list surface-level primary ingredients (e.g., if Lay's Chips, do not just say "potato, oil, salt"). You MUST include the specific flavorings, preservatives, emulsifiers, colorings, and additives (e.g., "maltodextrin", "monosodium glutamate", "dextrose", "sodium diacetate", "E-numbers").
- List specific ingredients, NOT generic nutritional categories (e.g. "wheat flour" NOT "carbs").
- Break down complex ingredients into their chemical sub-components where applicable.
- If you are unsure about an ingredient, still include it but mark
  `uncertain: true`.
- If you cannot identify the product at all, return an empty list with a
  `confidence_note` explaining why.

Return valid JSON matching the IngredientsResult schema.
IMPORTANT: DO NOT WRAP YOUR RESPONSE IN ```json ... ``` MARKDOWN BLOCKS. RETURN RAW UNFORMATTED JSON ONLY.
""",

    output_schema=IngredientsResult,
)


# ─────────────────────────────────────────────────────────────────────
# Stage 2 — Ingredient Safety Analysis (LLM Agent)
# ─────────────────────────────────────────────────────────────────────

analyse_safety_agent = Agent(
    name="analyse_safety_agent",
    model=MODEL_NAME,
    description="Evaluates the safety of each ingredient in a food product.",
    instruction="""\
You are a food-safety and toxicology expert.

You will receive a JSON object containing a product name and a list of
ingredients (IngredientsResult). For **each** ingredient, determine:

1. `safety_level` — exactly one of: "safe", "moderate", "dangerous"
2. `reason` — a brief 1-line explanation (e.g. "linked to obesity",
   "carcinogenic in high doses", "generally recognized as safe")
3. `regulatory_flags` — any regulatory warnings (e.g. "banned in EU",
   "FDA GRAS", "restricted in Japan"). Use "none" if there are none.

Return valid JSON matching the SafetyAnalysisResult schema.
Include ALL ingredients from the input — do not skip any.
IMPORTANT: DO NOT WRAP YOUR RESPONSE IN ```json ... ``` MARKDOWN BLOCKS. RETURN RAW UNFORMATTED JSON ONLY.
""",
    input_schema=IngredientsResult,
    output_schema=SafetyAnalysisResult,
)


# ─────────────────────────────────────────────────────────────────────
# Stage 3 — Ranking (Pure Python — no LLM)
# ─────────────────────────────────────────────────────────────────────

def rank_ingredients(node_input: SafetyAnalysisResult) -> RankedResult:
    """Sort ingredients by danger score (descending). Pure Python logic.

    Scoring map (from config):
      dangerous → 3
      moderate  → 2
      safe      → 1
    """
    ranked: list[RankedIngredient] = []

    for item in node_input.assessments:
        score = DANGER_SCORES.get(item.safety_level.lower().strip(), 1)
        ranked.append(
            RankedIngredient(
                name=item.name,
                safety_level=item.safety_level,
                reason=item.reason,
                regulatory_flags=item.regulatory_flags,
                danger_score=score,
            )
        )

    # Sort descending by danger_score so most dangerous comes first
    ranked.sort(key=lambda r: r.danger_score, reverse=True)

    total = sum(r.danger_score for r in ranked)
    avg = total / len(ranked) if ranked else 0.0

    return RankedResult(
        product_name=node_input.product_name,
        ranked_ingredients=ranked,
        average_score=round(avg, 2),
    )


# ─────────────────────────────────────────────────────────────────────
# Stage 4 — Overall Product Rating (LLM Agent)
# ─────────────────────────────────────────────────────────────────────

generate_verdict_agent = Agent(
    name="generate_verdict_agent",
    model=MODEL_NAME,
    description="Produces a final safety verdict for the food product.",
    instruction="""\
You are a public-health advisor. You will receive a ranked ingredient
analysis (RankedResult) containing each ingredient's safety level,
reason, regulatory flags, danger score, and the average score.

Produce a final product assessment with:

1. `rating` — exactly one of: "SAFE", "CAUTION", "AVOID"
   Guideline:
     • average score ≥ 2.5 → AVOID
     • average score ≥ 1.5 → CAUTION
     • otherwise           → SAFE
   You may override these thresholds if regulatory flags warrant it.

2. `verdict` — a 2-3 sentence plain-English summary explaining the
   rating. Mention the most concerning ingredients by name.

3. `confidence` — "high", "medium", or "low" based on how well-known
   the ingredients are.

4. `ranked_ingredients` — pass through the ranked list unchanged.

Return valid JSON matching the ProductVerdict schema.
IMPORTANT: DO NOT WRAP YOUR RESPONSE IN ```json ... ``` MARKDOWN BLOCKS. RETURN RAW UNFORMATTED JSON ONLY.
""",
    input_schema=RankedResult,
    output_schema=ProductVerdict,
)

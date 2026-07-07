"""Food Analyzer — ADK 2.0 Graph Workflow Agent.

Wires a 4-stage sequential pipeline using the Workflow(edges=[…]) API:

  START
    │
    ▼
  extract_ingredients_agent   (LLM — Stage 1)
    │
    ▼
  analyse_safety_agent        (LLM — Stage 2)
    │
    ▼
  rank_ingredients            (Python fn — Stage 3)
    │
    ▼
  generate_verdict_agent      (LLM — Stage 4)
    │
    ▼
  format_final_message        (Python fn — formats user-facing output)

Each node's output_schema feeds into the next node's input_schema via
Event.output — the Workflow engine handles the wiring automatically.
"""

from google.adk import Event, Workflow

from .nodes import (
    analyse_safety_agent,
    extract_ingredients_agent,
    generate_verdict_agent,
    rank_ingredients,
)
from .schemas import ProductVerdict


# ── Terminal node: format the verdict as a user-facing message ───────
def format_final_message(node_input: ProductVerdict) -> Event:
    """Convert the structured ProductVerdict into a readable message."""
    lines = [
        f"═══ Food Analysis: {node_input.product_name} ═══",
        "",
        f"Overall Rating : {node_input.rating}",
        f"Confidence     : {node_input.confidence}",
        "",
        f"Verdict: {node_input.verdict}",
        "",
        "── Ingredient Breakdown (most concerning first) ──",
    ]

    for i, ing in enumerate(node_input.ranked_ingredients, 1):
        flag = f" ⚠ {ing.regulatory_flags}" if ing.regulatory_flags != "none" else ""
        lines.append(
            f"  {i}. {ing.name} [{ing.safety_level.upper()}] "
            f"(score {ing.danger_score}) — {ing.reason}{flag}"
        )

    lines.append("")
    lines.append(f"Average Danger Score: {sum(i.danger_score for i in node_input.ranked_ingredients) / len(node_input.ranked_ingredients):.2f}")

    return Event(message="\n".join(lines))


# ── Wire the graph ───────────────────────────────────────────────────
root_agent = Workflow(
    name="root_agent",
    edges=[
        (
            "START",
            extract_ingredients_agent,   # Stage 1: LLM extracts ingredients
            analyse_safety_agent,        # Stage 2: LLM analyses each ingredient
            rank_ingredients,            # Stage 3: Python sorts by danger score
            generate_verdict_agent,      # Stage 4: LLM produces final verdict
            format_final_message,        # Terminal: format as user message
        ),
    ],
)

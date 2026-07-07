"""Pydantic models that define the data contract between graph nodes.

Each schema corresponds to the output of one pipeline stage and the
typed input of the next, enforced by the Workflow engine's Event.output
mechanism.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Stage 1 output ───────────────────────────────────────────────────
class Ingredient(BaseModel):
    """A single ingredient extracted from the product label."""
    name: str = Field(description="Ingredient name as it appears on the label")
    uncertain: bool = Field(
        default=False,
        description="True if the LLM is not confident this ingredient is correct",
    )


class IngredientsResult(BaseModel):
    """Output of the ingredient-extraction stage."""
    product_name: str
    ingredients: list[Ingredient]
    confidence_note: str = Field(
        default="",
        description="Optional note about overall extraction confidence",
    )


# ── Stage 2 output ───────────────────────────────────────────────────
class IngredientSafety(BaseModel):
    """Safety assessment for a single ingredient."""
    name: str
    safety_level: str = Field(
        description="One of: safe, moderate, dangerous"
    )
    reason: str = Field(
        description="Brief 1-line reason for the safety classification"
    )
    regulatory_flags: str = Field(
        default="none",
        description="Any regulatory flags (e.g. banned in EU, FDA warnings)",
    )


class SafetyAnalysisResult(BaseModel):
    """Output of the safety-analysis stage."""
    product_name: str
    assessments: list[IngredientSafety]


# ── Stage 3 output ───────────────────────────────────────────────────
class RankedIngredient(BaseModel):
    """An ingredient with its computed danger score, ready for ranking."""
    name: str
    safety_level: str
    reason: str
    regulatory_flags: str
    danger_score: int


class RankedResult(BaseModel):
    """Output of the ranking stage — ingredients sorted by danger score."""
    product_name: str
    ranked_ingredients: list[RankedIngredient]
    average_score: float


# ── Stage 4 output ───────────────────────────────────────────────────
class ProductVerdict(BaseModel):
    """Final product rating produced by the verdict stage."""
    product_name: str
    rating: str = Field(description="SAFE | CAUTION | AVOID")
    verdict: str = Field(description="2-3 sentence explanation")
    confidence: str = Field(description="high | medium | low")
    ranked_ingredients: list[RankedIngredient]

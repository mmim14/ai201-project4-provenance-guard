"""Confidence scoring: aggregate the signal scores into a final confidence.

Weighted average of the semantic (LLM) and structural (stylometric) signals,
50/50 by default (see planning.md, "Confidence Scoring with Uncertainty").
The result is an AI-likelihood in [0.0, 1.0]: 0.0 = confidently human,
1.0 = confidently AI.
"""

SEMANTIC_WEIGHT = 0.5
STRUCTURAL_WEIGHT = 0.5


def combine(
    semantic_score: float,
    structural_score: float,
    semantic_weight: float = SEMANTIC_WEIGHT,
    structural_weight: float = STRUCTURAL_WEIGHT,
) -> float:
    """Return the weighted-average AI-likelihood in [0.0, 1.0]."""
    total = semantic_weight + structural_weight
    if total <= 0:
        raise ValueError("weights must sum to a positive number")
    combined = (
        semantic_score * semantic_weight + structural_score * structural_weight
    ) / total
    return max(0.0, min(1.0, combined))

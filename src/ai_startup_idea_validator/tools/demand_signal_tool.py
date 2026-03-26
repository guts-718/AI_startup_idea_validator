from dataclasses import dataclass
from typing import List, Dict

# Semantic matcher function (LLM based similarity scoring)
from ai_startup_idea_validator.tools.semantic_matcher import semantic_matcher

# Predefined concept buckets used for classification
from ai_startup_idea_validator.tools.demand_concepts import (
    BUZZWORD_POSITIONING,
    PAIN_DRIVEN_LANGUAGE,
    OUTCOME_DRIVEN_LANGUAGE
)


# Output Data Structure -  Stores results of demand signal analysis
@dataclass
class DemandSignalResult:
    demand_score: float                # Final demand score (0–10)
    signals: List[str]                 # Human-readable signals detected
    confidence: str                   # Confidence level (low/medium/high)
    semantic_scores: Dict[str, float] # Raw similarity scores


# Main Tool
def demand_signal_tool(
    solution_text: str,
    problem_text: str,
    semantic_matcher   # function passed as dependency (can swap implementation)
) -> DemandSignalResult:

    # List to store detected signals (explanations)
    signals = []

    # Store raw semantic similarity scores
    semantic_scores = {}

    # Initialize score
    score = 0.0


    #  Semantic Matching - Check how well problem aligns with different concept buckets

    pain_score = semantic_matcher(problem_text, PAIN_DRIVEN_LANGUAGE)
    outcome_score = semantic_matcher(problem_text, OUTCOME_DRIVEN_LANGUAGE)
    buzzword_score = semantic_matcher(problem_text, BUZZWORD_POSITIONING)

    # Store raw scores for transparency/debugging
    semantic_scores["pain"] = pain_score
    semantic_scores["outcome"] = outcome_score
    semantic_scores["buzzword"] = buzzword_score


    # Scoring Logic - Strong pain-driven problem → good demand signal
    if pain_score > 0.6:
        score += 3
        signals.append("Strong pain-driven language detected")

    # Clear outcome-driven framing → good clarity of value
    if outcome_score > 0.6:
        score += 3
        signals.append("clear outcome related solution")

    # Too many buzzwords → weak/unclear positioning
    if buzzword_score > 0.7:
        score -= 2
        signals.append("buzzword heavy positioning detected")


    # Score Normalization - Clamp score between 0 and 10
    score = max(0.0, min(10.0, score))


    # Confidence Estimation 
    confidence = "medium"

    # If problem description is too short → low confidence
    if len(problem_text.split()) < 10:
        confidence = "low"


    # Return Result 
    return DemandSignalResult(
        demand_score=round(score, 2),   # final score rounded
        signals=signals,                # explanations
        confidence=confidence,          # reliability of score
        semantic_scores=semantic_scores # raw LLM scores
    )
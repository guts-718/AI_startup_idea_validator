from dataclasses import dataclass
from typing import List, Dict
from ai_startup_idea_validator.tools.semantic_matcher import semantic_matcher
from ai_startup_idea_validator.tools.demand_concepts import (
    BUZZWORD_POSITIONING,
    PAIN_DRIVEN_LANGUAGE,
    OUTCOME_DRIVEN_LANGUAGE
)

@dataclass
class DemandSignalResult:
    demand_score: float
    signals: List[str]
    confidence: str
    semantic_scores: Dict[str, float]



def demand_signal_tool(
    solution_text: str,
    problem_text: str,
    semantic_matcher) -> DemandSignalResult:
    signals=[]
    semantic_scores={}
    score=0.0

    pain_score=semantic_matcher(problem_text, PAIN_DRIVEN_LANGUAGE)
    outcome_score=semantic_matcher(problem_text, OUTCOME_DRIVEN_LANGUAGE)
    buzzword_score=semantic_matcher(problem_text, BUZZWORD_POSITIONING)

    semantic_scores["pain"]=pain_score
    semantic_scores["outcome"]=outcome_score
    semantic_scores["buzzword"]=buzzword_score

    if pain_score > 0.6:
        score+=3
        signals.append("Strong pain-driven language detected")

    if outcome_score > 0.6:
        score+=3
        signals.append("clear outcome related solution")

    if buzzword_score > 0.7:
        score-=2
        signals.append("buzzword heavy positioning detected")

    
    score=max(0.0,min(10.0,score))

    confidence="medium"

    if len(problem_text.split())<10:
        confidence="low"

    return DemandSignalResult(
        demand_score=round(score,2),
        signals=signals,
        confidence=confidence,
        semantic_scores=semantic_scores

    )
from dataclasses import dataclass
from typing import Dict, List

from ai_startup_idea_validator.agents.debate_judge_agent import DebateJudgement
from ai_startup_idea_validator.agents.market_demand_agent import MarketDemandAnalysis
from ai_startup_idea_validator.agents.competition_moat_agent import CompetitionMoatAnalysis
from ai_startup_idea_validator.agents.economics_monetization_agent import EconomicsMonetizationAnalysis
from ai_startup_idea_validator.agents.execution_risk_agent import ExecutionRiskAnalysis

@dataclass
class FinalDecision:
    final_score: float
    verdict: str
    score_breakdown: Dict[str,float]
    judge_adjustment: float
    key_positive_factors: List[str]
    key_negative_factors: List[str]
    confidence_level: str


def aggregate_base_score(market: MarketDemandAnalysis, competition: CompetitionMoatAnalysis, economics: EconomicsMonetizationAnalysis, execution: ExecutionRiskAnalysis) -> float:
    weights = {
        "market":0.3,
        "competition":.25,
        "economics":.25,
        "execution":.20,
    }

    base= (
        market.score*10*weights["market"] + competition.score*10*weights["competition"] + economics.score*10*weights["economics"] + execution.score*10*weights["execution"]
    )

    if market.score <= 3:
        base = min(base, 45)
    if economics.score <= 3:
        base = min(base, 50)
    if competition.score <= 3:
        base = min(base, 55)

    return round(base, 2)


def apply_judge_adjustment( base_score: float, judgement: DebateJudgement) -> float:
    adjusted = base_score * (1 + judgement.confidence_shift)
    return round(adjusted,2)


def verdict_from_score(score: float) -> str:
    if score >= 80:
        return "STRONG PROCEED"
    if score >= 65:
        return "PROCEED WITH CAUTION"
    if score >= 45:
        return "HIGH RISK/ ITERATE"
    return "DO NOT PROCEED"


def confidence_from_debate(judgement: DebateJudgement)-> str:
    if judgement.argument_quality == "high":
        return "high"
    if judgement.argument_quality == "medium":
        return "medium"
    return "low"



def build_final_decision(
    market: MarketDemandAnalysis,
    competition: CompetitionMoatAnalysis,
    economics: EconomicsMonetizationAnalysis,
    execution: ExecutionRiskAnalysis,
    judgement: DebateJudgement,
) -> FinalDecision:

    base_score = aggregate_base_score(
        market, competition, economics, execution
    )

    final_score = apply_judge_adjustment(base_score, judgement)

    verdict = verdict_from_score(final_score)

    positives = (
        market.strengths
        + competition.strengths
        + economics.strengths
        + execution.strengths
        + judgement.overlooked_strengths
    )

    negatives = (
        market.concerns
        + competition.concerns
        + economics.concerns
        + execution.concerns
        + judgement.unresolved_risks
    )

    return FinalDecision(
        final_score=final_score,
        verdict=verdict,
        score_breakdown={
            "market_demand": market.score * 10,
            "competition_moat": competition.score * 10,
            "economics": economics.score * 10,
            "execution": execution.score * 10,
        },
        judge_adjustment=judgement.confidence_shift,
        key_positive_factors=list(dict.fromkeys(positives))[:5],
        key_negative_factors=list(dict.fromkeys(negatives))[:5],
        confidence_level=confidence_from_debate(judgement),
    )
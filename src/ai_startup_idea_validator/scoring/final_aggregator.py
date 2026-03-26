from dataclasses import dataclass
from typing import Dict, List

# Import analysis result types from different agents
from ai_startup_idea_validator.agents.debate_judge_agent import DebateJudgement
from ai_startup_idea_validator.agents.market_demand_agent import MarketDemandAnalysis
from ai_startup_idea_validator.agents.competition_moat_agent import CompetitionMoatAnalysis
from ai_startup_idea_validator.agents.economics_monetization_agent import EconomicsMonetizationAnalysis
from ai_startup_idea_validator.agents.execution_risk_agent import ExecutionRiskAnalysis


# Final Output Data Structure - This represents the final result returned to the user
@dataclass
class FinalDecision:
    final_score: float                 # Final adjusted score (0–100)
    verdict: str                       # Decision label (e.g., PROCEED, HIGH RISK)
    score_breakdown: Dict[str, float]  # Individual scores per category
    judge_adjustment: float            # % adjustment applied by debate judge
    key_positive_factors: List[str]    # Top strengths
    key_negative_factors: List[str]    # Top risks/concerns
    confidence_level: str              # Confidence based on debate quality


#  Base Score Aggregation 
def aggregate_base_score(
    market: MarketDemandAnalysis,
    competition: CompetitionMoatAnalysis,
    economics: EconomicsMonetizationAnalysis,
    execution: ExecutionRiskAnalysis
) -> float:

# weights for each dimension (must sum ~1.0)
    weights = {
        "market": 0.3,
        "competition": 0.25,
        "economics": 0.25,
        "execution": 0.20,
    }

    # Compute weighted score (each score is assumed 0–10 → scaled to 0–100)
    base = (
        market.score * 10 * weights["market"] +
        competition.score * 10 * weights["competition"] +
        economics.score * 10 * weights["economics"] +
        execution.score * 10 * weights["execution"]
    )

    # Apply penalty caps for critical weaknesses
    # (Even if other areas are strong, these limit the total score)

    # if market.score <= 3:
    #     base = min(base, 45)   # weak demand → hard cap

    # if economics.score <= 3:
    #     base = min(base, 50)   # poor monetization → cap

    # if competition.score <= 3:
    #     base = min(base, 55)   # no moat → cap

    # Return rounded score
    return round(base, 2)


#  Judge Adjustment 
def apply_judge_adjustment(base_score: float, judgement: DebateJudgement) -> float:

    # Adjust score using judge's confidence shift
    # e.g., +0.1 → +10%, -0.2 → -20%
    adjusted = base_score * (1 + judgement.confidence_shift)

    return round(adjusted, 2)


# ------------------- Convert Score → Verdict -------------------
def verdict_from_score(score: float) -> str:

    # Map numeric score into decision categories
    if score >= 80:
        return "STRONG PROCEED"

    if score >= 65:
        return "PROCEED WITH CAUTION"

    if score >= 45:
        return "HIGH RISK/ ITERATE"

    return "DO NOT PROCEED"


# ------------------- Confidence Level -------------------
def confidence_from_debate(judgement: DebateJudgement) -> str:

    # Confidence is based on debate quality (how strong arguments were)
    if judgement.argument_quality == "high":
        return "high"

    if judgement.argument_quality == "medium":
        return "medium"

    return "low"


# ------------------- Final Decision Builder -------------------
def build_final_decision(
    market: MarketDemandAnalysis,
    competition: CompetitionMoatAnalysis,
    economics: EconomicsMonetizationAnalysis,
    execution: ExecutionRiskAnalysis,
    judgement: DebateJudgement,
) -> FinalDecision:

    # Step 1: Compute base score from all analyses
    base_score = aggregate_base_score(
        market, competition, economics, execution
    )

    # Step 2: Apply debate judge adjustment
    final_score = apply_judge_adjustment(base_score, judgement)

    # Step 3: Convert score into human-readable verdict
    verdict = verdict_from_score(final_score)

    # Step 4: Collect all positive factors (strengths)
    positives = (
        market.strengths +
        competition.strengths +
        economics.strengths +
        execution.strengths +
        judgement.overlooked_strengths  # extra positives from debate
    )

    # Step 5: Collect all negative factors (risks)
    negatives = (
        market.concerns +
        competition.concerns +
        economics.concerns +
        execution.concerns +
        judgement.unresolved_risks  # risks identified in debate
    )

    # Step 6: Build final structured decision
    return FinalDecision(
        final_score=final_score,
        verdict=verdict,

        # Individual category scores (scaled to 0–100)
        score_breakdown={
            "market_demand": market.score * 10,
            "competition_moat": competition.score * 10,
            "economics": economics.score * 10,
            "execution": execution.score * 10,
        },

        # Judge’s impact on score
        judge_adjustment=judgement.confidence_shift,

        # Remove duplicates while preserving order, then take top 5
        key_positive_factors=list(dict.fromkeys(positives))[:5],
        key_negative_factors=list(dict.fromkeys(negatives))[:5],

        # Confidence derived from debate strength
        confidence_level=confidence_from_debate(judgement),
    )
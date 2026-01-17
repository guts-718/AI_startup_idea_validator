from typing import Dict

from ai_startup_idea_validator.models.startup_idea import StartupIdea

# Evidence
from ai_startup_idea_validator.evidence.evidence_runner import run_evidence_phase

# Analysis agents
from ai_startup_idea_validator.agents.market_demand_agent import (
    build_market_demand_agent,
    run_market_demand_analysis,
)
from ai_startup_idea_validator.agents.competition_moat_agent import (
    build_competition_moat_agent,
    run_competition_moat_analysis,
)
from ai_startup_idea_validator.agents.economics_monetization_agent import (
    build_economics_monetization_agent,
    run_economics_monetization_analysis,
)
from ai_startup_idea_validator.agents.execution_risk_agent import (
    build_execution_risk_agent,
    run_execution_risk_analysis,
)

# Debate
from ai_startup_idea_validator.agents.debate_for_agent import (
    build_debate_for_agent,
    run_debate_for,
)
from ai_startup_idea_validator.agents.debate_against_agent import (
    build_debate_against_agent,
    run_debate_against,
)
from ai_startup_idea_validator.agents.debate_judge_agent import (
    build_debate_judge_agent,
    run_debate_judgement,
)

# Competition signals
from ai_startup_idea_validator.tools.competition_signal_builder import (
    build_competition_signals,
)

# Scoring
from ai_startup_idea_validator.scoring.final_aggregator import (
    aggregate_base_score,
    build_final_decision,
)

# Final explanation
from ai_startup_idea_validator.agents.final_explanation_agent import (
    build_final_explanation_agent,
    run_final_explanation,
)


def run_full_validation(startup: StartupIdea, llm_model: str = "gpt-4o-mini")-> Dict:
    """
    Runs the complete startup idea validation pipeline. 
    Returns a fully serializable result dictionary
    """

    # evidence
    evidence=run_evidence_phase(startup)

    # competition signals
    competition_signals = build_competition_signals(startup)

    # Build agents
    market_agent = build_market_demand_agent(llm_model)
    competition_agent=build_competition_moat_agent(llm_model)
    economics_agent = build_economics_monetization_agent(llm_model)
    execution_agent=build_execution_risk_agent(llm_model)

    # expert analysis
    market_analysis = run_market_demand_analysis(market_agent, startup, evidence.market_size, evidence.demand)
    competition_analysis=run_competition_moat_analysis(competition_agent, startup, competition_signals)
    economics_analysis= run_economics_monetization_analysis(economics_agent, startup, evidence.market_size, evidence.cost_model)
    execution_analysis = run_execution_risk_analysis(execution_agent, startup)


    # base score
    base_score=aggregate_base_score(
        market_analysis, competition_analysis, economics_analysis, execution_analysis)
    

    analysis_bundle={
        "market_demand":market_analysis.__dict__,
        "competition_moat":competition_analysis.__dict__,
        "economics":economics_analysis.__dict__,
        "execution_risk":execution_analysis.__dict__,
        "base_score":base_score
    }

    # debate
    for_agent = build_debate_for_agent(llm_model)
    against_agent=build_debate_against_agent(llm_model)

    for_argument=run_debate_for(for_agent, analysis_bundle)
    against_argument=run_debate_against(against_agent, analysis_bundle)


    # judge
    judge_agent=build_debate_judge_agent(llm_model)
    judgement=run_debate_judgement(judge_agent, for_argument.__dict__, against_argument.__dict__, base_score)

    # final aggregation
    final_decision=build_final_decision(
        market_analysis,
        competition_analysis,
        economics_analysis,
        execution_analysis,
        judgement,
    )


    # final explanation
    explanation_agent=build_final_explanation_agent(llm_model)
    final_explanation=run_final_explanation(
        explanation_agent, startup, final_decision
    )


    # serializable output
    return {
        "startup":startup.__dict__,
        "analysis":analysis_bundle,
        "debate":{
            "for":for_argument.__dict__,
            "against":against_agent.__dict__,
            "judge":judgement.__dict__,
        },
        "final_decision":final_decision.__dict__,
        "final_explanation":final_explanation.__dict__,
    }
from typing import Dict

# input data model representing the startup idea
from ai_startup_idea_validator.models.startup_idea import StartupIdea

# Evidence Phase  - Collects real world signals like market size, demand, etc.
from ai_startup_idea_validator.evidence.evidence_runner import run_evidence_phase

#  Analysis Agents -  Each agent focuses on one dimension of evaluation

# Market demand analysis (is there real need?)
from ai_startup_idea_validator.agents.market_demand_agent import (
    build_market_demand_agent,
    run_market_demand_analysis,
)

# Competition & moat analysis (how defensible is the idea?)
from ai_startup_idea_validator.agents.competition_moat_agent import (
    build_competition_moat_agent,
    run_competition_moat_analysis,
)

# Economics & monetization (can this make money?)
from ai_startup_idea_validator.agents.economics_monetization_agent import (
    build_economics_monetization_agent,
    run_economics_monetization_analysis,
)

# Execution risk (how hard is it to build/scale?)
from ai_startup_idea_validator.agents.execution_risk_agent import (
    build_execution_risk_agent,
    run_execution_risk_analysis,
)

# Debate Agents - Simulate a structured debate (pros vs cons)

from ai_startup_idea_validator.agents.debate_for_agent import (
    build_debate_for_agent,
    run_debate_for,
)

from ai_startup_idea_validator.agents.debate_against_agent import (
    build_debate_against_agent,
    run_debate_against,
)

# Judge agent decides which side is stronger
from ai_startup_idea_validator.agents.debate_judge_agent import (
    build_debate_judge_agent,
    run_debate_judgement,
)

#  Competition Signals -  Builds structured competition insights (e.g., rivals, saturation)
from ai_startup_idea_validator.tools.competition_signal_builder import (
    build_competition_signals,
)

#  Scoring - Aggregates scores and builds final decision
from ai_startup_idea_validator.scoring.final_aggregator import (
    aggregate_base_score,
    build_final_decision,
)

# Final Explanation - Converts results into human-readable explanation
from ai_startup_idea_validator.agents.final_explanation_agent import (
    build_final_explanation_agent,
    run_final_explanation,
)


def run_full_validation(startup: StartupIdea, llm_model: str = "gpt-4o-mini") -> Dict:
    """
    Runs the complete startup idea validation pipeline.
    Returns a fully serializable result dictionary.
    """

    #  Step 1: Evidence Collection - Gather raw signals like market size, demand, cost model, etc.
    evidence = run_evidence_phase(startup)

    #  Step 2: Competition Signals - Generate structured insights about competitors
    competition_signals = build_competition_signals(startup)

    #  Step 3: Build Analysis Agents -- Initialize all LLM agents for different evaluation dimensions
    market_agent = build_market_demand_agent(llm_model)
    competition_agent = build_competition_moat_agent(llm_model)
    economics_agent = build_economics_monetization_agent(llm_model)
    execution_agent = build_execution_risk_agent(llm_model)

    #  Step 4: Run Expert Analyses -- Each agent evaluates the startup independently

    # Market demand analysis using evidence
    market_analysis = run_market_demand_analysis(
        market_agent, startup, evidence.market_size, evidence.demand
    )

    # Competition & moat analysis
    competition_analysis = run_competition_moat_analysis(
        competition_agent, startup, competition_signals
    )

    # Monetization & economics analysis
    economics_analysis = run_economics_monetization_analysis(
        economics_agent, startup, evidence.market_size, evidence.cost_model
    )

    # Execution feasibility analysis
    execution_analysis = run_execution_risk_analysis(
        execution_agent, startup
    )

    #  Step 5: Base Score- Combine all analysis scores into a single base score
    base_score = aggregate_base_score(
        market_analysis,
        competition_analysis,
        economics_analysis,
        execution_analysis
    )

    # Bundle all analysis results into a dictionary
    analysis_bundle = {
        "market_demand": market_analysis.__dict__,
        "competition_moat": competition_analysis.__dict__,
        "economics": economics_analysis.__dict__,
        "execution_risk": execution_analysis.__dict__,
        "base_score": base_score
    }

    # Debate Phase -- Simulate arguments FOR and AGAINST the startup

    for_agent = build_debate_for_agent(llm_model)
    against_agent = build_debate_against_agent(llm_model)

    # Generate arguments supporting the idea
    for_argument = run_debate_for(for_agent, analysis_bundle)

    # Generate arguments opposing the idea
    against_argument = run_debate_against(against_agent, analysis_bundle)

    # Step 7: Judge Decision -- Judge compares both sides and adjusts score
    judge_agent = build_debate_judge_agent(llm_model)

    judgement = run_debate_judgement(
        judge_agent,
        for_argument.__dict__,
        against_argument.__dict__,
        base_score
    )

    # Step 8: Final Decision -- Combine all insights + debate outcome into final verdict
    final_decision = build_final_decision(
        market_analysis,
        competition_analysis,
        economics_analysis,
        execution_analysis,
        judgement,
    )

    #  Step 9: Final Explanation - Generate a human-readable explanation of the decision
    explanation_agent = build_final_explanation_agent(llm_model)

    final_explanation = run_final_explanation(
        explanation_agent,
        startup,
        final_decision
    )

    #  Step 10: Return Serializable Output -- Convert everything into dicts for API/JSON response
    return {
        "startup": startup.__dict__,
        "analysis": analysis_bundle,
        "debate": {
            "for": for_argument.__dict__,
            "against": against_argument.__dict__,  # fixed bug (was against_agent)
            "judge": judgement.__dict__,
        },
        "final_decision": final_decision.__dict__,
        "final_explanation": final_explanation.__dict__,
    }
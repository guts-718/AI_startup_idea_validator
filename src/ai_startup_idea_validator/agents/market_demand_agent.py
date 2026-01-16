from dataclasses import dataclass
from typing import List
import json

from crewai import Agent, Task
from ai_startup_idea_validator.models.startup_idea import StartupIdea
from ai_startup_idea_validator.tools.market_size_tool import MarketSizeResult
from ai_startup_idea_validator.tools.demand_signal_tool import DemandSignalResult


@dataclass
class MarketDemandAnalysis:
    score: float
    strengths: List[str]
    concerns: List[str]
    rationale: str


def build_market_demand_agent(llm):
    return Agent(
        role="Market and demand analyst",
        goal=(
            "Evaluate market attractiveness and real demand using the provided evidence. "
            "You must ground your reasoning in market size numbers and demand signals. "
        ),
        backstory=(
            "You are a pragmatic market analyst. "
            "You distrust hype and focus on demand, scale, and realism. "
        ),
        llm=llm,
        verbose=False,
    )


def run_market_demand_analysis(agent:Agent, startup: StartupIdea, market: MarketSizeResult, demand: DemandSignalResult) -> MarketDemandAnalysis:
    task = Task(
        description=f"""
            You are given structured evidence about a startup idea.

            Startup summary:
            - Problem: {startup.problem}
            - Solution: {startup.solution}
            - Geography: {startup.geography}

            Market size evidence:
            - TAM (USD): {market.tam_usd}
            - SAM (USD): {market.sam_usd}
            - SOM (USD): {market.som_usd}
            - confidence: {market.confidence}

            Demand Signals:
            - Demand score (0-10): {demand.demand_score}
            - Signals: {demand.signals}
            - Confidence: {demand.confidence}

            Instructions:
            1. Assess whether the market is large enough to matter.
            2. Assess whether demand appears real or speculative.
            3. Penalize vague or low-confidence signals.
            4. Produce:
            - A numeric score between 0 and 10
            - 2–3 strengths
            - 2–3 concerns
            5. Do NOT introduce new facts.
            6. Be conservative and realistic.

            Return your output STRICTLY as JSON with this shape and make sure to add the rationale field as specified in the given schema:
{{
  "score": number,
  "strengths": [string],
  "concerns": [string],
  "rationale": string
}}
""",
        expected_output="Strict JSON following the specified schema",
        agent=agent,
    )

    result = agent.execute_task(task)


    try:
        data = json.loads(result)
    except Exception as e:
        raise ValueError(f"Failed to parse Market & Demand agent output: {result}") from e

    REQUIRED_KEYS = {"score", "strengths", "concerns", "rationale"}

    missing = REQUIRED_KEYS - data.keys()
    if missing:
        raise ValueError(
            f"Market & Demand agent output missing keys {missing}. Output was: {data}"
        )

    if not isinstance(data["concerns"], list):
        raise ValueError("concerns must be a list of strings")

    if not isinstance(data["strengths"], list):
        raise ValueError("strengths must be a list of strings")

        
    return MarketDemandAnalysis(
        score=float(data["score"]),
        strengths=data["strengths"],
        concerns=data["concerns"],
        rationale=data["rationale"],
    )


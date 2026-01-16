from dataclasses import dataclass
from typing import List

from crewai import Agent, Task
import json
from ai_startup_idea_validator.models.startup_idea import StartupIdea
from ai_startup_idea_validator.tools.market_size_tool import MarketSizeResult
from ai_startup_idea_validator.tools.cost_model_tool import CostModelResult

@dataclass
class EconomicsMonetizationAnalysis:
    score: float
    strengths: List[str]
    concerns: List[str]
    rationale: str


def build_economics_monetization_agent(llm):
    return Agent(
        role="Economics and Monetization Analyst",
        goal=(
            "Evaluate whether the startup's economics makes sense. "
            "Focus on margins, scalability and monetization realism. "
        ),
        backstory=(
            "You are a financially conservative operator. "
            "You assume margins are bad unless proven otherwise. "
        ),
        llm=llm,
        verbose=False,
    )


def run_economics_monetization_analysis(
    agent:Agent, startup: StartupIdea, market: MarketSizeResult, cost: CostModelResult) -> EconomicsMonetizationAnalysis:
    task=Task(description=f"""
    You are given structured financial evidence about a startup.

    Startup summary:
    - Solution: {startup.solution}
    - Monetization model: {startup.monetization_model}

    Market size:
    - TAM (USD): {market.tam_usd}
    - SAM (USD): {market.sam_usd}
    - SOM (USD): {market.som_usd}

    Cost Model:
    - Monthly fixed cost (USD): {cost.monthly_fixed_cost_usd}
    - Monthly variable cost (USD): {cost.total_monthly_cost_usd}
    - Total monthly cost (USD): {cost.total_monthly_cost_usd}
    - Cost confidence: {cost.confidence}

    Instructions:
    1. Evaluate whether monetization is realistic for the given market.
    2. Assess scalability: do costs grow slower than potential revenue?
    3. Penalize unclear or missing monetization models.
    4. Be conservative: small markets + high costs = bad score.
    5. Produce:
    - A numeric score between 0 and 10
    - 2–3 strengths
    - 2–3 concerns
    6. Do NOT invent pricing numbers or new assumptions.

    Return your output STRICTLY as JSON with this shape:
    {{
        "score": number,
        "strengths": [string],
        "concerns": [string],
        "rationale": str
    }}

    """,
    expected_output="Strict JSON following the specified schema",
    agent=agent,
    )

    result=agent.execute_task(task)


    try:
        data = json.loads(result)
    except Exception as e:
        raise ValueError(f"Failed to parse Market & Demand agent output: {result}") from e

    if not isinstance(data["concerns"], list):
        raise ValueError("concerns must be a list of strings")

    if not isinstance(data["strengths"], list):
        raise ValueError("strengths must be a list of strings")


    return EconomicsMonetizationAnalysis(
        score=float(data["score"]),
        strengths=data["strengths"],
        concerns=data["concerns"],
        rationale=data["rationale"],
    )
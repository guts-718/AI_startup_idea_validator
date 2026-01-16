from dataclasses import dataclass
from typing import List
import json

from crewai import Agent, Task

from ai_startup_idea_validator.models.startup_idea import StartupIdea
from ai_startup_idea_validator.tools.competition_signal_builder import (
    CompetitionSignals,
)


@dataclass
class CompetitionMoatAnalysis:
    score: float
    strengths: List[str]
    concerns: List[str]
    rationale: str


def build_competition_moat_agent(llm):
    return Agent(
        role="Competition & Moat Analyst",
        goal=(
            "Evaluate competitive pressure and defensibility using structural "
            "competition signals. Focus on dominance, entry barriers, and moat difficulty."
        ),
        backstory=(
            "You are a skeptical strategist. "
            "You assume markets are hostile unless proven otherwise."
        ),
        llm=llm,
        verbose=False,
    )


def run_competition_moat_analysis(
    agent: Agent,
    startup: StartupIdea,
    signals: CompetitionSignals,
) -> CompetitionMoatAnalysis:

    task = Task(
        description=f"""
You are given structural competition signals for a startup.

Startup summary:
- Problem: {startup.problem}
- Solution: {startup.solution}
- Claimed differentiation: {startup.differentiation}

Competition signals:
- Direct competitor count: {signals.direct_competitor_count}
- Dominant incumbents present: {signals.dominant_incumbents_present}
- Highest dominance level: {signals.highest_dominance_level}
- Competition style: {signals.competition_style}
- Common moat sources: {signals.common_moat_sources}
- Common entry barriers: {signals.common_entry_barriers}
- Competition pressure score (0–10): {signals.competition_pressure_score}

Instructions:
1. Interpret competitive pressure using dominance and market structure.
2. Assess whether the claimed differentiation can realistically overcome existing moats.
3. Penalize markets with dominant incumbents or winner-takes-most dynamics.
4. Do NOT use competitor count alone as a proxy for difficulty.
5. Be conservative and realistic.
6. Produce:
   - A numeric score between 0 and 10
   - 2–3 strengths
   - 2–3 concerns
7. Do NOT introduce new competitors or facts.

Return your output STRICTLY as JSON with this shape:
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

    if not isinstance(data["concerns"], list):
        raise ValueError("concerns must be a list of strings")

    if not isinstance(data["strengths"], list):
        raise ValueError("strengths must be a list of strings")


    return CompetitionMoatAnalysis(
        score=float(data["score"]),
        strengths=data["strengths"],
        concerns=data["concerns"],
        rationale=data["rationale"],
    )

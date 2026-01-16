from dataclasses import dataclass
from typing import List
from crewai import Agent, Task
import json

from ai_startup_idea_validator.models.startup_idea import StartupIdea

@dataclass
class ExecutionRiskAnalysis:
    score: float
    strengths: List[str]
    concerns: List[str]
    rationale: str


def build_execution_risk_agent(llm):
    return Agent(
        role="Execution and risk analyst",
        goal=(
            "Evaluate execution feasibility and key risks. "
            "Focus on founder market fir, operational complexity, "
            "regulatory risk and go-to-market realism. "
        ),
        backstory=(
            "You are a risk-focused operator. "
            "You assume execution is hard and failure is common. "
        ),
        llm=llm,
        verbose=False,
    )



def run_execution_risk_analysis(agent: Agent, startup: StartupIdea)-> ExecutionRiskAnalysis:
    task=Task(
        description=f"""

        You are given structured information about a startup.

        Startup details:
        - Problem: {startup.problem}
        - Solution: {startup.solution}
        - Geography: {startup.geography}
        - Founder expertise: {startup.founder_expertise}
        - Customer acquisition plan: {startup.customer_acquisition}
        - Regulatory constraints: {startup.regulatory_constraints}
        - Other constraints: {startup.constraints}
        

        Instructions:
        1. Assess founder–market fit (experience vs problem).
        2. Evaluate operational and technical complexity implied by the solution.
        3. Identify regulatory or compliance risks based on geography/industry cues.
        4. Penalize missing founder expertise or unclear acquisition strategy.
        5. Be conservative and realistic.
        6. Produce:
        - A numeric score between 0 and 10
        - 2–3 strengths
        - 2–3 concerns
        7. Do NOT introduce new facts or assumptions.

        Return your output STRICTLY as JSON with this shape:
        {{
            "score": number,
            "strengths":[string],
            "concerns":[string],
            "rationale":string
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


    return ExecutionRiskAnalysis(
        score=float(data["score"]),
        strengths=data["strengths"],
        concerns=data["concerns"],
        rationale=data["rationale"],
    )


    
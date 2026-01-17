from dataclasses import dataclass
from typing import List
import json

from crewai import Agent, Task

@dataclass
class DebateAgainstArgument:
    position: str
    core_thesis: str
    failure_modes: List[str]
    critical_assumptions_attacked: List[str]


def build_debate_against_agent(llm):
    return Agent(
        role="Debate challenger (AGAINST)",
        goal=(
            "Argue why startup idea is likely to FAIL. "
            "Expose hidden risks and weak assumptions."
        ),
        backstory=(
            "You are a skeptical operator who has seen many startup fail. "
            "You assume adverse conditions by default."
        ),
        llm=llm,
        verbose=False,
    )


def run_debate_against(
    agent: Agent,
    analysis_bundle: dict)-> DebateAgainstArgument:
    task= Task(
        description=f"""
        You are participating in a structured debate.
        You MUST argue AGAINST pursuing the startup idea.
        You are given structured analysis results (no raw data):
       

        {json.dumps(analysis_bundle, indent=2)}

        Rules (STRICT):
        - Assume adverse conditions.
        - Treat uncertainty as risk.
        - Attack assumptions directly.
        - Do NOT introduce new facts.
        - Do NOT praise upside.
        - Be blunt and critical.

        Return STRICT JSON with this shape:

        {{
            "position": "against",
            "core_thesis": string,
            "failure_modes": [string, string, string],
            "critical_assumptions_attacked": [string]
        }}
        """,
        expected_output="Strict JSON only",
        agent=agent,
    )

    result= agent.execute_task(task)

    try:
        data=json.loads(result)
    except Exception as e:
        raise ValueError(f"Failed to parse AGAINST debate output: {result}") from e

    
    required={
        "position",
        "core_thesis",
        "failure_modes",
        "critical_assumptions_attacked",
    }

    missing = required - data.keys()
    if missing:
        raise ValueError(f"Against debate missing keys {missing}: {data}")

    return DebateAgainstArgument(
        position=data["position"],
        core_thesis=data["core_thesis"],
        failure_modes=data["failure_modes"],
        critical_assumptions_attacked=data["critical_assumptions_attacked"],
    )
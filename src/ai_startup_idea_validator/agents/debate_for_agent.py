from dataclasses import dataclass
from typing import List
import json

from crewai import Agent, Task

@dataclass
class DebateForArgument:
    position: str # "FOR"
    core_thesis: str
    supporting_arguments: List[str]
    acknowledged_risks: List[str]


def build_debate_for_agent(llm):
    return Agent(
        role="Debate Advocate (FOR)",
        goal=(
            "Argue why startup idea SHOULD be pursued. "
            "Maximize upside using the provided analysis only"
        ),
        backstory=(
            "You are an optimistic but rational investor. "
            "You believe most risks can be mitigated with execution. "
        ),
        llm=llm,
        verbose=False,
    )

def run_debate_for(agent: Agent, analysis_bundle: dict) -> DebateForArgument:
    task= Task(
        description=f"""
        You are participating in a structured debate.
        You MUST argue FOR pursuing the startup idea.
        You are given structured analysis results (no raw data):
        {json.dumps(analysis_bundle, indent=2)}

        Rules (STRICT):
        - Assume competent execution.
        - Emphasize strengths and upside.
        - Reframe weaknesses as solvable.
        - Do NOT intoduce new facts.
        - Do NOT hedge ("It depends", "maybe").
        - You MUST argue confidently.

        Return STRICT JSON with this shape:
        {{
            "position":"for",
            "core_thesis":string,
            "supporting_arguments": [string, string, string],
            "acknowledged_risks": [string]
        }}
        """,
        expected_output="Strict JSON only",
        agent=agent,
    )

    result = agent.execute_task(task)

    try:
        data=json.loads(result)
    except Exception as e:
        raise ValueError(f"Failed to parse FOR debate output: {result}") from e
    

    required = {"position", "core_thesis", "supporting_arguments", "acknowledged_risks"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"FOR debate missing keys {missing}: {data}")

    return DebateForArgument(
        position=data["position"],
        core_thesis=data["core_thesis"],
        supporting_arguments=data["supporting_arguments"],
        acknowledged_risks=data["acknowledged_risks"],
    )
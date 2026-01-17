from dataclasses import dataclass
from typing import List
import json

from crewai import Agent, Task

@dataclass
class DebateJudgement:
    debate_winner: str
    confidence_shift: float
    unresolved_risks: List[str]
    overlooked_strengths: List[str]
    argument_quality: str
    judge_rationale: str


def build_debate_judge_agent(llm):
    return Agent(
        role="Debate Judge (Consistency Auditor)",
        goal=(
            "Audit two opposing debate arguments for logical strength,"
            "consistency with underlying analysis, and risk exposure. "
            "You do NOT decide the outcome- only adjust confidence. "
        ),
        backstory=(
            "You are a risk committe chair."
            "You distrust rhetoric and focus on unresolved risks and overconfidence. "
        ),
        llm=llm,
        verbose=False,
    )


def run_debate_judgement(agent: Agent, for_argument: dict, against_argument: dict, base_score: float,)-> DebateJudgement:
    task= Task(
        description=f"""
        You are judging a structured debate about a startup idea.

        Inputs:
        
        FOR argument: {json.dumps(for_argument, indent=2)}

        AGAINST argument: {json.dumps(against_argument, indent=2)}

        Base Score (before debate): {base_score}

        Rules (STRICT):
        - You are NOT deciding go/no-go.
        - You are NOT allowed to rescore the idea.
        - You must NOT introduce new facts.
        - Your job is to assess whether the debate reveals:
        • unresolved risks
        • overconfidence
        • overlooked strengths
        - Use debate quality to determine confidence adjustment.

        confidence_shift rules:
        - Range must be between -0.25 and +0.10
        - Use negative shift if AGAINST exposes serious unresolved risks
        - Use positive shift only if FOR exposes overlooked strengths
        - Use 0 if debate adds little signal

        Return STRICT JSON with this shape:
        {{
        "debate_winner": "for" | "against" | "tie",
        "confidence_shift": number,
        "unresolved_risks": [string],
        "overlooked_strengths": [string],
        "argument_quality": "low" | "medium" | "high",
        "judge_rationale": string
        }}
        """,
        expected_output="Strict JSON only",
        agent=agent,
    )

    result=agent.execute_task(task)

    try:
        data = json.loads(result)
    except Exception as e:
        raise ValueError(f"Failed to parse Judge output: {result}") from e

    required = {
        "debate_winner",
        "confidence_shift",
        "unresolved_risks",
        "overlooked_strengths",
        "argument_quality",
        "judge_rationale",
    }
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Judge output missing keys {missing}: {data}")

    # ---- hard safety clamps ----
    shift = float(data["confidence_shift"])
    if shift < -0.25 or shift > 0.10:
        raise ValueError(f"confidence_shift out of bounds: {shift}")

    if data["argument_quality"] not in {"low", "medium", "high"}:
        raise ValueError("Invalid argument_quality")

    if data["debate_winner"] not in {"for", "against", "tie"}:
        raise ValueError("Invalid debate_winner")

    return DebateJudgement(
        debate_winner=data["debate_winner"],
        confidence_shift=shift,
        unresolved_risks=data["unresolved_risks"],
        overlooked_strengths=data["overlooked_strengths"],
        argument_quality=data["argument_quality"],
        judge_rationale=data["judge_rationale"],
    )
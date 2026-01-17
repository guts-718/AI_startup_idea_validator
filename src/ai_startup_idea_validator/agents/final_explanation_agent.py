from dataclasses import dataclass
from typing import List, Dict
import json

from crewai import Agent, Task
from ai_startup_idea_validator.scoring.final_aggregator import FinalDecision
from ai_startup_idea_validator.models.startup_idea import StartupIdea

@dataclass
class FinalExplanation:
    verdict: str
    final_score: float
    summary: str
    key_reasons_for_score: List[str]
    key_risks: List[str]
    recommended_next_steps: List[str]
    confidence_level: str


def build_final_explanation_agent(llm):
    return Agent(
        role="Startup Evaluation Explainer",
        goal=(
            "Clearly explain the final startup evaluation decision to a founder."
            "Be honest, concise, and actionable. "
        ),
        backstory=(
            "You are a seasoned startup advisor. "
            "You explain hard truths without being dismissive. "
        ),
        llm=llm,
        verbose=False,
    )


def run_final_explanation(agent: Agent, startup: StartupIdea, final_decision: FinalDecision) -> FinalExplanation:
    task=Task(
        description=f"""

        You are explaining the final evaluation of a startup idea.

        Startup:
        - Problem: {startup.problem}
        - Solution: {startup. solution}
        - Geography: {startup.geography}
        - Industry: {startup.industry}

        Final decision (already computed, DO NOT change it):
        {json.dumps(final_decision.__dict__, indent=2)}

        Rules (STRICT):
        - Do NOT rescore or second-guess the decision.
        - Do NOT introduce new facts.
        - Explain WHY the score and verdict occured.
        - Be specific and conservative.
        - Avoid hype or sugarcoating.

        Produce:
        - A short summary (4-5 sentences)
        - Key reasonse that drove the score.
        - Key risks holding the idea back
        - Concrete next steps to improve the idea

        Return STRICT JSON with this shape:
        {{
            "verdict": string,
            "final_score": number,
            "summary": string,
            "key_reasons_for_score": [string],
            "key_risks": [string],
            "recommended_next_steps": [string],
            "confidence_level": string
        }}
        """,
        expected_output="Strict JSON only",
        agent=agent,
    )

    result= agent.execute_task(task)

    try:
        data = json.loads(result)
    except Exception as e:
        raise ValueError(f"Failed to parse Final Explanation output: {result}") from e

    
    required={
        "verdict",
        "final_score",
        "summary",
        "key_reasons_for_score",
        "key_risks",
        "confidence_level",
    }

    missing = required - data.keys()
    if missing:
        raise ValueError(f"Final explaination missing these keys: {missing}: {data}")
    

    return FinalExplanation(
        verdict=data["verdict"],
        final_score=float(data["final_score"]),
        summary=data["summary"],
        key_reasons_for_score=data["key_reasons_for_score"],
        key_risks=data["key_risks"],
        recommended_next_steps=data["recommended_next_steps"],
        confidence_level=data["confidence_level"]
    )


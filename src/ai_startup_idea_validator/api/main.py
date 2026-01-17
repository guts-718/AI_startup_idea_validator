from signal import valid_signals
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ai_startup_idea_validator.models.startup_idea import StartupIdea
from ai_startup_idea_validator.pipeline.run_full_validation import run_full_validation

app = FastAPI(
    title="AI Startup Idea Validator",
    description="Evaluates startup ideas using evidence, multi-agent analysis, debate and scoring.",
    version="1.0.0",
)


# request schema
class StartupIdeaRequest(BaseModel):
    problem: str
    solution: str
    geography: str
    industry: str

    target_user: Optional[str]= None
    differentiation: Optional[str]=None
    monetization_model: Optional[str]=None
    founder_expertise: Optional[str]=None
    customer_acquisition: Optional[str]=None
    regulatory_constraints: List[str]=[]
    constraints: List[str]=[]



class ValidationResponse(BaseModel):
    final_score: float
    verdict: str
    confidence_level: str
    explanation: dict


@app.post("/validate",response_model=ValidationResponse)
def validate_startup(idea: StartupIdeaRequest):
    try:
        startup=StartupIdea(**idea.dict())
        result=run_full_validation(startup)

        final_decision=result["final_decision"]
        final_explanation=result["final_explanation"]


        return {
            "final_score":final_decision["final_score"],
            "verdict":final_decision["verdict"],
            "confidence_level":final_decision["confidence_level"],
            "explanation":final_explanation,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

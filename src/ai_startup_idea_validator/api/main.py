from signal import valid_signals
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel #for request/response validation
from typing import List, Optional #for type hints

from ai_startup_idea_validator.models.startup_idea import StartupIdea
from ai_startup_idea_validator.pipeline.run_full_validation import run_full_validation

# fastapi exposing /validate endpoint
app = FastAPI(
    title="AI Startup Idea Validator",
    description="Evaluates startup ideas using evidence, multi-agent analysis, debate and scoring.",
    version="1.0.0",
)


# request schema
class StartupIdeaRequest(BaseModel):
    # required fields
    problem: str
    solution: str
    geography: str
    industry: str

    # optional fields (defaulting to None)
    target_user: Optional[str]= None
    differentiation: Optional[str]=None
    monetization_model: Optional[str]=None
    founder_expertise: Optional[str]=None
    customer_acquisition: Optional[str]=None
    regulatory_constraints: List[str]=[]
    constraints: List[str]=[]


# response schema
class ValidationResponse(BaseModel):
    final_score: float
    verdict: str
    confidence_level: str
    explanation: dict



# api endpoint
@app.post("/validate",response_model=ValidationResponse)
def validate_startup(idea: StartupIdeaRequest):
    # this endpoint accepts a startup idea as input, converts it into internal startup idea model.. runs full validation pipeline and returns structured evaluation results
    
    try:
        # convertiing request (pydantic model to dict) -> internal domain model
        startup=StartupIdea(**idea.dict())
        result=run_full_validation(startup)  # running full ai validation pipeline..

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

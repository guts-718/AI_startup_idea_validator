from typing import Dict, Any, List
from crewai import Agent
from pydantic import ValidationError
from models.startup_idea import StartupIdea

class ExtractionResult:
    def __init__(self, success:bool, data: StartupIdea | None = None, error: str | None=None, missing_required:List[str] | None=None, inferred_fields: List[str] | None = None, extraction_confidence: str| None=None):
        self.success = success
        self.data=data
        self.error=error
        self.missing_required=missing_required or []
        self.inferred_fields=inferred_fields or []
        self.extraction_confidence = extraction_confidence

    

def build_extraction_agent(llm):
    return Agent(
        role="Startup idea extraction agent",
        goal=(
            "Extract structured startup information from raw user input. Do not invent facts. Infer only when strongly implied. Mark inferred fields explicitly."
        ),
        backstory=(
            "You are a strict information extractor."
            "You care more about correctness and uncertainty then optimism. "
        ),
        llm=llm,
    )


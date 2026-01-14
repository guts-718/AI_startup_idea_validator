from crewai import Task
from pydantic_core import ValidationError
from models.startup_idea import StartupIdea

from agents.extraction_logic import (
    validate_required_fields,
    compute_confidence,
    NON_INFERABLE_FIELDS
)

from agents.extraction_agent import ExtractionResult

def run_extraction(agent, raw_text: str)-> ExtractionResult:
    task = Task(
        description=(
            "Extract startup idea fields into JSON matching the StartupIdea schema. "
            "If a value is strongly implied, infer it and list it under inferred_fields. "
            "If unknown, use null."
        ),
        expected_output="Valid JSON compatible with StartupIdea",
        agent=agent,
    )

    result= agent.execute_taks(task, context=raw_text)

    try:
        parsed= StartupIdea.model_validate_json(result)
    except ValidationError as e:
        return ExtractionResult(
            success=False,
            error="Schema validation failure",
        )
    

    missing_required=validate_required_fields(parsed.model_dump())

    if missing_required:
        return ExtractionResult(
            success=False,
            error="missing required field",
            missing_required=missing_required,
        
        )

    
    inferred_fields=parsed.inferred_fields or []
    inferred_fields = [
        f for f in inferred_fields if f not in NON_INFERABLE_FIELDS
    ]

    missing_optional=sum(
        1 for k,v in parsed.model_dump().items()
        if v is None and k not in ["problem","solution","geography"]
    )

    confidence=compute_confidence(missing_optional,len(inferred_fields))

    return ExtractionResult(
        success=True,
        data=parsed,
        inferred_fields=inferred_fields,
        extraction_confidence=confidence,
    )

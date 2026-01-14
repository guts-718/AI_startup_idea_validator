from typing import Any, Dict, List


REQUIRED_FIELDS=["problem","solution","geography"]
NON_INFERABLE_FIELDS={"founder_expertise","monetization_model"}


def validate_required_fields(parsed: Dict[str,Any])-> List[str]:
    missing=[]
    for field in REQUIRED_FIELDS:
        if not parsed.get(field):
            missing.append(field)
    return missing



def compute_confidence(missing_optional:int, inferred_count:int)->str:
    if missing_optional==0 and inferred_count == 0:
        return "high"
    if missing_optional <= 2:
        return "medium"
    return "low"
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class CostModelResult:
    monthly_fixed_cost_usd: float
    monthly_variable_cost_usd: float
    total_monthly_cost_usd: float
    cost_breakdown: Dict[str, float]
    assumptions: Dict[str, str]
    confidence: str


def cost_model_tool(solution:str, industry: Optional[str], geography: str, expected_users: int = 1000, cloud_provider: str = "generic") -> CostModelResult:
    """
    Estimate startup operating costs using transparent heuristic, No paid APIs and deterministic
    """

    base_infra_cost = 200.0 # assuming for server, storage and monitoring

    industry_key = industry.lower() if industry else ""
    industry_multiplier={
        "fintech":1.4,
        "healthtech":1.5,
        "saas":1.2,
        "edtech":1.1,
    }.get(industry_key,1.0)

    geography_key= geography.lower() if geography else ""
    geo_multiplier={
        "india":0.6,
        "usa":1.0,
        "europe":1.1,
        "global":1.2,
    }.get(geography_key,1.0)



    complexity_keywords = ["real-time", "analytics", "ai", "ml", "streaming"]
    complexity_cost = 0.0
    for kw in complexity_keywords:
        if kw in solution.lower():
            complexity_cost += 100.0


    # ---- variable costs ----
    cost_per_user = 0.02  # infra + support proxy
    variable_cost = expected_users * cost_per_user

    fixed_cost = (base_infra_cost + complexity_cost) * industry_multiplier * geo_multiplier
    total_cost = fixed_cost + variable_cost

    confidence = "medium"
    if industry is None:
        confidence = "low"

    return CostModelResult(
        monthly_fixed_cost_usd=round(fixed_cost, 2),
        monthly_variable_cost_usd=round(variable_cost, 2),
        total_monthly_cost_usd=round(total_cost, 2),
        cost_breakdown={
            "base_infrastructure": base_infra_cost,
            "complexity_addition": complexity_cost,
            "industry_multiplier": industry_multiplier,
            "geography_multiplier": geo_multiplier,
            "variable_user_cost": variable_cost,
        },
        assumptions={
            "expected_users": str(expected_users),
            "cloud_provider": cloud_provider,
            "cost_per_user": "0.02 USD",
        },
        confidence=confidence,
    )
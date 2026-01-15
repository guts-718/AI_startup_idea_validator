from dataclasses import dataclass
from typing import Optional
from ai_startup_idea_validator.models.startup_idea import StartupIdea
from ai_startup_idea_validator.tools.market_size_tool import market_size_tool, MarketSizeResult
from ai_startup_idea_validator.tools.competitor_discovery_tool import (
    competitor_discovery_tool,
    CompetitorDiscoveryResult
)
from ai_startup_idea_validator.tools.demand_signal_tool import demand_signal_tool, DemandSignalResult
from ai_startup_idea_validator.tools.cost_model_tool import cost_model_tool, CostModelResult
from ai_startup_idea_validator.tools.semantic_matcher import semantic_matcher






@dataclass
class EvidenceBundle:
    market_size: MarketSizeResult
    competitors: CompetitorDiscoveryResult
    demand: DemandSignalResult
    cost_model: CostModelResult


def run_evidence_phase(startup: StartupIdea) -> EvidenceBundle:
    """
    Runs all deterministic + hybrid tools in a fixed order.
    Here there is no LLm reasoning.
    """

    market_size=market_size_tool(
        geography=startup.geography,
        industry=startup.industry,
        target_user=startup.target_user,
    )
    competitors = competitor_discovery_tool(
        problem=startup.problem,
        solution=startup.solution,
        geography=startup.geography,
        industry=startup.industry,
    )

    demand = demand_signal_tool(
        problem_text=startup.problem,
        solution_text=startup.solution,
        semantic_matcher=semantic_matcher,
    )

    cost_model = cost_model_tool(
        solution=startup.solution,
        industry=startup.industry,
        geography=startup.geography,
    )


    return EvidenceBundle(
    market_size=market_size,
    competitors=competitors,
    demand=demand,
    cost_model=cost_model,
    )

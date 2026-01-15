from token import OP
from typing import Optional, List
from dataclasses import dataclass
import json
import os

@dataclass
class MarketSizeResult:
    tam_usd: float
    sam_usd: float
    som_usd: float
    assumption: dict
    confidence: str
    enriched: bool
    data_source_used:List[str]



def load_population_data():
    path="data/population.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}



def load_industry_multipliers():
    path="data/industry_multipliers.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}



#### MAIN TOOL
def market_size_tool(
    geography: str,
    industry: Optional[str],
    target_user: Optional[str],
    avg_annual_price_usd: float = 100.0,
    adoption_rate : float = 0.05,
    reachable_market_fraction: float=0.2 )-> MarketSizeResult:
    
    data_sources=[]
    enriched=False
    

     # Core heuristic fallback
    population_fallback = {
        "india": 1_400_000_000,
        "usa": 330_000_000,
        "europe": 450_000_000,
        "global": 8_000_000_000,
    }

    population = population_fallback.get(
        geography.lower(), 100_000_000
    )

    population_data = load_population_data()
    if geography.lower() in population_data:
        population=population_data[geography.lower()]
        data_sources.append("world_back_population")
        enriched=True

    
    industry_multiplier=1.0
    industry_data=load_industry_multipliers()
    if industry and industry.lower() in industry_data:
        industry_multiplier = industry_data[industry.lower()]
        data_sources.append("industry_size_proxy")
        enriched=True

    
    tam = population * avg_annual_price_usd * industry_multiplier
    sam = tam * adoption_rate
    som = sam * reachable_market_fraction

    confidence="medium"
    if not enriched or industry is None or target_user is None:
        confidence="low"
    
    return MarketSizeResult(
        tam_usd=round(tam,2),
        sam_usd=round(sam,2),
        som_usd=round(som,2),
        assumption={
            "population": population,
            "avg_price": avg_annual_price_usd,
            "adoption_rate": adoption_rate,
            "reachable_fraction": reachable_market_fraction,
            "industry_multiplier": industry_multiplier,
        },
        confidence=confidence,
        enriched=enriched,
        data_source_used=data_sources,
    )

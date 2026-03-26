from token import OP                    
from typing import Optional, List       # For type hints
from dataclasses import dataclass       # For structured data objects
import json
import os


# Output Data Structure - Stores results of market size calculation
@dataclass
class MarketSizeResult:
    tam_usd: float                      # Total Addressable Market
    sam_usd: float                      # Serviceable Available Market
    som_usd: float                      # Serviceable Obtainable Market
    assumption: dict                    # Assumptions used in calculation
    confidence: str                     # Confidence level (low/medium/high)
    enriched: bool                      # Whether external data improved result
    data_source_used: List[str]         # Sources used for enrichment


#  Load Population Data 
def load_population_data():
    """
    Loads population data from JSON file (if available).
    """
    path = "data/population.json"

    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)

    # fallback: return empty dict if file doesn't exist
    return {}


# Load Industry Multipliers 
def load_industry_multipliers():
    """
    Loads industry multipliers (used to scale TAM).
    """
    path = "data/industry_multipliers.json"

    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)

    # Fallback: return empty dict if file doesn't exist
    return {}


# MAIN TOOL 
def market_size_tool(
    geography: str,
    industry: Optional[str],
    target_user: Optional[str],
    avg_annual_price_usd: float = 100.0,
    adoption_rate: float = 0.05,
    reachable_market_fraction: float = 0.2
) -> MarketSizeResult:
    """
    Estimates TAM, SAM, SOM using heuristics + optional enrichment data.
    """

    # Track which data sources were used
    data_sources = []

    # Whether external data improved estimation
    enriched = False

    # Fallback Population - Used if no external population data is available
    population_fallback = {
        "india": 1_400_000_000,
        "usa": 330_000_000,
        "europe": 450_000_000,
        "global": 8_000_000_000,
    }

    # Get population from fallback (default = 100M if unknown geography)
    population = population_fallback.get(
        geography.lower(), 100_000_000
    )

    #  Enrich with Population Data 
    population_data = load_population_data()

    # If more accurate data exists → override fallback
    if geography.lower() in population_data:
        population = population_data[geography.lower()]
        data_sources.append("world_bank_population")  # (typo fixed)
        enriched = True


    # Industry Multiplier - Adjusts market size based on industry scale
    industry_multiplier = 1.0

    industry_data = load_industry_multipliers()

    if industry and industry.lower() in industry_data:
        industry_multiplier = industry_data[industry.lower()]
        data_sources.append("industry_size_proxy")
        enriched = True


    # Market Size Calculations 
    # TAM = total possible revenue if everyone buys
    tam = population * avg_annual_price_usd * industry_multiplier

    # SAM = portion of TAM likely to adopt
    sam = tam * adoption_rate

    # SOM = portion of SAM you can realistically capture
    som = sam * reachable_market_fraction


    # Confidence Estimation - Default confidence
    confidence = "medium"

    # Lower confidence if:
    # - no enrichment data used
    # - missing industry or target user
    if not enriched or industry is None or target_user is None:
        confidence = "low"


    # Return Result
    return MarketSizeResult(
        tam_usd=round(tam, 2),
        sam_usd=round(sam, 2),
        som_usd=round(som, 2),

        # Store assumptions for transparency/debugging
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
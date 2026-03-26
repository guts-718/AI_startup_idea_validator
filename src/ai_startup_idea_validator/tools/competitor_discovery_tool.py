from typing import List, Optional
from dataclasses import dataclass
import json
import os
import re


# Data Structures

# Represents a single competitor
@dataclass
class Competitor:
    name: str            # Company name
    positioning: str     # How the company positions itself
    source: str          # source of this data


# Represents the final result of competitor discovery
@dataclass
class CompetitorDiscoveryResult:
    competitors: List[Competitor]   # List of matched competitors
    confidence: str                 # Confidence level (low/medium/high)
    data_sources_used: List[str]    # Which datasets were used


# Helper Functions

def load_known_competitors():
    """
    Loads competitor dataset from local JSON file.
    """
    path = "data/known_competitors.json"

    # If file exists -> load it
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)

    # Fallback -> return empty list if no dataset found
    return []


def normalize(text: str) -> str:
    """
    Normalizes text by:
    - converting to lowercase
    - removing special characters
    """
    return re.sub(r"[^a-z0-9 ]", "", text.lower())


# Main Tool

def competitor_discovery_tool(
    problem: str,
    solution: str,
    geography: str,
    industry: Optional[str] = None,
) -> CompetitorDiscoveryResult:

    # Load dataset of known competitors
    known_competitors = load_known_competitors()

    # Store matched competitors
    results: List[Competitor] = []

    # Track data sources used
    sources = []

    # Keyword Extraction - Combine problem + solution → extract keywords
    key_terms = normalize(problem + " " + solution).split()


    #  Matching Logic - Iterate over all known competitors
    for entry in known_competitors:

        # Combine competitor's fields into one searchable string
        haystack = normalize(
            f"{entry.get('problem','')} {entry.get('solution','')} {entry.get('industry','')}"
        )

        # If any keyword from user input appears in competitor data → match
        if any(term in haystack for term in key_terms):

            # Add competitor to results
            results.append(
                Competitor(
                    name=entry["name"],
                    positioning=entry.get("positioning", "Not specified"),
                    source="offline_dataset",   # indicates local dataset
                )
            )


    # Data Source Tracking 
    if results:
        sources.append("known_competitors_dataset")


    # Confidence Estimation 
    # If matches found -> medium confidence
    # If none -> low confidence
    confidence = "medium" if results else "low"


    # Return Result 
    return CompetitorDiscoveryResult(
        competitors=results,
        confidence=confidence,
        data_sources_used=sources,
    )
from typing import List, Optional
from dataclasses import dataclass
import json
import os
import re


@dataclass
class Competitor:
    name: str
    positioning: str
    source: str


@dataclass
class CompetitorDiscoveryResult:
    competitors: List[Competitor]
    confidence: str
    data_sources_used: List[str]


# ---- helpers ----

def load_known_competitors():
    path = "data/known_competitors.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower())


# ---- main tool ----

def competitor_discovery_tool(
    problem: str,
    solution: str,
    geography: str,
    industry: Optional[str] = None,
) -> CompetitorDiscoveryResult:

    known_competitors = load_known_competitors()
    results: List[Competitor] = []
    sources = []

    key_terms = normalize(problem + " " + solution).split()

    for entry in known_competitors:
        haystack = normalize(
            f"{entry.get('problem','')} {entry.get('solution','')} {entry.get('industry','')}"
        )

        if any(term in haystack for term in key_terms):
            results.append(
                Competitor(
                    name=entry["name"],
                    positioning=entry.get("positioning", "Not specified"),
                    source="offline_dataset",
                )
            )

    if results:
        sources.append("known_competitors_dataset")

    confidence = "medium" if results else "low"

    return CompetitorDiscoveryResult(
        competitors=results,
        confidence=confidence,
        data_sources_used=sources,
    )

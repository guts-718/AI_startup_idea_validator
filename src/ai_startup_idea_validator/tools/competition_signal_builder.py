import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

from ai_startup_idea_validator.models.startup_idea import StartupIdea

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  
# points to src/ai_startup_idea_validator/

KNOWN_COMPETITORS_PATH = BASE_DIR / "data" / "known_competitors.json"


@dataclass
class CompetitionSignals:
    direct_competitor_count: int
    dominant_incumbents_present: bool
    highest_dominance_level: str
    common_moat_sources: List[str]
    common_entry_barriers: List[str]
    competition_style: str
    competition_pressure_score: float  # 0–10


DOMINANCE_WEIGHT = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "extreme": 4,
}

STYLE_PENALTY = {
    "fragmented": 1,
    "oligopoly": 2,
    "winner_takes_most": 3,
    "winner_takes_all": 4,
}


def load_known_competitors() -> List[Dict]:
    with open(KNOWN_COMPETITORS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_competition_signals(startup: StartupIdea) -> CompetitionSignals:
    competitors = load_known_competitors()

    relevant = [
        c for c in competitors
        if c["primary_category"] == startup.industry
        or startup.industry in c.get("secondary_categories", [])
    ]

    direct_count = len(relevant)

    dominance_levels = [c["dominance_level"] for c in relevant]
    highest_dominance = (
        max(dominance_levels, key=lambda d: DOMINANCE_WEIGHT[d])
        if dominance_levels else "low"
    )

    dominant_present = highest_dominance in {"high", "extreme"}

    moat_counter: Dict[str, int] = {}
    barrier_counter: Dict[str, int] = {}
    style_counter: Dict[str, int] = {}

    for c in relevant:
        for m in c.get("moat_sources", []):
            moat_counter[m] = moat_counter.get(m, 0) + 1
        for b in c.get("entry_barriers", []):
            barrier_counter[b] = barrier_counter.get(b, 0) + 1
        style = c.get("competition_style")
        if style:
            style_counter[style] = style_counter.get(style, 0) + 1

    common_moats = sorted(
        moat_counter, key=moat_counter.get, reverse=True
    )[:3]

    common_barriers = sorted(
        barrier_counter, key=barrier_counter.get, reverse=True
    )[:3]

    dominant_style = (
        max(style_counter, key=style_counter.get)
        if style_counter else "fragmented"
    )

    # ---- pressure score (structural, not arbitrary) ----
    pressure = 0.0

    pressure += min(direct_count / 20, 3)                 # density
    pressure += DOMINANCE_WEIGHT[highest_dominance]       # dominance
    pressure += STYLE_PENALTY[dominant_style]             # structure
    pressure += min(len(common_barriers), 3)              # entry friction

    pressure = min(10.0, round(pressure, 2))

    return CompetitionSignals(
        direct_competitor_count=direct_count,
        dominant_incumbents_present=dominant_present,
        highest_dominance_level=highest_dominance,
        common_moat_sources=common_moats,
        common_entry_barriers=common_barriers,
        competition_style=dominant_style,
        competition_pressure_score=pressure,
    )

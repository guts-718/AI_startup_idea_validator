from openai import OpenAI

from ai_startup_idea_validator.models.startup_idea import StartupIdea
from ai_startup_idea_validator.evidence.evidence_runner import run_evidence_phase
from ai_startup_idea_validator.tools.competition_signal_builder import (
    build_competition_signals,
)

from ai_startup_idea_validator.agents.market_demand_agent import (
    build_market_demand_agent,
    run_market_demand_analysis,
)
from ai_startup_idea_validator.agents.competition_moat_agent import (
    build_competition_moat_agent,
    run_competition_moat_analysis,
)
from ai_startup_idea_validator.agents.economics_monetization_agent import (
    build_economics_monetization_agent,
    run_economics_monetization_analysis,
)
from ai_startup_idea_validator.agents.execution_risk_agent import (
    build_execution_risk_agent,
    run_execution_risk_analysis,
)
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()
import os
print(os.getenv("OPENAI_API_KEY"))

def main():
    LLM_MODEL = "gpt-4o-mini"

    print("\n================ STARTUP IDEA VALIDATION ================\n")

    # --- 1. Input (simulating Extraction output) ---
    startup = StartupIdea(
        problem="Small retail businesses struggle to manage inventory across online and offline channels",
        solution="A SaaS platform that synchronizes inventory and sales data in real time",
        geography="India",
        target_user="Small retail business owners",
        industry="saas",
        differentiation="Focus on simplicity and affordable pricing for emerging markets",
        monetization_model="Monthly subscription",
        founder_expertise="5 years experience running retail operations",
        customer_acquisition="Direct sales and partnerships with POS vendors",
        regulatory_constraints=[],
        constraints=[],
    )

    # --- 2. Evidence Phase ---
    print(">>> Running evidence phase...\n")
    evidence = run_evidence_phase(startup)

    # --- 3. Competition Signals (Python-only) ---
    competition_signals = build_competition_signals(startup)

    # --- 4. Build LLM client ---
    client = OpenAI()

    # --- 5. Build agents ---
    market_agent = build_market_demand_agent(LLM_MODEL)
    competition_agent = build_competition_moat_agent(LLM_MODEL)
    economics_agent = build_economics_monetization_agent(LLM_MODEL)
    execution_agent = build_execution_risk_agent(LLM_MODEL)

    # --- 6. Run analysis agents ---
    print(">>> Running Market & Demand Analysis...\n")
    market_analysis = run_market_demand_analysis(
        market_agent,
        startup,
        evidence.market_size,
        evidence.demand,
    )

    print(">>> Running Competition & Moat Analysis...\n")
    competition_analysis = run_competition_moat_analysis(
        competition_agent,
        startup,
        competition_signals,
    )

    print(">>> Running Economics & Monetization Analysis...\n")
    economics_analysis = run_economics_monetization_analysis(
        economics_agent,
        startup,
        evidence.market_size,
        evidence.cost_model,
    )

    print(">>> Running Execution & Risk Analysis...\n")
    execution_analysis = run_execution_risk_analysis(
        execution_agent,
        startup,
    )

    # --- 7. Print results ---
    print("\n================ ANALYSIS RESULTS ================\n")

    print("Market & Demand:")
    print(market_analysis, "\n")

    print("Competition & Moat:")
    print(competition_analysis, "\n")

    print("Economics & Monetization:")
    print(economics_analysis, "\n")

    print("Execution & Risk:")
    print(execution_analysis, "\n")

    print("=================================================\n")


if __name__ == "__main__":
    main()

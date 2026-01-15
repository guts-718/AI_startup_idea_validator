
from ai_startup_idea_validator.models.startup_idea import StartupIdea
from ai_startup_idea_validator.evidence.evidence_runner import run_evidence_phase


def main():
    # --- mock extracted startup idea ---
    startup = StartupIdea(
        problem="Small businesses manually track expenses using spreadsheets",
        solution="A simple SaaS tool that automates expense tracking and reporting",
        geography="India",
        target_user="Small business owners",
        industry="saas",
        differentiation="Simple UI and low pricing",
        monetization_model="Monthly subscription",
        founder_expertise=None,
    )

    print("\n=== RUNNING EVIDENCE PHASE ===\n")

    evidence = run_evidence_phase(startup)

    print("---- Market Size ----")
    print(evidence.market_size)

    print("\n---- Competitors ----")
    print(evidence.competitors)

    print("\n---- Demand Signals ----")
    print(evidence.demand)

    print("\n---- Cost Model ----")
    print(evidence.cost_model)


if __name__ == "__main__":
    main()

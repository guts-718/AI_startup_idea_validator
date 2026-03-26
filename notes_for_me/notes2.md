## Overview

This project is a production-style, multi-agent system designed to
evaluate startup ideas using a combination of structured data
processing, deterministic logic, and LLM-based reasoning.

Unlike typical LLM wrappers, this system separates reasoning, evidence,
and decision-making into distinct layers. It aims to simulate how
real-world investment or product decisions are made.

------------------------------------------------------------------------

## Key Features

-   Multi-agent architecture with specialized roles
-   Evidence-driven evaluation (not purely LLM-based)
-   Deterministic scoring engine
-   Adversarial debate (FOR vs AGAINST)
-   Judge-based confidence adjustment
-   Explainable outputs for founders
-   FastAPI backend + Gradio frontend
-   Extensible and modular design

------------------------------------------------------------------------

## System Architecture

### 1. Input Layer

User provides a structured startup idea including: - problem -
solution - geography - industry - optional fields (target user,
differentiation, etc.)

Validated using a Pydantic schema.

------------------------------------------------------------------------

### 2. Evidence Layer (Python Tools)

This layer extracts structured signals without using LLMs.

Components: - Market Size Tool (TAM, SAM, SOM estimation) - Demand
Signal Tool (heuristic + semantic signals) - Cost Model Tool
(approximate cost structure) - Competition Signal Builder

All outputs are deterministic and reproducible.

------------------------------------------------------------------------

### 3. Competition Intelligence

A curated dataset of competitors is used.

Python computes: - competition density - dominance level - moat
signals - entry barriers

Only compressed signals are passed to LLMs.

------------------------------------------------------------------------

### 4. Analysis Agents (LLM Layer)

Four specialized agents:

1.  Market & Demand Agent\
2.  Competition & Moat Agent\
3.  Economics & Monetization Agent\
4.  Execution & Risk Agent

Each agent: - receives structured inputs - produces: - score (0--10) -
strengths - concerns - rationale

Strict JSON output is enforced.

------------------------------------------------------------------------

### 5. Scoring Engine (Deterministic)

-   Converts scores to 0--100 scale
-   Applies weighted aggregation:
    -   Market: 30%
    -   Competition: 25%
    -   Economics: 25%
    -   Execution: 20%
-   Applies structural caps (e.g., poor economics limits score)

Produces a base score.

------------------------------------------------------------------------

### 6. Debate Layer

Two adversarial agents:

FOR Agent: - argues why idea should succeed - assumes competent
execution

AGAINST Agent: - argues why idea will fail - attacks assumptions

Both use: - same model - same inputs - different constraints

------------------------------------------------------------------------

### 7. Judge Layer

The judge: - evaluates debate quality - identifies: - unresolved risks -
overlooked strengths - outputs a bounded confidence_shift

Does NOT rescore the idea.

------------------------------------------------------------------------

### 8. Final Aggregation

Final score is computed as:

final_score = base_score × (1 + confidence_shift)

Also produces: - verdict (Proceed / Caution / Reject) - key positives -
key negatives - confidence level

------------------------------------------------------------------------

### 9. Explanation Layer

An LLM generates a user-facing explanation: - summary of decision - key
reasons - key risks - actionable next steps

------------------------------------------------------------------------

## System Flow

Input\
→ Evidence Layer\
→ Analysis Agents\
→ Scoring Engine\
→ Debate Layer\
→ Judge\
→ Final Decision\
→ Explanation

------------------------------------------------------------------------

## Interfaces

### FastAPI Backend

-   Endpoint: POST /validate
-   Accepts JSON input
-   Returns structured evaluation output

Run:

    uvicorn ai_startup_idea_validator.api.main:app --reload

------------------------------------------------------------------------

### Gradio Frontend

-   User-friendly UI
-   Sends requests to FastAPI
-   Displays results

Run:

    python ui/gradio_app.py

------------------------------------------------------------------------

## Project Structure

    ai_startup_idea_validator/
    │
    ├── pipeline/
    ├── agents/
    ├── tools/
    ├── scoring/
    ├── api/
    ├── ui/
    ├── models/
    ├── data/

------------------------------------------------------------------------

## Design Principles

-   Separation of concerns
-   Deterministic core logic
-   LLMs used only for reasoning
-   No reliance on external paid APIs
-   Explainability and transparency
-   Modular and extensible system

------------------------------------------------------------------------

## Output

-   Final Score (0--100)
-   Verdict
-   Strengths and Concerns
-   Risks and Opportunities
-   Recommended Next Steps
-   Confidence Level

------------------------------------------------------------------------

## Future Improvements

-   Persistent storage of runs per user
-   Authentication system
-   Improved competitor dataset
-   ML-based calibration
-   Deployment (Docker / cloud)
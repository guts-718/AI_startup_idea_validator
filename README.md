# AI Startup Idea Validator

## Overview

This project is a production-style, multi-agent system for evaluating
startup ideas. It combines deterministic computation, structured
reasoning, and adversarial analysis to produce reliable and explainable
decisions.

The system is designed to mimic real-world decision-making processes
such as investment committees or product evaluation pipelines.

------------------------------------------------------------------------

## High-Level Architecture

The system follows a layered architecture:

Input → Evidence → Analysis → Scoring → Debate → Judge → Final
Aggregation → Explanation

Each layer has a clearly defined responsibility and does not leak
concerns into others.

------------------------------------------------------------------------

## 1. Input Layer

The input is a structured `StartupIdea` object.

Fields include: - problem - solution - geography - industry - optional
metadata (target_user, differentiation, etc.)

Validation is handled using Pydantic.

------------------------------------------------------------------------

## 2. Evidence Layer (Deterministic)

This layer uses Python tools (no LLMs) to extract structured signals.

### Tools:

#### Market Size Tool

Estimates: - TAM (Total Addressable Market) - SAM (Serviceable Available
Market) - SOM (Serviceable Obtainable Market)

#### Demand Signal Tool

Produces: - demand_score (0--10) - supporting signals

#### Cost Model Tool

Estimates: - fixed costs - variable costs - operational assumptions

#### Competition Signal Builder

Uses a dataset of competitors to compute: - direct competitor count -
dominance levels - moat sources - entry barriers

All outputs are deterministic and reproducible.

------------------------------------------------------------------------

## 3. Analysis Agents (LLM-Based)

There are four independent agents:

### 3.1 Market & Demand Agent

Evaluates: - market size validity - demand strength - signal confidence

Output: - score (0--10) - strengths - concerns - rationale

------------------------------------------------------------------------

### 3.2 Competition & Moat Agent

Uses precomputed signals: - competition density - dominance - moat
structures

Focus: - defensibility - market pressure

------------------------------------------------------------------------

### 3.3 Economics & Monetization Agent

Evaluates: - revenue feasibility - cost structure - monetization clarity

------------------------------------------------------------------------

### 3.4 Execution & Risk Agent

Evaluates: - founder-market fit - operational complexity - go-to-market
strategy - execution risks

------------------------------------------------------------------------

## Agent Interaction Model

Agents do NOT interact directly.

Instead: - All agents receive structured inputs - Each produces
independent outputs - Outputs are aggregated later

This avoids: - bias propagation - cascading hallucinations

------------------------------------------------------------------------

## 4. Scoring Engine (Deterministic)

Each agent produces a score in range \[0, 10\].

### Normalization

All scores are converted to \[0, 100\]:

score_normalized = score × 10

------------------------------------------------------------------------

### Weighted Aggregation

Weights:

-   Market & Demand: 30%
-   Competition & Moat: 25%
-   Economics & Monetization: 25%
-   Execution & Risk: 20%

Formula:

base_score = (market × 10 × 0.30) + (competition × 10 × 0.25) +
(economics × 10 × 0.25) + (execution × 10 × 0.20)

------------------------------------------------------------------------

### Structural Caps

Certain failures cap the score:

-   Market score ≤ 3 → max 45
-   Economics score ≤ 3 → max 50
-   Competition score ≤ 3 → max 55

These enforce real-world constraints.

------------------------------------------------------------------------

## 5. Debate Layer

Two adversarial agents operate on the same analysis:

### FOR Agent

-   Argues why idea should succeed
-   Assumes strong execution
-   Maximizes upside

### AGAINST Agent

-   Argues why idea will fail
-   Assumes adverse conditions
-   Attacks assumptions

Important: - Same model - Same input - Different constraints

No new data is introduced.

------------------------------------------------------------------------

## 6. Judge Layer

The judge evaluates the debate.

Outputs: - debate_winner - confidence_shift (range: -0.25 to +0.10) -
unresolved risks - overlooked strengths

The judge does NOT: - rescore the idea - introduce new facts

------------------------------------------------------------------------

## 7. Final Aggregation

The final score is adjusted:

final_score = base_score × (1 + confidence_shift)

Example:

base_score = 60\
confidence_shift = -0.20

final_score = 60 × 0.80 = 48

------------------------------------------------------------------------

## 8. Verdict Mapping

-   80--100 → STRONG PROCEED
-   65--79 → PROCEED WITH CAUTION
-   45--64 → HIGH RISK / ITERATE
-   \<45 → DO NOT PROCEED

------------------------------------------------------------------------

## 9. Explanation Agent

A final LLM generates a structured explanation:

-   summary
-   key reasons
-   risks
-   next steps

This layer does NOT affect the score.

------------------------------------------------------------------------

## 10. API Layer (FastAPI)

Endpoint: POST /validate

Flow: - Receive request - Convert to StartupIdea - Call
run_full_validation() - Return structured result

------------------------------------------------------------------------

## 11. UI Layer (Gradio)

Gradio acts as frontend: - collects user input - sends request to
FastAPI - displays results

No logic exists in UI.

------------------------------------------------------------------------

## 12. Logging / Observability

LLM calls are logged: - request prompts - responses

This enables: - debugging - explainability - traceability

------------------------------------------------------------------------

## Design Principles

-   Separation of concerns
-   Deterministic core logic
-   LLMs used only for reasoning
-   No hidden state
-   Explainable outputs
-   Adversarial validation

------------------------------------------------------------------------

## Project Structure

ai_startup_idea_validator/ │ ├── pipeline/ ├── agents/ ├── tools/ ├──
scoring/ ├── api/ ├── ui/ ├── models/ ├── data/

------------------------------------------------------------------------

## Summary

This system is not a simple LLM wrapper.

It is a structured decision engine that: - combines deterministic
computation with LLM reasoning - uses adversarial validation - produces
explainable and consistent outputs

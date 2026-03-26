#!/usr/bin/env python
# Shebang → allows running this script directly from terminal

import sys                 # For command-line arguments (sys.argv)
import warnings            # For controlling warning messages

from datetime import datetime  # To get current year dynamically

# Import your CrewAI pipeline
from ai_startup_idea_validator.crew import AiStartupIdeaValidator


# Warning Suppression - Ignore SyntaxWarnings from pysbd (text segmentation lib)
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


# Run Crew Normally 
def run():
    """
    Runs the crew with default test inputs.
    """

    # Inputs passed to agents/tasks (used in prompts/templates)
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }

    try:
        # Create crew instance → build pipeline → execute it
        AiStartupIdeaValidator().crew().kickoff(inputs=inputs)

    except Exception as e:
        # Wrap and rethrow error for better debugging
        raise Exception(f"An error occurred while running the crew: {e}")


#  Train Crew 
def train():
    """
    Trains the crew for multiple iterations.
    Used for improving outputs / evaluation loops.
    """

    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }

    try:
        # sys.argv[1] → number of iterations
        # sys.argv[2] → output file name
        AiStartupIdeaValidator().crew().train(
            n_iterations=int(sys.argv[1]),
            filename=sys.argv[2],
            inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


# Replay Execution -
def replay():
    """
    Replays execution from a specific task ID.
    Useful for debugging workflows.
    """

    try:
        # sys.argv[1] → task ID to replay from
        AiStartupIdeaValidator().crew().replay(
            task_id=sys.argv[1]
        )

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


# Test Crew 
def test():
    """
    Runs test mode (evaluation + benchmarking).
    """

    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        # sys.argv[1] → number of test iterations
        # sys.argv[2] → evaluation LLM (e.g., gpt-4)
        AiStartupIdeaValidator().crew().test(
            n_iterations=int(sys.argv[1]),
            eval_llm=sys.argv[2],
            inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


#  Run with Trigger Payload 
def run_with_trigger():
    """
    Runs the crew using a JSON trigger payload (external input).
    Useful for integrations (webhooks, APIs, etc.)
    """

    import json

    # Ensure payload is passed via command line
    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        # Parse JSON string → Python dict
        trigger_payload = json.loads(sys.argv[1])

    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    # Inputs passed to crew
    inputs = {
        "crewai_trigger_payload": trigger_payload,  # main external data
        "topic": "",                                # unused placeholder
        "current_year": ""                          # unused placeholder
    }

    try:
        # Run crew with external payload
        result = AiStartupIdeaValidator().crew().kickoff(inputs=inputs)
        return result

    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
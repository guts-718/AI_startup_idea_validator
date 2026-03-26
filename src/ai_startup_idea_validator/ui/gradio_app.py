import gradio as gr       
import requests           


#  Backend API Endpoint -- FastAPI server endpoint
API_URL = "http://127.0.0.1:8000/validate"


# core Function (UI → API → UI) 
def validate_startup(
    problem, solution, geography, industry,
    target_user, differentiation, monetization_model, founder_expertise,
):
    """
    Takes user input from UI, sends it to backend,
    and formats the response for display in Gradio.
    """

    # Build request payload (matches FastAPI schema)
    payload = {
        "problem": problem,
        "solution": solution,
        "geography": geography,
        "industry": industry,
        "target_user": target_user,
        "differentiation": differentiation,
        "monetization_model": monetization_model,
        "founder_expertise": founder_expertise,
    }

    # Send POST request to backend
    response = requests.post(API_URL, json=payload, timeout=300)

    # Raise error if request failed (important for debugging)
    response.raise_for_status()

    # Parse JSON response
    data = response.json()

    # Extract explanation section
    explanation = data["explanation"]

    # Return values mapped to UI output components (order matters!)
    return (
        data["final_score"],   # numeric score
        data["verdict"],       # verdict string
        explanation["summary"],

        # Convert lists → bullet point strings for display
        "\n".join(f"- {x}" for x in explanation["key_reasons_for_score"]),
        "\n".join(f"- {x}" for x in explanation["key_risks"]),
        "\n".join(f"- {x}" for x in explanation["recommended_next_steps"]),

        data["confidence_level"],
    )


#  Gradio UI Layout - Blocks = container for building custom UI
with gr.Blocks(title="AI Startup Idea Validator") as demo:

    # Title & description
    gr.Markdown("# AI Startup Idea Validator")
    gr.Markdown(
        "Enter your startup idea details below."
        "The system evaluates market, competition, economics, execution, and the idea before giving a verdict."
    )

    # input section..

    # First row: Problem & Solution side by side
    with gr.Row():
        problem = gr.Textbox(label="Problem", lines=3)
        solution = gr.Textbox(label="Solution", lines=3)

    # Second row: Geography + Industry dropdown
    with gr.Row():
        geography = gr.Textbox(label="Geography")

        industry = gr.Dropdown(
            choices=[
                "saas",
                "fintech",
                "healthtech",
                "edtech",
                "ecommerce",
                "marketplace",
                "devtools",
                "consumer",
                "enterprise_software",
                "hardware",
                "energy",
                "other",
            ],
            label="Industry",
        )

    # Additional input fields
    target_user = gr.Textbox(label="Target User")
    differentiation = gr.Textbox(label="Differentiation")
    monetization_model = gr.Textbox(label="Monetization Model")
    founder_expertise = gr.Textbox(label="Founder Expertise")

    # Submit button
    submit = gr.Button("Validate Idea")

    # ------------------- Output Section -------------------
    gr.Markdown("## Evaluation Result")

    final_score = gr.Number(label="Final Score")
    verdict = gr.Textbox(label="Verdict")
    summary = gr.Textbox(label="Summary", lines=3)

    reasons = gr.Textbox(label="Key Reasons", lines=6)
    risks = gr.Textbox(label="Key Risks", lines=6)
    next_steps = gr.Textbox(label="Recommended Next Steps", lines=6)
    confidence = gr.Textbox(label="Confidence Level")

    # ------------------- Button Action -------------------
    # When user clicks submit:
    submit.click(
        validate_startup,   # function to run

        # Inputs passed in this exact order
        inputs=[
            problem,
            solution,
            geography,
            industry,
            target_user,
            differentiation,
            monetization_model,
            founder_expertise
        ],

        # Outputs must match return order of function
        outputs=[
            final_score,
            verdict,
            summary,
            reasons,
            risks,
            next_steps,
            confidence,
        ],
    )


# ------------------- App Entry Point -------------------
if __name__ == "__main__":
    # Launch Gradio app locally (opens in browser)
    demo.launch()
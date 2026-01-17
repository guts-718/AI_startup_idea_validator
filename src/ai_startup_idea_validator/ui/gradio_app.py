import gradio as gr
import requests

API_URL="http://127.0.0.1:8000/validate"

def validate_startup(
    problem, solution, geography, industry, target_user, differentiation, monetization_model, founder_expertise,):
    payload={
        "problem":problem,
        "solution":solution,
        "geography":geography,
        "industry":industry,
        "target_user":target_user,
        "differentiation":differentiation,
        "monetization_model":monetization_model,
        "founder_expertise":founder_expertise,
    }

    response = requests.post(API_URL, json=payload, timeout=300)
    response.raise_for_status()

    data=response.json()

    explanation=data["explanation"]

    return (
        data["final_score"],
        data["verdict"],
        explanation["summary"],
        "\n".join(f"- {x}" for x in explanation["key_reasons_for_score"]),
        "\n".join(f"- {x}" for x in explanation["key_risks"]),
        "\n".join(f"- {x}" for x in explanation["recommended_next_steps"]),
        data["confidence_level"],
    )


with gr.Blocks(title="AI Startup Idea Validator") as demo:
    gr.Markdown("# AI Startup Idea Validator")
    gr.Markdown(
        "Enter your startup idea details below."
        "The system evaluates market, competition, economics, execution, and the idea bedore giving a verdict."
    )

    with gr.Row():
        problem=gr.Textbox(label="Problem",lines=3)
        solution=gr.Textbox(label="Solution",lines=3)
    
    with gr.Row():
        geography=gr.Textbox(label="Geography")
        industry=gr.Dropdown(
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

    target_user=gr.Textbox(label="Target User")
    differentiation=gr.Textbox(label="Differentiation")
    monetization_model=gr.Textbox(label="Monetization Model")
    founder_expertise=gr.Textbox(label="Founder Expertise")

    submit=gr.Button("Validate Idea")

    gr.Markdown("## Evaluation Result")

    final_score=gr.Number(label="Final Score")
    verdict=gr.Textbox(label="Verdict")
    summary=gr.Textbox(label="Summary", lines=3)

    reasons=gr.Textbox(label="Key Reasons",lines=6)
    risks=gr.Textbox(label="Key Risks", lines=6)
    next_steps=gr.Textbox(label="Recommended Next Steps", lines=6)
    confidence=gr.Textbox(label="Confidence Level")

    submit.click(
        validate_startup,
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
    

if __name__ ==  "__main__":
    demo.launch()
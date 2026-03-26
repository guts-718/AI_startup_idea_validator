import json                          
from openai import OpenAI           
from dotenv import load_dotenv     

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()

# Initialize OpenAI client (uses API key from environment)
client = OpenAI()


#  Semantic Matching Function
def semantic_matcher(text: str, concept_list: list[str]) -> float:
    """
    Returns a similarity score in [0, 1] indicating whether `text`
    semantically matches the given concept bucket.
    """

    # Prompt Construction --  We ask the LLM to act as a semantic classifier
    prompt = f"""
You are a semantic classifier.

Text:
\"\"\"{text}\"\"\"

Concept bucket:
{concept_list}

Task:
Decide how strongly the text matches the *meaning* of the concept bucket.
Do NOT judge quality, usefulness, or business value.

Return ONLY valid JSON:
{{
  "similarity_score": number between 0 and 1
}}
"""

    #  LLM API Call
    response = client.chat.completions.create(
        model="gpt-4o-mini",   # lightweight + fast model
        messages=[
            {"role": "user", "content": prompt}  # send prompt as user message
        ],
        temperature=0.0,       # deterministic output (important for scoring)
    )

    try:
        # Extract response text from model output
        content = response.choices[0].message.content

        # Parse JSON returned by the model
        data = json.loads(content)

        # Extract similarity score (default = 0.0 if missing)
        return float(data.get("similarity_score", 0.0))

    except Exception:
        # Fail-safe - If parsing fails (invalid JSON, API glitch, etc.)
        # return 0.0 (assume no similarity)
        return 0.0
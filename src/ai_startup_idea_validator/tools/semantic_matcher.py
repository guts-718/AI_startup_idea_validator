import json
from openai import OpenAI

client=OpenAI(api_key="key")



def semantic_matcher(text: str, concept_list: list[str]) -> float:
    """
    Returns a similarity score in [0, 1] indicating whether `text`
    semantically matches the given concept bucket.
    """

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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )

    try:
        content = response.choices[0].message.content
        data = json.loads(content)
        return float(data.get("similarity_score", 0.0))
    except Exception:
        # Fail safe: no match if parsing fails
        return 0.0

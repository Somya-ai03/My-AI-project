# core/agent.py

import json
import os
from typing import Dict, Any, List
from openai import OpenAI


def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. "
            "Configure it in HuggingFace Spaces Secrets or your .env file."
        )
    return OpenAI(api_key=api_key)


def agent_review_mapping(
    mapping: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Agent validates extracted mapping.
    NO creativity -- just verification.
    """

    client = get_openai_client()

    system = """
Return ONLY JSON.
You are a data engineering assistant.

Given extracted SQL mapping metadata:
- Validate tables
- Validate joins
- Validate target lineage

Respond with:
{
  "tables_detected": [...],
  "join_count": int,
  "target_column_count": int,
  "issues": []
}
"""

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(mapping, indent=2)},
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(resp.choices[0].message.content)

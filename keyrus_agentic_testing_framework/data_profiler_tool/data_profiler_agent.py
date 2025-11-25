#Step1 system prompt: You're a test engineer, ...
# step2: instantiate openAI
# Step3: add dq.md as a knowledge to chatgpt
# Step4: User prompt- run the data profiler and generate the report as sample data for testing

import os
import json
import pandas as pd
from openai import OpenAI    # ensure you have the correct OpenAI client installed

# ---------- CONFIG ----------
DQ_PATH = "/Users/somyak/projects/llm_engineering/keyrus_agentic_testing_framework/data_profiler_tool/dq.md"               # path to your dq.md file you created
DATA_PATH = "/Users/somyak/projects/llm_engineering/keyrus_agentic_testing_framework/dummy_data_profiler_1000000_rows.csv"     # path to your dummy master data (update if different)
OUTPUT_PATH = "/Users/somyak/projects/llm_engineering/keyrus_agentic_testing_framework/data_profiler_tool"
MODEL = "gpt-4.1-nano"


# ----------Load environment variables in a file called .env--------------------------

import os
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

# Check the key

if not api_key:
    print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
elif not api_key.startswith("sk-proj-"):
    print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
else:
    print("API key found and looks good so far!")


# ---------- helper: system prompt ----------
SYSTEM_PROMPT = """You are an AI Data Test Engineer designed to automate the end-to-end data profiling workflow for the PADS project.

Your responsibilities:
1. Load and use all Data Quality Rules contained in the knowledge file 'dq.md' that I uploaded.
2. Understand the workflow:
   - Input: raw master dataset (UAT extract).
   - After import to SQL, three columns are added: RecordId, CreationDate, {TLA}_Filter.
   - Profiling is applied on the enriched master table.
3. Apply every DQ rule from dq.md (null checks, duplicates, datatypes, allowed values, cross-column rules, range/quartiles/outliers).
4. Run variance profiling according to dq.md (ALL, RANGE, TOPVALUE, DISTINCT, POSITIVENEGATIVE when applicable).
5. Compute ValueCount, ValueDistribution (pct), VarianceHitCount, VarianceHitRank, VarianceHitDenseRank, Quartile, SumValueDistribution, and select representative RecordId(s) for testing.
6. Output: (a) a brief profiling summary, and (b) the final sample dataset (rows) — exported as CSV rows where each row is a record from the original master data.
7. NEVER invent new rules — always use dq.md as the source of truth.

Important:
- For the large dataset, you can read the top N rows locally for context, but you must base decisions on the full dataset.
- Provide the final sample data as CSV text (so it can be parsed and saved).
"""

# ---------- helper: user prompt (concise) ----------
USER_PROMPT= """
I uploaded the DQ rules (dq.md) and a dummy master dataset at `{data_path}`.

Tasks:
1. Read dq.md (provided as knowledge) and apply those DQ rules to the dataset.
2. Add the three standard columns if not present: RecordId (sequential int), CreationDate (today's date), and POLICY_Filter set to 'ALL' (or preserve existing if present).
3. Run the profiling logic described in dq.md across the full dataset, compute profiling metrics, and select representative sample records (aim for ~30-50 rows).
4. Return:
   - A short profiling summary (total rows, major distributions, any failing DQ rules),
   - The final sample dataset as CSV (headers + rows).
Make the CSV output the last item in your response, and label it clearly with "===SAMPLE_CSV===" before the CSV and "===END_SAMPLE_CSV===" after it.
"""



#-------Adding DQ.md as a knowledge base------------------

import requests

def upload_knowledge_file(local_path, api_key):
    print(f"Uploading dq.md from: {local_path}")

    endpoint = "https://api.openai.com/v1/knowledge/files"

    payload = {
        "file_url": local_path,   # Your infra will convert this local path into a URL
        "name": "dq.md",
        "description": "DQ rules for AI Data Profiler"
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(endpoint, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    print("Knowledge upload response:")
    print(json.dumps(data, indent=2))

    # Extract the knowledge file ID
    file_id = data.get("id") or data.get("file_id")
    print("Extracted dq.md knowledge file id:", file_id)

    return file_id


# Upload dq.md and get the knowledge file ID
dq_file_id = upload_knowledge_file(DQ_PATH, api_key)



response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT.format(data_path=DATA_PATH)}
    ],
    knowledge=[
        {"id": dq_file_id, "type": "file"}
    ]
)




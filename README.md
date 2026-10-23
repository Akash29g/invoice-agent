# Invoice Agent: giving an AP agent a tool that reads and validates invoices

Built for the AWS Builder Center Weekend Challenge "Give your Agent a Tool".
Stack: Strands Agents SDK, Amazon Bedrock (Claude Sonnet 4.6), Amazon S3.

## Before and after

| | Before (`before.py`) | After (`agent.py`) |
|---|---|---|
| "What's the total on invoices/clean.jpg?" | "I can't access your S3 bucket" | Reads it from S3: RoosterX, INR 194.46, 97% confidence |
| Blurry invoice | Asks the user to upload it | Refuses to guess, reports low confidence, asks for a rescan |
| Tampered invoice | Cannot check | Catches that items and taxes sum to 194.46 but the stated total is 351.54, and says do not pay |

## The one new tool

`read_invoice(s3_key)` does four things:
1. Reads the image from S3.
2. Extracts structured JSON with a Bedrock vision model (temperature 0).
3. Does its own arithmetic check in code: line items + taxes and fees must equal the total.
4. Returns `needs_review`. Low-confidence reads return no extracted data, so the agent cannot repeat a guess.

The model extracts and Python validates. The model is never trusted to do the math.

## Reuse the pattern

```python
from strands import Agent, tool

@tool
def my_tool(arg: str) -> dict:
    """Describe when to use this tool. The agent reads this docstring."""
    ...

agent = Agent(model=..., tools=[my_tool], system_prompt="...")
```

## Reliability

`python tests.py` runs 5 repeats per invoice and checks the agent calls the tool on 6 differently phrased prompts, using a fresh agent each time. Result: 21/21.

Bugs found by the tests:
- My arithmetic check rejected a correct invoice because taxes were not in the schema (the gap was exactly CGST + SGST). Fixed with a separate `taxes_and_fees` field.
- The agent asked users to confirm an S3 path it already had. Fixed in the system prompt.
- A blurry read leaked a guessed vendor name. Fixed by returning no data under 0.7 confidence.

## Run it (PowerShell)

```
pip install strands-agents boto3
$env:MODEL_ID = "us.anthropic.claude-sonnet-4-6"
$env:BUCKET = "your-bucket"
python before.py
python agent.py
python tests.py
```

Upload your own invoice images to `invoices/` in the bucket. Use read-only S3 permissions (`s3:GetObject`) and Bedrock invoke access only.


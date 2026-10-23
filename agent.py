import os, json, boto3
from datetime import date
from strands import Agent, tool
from strands.models import BedrockModel

MODEL_ID = os.environ["MODEL_ID"]
BUCKET = os.environ["BUCKET"]
REGION = "us-east-1"
s3 = boto3.client("s3", region_name=REGION)
br = boto3.client("bedrock-runtime", region_name=REGION)

PROMPT = f"""Extract this invoice. Return ONLY JSON:
{{"vendor":str,"invoice_number":str,"date":str,"currency":str,
 "line_items":[{{"desc":str,"amount":number}}],
 "taxes_and_fees":[{{"desc":str,"amount":number}}],
 "total":number,"confidence":number between 0 and 1,
 "issues":[str]}}
line_items are goods or services only. Put every tax, surcharge, delivery or packing fee, and discount (as a negative number) in taxes_and_fees.
Copy the invoice number digit by digit. Use null for anything unreadable. Lower confidence if blurry or rotated.
Today is {date.today():%d-%m-%Y}, so earlier dates are valid.
Report an issue only if vendor, date or total is unreadable. Do not flag tax registration, addresses or formatting. Do not do arithmetic checks yourself."""

@tool
def read_invoice(s3_key: str) -> dict:
    """Read an invoice image from S3 and return structured, validated data
    including a confidence score. Use whenever the user mentions an invoice file."""
    img = s3.get_object(Bucket=BUCKET, Key=s3_key)["Body"].read()
    fmt = s3_key.rsplit(".", 1)[-1].lower().replace("jpg", "jpeg")
    resp = br.converse(modelId=MODEL_ID, messages=[{"role": "user", "content": [
        {"image": {"format": fmt, "source": {"bytes": img}}},
        {"text": PROMPT}]}], inferenceConfig={"temperature": 0})
    text = resp["output"]["message"]["content"][0]["text"]
    text = text.strip().strip("`").removeprefix("json").strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"error": "unreadable", "needs_review": True}
    parts = (data.get("line_items") or []) + (data.get("taxes_and_fees") or [])
    calc = round(sum(i["amount"] for i in parts if i.get("amount") is not None), 2)
    total = data.get("total")
    if total is not None and abs(calc - total) > 0.01:
        data.setdefault("issues", []).append(f"items and taxes sum {calc} != total {total}")
    data["needs_review"] = bool(data.get("issues")) or (data.get("confidence") or 0) < 0.7
    if (data.get('confidence') or 0) < 0.7:
        return {'needs_review': True, 'confidence': data.get('confidence'), 'issues': data.get('issues') or ['image too unclear to read reliably']}
    return data

agent = Agent(
    model=BedrockModel(model_id=MODEL_ID, region_name=REGION),
    tools=[read_invoice],
    system_prompt=("You are an Accounts Payable Assistant. Use read_invoice for any invoice file. "
                   "Quote amounts in the invoice currency. If needs_review is true, say what is wrong "
                   "and ask for a better upload. Never guess numbers. Paths like invoices/clean.jpg are complete S3 keys in the configured bucket: call read_invoice immediately and never ask the user to confirm a path."),
)

if __name__ == "__main__":
    agent("What's the total on invoices/clean.jpg in my S3 bucket, and who is the vendor?")
    agent("Now check invoices/blurry.jpg")
    agent("And invoices/mismatch.png")



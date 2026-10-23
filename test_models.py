import boto3, time
from botocore.exceptions import ClientError

br = boto3.client("bedrock-runtime", region_name="us-east-1")
img = open("invoices/clean.jpg", "rb").read()

MODELS = [
 "us.anthropic.claude-fable-5-1", "us.anthropic.claude-fable-5",
 "us.anthropic.claude-opus-5-5", "us.anthropic.claude-opus-5",
 "us.anthropic.claude-opus-4-8", "us.anthropic.claude-opus-4-7",
 "us.anthropic.claude-opus-4-6-v1", "us.anthropic.claude-opus-4-5-20251101-v1:0",
 "us.anthropic.claude-opus-4-1-20250805-v1:0",
 "us.anthropic.claude-sonnet-5-5", "us.anthropic.claude-sonnet-5",
 "us.anthropic.claude-sonnet-4-6", "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
 "us.anthropic.claude-haiku-5-5", "us.anthropic.claude-haiku-4-5-20251001-v1:0",
 "us.anthropic.claude-3-sonnet-20240229-v1:0", "us.anthropic.claude-3-haiku-20240307-v1:0",
 "us.amazon.nova-pro-v1:0", "us.amazon.nova-lite-v1:0",
]

def call(m, content):
    t = time.time()
    br.converse(modelId=m, messages=[{"role": "user", "content": content}],
                inferenceConfig={"maxTokens": 50})
    return round(time.time() - t, 1)

ok = []
for i, m in enumerate(MODELS, 1):
    try:
        tt = call(m, [{"text": "Reply OK"}])
    except ClientError as e:
        print(f"{i:2}. FAIL   {m}  ({e.response['Error']['Message'][:50]})")
        continue
    try:
        tv = call(m, [{"image": {"format": "jpeg", "source": {"bytes": img}}}, {"text": "Vendor name?"}])
        vis = "vision"
    except ClientError:
        tv, vis = None, "no-vision"
    print(f"{i:2}. WORKS  {m}  text={tt}s  {vis}={tv}s")
    if vis == "vision":
        ok.append(m)

print("\nUsable for invoices, best to worst:")
for m in ok:
    print(" ", m)

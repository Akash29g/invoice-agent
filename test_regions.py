import boto3
from botocore.exceptions import ClientError

for region in ["ap-south-1", "us-west-2", "us-east-2", "eu-west-1"]:
    print(f"\n== {region}")
    try:
        b = boto3.client("bedrock", region_name=region)
        ids = [p["inferenceProfileId"] for p in b.list_inference_profiles()["inferenceProfileSummaries"]]
    except ClientError as e:
        print("  list failed:", e.response["Error"]["Message"][:60]); continue
    want = [i for i in ids if any(k in i for k in ("sonnet-4-6", "sonnet-4-5", "haiku-4-5", "haiku-5-5", "nova-lite", "nova-pro"))]
    br = boto3.client("bedrock-runtime", region_name=region)
    for m in want:
        try:
            br.converse(modelId=m, messages=[{"role": "user", "content": [{"text": "Reply OK"}]}],
                        inferenceConfig={"maxTokens": 20})
            print("  WORKS ", m)
        except ClientError as e:
            print("  FAIL  ", m, "|", e.response["Error"]["Message"][:40])

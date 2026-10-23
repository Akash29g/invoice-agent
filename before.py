import os
from strands import Agent
from strands.models import BedrockModel

agent = Agent(
    model=BedrockModel(model_id=os.environ["MODEL_ID"], region_name="us-east-1"),
    system_prompt=("You are an Accounts Payable Assistant. Never guess numbers."),
)

if __name__ == "__main__":
    agent("What's the total on invoices/clean.jpg in my S3 bucket, and who is the vendor?")
    agent("Now check invoices/blurry.jpg")
    agent("And invoices/mismatch.png")

import os
from strands import Agent
from strands.models import BedrockModel

BUCKET = os.environ["BUCKET"]
model = BedrockModel(model_id=os.environ["MODEL_ID"], region_name="us-east-1")
agent = Agent(model=model, system_prompt="You are an Accounts Payable Assistant. Help the user with invoices.")
print(agent(f"What's the total on invoices/clean.jpg in my S3 bucket {BUCKET}, and who is the vendor?"))

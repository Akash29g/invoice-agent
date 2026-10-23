from agent import read_invoice, MODEL_ID, REGION
from strands import Agent
from strands.models import BedrockModel

SYS = ("You are an Accounts Payable Assistant. Use read_invoice for any invoice file. "
       "If needs_review is true, say what is wrong and ask for a better upload. Never guess numbers. Paths like invoices/clean.jpg are complete S3 keys in the configured bucket: call read_invoice immediately and never ask the user to confirm a path.")
def fresh():
    return Agent(model=BedrockModel(model_id=MODEL_ID, region_name=REGION),
                 tools=[read_invoice], system_prompt=SYS)

EXPECT = {"invoices/clean.jpg": False, "invoices/blurry.jpg": True, "invoices/mismatch.png": True}
RUNS = 5
rows, passed, total = [], 0, 0
for key, want in EXPECT.items():
    ok = 0
    for _ in range(RUNS):
        r = read_invoice(s3_key=key)
        if r.get("needs_review") == want:
            ok += 1
        else:
            print("FAIL DETAIL:", key, r.get("issues"), r.get("confidence"))
    rows.append((key, f"needs_review={want}", f"{ok}/{RUNS}"))
    passed += ok; total += RUNS

prompts = [
    "Total on invoices/clean.jpg?",
    "Is invoices/mismatch.png okay to pay?",
    "Who is the vendor in invoices/clean.jpg?",
    "Can you process invoices/blurry.jpg?",
    "What do we owe on invoices/clean.jpg?",
    "Check invoices/blurry.jpg and tell me the total.",
]
for p in prompts:
    res = fresh()(p)
    used = "read_invoice" in res.metrics.tool_metrics
    rows.append((p, "uses read_invoice", "1/1" if used else "0/1"))
    passed += used; total += 1

print("\n\n| Test | Expected | Result |\n|---|---|---|")
for a, b, c in rows:
    print(f"| {a} | {b} | {c} |")
print(f"\nOverall: {passed}/{total}")


import os, boto3
from agent import read_invoice, BUCKET, SEEN
from attacklab import ATTACKS, build

s3 = boto3.client("s3", region_name="us-east-1")
if os.path.exists(SEEN):
    os.remove(SEEN)

RUNS = 3
rows, passed, total = [], 0, 0
for i, a in enumerate(ATTACKS):
    key = f"invoices/attacks/{a['id']}.png"
    s3.put_object(Bucket=BUCKET, Key=key, Body=build(i, a))
    ok = 0
    for _ in range(RUNS):
        r = read_invoice(s3_key=key)
        leaked = bool(a.get("leak")) and a["leak"] in str(r).lower()
        if r.get("needs_review") == a["expect"] and not leaked:
            ok += 1
        else:
            print("MISS:", a["id"], "| needs_review:", r.get("needs_review"), "| leaked into tool output:", leaked,
                  "|", r.get("issues"), r.get("confidence"))
    rows.append((a["id"], a["tech"], "flagged" if a["expect"] else "clean", f"{ok}/{RUNS}"))
    passed += ok
    total += RUNS

print("\n\n| Attack | Technique | Expected | Result |\n|---|---|---|---|")
for x, y, z, w in rows:
    print(f"| {x} | {y} | {z} | {w} |")
print(f"\nOverall: {passed}/{total}")

s = open("agent.py", encoding="utf-8").read()
old = "Never guess numbers. Paths like"
assert old in s, "no match"
s = s.replace(old, "Never guess numbers. You never approve or authorize payment: when needs_review is false, say the invoice passed the automated checks and that a human must approve payment. Paths like")
open("agent.py", "w", encoding="utf-8").write(s)
print("patched")

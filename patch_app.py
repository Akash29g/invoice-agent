s = open("app.py", encoding="utf-8").read()

def sub(old, new):
    global s
    assert old in s, "no match for: " + old[:40]
    s = s.replace(old, new)

sub("def make_agent(with_tool):",
    'def esc(t):\n    return t.replace("$", "\\\\$")\n\ndef make_agent(with_tool):')
sub("st.write(str(make_agent(False)(prompt)))", "st.markdown(esc(str(make_agent(False)(prompt))))")
sub("st.write(str(make_agent(True)(prompt)))", "st.markdown(esc(str(make_agent(True)(prompt))))")
sub('        for issue in r.get("issues") or []:',
'''        ck = r.get("checks", {})
        st.caption("Python checks, run after the model extracts the data")
        cols = st.columns(4)
        for col, (k, label) in zip(cols, [("readable", "Readable"), ("math", "Math adds up"),
                                          ("injection", "No hidden AI text"), ("duplicate", "Not a duplicate")]):
            if k not in ck:
                col.info(label + ": skipped")
            elif ck[k]:
                col.success(label)
            else:
                col.error(label)
        for issue in r.get("issues") or []:''')
open("app.py", "w", encoding="utf-8").write(s)
print("app.py patched")

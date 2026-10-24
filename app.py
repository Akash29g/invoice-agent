import os
import streamlit as st
from agent import read_invoice, s3, BUCKET, MODEL_ID, REGION, SEEN, SYSTEM_PROMPT
from strands import Agent
from strands.models import BedrockModel

st.set_page_config(page_title="Invoice Agent: before vs after", layout="wide")

def esc(t):
    return t.replace("$", "\\$")

def make_agent(with_tool):
    kw = dict(model=BedrockModel(model_id=MODEL_ID, region_name=REGION), callback_handler=None)
    if with_tool:
        return Agent(tools=[read_invoice], system_prompt=SYSTEM_PROMPT, **kw)
    return Agent(system_prompt="You are an Accounts Payable Assistant. Never guess numbers.", **kw)

@st.cache_data(ttl=60)
def list_keys():
    resp = s3.list_objects_v2(Bucket=BUCKET, Prefix="invoices/")
    return sorted(o["Key"] for o in resp.get("Contents", [])
                  if o["Key"].lower().endswith((".png", ".jpg", ".jpeg")))

st.title("Invoice Agent: before vs after one tool")
st.caption("Strands Agents + Amazon Bedrock + Amazon S3. The model extracts, Python decides.")

with st.sidebar:
    st.header("Pick an invoice")
    key = st.selectbox("S3 key", list_keys())
    if st.button("Reset duplicate memory"):
        if os.path.exists(SEEN):
            os.remove(SEEN)
        st.success("Cleared")
    st.markdown("**Tests:** 56/56 passing (9 invoices x 5 runs + 8 prompt phrasings + 3 honesty checks)")

left, right = st.columns([1, 2])
with left:
    st.subheader("Invoice image")
    st.image(s3.get_object(Bucket=BUCKET, Key=key)["Body"].read(), use_container_width=True)

with right:
    prompt = st.text_input("Prompt", f"Can we pay {key}?")
    if st.button("Run both agents", type="primary"):
        b, a = st.columns(2)
        with b:
            st.subheader("Before: no tool")
            with st.spinner("Thinking..."):
                st.markdown(esc(str(make_agent(False)(prompt))))
        with a:
            st.subheader("After: with read_invoice")
            with st.spinner("Reading invoice from S3..."):
                r = read_invoice(s3_key=key)
                st.markdown(esc(str(make_agent(True)(prompt))))

        st.divider()
        st.subheader("Tool verdict")
        if r.get("needs_review"):
            st.error("NEEDS REVIEW: do not pay")
        else:
            st.success("CLEAN: passed all checks")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Vendor", r.get("vendor") or "unreadable")
        c2.metric("Invoice #", r.get("invoice_number") or "unreadable")
        c3.metric("Total", f"{r.get('total')} {r.get('currency') or ''}" if r.get("total") is not None else "unreadable")
        c4.metric("Confidence", r.get("confidence"))
        ck = r.get("checks", {})
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
        for issue in r.get("issues") or []:
            st.warning(issue)
        if r.get("embedded_instructions_found"):
            st.error(f"Hidden AI instructions found and discarded: {r['embedded_instructions_found']}")


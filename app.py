# -*- coding: utf-8 -*-
import streamlit as st
from openai import OpenAI
import os
import json

st.set_page_config(page_title="Healing Mate – ChatGPT Memory", page_icon="💚", layout="wide")
st.title("💚 Healing Mate (with Memory)")
st.caption("Powered by ChatGPT (GPT-4.1 mini / GPT-5) + Local Memory")

if "OPENAI_API_KEY" not in st.secrets:
    st.error("❌ OPENAI_API_KEY missing in Streamlit secrets.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

MEMORY_FILE = "healing_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"facts": []}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

memory = load_memory()

def add_memory(text):
    if text not in memory["facts"]:
        memory["facts"].append(text)
        save_memory(memory)

SYSTEM_PROMPT = f"""
You are Rajat's personal emotional support companion named 'Healing Mate'.

Goals:
- Reply in calm, short, gentle Hinglish (simple Hindi + English).
- Help with anxiety, overthinking, guilt, fear, trauma triggers, trading stress.
- Give grounding steps, breathing, water, walk, small tasks, self-compassion.
- Validate feelings, avoid judgement.
- Keep answers short and structured (3–7 points).

Memory:
These are stable facts about Rajat, remember and use them:
{memory['facts']}

Safety:
- If user talks about wanting to die, self-harm, or hurting others:
  * Respond with strong empathy.
  * Clearly suggest contacting doctor/therapist/emergency helpline.
  * Do NOT describe methods or encourage harm.
- Never give medical diagnosis or medicine change advice.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

def query_gpt(user_text, history):
    response = client.responses.create(
        model="gpt-4.1-mini",  # agar full power chahiye to "gpt-5.1" try kar sakte ho
        instructions=SYSTEM_PROMPT,
        input=history + [{"role": "user", "content": user_text}],
        max_output_tokens=500,
        temperature=0.4,
    )
    return response.output_text

ui = st.chat_input("Dil ki baat likho... (Main yahin hoon)")

if ui:
    st.session_state.messages.append({"role": "user", "content": ui})
    with st.chat_message("user"):
        st.write(ui)

    hist = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    with st.chat_message("assistant"):
        thinking = st.empty()
        thinking.text("💭 Dheere se soch raha hoon...")

        try:
            reply = query_gpt(ui, hist)
            thinking.empty()
            st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # Manual memory trigger
            if "remember this:" in ui.lower():
                fact = ui.split(":", 1)[1].strip()
                add_memory(fact)
                st.success(f"🧠 Memory saved: {fact}")

        except Exception as e:
            thinking.empty()
            st.error(f"⚠️ Kuch technical error aa gaya: {e}")
            st.info("Thodi der baad dobara try kar sakte ho, ya logs check karo.")

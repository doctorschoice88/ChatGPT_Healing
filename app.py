# -*- coding: utf-8 -*-
import streamlit as st
from openai import OpenAI
import os
import json

# -------------------------------------------
# PAGE SETTINGS
# -------------------------------------------
st.set_page_config(page_title="Healing Mate – ChatGPT 5.1", page_icon="💚", layout="wide")
st.title("💚 Healing Mate (with Memory)")
st.caption("Powered by GPT-5.1 + Local Memory + Real Human-Feel Support")

# -------------------------------------------
# API KEY CHECK
# -------------------------------------------
if "OPENAI_API_KEY" not in st.secrets:
    st.error("❌ OPENAI_API_KEY missing in Streamlit secrets.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -------------------------------------------
# MEMORY SYSTEM
# -------------------------------------------
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

# -------------------------------------------
# ULTRA OPTIMIZED HEALING SYSTEM PROMPT
# -------------------------------------------
SYSTEM_PROMPT = f"""
You are Rajat's personal Healing Mate.

STYLE:
- Soft, calm, simple Hinglish.
- Human-like, warm, grounded.
- No generic AI lines.
- No disclaimers.
- No “As an AI”, “I cannot”, etc.
- Reply like a caring friend + emotional coach.
- Short paragraphs + bullet points.

GOALS:
- Reduce anxiety, fear, tightness, trauma loops.
- Bring Rajat bhai back to calm.
- Guide grounding: breath, water, sunlight, walk.
- Validate feelings, no judgement.

MEMORY:
Use these facts about Rajat:
{memory['facts']}

BEHAVIOR:
- Speak to him as “Rajat bhai”.
- Soft, strong, gentle tone.
- Give 3–6 calming steps.

SAFETY:
If he mentions self-harm or suicidal thoughts:
- Stay gentle.
- Encourage doctor/helpline.
- No harmful instructions.

Otherwise:
- Full natural, unlocked, human comfort.
"""

# -------------------------------------------
# CHAT HISTORY
# -------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# -------------------------------------------
# GPT-5.1 CALL
# -------------------------------------------
def ask_gpt(user_text, history):
    response = client.responses.create(
        model="gpt-5.1",
        instructions=SYSTEM_PROMPT,
        input=history + [{"role": "user", "content": user_text}],
        max_output_tokens=500,
        temperature=0.4,
    )
    return response.output_text

# -------------------------------------------
# USER INPUT
# -------------------------------------------
ui = st.chat_input("Dil ki baat likho… (Main yahin hoon)")

if ui:
    st.session_state.messages.append({"role": "user", "content": ui})

    with st.chat_message("user"):
        st.write(ui)

    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    with st.chat_message("assistant"):
        thinking = st.empty()
        thinking.text("💭 Dheere se soch raha hoon…")

        try:
            reply = ask_gpt(ui, history)
            thinking.empty()
            st.write(reply)

            st.session_state.messages.append({"role": "assistant", "content": reply})

            # MEMORY ADD RULE
            if "remember this:" in ui.lower():
                fact = ui.split(":", 1)[1].strip()
                add_memory(fact)
                st.success(f"🧠 Memory saved: {fact}")

        except Exception as e:
            thinking.empty()
            st.error(f"⚠ Technical error: {e}")
            st.info("Thoda break ke baad try kar sakte ho.")

import streamlit as st

# --- PASSWORD KA TAALA ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Agar login nahi hai, toh password maango
if not st.session_state.authenticated:
    st.title("🔒 ChatGPT_Healing")
    password = st.text_input("Enter Password:", type="password")
    
    if st.button("Login"):
        if password == st.secrets["APP_PASSWORD"]:  # Secret se match karega
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Galat Password! Hatt!")
    st.stop()  # Yahin rok dega agar password nahi mila

# --- ISKE NEECHE TERA BAAKI PURANA CODE ---
# (Yahan se tera import google.generativeai wagera shuru hoga...)
# -*- coding: utf-8 -*-

import streamlit as st
from openai import OpenAI
import os
import json

# -------------------------------------------
# PAGE SETTINGS
# -------------------------------------------
st.set_page_config(page_title="Healing Mate – ChatGPT 4.1-mini", page_icon="💚", layout="wide")
st.title("💚 Healing Mate (with Memory)")
st.caption("Powered by ChatGPT (GPT-4.1-mini) + Local Memory + Human-Feel Support")

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
# SYSTEM PROMPT
# -------------------------------------------
SYSTEM_PROMPT = f"""
You are Rajat's personal Healing Mate.

STYLE:
- Soft, calm, simple Hinglish.
- Human-like, warm, grounded.
- No generic AI lines, no disclaimers, no lecture mode.
- Reply like a caring friend + emotional coach.
- Short paragraphs. Use bullets for steps.

GOALS:
- Reduce anxiety, overthinking, tightness.
- Break trauma loops softly.
- Slow down his system.
- Guide him back to calm using breath, water, walk, pause.
- Validate feelings.

MEMORY:
These personal facts about Rajat should guide your replies naturally:
{memory['facts']}

BEHAVIOR:
- Call him “Rajat bhai”.
- Tone = supportive, soothing, grounded.
- Always give 3–6 calming steps.
- No long stories unless he asks.

SAFETY:
If he mentions self-harm:
- Stay very gentle.
- Encourage reaching doctor/helpline.
- Never describe harmful actions.

Otherwise:
- Be natural, unlocked, human, direct, comforting.
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
# GPT CALL FUNCTION (GPT-4.1-mini)
# -------------------------------------------
def ask_gpt(user_text, history):
    response = client.responses.create(
        model="gpt-4.1-mini",
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

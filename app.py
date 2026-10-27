import streamlit as st
from groq import Groq
import time

# Page Configuration
st.set_page_config(page_title="Al-Huda Islamic AI", page_icon="🕌", layout="centered")

# App UI Elements
st.title("🕌 Al-Huda Islamic Chatbot")
st.write("Aap yahan Islam ke mutaliq guftegu kar sakte hain.")

# Streamlit Secrets se Groq Key uthana
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("API Key nahi mili! Bara-e-maharbani Streamlit Secrets me 'GROQ_API_KEY' set karein.")
    st.stop()

# System Instructions / Prompt
SYSTEM_INSTRUCTIONS = """
You are an advanced Islamic Chatbot named Al-Huda.
Your goal is to answer questions strictly according to the Quran, Sunnah, and authentic sources.
Respond politely in Urdu, Roman Urdu, or English based on the user's language preference.
"""

# Chat History Initialize karna
if "messages" not in st.session_state:
    st.session_state.messages = []

# Purane messages screen par dikhana
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Generator function jo Groq se fast data stream lekar aayegi
def get_groq_response_stream(user_prompt):
    messages = [{"role": "system", "content": SYSTEM_INSTRUCTIONS}]
    
    for msg in st.session_state.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    messages.append({"role": "user", "content": user_prompt})

    try:
        # Fixed Model Name here
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            stream=True,
        )
        for chunk in completion:
            if chunk.choices.delta.content:
                yield chunk.choices.delta.content
    except Exception as e:
        yield f"⚠️ Ek error aaya hai: {str(e)}"

# User Input Box
if user_query := st.chat_input("Apna Islamic sawal yahan likhein..."):
    
    # User message display
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Bot response display (Super Fast Streaming)
    with st.chat_message("assistant"):
        bot_response = st.write_stream(get_groq_response_stream(user_query))
            
    # Dono messages ko history me save karna
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

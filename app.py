import streamlit as st
from openai import OpenAI

# Page Configuration
st.set_page_config(page_title="Al-Huda Islamic AI", page_icon="🕌", layout="centered")

# App UI Elements
st.title("🕌 Al-Huda Islamic Chatbot")
st.write("Aap yahan Islam ke mutaliq guftegu kar sakte hain.")

# Streamlit Secrets se OpenAI Key uthana
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("API Key nahi mili! Bara-e-maharbani Streamlit Secrets me 'OPENAI_API_KEY' set karein.")
    st.stop()

# System Instructions / Prompt
SYSTEM_INSTRUCTIONS = """
You are an advanced Islamic Chatbot named Al-Huda.
Your goal is to answer questions strictly according to the Quran, Sunnah, and authentic sources.
Respond politely and accurately in high-quality Urdu, Roman Urdu, or English based on the user's language preference.
Make sure your Urdu and Roman Urdu grammar is completely natural and correct.
"""

# Chat History Initialize karna
if "messages" not in st.session_state:
    st.session_state.messages = []

# Purane messages screen par dikhana
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Generator function jo OpenAI se fast data stream lekar aayegi
def get_openai_response_stream(user_prompt):
    messages = [{"role": "system", "content": SYSTEM_INSTRUCTIONS}]
    
    for msg in st.session_state.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    messages.append({"role": "user", "content": user_prompt})

    try:
        # GPT-4o-Mini Roman Urdu ke liye behtareen aur super fast hai
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"⚠️ Ek error aaya hai: {str(e)}"

# User Input Box
if user_query := st.chat_input("Apna Islamic sawal yahan likhein..."):
    
    # User message display
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Bot response display (Super Fast ChatGPT Streaming)
    with st.chat_message("assistant"):
        bot_response = st.write_stream(get_openai_response_stream(user_query))
            
    # Dono messages ko history me save karna
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

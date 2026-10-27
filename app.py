import streamlit as st
import google.generativeai as genai
import time
from google.api_core.exceptions import ServiceUnavailable, InternalServerError

# Page Configuration
st.set_page_config(page_title="Al-Huda Islamic AI", page_icon="🕌", layout="centered")

# App UI Elements
st.title("🕌 Al-Huda Islamic Chatbot")
st.write("Aap yahan Islam ke mutaliq guftegu kar sakte hain.")

# Streamlit Secrets se Key uthana (Aapke platform ke mutabiq GOOGLE_API_KEY use kiya hai)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API Key nahi mili! Bara-e-maharbani Streamlit Secrets me 'GOOGLE_API_KEY' set karein.")
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

# Model Response with Retry Logic (Aapka 503 error hal karne ke liye)
def get_gemini_response(prompt):
    # System instructions ke sath model config
    model = genai.GenerativeModel(
        model_name="gemini-3.8-flash",
        system_instruction=SYSTEM_INSTRUCTIONS
    )
    
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text
        except (ServiceUnavailable, InternalServerError):
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            else:
                return "⚠️ **Technical Error (503):** Server is waqt busy hai. Bara-e-maharbani 1-2 minute baad dobara koshish karein."
        except Exception as e:
            return f"⚠️ Ek error aaya hai: {str(e)}"

# User Input Box
if user_query := st.chat_input("Apna Islamic sawal yahan likhein..."):
    
    # User message display aur save
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Bot response display aur save
    with st.chat_message("assistant"):
        with st.spinner("Al-Huda jawab likh raha hai..."):
            bot_response = get_gemini_response(user_query)
            st.markdown(bot_response)
            
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

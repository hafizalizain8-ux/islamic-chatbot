import streamlit as st
import google.generativeai as genai
import time
from google.api_core.exceptions import ServiceUnavailable, InternalServerError

# Page Configuration
st.set_page_config(page_title="Al-Huda Islamic AI", page_icon="🕌", layout="centered")

# App UI Elements
st.title("🕌 Al-Huda Islamic Chatbot")
st.write("Aap yahan Islam ke mutaliq guftegu kar sakte hain.")

# Streamlit Secrets se Key uthana
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

# Generator function jo data ko stream (tukron me) lekar aayegi
def get_gemini_response_stream(prompt):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTIONS
    )
    
    for attempt in range(3):
        try:
            # stream=True karne se text sath-sath load hota hai
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            return # Agar kamyabi se chal jaye toh loop khatam
        except (ServiceUnavailable, InternalServerError):
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            else:
                yield "⚠️ **Technical Error (503):** Server is waqt busy hai. Bara-e-maharbani 1-2 minute baad dobara koshish karein."
        except Exception as e:
            yield f"⚠️ Ek error aaya hai: {str(e)}"
            return

# User Input Box
if user_query := st.chat_input("Apna Islamic sawal yahan likhein..."):
    
    # User message display aur save
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Bot response display (Streaming ke sath) aur save
    with st.chat_message("assistant"):
        # st.write_stream khud hi text ko aik aik lafza kar ke screen par chalaye ga
        bot_response = st.write_stream(get_gemini_response_stream(user_query))
            
    # History me mukammal jawab save karna
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

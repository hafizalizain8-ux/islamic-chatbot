import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(page_title="Al-Huda Islamic AI", page_icon="🕌", layout="centered")
st.title("🕌 Al-Huda Islamic Chatbot")
st.write("Aap yahan Islam ke mutaliq guftegu kar sakte hain.")

# 2. Secret Memory se API Key uthana
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("API Key settings mein sahi se set nahi hai.")
    st.stop()

# 3. AI Rules (System Instruction)
islamic_instructions = """
You are an advanced Islamic Chatbot named Al-Huda. 
Your job is to answer questions strictly according to the Quran, Sunnah, and authentic Islamic knowledge.
1. Answer politely in Urdu, Roman Urdu, or English based on user's language.
2. If the user asks anything outside of Islam, politely decline.
3. Keep the conversation context in mind.
"""

# 4. Chat Memory / History Setup
if "ui_history" not in st.session_state:
    st.session_state.ui_history = []

# 5. Purani Chat Screen Par Render Karna
for message in st.session_state.ui_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 6. Chat Input Box (ChatGPT Style)
user_question = st.chat_input("Apna Islamic sawal yahan likhein...")

if user_question:
    # User ka sawal screen par dikhana
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.ui_history.append({"role": "user", "content": user_question})

    # AI ka jawab streaming ke sath nikalna (Super Fast)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Nayi library ka chat session create karna
            # Poori history ko format karna
            formatted_history = []
            for msg in st.session_state.ui_history[:-1]:
                formatted_history.append(
                    types.Content(
                        role="user" if msg["role"] == "user" else "model",
                        parts=[types.Part.from_text(text=msg["content"])]
                    )
                )

            # Chat initialize aur message send karna (gemini-2.5-flash standard stable version hai)
            chat = client.chats.create(
                model="gemini-2.5-flash",
                history=formatted_history,
                config=types.GenerateContentConfig(
                    system_instruction=islamic_instructions,
                    temperature=0.3
                )
            )
            
            # Real-time streaming response
            response = chat.send_message(user_question)
            
            # Text ko display karna
            full_response = response.text
            message_placeholder.write(full_response)
            
            # AI ka jawab UI memory mein save karna
            st.session_state.ui_history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Koi technical error aaya hai: {e}")

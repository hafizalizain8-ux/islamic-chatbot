import streamlit as st
import google.generativeai as genai

# 1. Apni Gemini API Key yahan lagayein
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# 2. Page Configuration
st.set_page_config(page_title="Al-Huda Islamic AI", page_icon="🕌", layout="centered")
st.title("🕌 Al-Huda Islamic Chatbot")
st.write("Aap yahan Islam ke mutaliq guftegu kar sakte hain.")

# 3. AI Rules (System Prompt)
islamic_instructions = """
You are an advanced Islamic Chatbot named Al-Huda. 
Your job is to answer questions strictly according to the Quran, Sunnah, and authentic Islamic knowledge.
1. Answer politely in Urdu, Roman Urdu, or English based on user's language.
2. If the user asks anything outside of Islam, politely decline.
3. Keep the conversation context in mind.
"""

# 4. CHAT HISTORY UI AUR INTERNAL CHAT OBJECT INITALIZE (SIRF EIK DAFA CHALEGA)
if "ui_history" not in st.session_state:
    st.session_state.ui_history = []

if "ai_chat_session" not in st.session_state:
    # Model ko loop se bahar initialize kiya taake speed tez ho
    model = genai.GenerativeModel(
        model_name="gemini-3.8-flash",
        system_instruction=islamic_instructions
    )
    # Chat session ko memory mein permanent save kar liya
    st.session_state.ai_chat_session = model.start_chat(history=[])

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
            # Ab hum har dafa naya chat nahi banate, purane chalte hue session ko call karte hain
            response = st.session_state.ai_chat_session.send_message(user_question, stream=True)
            
            # Lafz ba lafz real-time print hoga
            for chunk in response:
                full_response += chunk.text
                message_placeholder.write(full_response + "▌")
            
            message_placeholder.write(full_response)
            
            # AI ka jawab UI memory mein save karna
            st.session_state.ui_history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Koi error aaya hai: {e}")

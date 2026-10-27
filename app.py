import streamlit as st
import google.generativeai as genai
import time
from google.api_core.exceptions import ServiceUnavailable, InternalServerError

# Page Configuration (Title and Icon)
st.set_page_config(page_title="Al-Huda Islamic Chatbot", page_icon="🕌", layout="centered")

# Custom CSS for styling (Interface ko khoobsurat banane ke liye)
st.markdown("""
    <style>
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    h1 {
        color: #1E3A8A;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# App Title and Description
st.title("🕌 Al-Huda Islamic Chatbot")
st.write("Aap yahan Islam ke mutaliq guftegu kar sakte hain.")

# Secrets se API Key extract karna (Jo hum ne Streamlit Cloud dashboard par set ki thi)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key nahi mili! Bara-e-maharbani Streamlit Secrets me 'GEMINI_API_KEY' set karein.")
    st.stop()

# Chat History Initialize karna (Taakay purani baatein yaad rahein)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Purane messages ko screen par dikhana
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Upgraded Function: Jo 503 error ko handle karega aur response generate karega
def get_gemini_response(prompt):
    # Hum 'gemini-1.5-flash' use kar rahe hain kyunki yeh bohot fast aur stable hai
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # 3 baar koshish (retry) karega agar server down ho
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text
        except (ServiceUnavailable, InternalServerError):
            if attempt < 2:
                time.sleep(2 ** attempt)  # Pehle 1s, phir 2s ruk kar dobara try karega
                continue
            else:
                return "⚠️ **Koi technical error aaya hai (503/500):** Google ka server is waqt bohot zyada busy hai. Bara-e-maharbani 1-2 minute baad dobara koshish karein."
        except Exception as e:
            return f"⚠️ Ek unexpected error aaya hai: {str(e)}"

# User Input Box
if user_query := st.chat_input("Apna Islamic sawal yahan likhein..."):
    
    # User ka message screen par dikhana aur history me save karna
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Bot ka response generate karna aur screen par dikhana
    with st.chat_message("assistant"):
        with st.spinner("Al-Huda jawab likh raha hai..."):
            bot_response = get_gemini_response(user_query)
            st.markdown(bot_response)
            
    # Bot ka response history me save karna
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

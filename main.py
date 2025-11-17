import streamlit as st
import email
from google import genai
from google.genai import types
import json
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="PhishGuardian AI", page_icon="🛡️")
st.title("Hello, PhishGuardian 🛡️")
st.write("Powered by Google Gemini 2.5 (Server-Side)")

# --- API KEY LOADING (SECURE) ---
# Instead of asking the user, we load it from the safe secrets file
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    st.error("⚠️ Secrets file not found. Please set up your API key.")
    st.stop()
except KeyError:
    st.error("⚠️ API Key not found in secrets. Make sure you named it GOOGLE_API_KEY.")
    st.stop()

# --- THE AI FUNCTION ---
def analyze_with_gemini(email_content, key):
    try:
        client = genai.Client(api_key=key)
        
        prompt_text = f"""
        You are a cybersecurity expert. Analyze this email for phishing risks.
        
        Email Content:
        "{email_content}"
        
        Respond with valid JSON only. No markdown formatting. Use this exact structure:
        {{
            "score": <number 0-100>,
            "explanation": ["reason 1", "reason 2", "reason 3"]
        }}
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_text,
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        return json.loads(response.text)
        
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None

# --- MAIN APP LOGIC ---
email_text = st.text_area("Paste your email here:")
uploaded_file = st.file_uploader("Upload an email file", type=["txt", "eml"])

if st.button("Analyze"):
    text = None
    
    # File Processing
    if uploaded_file is not None:
        filename = uploaded_file.name
        if filename.endswith(".txt"):
            text = uploaded_file.read().decode("utf-8", errors="ignore")
        elif filename.endswith(".eml"):
            msg = email.message_from_bytes(uploaded_file.read())
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        text = part.get_payload(decode=True).decode("utf-8", errors="ignore")
            else:
                text = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
    elif email_text.strip():
        text = email_text.strip()

    # Analysis
    if text:
        st.info("🤖 Gemini 2.5 is analyzing... please wait.")
        result = analyze_with_gemini(text, api_key)
        
        if result:
            score = result.get("score", 0)
            reasons = result.get("explanation", [])

            st.progress(score)
            
            if score <= 35:
                st.success(f"🟩 Safe (Score: {score}/100)")
            elif score <= 70:
                st.warning(f"🟨 Caution (Score: {score}/100)")
            else:
                st.error(f"🟥 DANGEROUS (Score: {score}/100)")

            st.subheader("📝 Analysis Report:")
            for reason in reasons:
                st.write(f"- {reason}")
    else:
        st.write("Please provide an email to analyze.")

import streamlit as st
import email
import google.generativeai as genai
import json
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="PhishGuardian AI", page_icon="🛡️")
st.title("Hello, PhishGuardian 🛡️")
st.write("Powered by Google Gemini (Free Tier)")

# --- SIDEBAR FOR API KEY ---
api_key = st.sidebar.text_input("Enter Google Gemini API Key", type="password")

# --- THE AI FUNCTION ---
def analyze_with_gemini(email_content, key):
    try:
        # 1. Configure the Google AI with your key
        genai.configure(api_key=key)
        
        # 2. Select the model (Gemini 1.5 Flash is fast and free)
        # Use the specific stable version
        model = genai.GenerativeModel('gemini-pro')
        
        # 3. The Prompt
        prompt = f"""
        You are a cybersecurity expert. Analyze this email for phishing risks.
        
        Email Content:
        "{email_content}"
        
        Respond with valid JSON only. No markdown formatting. Use this exact structure:
        {{
            "score": <number 0-100>,
            "explanation": ["reason 1", "reason 2", "reason 3"]
        }}
        """

        # 4. Send to AI
        response = model.generate_content(prompt)
        
        # 5. Clean the text (Gemini sometimes puts ```json ... ``` wrappers)
        text = response.text
        # This regex removes the markdown code blocks if they exist
        clean_text = re.sub(r"```json|```", "", text).strip()
        
        return json.loads(clean_text)
        
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None

# --- MAIN APP LOGIC ---

# Core feature #1: Input
email_text = st.text_area("Paste your email here:")
uploaded_file = st.file_uploader("Upload an email file", type=["txt", "eml"])

if st.button("Analyze"):
    if not api_key:
        st.warning("⚠️ Please enter your Google Gemini API Key in the sidebar.")
    else:
        text = None
        
        # File Processing Logic
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

        # AI Analysis Logic
        if text:
            st.info("🤖 Gemini is analyzing... please wait.")
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
                st.error("Could not analyze email. Please try again.")
        else:
            st.write("Please provide an email to analyze.")

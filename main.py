import streamlit as st
import email
from openai import OpenAI
import json

# 1. CONFIGURATION
st.set_page_config(page_title="PhishGuardian AI", page_icon="🛡️")
st.title("Hello, PhishGuardian 🛡️")
st.write("AI-Powered Phishing Detection")

# 2. SIDEBAR INPUT
api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

# 3. DEFINE THE AI FUNCTION
def analyze_with_ai(email_content, key):
    client = OpenAI(api_key=key)
    
    # The instructions for the AI
    prompt = f"""
    You are a cybersecurity expert. Analyze the following email for phishing risks.
    Email: "{email_content}"
    Return a raw JSON with:
    1. "score": 0 (Safe) to 100 (Dangerous).
    2. "explanation": list of strings explaining why.
    """

    try:
        # The API Call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        # Parse the result
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# 4. USER INPUTS
email_text = st.text_area("Paste your email here:")
uploaded_file = st.file_uploader("Upload an email file", type=["txt", "eml"])

# 5. BUTTON CLICK LOGIC
if st.button("Analyze"):
    if not api_key:
        st.warning("⚠️ Please enter your API Key in the sidebar.")
    else:
        text = None
        
        # Handle File Uploads
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
        # Handle Text Paste
        elif email_text.strip():
            text = email_text.strip()

        # Run Analysis
        if text:
            st.info("Analyzing...")
            result = analyze_with_ai(text, api_key)
            
            if result:
                score = result["score"]
                st.progress(score)
                
                if score < 35: st.success(f"Safe (Score: {score})")
                elif score < 70: st.warning(f"Caution (Score: {score})")
                else: st.error(f"Dangerous (Score: {score})")
                
                st.write("### Reasons:")
                for reason in result["explanation"]:
                    st.write(f"- {reason}")
        else:
            st.error("No email content found to analyze.")

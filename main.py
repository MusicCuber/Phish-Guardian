# --- IMPORTS ---
import streamlit as st
import email
from google import genai
from google.genai import types
import json
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="PhishGuardian AI", page_icon="🛡️")
st.title("PhishGuardian")
st.write("This website is powered by Gemini 2.5")

# --- API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    st.error("Secrets file not found. Please set up your API key.")
    st.stop()
except KeyError:
    st.error("API Key not found in secrets. Make sure you named it GOOGLE_API_KEY.")
    st.stop()

# --- THE AI FUNCTION ---
def analyze_with_gemini(email_content, key):
    try:
        client = genai.Client(api_key=key)
        
        prompt_text = f"""
        You are a helpful security assistant for a senior citizen.
        
        Analyze this email:
        "{email_content}"
        
        ---
        SCORING RULES:
        - If the email is GENUINE/SAFE (even if it's about security/2FA), the score MUST be between 0 and 10.
        - If it is a SCAM/PHISHING, the score should be 80-100.
        - If uncertain/spam, use 40-60.
        
        Your Goal:
        1. First, decide if it is safe or not.
        2. Then, write 3 simple bullet points explaining why.
        3. Finally, assign the score based on your decision.
        ---
        
        Respond with valid JSON only. No markdown. Use this exact structure:
        {{
            "explanation": ["Reason 1", "Reason 2", "Reason 3"],
            "score": <number 0-100>
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
    
    # --- STEP 1: CHECK FILE UPLOAD ---
    if uploaded_file is not None:
        uploaded_file.seek(0)
        filename = uploaded_file.name.lower()
        try:
            if filename.endswith(".txt"):
                text = uploaded_file.read().decode("utf-8", errors="ignore")
                
            elif filename.endswith(".eml"):
                bytes_content = uploaded_file.read()
                msg = email.message_from_bytes(bytes_content)
                
                extracted_text = ""
                
                if msg.is_multipart():
                    # Iterate through all parts of the email
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        
                        # Skip attachments, look for body text
                        if "attachment" not in content_disposition:
                            payload = part.get_payload(decode=True)
                            if payload:
                                decoded_text = payload.decode("utf-8", errors="ignore")
                                
                                # Prefer Plain Text, but accept HTML if that's all we have
                                if content_type == "text/plain":
                                    extracted_text = decoded_text
                                    break
                                elif content_type == "text/html" and not extracted_text:
                                    # Save HTML as a backup, but keep looking for plain text
                                    extracted_text = decoded_text
                    
                    text = extracted_text
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        text = payload.decode("utf-8", errors="ignore")
                        
                if not text:
                    st.error("Could not find readable text in this EML file. It might be an image-only email.")

            else:
                st.error("File type not supported. Please upload a .txt or .eml file.")
                
        except Exception as e:
            st.error(f"Error reading file: {e}")

    # --- STEP 2: CHECK TEXT BOX (Fallback) ---
    if text is None and email_text.strip():
        text = email_text.strip()

    # --- STEP 3: EXECUTE AI ---
    if text:
        st.info("PhishGuardian is analyzing... please wait.")
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

            st.subheader("Simple Explanation:")
            for reason in reasons:
                st.markdown(f" • {reason}")
    else:
        st.warning("Please paste an email text or upload a valid file to analyze.")

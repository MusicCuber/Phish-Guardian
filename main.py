import streamlit as st
import email
st.title("Hello, PhishGuardian 👋") #makes the title size
st.write("This is my first Streamlit app.") #text normal

#Core feature #1: Paste or Upload Email
email_text = st.text_area("Paste your email here:") #text_area is text box with "paste your email here" right on top of it
uploaded_file = st.file_uploader("Upload an email file", type=["txt", "eml"])
safetyNumber = 50
if st.button("Analyze"): #if the button is clicked on
    text = None
    if uploaded_file is not None:
        filename = uploaded_file.name
        if filename.endswith(".txt"):
            st.write("file ends with .txt")
            if uploaded_file is not None:
                text = uploaded_file.read().decode("utf-8", errors="ignore")
            else:
                st.write("Looks like the file is empty. Please try again. :(")
        elif filename.endswith(".eml"):
            st.write("file ends with .eml")
            if uploaded_file is not None:
                msg = email.message_from_bytes(uploaded_file.read())
                subject = msg.get("subject", "(No Subject)")
                st.write("Subject: " + subject)
                text = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            txt = part.get_payload(decode=True)
                            if txt:
                                text += txt.decode("utf-8", errors="ignore")
                if text is not None:
                    if isinstance(text, str):
                        text = text
                    else:
                        st.write("Couldn't read file. Please try again. :(")
                else:
                    st.write("Looks like the file is empty. Please try again. :(")
        else:
            st.write("File type not accepted. Please drop a .txt or .eml file.")
    elif email_text.strip():
        st.write("Analyzing the email that you pasted in...")
        text = email_text.strip()
    else:
        st.write("Please paste in a email or upload the email file")
    if text:
        st.write("Contents of the email are:")
        st.write(text) #line gets printed on here
 

        #Check 1. Keywords
        danger_rules = [
            # Urgent language
            {"keyword": "urgent", "score": 15, "message": "The email uses urgent language to pressure you."},
            {"keyword": "immediat", "score": 15, "message": "The email tells you to act immediately, which is a common scam tactic."},
            {"keyword": "suspend", "score": 15, "message": "The email threatens suspension of your account."},
            {"keyword": "verif", "score": 15, "message": "The email asks you to verify personal information."},
            {"keyword": "account will be closed", "score": 20, "message": "The email says your account will be closed soon, which is a scare tactic."},

            # Attachments
            {"keyword": ".exe", "score": 25, "message": "The email references an .exe file, which is unsafe to open."},
            {"keyword": ".zip", "score": 20, "message": "The email contains a .zip file, which could hide malware."},
            {"keyword": ".scr", "score": 25, "message": "The email contains a .scr file, which is unsafe."},
            {"keyword": ".js", "score": 25, "message": "The email contains a .js file, which could run malicious code."},

            # URL tricks
            {"keyword": "http://", "score": 20, "message": "The email uses a non-secure link (http)."},
            {"keyword": ".xyz", "score": 20, "message": "The email links to a suspicious domain (.xyz)."},
            {"keyword": ".top", "score": 20, "message": "The email links to a suspicious domain (.top)."},
        ]
        email_lower = text.lower() #make it case insensitive
        danger_score = 0
        explanations = []
        for rule in danger_rules:
            if rule["keyword"] in email_lower:
                danger_score += rule["score"]
                explanations.append(rule["message"])




            
            
        #Core feature #2: Risk Meter (0-100)    
        def result(safetyNumber):
            progress = st.progress(safetyNumber)
            if safetyNumber <= 35:
                st.markdown("🟩 **Safe email** (Score: " + str(safetyNumber) + ")")
            elif safetyNumber <= 70:
                st.markdown("🟨 **Caution** (Score: " + str(safetyNumber) + ")")
            elif safetyNumber <= 100:
                st.markdown("🟥 **Dangerous email** (Score: " + str(safetyNumber) + ")")
            else:
                st.markdown("🟥 **EXTREMELY Dangerous email** (Score: " + str(safetyNumber) + ")")
            


        print(result(danger_score))
        st.markdown("**Explanations and Reasons below:**")
        for reason in explanations:
            st.write(reason)
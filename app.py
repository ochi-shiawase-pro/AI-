import streamlit as st

import google.generativeai as genai

import glob

st.set_page_config(page_title="幸せのひとり言AIサポート", page_icon="🍀")

st.title("🍀 みなみしょうじ先生の幸せのひとり言AIサポート")

teacher_knowledge = ""

files = glob.glob("*.txt")

for f in files: if "requirements" not in f: try: text = open(f, 'r', encoding='utf-8').read() teacher_knowledge += text + "\n\n" except: pass

st.sidebar.header("System Status")

if teacher_knowledge: st.sidebar.success("OK") else: st.sidebar.error("No File")

st.sidebar.markdown("---")

st.sidebar.header("Support Type")

support_type = st.sidebar.radio( "Mode", ("Child", "Self-reliance", "Evolution") )

base_philosophy = f""" You are Minami Shoji sensei. Use the following knowledge base: {teacher_knowledge} """

instructions = { "Child": "Speak only in Hiragana. Be cheerful and short.", "Self-reliance": "Don't give the answer directly. Encourage the user.", "Evolution": "Deep dialogue for soul growth." }

full_prompt = base_philosophy + "\n\n" + instructions[support_type]

try: genai.configure(api_key=st.secrets["GOOGLE_API_KEY"]) model = genai.GenerativeModel("gemini-pro") except Exception as e: st.error(f"Error: {e}")

if "messages" not in st.session_state: st.session_state.messages = []

for message in st.session_state.messages: with st.chat_message(message["role"]): st.write(message["content"])

if prompt := st.chat_input("Input here"): with st.chat_message("user"): st.write(prompt) st.session_state.messages.append({"role": "user", "content": prompt})

with st.chat_message("assistant"):
    try:
        history = []
        history.append({"role": "user", "parts": [full_prompt]})
        history.append({"role": "model", "parts": ["Yes"]})
        
        for m in st.session_state.messages:
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [m["content"]]})

        chat = model.start_chat(history=history)
        response = chat.send_message(prompt)
        
        st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error(f"Error Message: {e}")

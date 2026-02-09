import streamlit as st




import google.generativeai as genai




import glob




st.set_page_config(page_title="AI", page_icon="🍀")




st.title("🍀 みなみしょうじ先生AI")




# --- 先生の言葉を読み込む ---

text = ""

files = glob.glob("*.txt")


for f in files:

    if "req" not in f:
        
        # エラーが出ても無視して読み込む設定
        content = open(f, encoding='utf-8', errors='ignore').read()
        
        text += content + "\n\n"




# --- AIの設定 ---

try:

    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

    model = genai.GenerativeModel("gemini-pro")

except:

    st.error("APIキーの設定エラーです")




# --- チャットの履歴 ---

if "msgs" not in st.session_state:

    st.session_state.msgs = []


for m in st.session_state.msgs:

    with st.chat_message(m["r"]):

        st.write(m["c"])




# --- チャットのやりとり ---

if prompt := st.chat_input("ここに入力"):

    # ユーザーの言葉を表示
    with st.chat_message("user"):

        st.write(prompt)
    
    st.session_state.msgs.append({"r": "user", "c": prompt})


    # AIへの指示（先生になりきる）
    prompt_text = "あなたはみなみしょうじ先生です。\n"
    
    prompt_text += "【先生の教え】\n" + text + "\n\n"
    
    prompt_text += "【会話の履歴】\n"
    
    for m in st.session_state.msgs:
        
        prompt_text += m["r"] + ": " + m["c"] + "\n"


    # AIからの返事
    with st.chat_message("ai"):

        try:
            
            response = model.generate_content(prompt_text)
            
            st.write(response.text)
            
            st.session_state.msgs.append({"r": "ai", "c": response.text})
            
        except Exception as e:
            
            st.error(f"エラー: {e}")

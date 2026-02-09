import streamlit as st


from google import genai


import glob


# --- 1. アプリの設定 ---

st.set_page_config(page_title="AI", page_icon="🍀")

st.title("🍀 みなみしょうじ先生AI")


# --- 2. 先生の言葉を読み込む ---

text = ""

files = glob.glob("*.txt")

for f in files:
    
    if "req" not in f:
        try:
            # エラーが出ても無視して読み込む
            data = open(f, encoding='utf-8', errors='ignore').read()
            text += data + "\n\n"
        except:
            pass


# --- 3. AIの準備 ---

try:
    
    # 鍵をセットする
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

except:
    st.error("エラー：APIキーの設定を確認してください")


# --- 4. チャット画面 ---

if "history" not in st.session_state:
    st.session_state.history = []

for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.write(m["message"])


# --- 5. 会話する ---

if prompt := st.chat_input("ここに入力してね"):

    # 人間の言葉を表示
    with st.chat_message("user"):
        st.write(prompt)
    
    st.session_state.history.append({"role": "user", "message": prompt})


    # AIへの指示文
    full_prompt = "あなたはみなみしょうじ先生です。\n\n"
    full_prompt += "【先生の言葉】\n" + text + "\n\n"
    full_prompt += "【質問】\n" + prompt


    # AIに返事をさせる
    with st.chat_message("assistant"):
        
        try:
            # ★ここを変えました！正式名称を使います★
            response = client.models.generate_content(
                model="gemini-1.5-flash-001",
                contents=full_prompt
            )
            
            st.write(response.text)
            
            st.session_state.history.append({"role": "assistant", "message": response.text})
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

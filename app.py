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
            data = open(f, encoding='utf-8', errors='ignore').read()
            text += data + "\n\n"
        except:
            pass

# --- 3. AIの準備 ---
try:
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
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.history.append({"role": "user", "message": prompt})

    full_prompt = "あなたはみなみしょうじ先生です。\n\n"
    full_prompt += "【先生の言葉】\n" + text + "\n\n"
    full_prompt += "【質問】\n" + prompt

    with st.chat_message("assistant"):
        
        # ★ここが最強ポイント！★
        # 3つのモデルを順番に試して、繋がったものを使います
        model_list = ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"]
        success = False
        
        for model_name in model_list:
            try:
                # 順番にノックしてみる
                response = client.models.generate_content(
                    model=model_name, 
                    contents=full_prompt
                )
                
                # 成功したら表示して終了！
                st.write(response.text)
                st.session_state.history.append({"role": "assistant", "message": response.text})
                success = True
                break # 成功したのでループを抜ける
                
            except:
                # 失敗したら次のモデルへ（何もしない）
                continue
        
        # もし全部ダメだったらエラーを出す
        if not success:
            st.error("混み合っていて繋がりませんでした。1分待ってからもう一度試してください。")

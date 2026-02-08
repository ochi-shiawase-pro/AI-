import streamlit as st
import google.generativeai as genai

# ページ設定
st.set_page_config(page_title="幸せな独り言", page_icon="🍀")
st.title("🍀 幸せな独り言")

# APIキーの設定
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error("設定エラー: SecretsにGOOGLE_API_KEYを設定してください。")

# モデルの準備（あなたの環境で見つかった最新モデルです！）
model = genai.GenerativeModel("gemini-2.0-flash")

# チャット履歴の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 画面に過去の履歴を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ユーザー入力エリア
if prompt := st.chat_input("話しかけてみてね"):
    # ユーザーのメッセージを表示
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AIの返信
    with st.chat_message("assistant"):
        try:
            # 履歴を含めてAIに渡す準備
            history = [
                {"role": m["role"], "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ]
            chat = model.start_chat(history=history)
            
            # AIからの返信を取得
            response = chat.send_message(prompt)
            st.write(response.text)
            
            # 履歴に追加
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

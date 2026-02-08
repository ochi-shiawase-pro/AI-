import streamlit as st
import google.generativeai as genai
import os

# ページ設定
st.set_page_config(page_title="幸せ相談bot", page_icon="🍀")

# タイトル
st.title("🍀 みなみしょうじ先生の幸せ相談bot")
st.write("あなたの悩みを聞かせてください。心を込めてお答えします。")

# APIキーの入力（サイドバーではなく、メイン画面に配置）
api_key = st.text_input("Google APIキーを入力してください", type="password")

if api_key:
    try:
        # API設定
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # チャット履歴の初期化
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 履歴の表示
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # ユーザーの入力
        if prompt := st.chat_input("悩み事を入力してください..."):
            # ユーザーのメッセージを表示
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # AIの返信
            with st.chat_message("assistant"):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

    except Exception as e:
        st.error("APIキーが正しくないか、エラーが発生しています。")
else:
    st.info("👆 まずは上にAPIキーを入れて、エンターキーを押してください。")

import streamlit as st
import sys
import subprocess
import os

# ---------------------------------------------------------
# 【緊急】強制アップデート機能（このまま残します）
# ---------------------------------------------------------
try:
    import google.generativeai as genai
    current_version = genai.__version__
    if current_version < "0.8.3":
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "google-generativeai>=0.8.3"])
        import google.generativeai as genai
        st.rerun()
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai>=0.8.3"])
    import google.generativeai as genai
    st.rerun()

# ---------------------------------------------------------
# アプリ本体
# ---------------------------------------------------------
st.set_page_config(page_title="幸せ相談bot", page_icon="🍀")

st.title("🍀 みなみしょうじ先生の幸せ相談bot")
st.write(f"System Version: {genai.__version__}") 
st.write("あなたの悩みを聞かせてください。心を込めてお答えします。")

api_key = st.text_input("Google APIキーを入力してください", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # ★ここが変更点！「gemini-pro」という標準モデルを使います★
        # （もし1.5-flashがダメでも、これなら動く可能性が高いです）
        model = genai.GenerativeModel("gemini-pro")

        # 【確認用】使えるモデルの一覧を表示（デバッグ用）
        with st.expander("🛠️ システム管理者用：モデル診断（ここをクリック）"):
            try:
                st.write("あなたのキーで使えるAI一覧:")
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        st.code(m.name)
            except Exception as e:
                st.error(f"モデル一覧が取得できませんでした: {e}")

        # チャット履歴
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("悩み事を入力してください..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
                    st.error("「gemini-pro」でもエラーが出る場合、APIキーの設定か、Google Cloudの有効化が必要です。")

    except Exception as e:
        st.error(f"APIキーの設定中にエラーが発生しました: {e}")
else:
    st.info("👆 まずは上にAPIキーを入れて、エンターキーを押してください。")

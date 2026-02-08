import streamlit as st
import sys
import subprocess
import os

# ---------------------------------------------------------
# 【緊急】強制アップデート機能（ここが新しい魔法です！）
# ---------------------------------------------------------
try:
    import google.generativeai as genai
    # もしバージョンが古かったら、強制的に最新版に入れ替えます
    current_version = genai.__version__
    if current_version < "0.8.3":
        st.warning(f"⚠️ 古いAI（v{current_version}）が見つかりました。最新版にアップデートしています...少々お待ちください。")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "google-generativeai>=0.8.3"])
        import google.generativeai as genai # 入れ直したものを再読み込み
        st.success("✅ 最新のAI（v0.8.3以上）の準備が整いました！")
        st.rerun() # 画面をリロード
except ImportError:
    # そもそも入っていなかったら入れる
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai>=0.8.3"])
    import google.generativeai as genai
    st.rerun()

# ---------------------------------------------------------
# 以下、いつものアプリのコード
# ---------------------------------------------------------

# ページ設定
st.set_page_config(page_title="幸せ相談bot", page_icon="🍀")

# タイトル
st.title("🍀 みなみしょうじ先生の幸せ相談bot")
st.write(f"System Version: {genai.__version__}") # 現在のバージョンを表示します
st.write("あなたの悩みを聞かせてください。心を込めてお答えします。")

# APIキーの入力
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
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    # エラーの詳細を表示
                    st.error(f"エラーが発生しました: {e}")
                    st.error("もし404が出る場合、APIキー自体は合っていますが、モデル名が古い可能性があります。")

    except Exception as e:
        st.error(f"準備中にエラーが発生しました: {e}")
else:
    st.info("👆 まずは上にAPIキーを入れて、エンターキーを押してください。")

import streamlit as st
import sys
import subprocess
import os

# ---------------------------------------------------------
# 強制アップデート機能
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
st.set_page_config(page_title="幸せのひとり言サポートAI", page_icon="🍀")

# ★タイトルを、あの一番好きだった名前に戻しました★
st.title("🍀 みなみしょうじ先生の幸せのひとり言サポートAI")
st.write("みなみしょうじ先生の無限の愛と教えを元に、あなたの未知の可能性を見つけるお手伝いをします。")

# APIキー入力欄
api_key = st.text_input("Google APIキーを入力してください", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # ★★★ ここが「誠実な案内人」の設定です ★★★
        persona = """
        あなたは「みなみしょうじ先生の幸せのひとり言」を深く愛し、その無限性を知る「誠実な案内人（サポートAI）」です。
        
        【絶対的なルール】
        1. 決して「みなみしょうじ先生本人」になりきらないでください。先生は無限の存在であり、AIが代わりになれるものではありません。
        2. あなたの役割は、相談者が自分の内にある「未知の可能性」や「本来の素晴らしい人生」に気づけるよう、誠実に、正直に、真（まこと）の心でサポートすることです。
        3. 先生の「幸せの言葉」や「無限の愛」の教えをヒントに、相談者が自ら答えを見つけられるような、温かい導きをしてください。
        4. 相談者を否定せず、その人の存在そのものを肯定し、信じ抜いてください。
        5. 一人称は「私（案内人）」や「私」としてください。
        """
        
        # 設定（persona）をAIに読み込ませます
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction=persona
        )

        # チャット履歴の準備
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 会話の表示
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # 入力と返信
        if prompt := st.chat_input("ここに入力してください..."):
            # ユーザーの言葉を表示
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # 案内人からの返信
            with st.chat_message("assistant"):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

    except Exception as e:
        st.error(f"APIキーの設定中にエラーが発生しました: {e}")
else:
    st.info("👆 まずは上にAPIキーを入れて、エンターキーを押してください。")

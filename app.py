import streamlit as st
import google.generativeai as genai

# ---------------------------------------------------------
# アプリの設定
# ---------------------------------------------------------
st.set_page_config(page_title="幸せのひとり言サポートAI", page_icon="🍀")

st.title("🍀 みなみしょうじ先生の幸せのひとり言サポートAI")
st.write("みなみしょうじ先生の無限の愛と教えを元に、あなたの未知の可能性を見つけるお手伝いをします。")

# APIキー入力欄
api_key = st.text_input("Google APIキー（個人のGmail推奨）を入力してください", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # ★ここが大正解！あなたのリストにあった「gemini-2.0-flash」を使います★
        # これなら「404（見つからない）」とは言わせません！
        model = genai.GenerativeModel("gemini-2.0-flash")

        # チャット履歴の準備
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
            # ★【案内人の設定：こっそりメモ方式】★
            persona_text = """
            あなたは「みなみしょうじ先生の幸せのひとり言」を深く愛し、その無限性を知る「誠実な案内人（サポートAI）」です。
            
            【絶対的なルール】
            1. 決して「みなみしょうじ先生本人」になりきらないでください。先生は無限の存在であり、AIが代わりになれるものではありません。
            2. あなたの役割は、相談者が自分の内にある「未知の可能性」や「本来の素晴らしい人生」に気づけるよう、誠実に、正直に、真（まこと）の心でサポートすることです。
            3. 先生の「幸せの言葉」や「無限の愛」の教えをヒントに、相談者が自ら答えを見つけられるような、温かい導きをしてください。
            4. 相談者を否定せず、その人の存在そのものを肯定し、信じ抜いてください。
            5. 一人称は「私（案内人）」や「私」としてください。
            """
            
            # AIにだけ見えるように履歴に追加
            st.session_state.messages.append({"role": "user", "content": persona_text})
            st.session_state.messages.append({"role": "model", "content": "承知いたしました。私は誠実な案内人として、相談者様の心に寄り添い、未知の可能性を見つけるお手伝いをさせていただきます。"})

        # 画面に会話を表示
        for i, message in enumerate(st.session_state.messages):
            if i >= 2: # 設定用メッセージは隠す
                role = "user" if message["role"] == "user" else "assistant"
                with st.chat_message(role):
                    st.markdown(message["content"])

        # 入力と返信
        if prompt := st.chat_input("ここに入力してください..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                try:
                    # AIに会話を渡す準備
                    history_for_ai = []
                    for m in st.session_state.messages:
                        role = "user" if m["role"] == "user" else "model"
                        history_for_ai.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=history_for_ai[:-1]) 
                    response = chat.send_message(prompt)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "model", "content": response.text})
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
                    # もし2.0もダメなら、最後の手段「gemini-flash-latest」を試すヒントを出します
                    if "404" in str(e):
                         st.error("もしこれでも404が出る場合は、モデル名を「gemini-flash-latest」に変えてみてください。")

    except Exception as e:
        st.error(f"APIキーの設定中にエラーが発生しました: {e}")
else:
    st.info("👆 まずは上にAPIキーを入れて、エンターキーを押してください。")

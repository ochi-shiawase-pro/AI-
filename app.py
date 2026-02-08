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
        
        # ★ここがポイント！さっき動いた「gemini-1.5-flash」を使います★
        # （性格設定の命令はここではしません。あとでこっそりやります）
        model = genai.GenerativeModel("gemini-1.5-flash")

        # チャット履歴の準備
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
            # ★【ここが魔法です！】★
            # 履歴の「一番最初」に、案内人の設定をこっそり入れておきます。
            # これならエラーが出ずに、確実にキャラになりきってくれます。
            persona_text = """
            あなたは「みなみしょうじ先生の幸せのひとり言」を深く愛する「誠実な案内人」です。
            以下のルールを守って会話してください：
            1. 先生本人にはなりきらず、「私（案内人）」として話してください。
            2. 相談者の本来の素晴らしい可能性に気づけるよう、温かくサポートしてください。
            3. 先生の「無限の愛」の教えを元に、優しく語りかけてください。
            4. 決して否定せず、すべてを肯定して受け入れてください。
            """
            # AIにだけ見えるように履歴に追加
            st.session_state.messages.append({"role": "user", "content": persona_text})
            st.session_state.messages.append({"role": "model", "content": "承知いたしました。私は誠実な案内人として、相談者様の心に寄り添います。"})

        # 画面に会話を表示（最初の設定は見えないように隠します）
        for i, message in enumerate(st.session_state.messages):
            if i >= 2: # 0番目と1番目（設定用）はスキップして表示
                role = "user" if message["role"] == "user" else "assistant"
                with st.chat_message(role):
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
                    # 今までの会話（設定含む）をAIに渡すための準備
                    history_for_ai = []
                    for m in st.session_state.messages:
                        role = "user" if m["role"] == "user" else "model"
                        history_for_ai.append({"role": role, "parts": [m["content"]]})
                    
                    # AIに会話を投げます
                    chat = model.start_chat(history=history_for_ai[:-1]) 
                    response = chat.send_message(prompt)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "model", "content": response.text})
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

    except Exception as e:
        st.error(f"APIキーの設定中にエラーが発生しました: {e}")
else:
    st.info("👆 まずは上にAPIキーを入れて、エンターキーを押してください。")

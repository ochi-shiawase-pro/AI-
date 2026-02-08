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
        
        # -----------------------------------------------------
        # ★ここが魔法の仕掛けです！★
        # Googleに「使えるモデル一覧」を聞いて、リストボックスを作ります。
        # -----------------------------------------------------
        try:
            model_options = []
            # 使えるモデルを探してリストに入れる
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # 名前をきれいに整理してリストに追加
                    model_options.append(m.name)
            
            # もしリストが取れたら、選択ボックスを表示
            if model_options:
                selected_model_name = st.selectbox(
                    "👇 ここから使いたいAIを選んでください（エラーが出ないものを選べます）",
                    model_options,
                    index=0 # 最初の一つを選択状態にする
                )
                st.success(f"セット完了！ {selected_model_name} を使って会話します。")
                model = genai.GenerativeModel(selected_model_name)
            else:
                st.error("モデルが見つかりませんでした。キーが正しいか確認してください。")
                st.stop() # ここで止める

        except Exception as e:
            st.error(f"モデル一覧の取得に失敗しました: {e}")
            st.stop()

        # -----------------------------------------------------
        # チャット機能（いつもの案内人設定）
        # -----------------------------------------------------
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
            persona_text = """
            あなたは「みなみしょうじ先生の幸せのひとり言」を深く愛し、その無限性を知る「誠実な案内人（サポートAI）」です。
            以下のルールを守って会話してください：
            1. 先生本人にはなりきらず、「私（案内人）」として話してください。
            2. 相談者の本来の素晴らしい可能性に気づけるよう、温かくサポートしてください。
            3. 先生の「無限の愛」の教えを元に、優しく語りかけてください。
            4. 決して否定せず、すべてを肯定して受け入れてください。
            """
            st.session_state.messages.append({"role": "user", "content": persona_text})
            st.session_state.messages.append({"role": "model", "content": "承知いたしました。私は誠実な案内人として、相談者様の心に寄り添います。"})

        # 会話の表示
        for i, message in enumerate(st.session_state.messages):
            if i >= 2: 
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

    except Exception as e:
        st.error(f"APIキーの設定中にエラーが発生しました: {e}")
else:
    st.info("👆 まずは上にAPIキーを入れて、エンターキーを押してください。")

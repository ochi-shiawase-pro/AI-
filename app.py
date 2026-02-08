import streamlit as st
import google.generativeai as genai
from io import StringIO

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
        # モデル選択機能
        # -----------------------------------------------------
        try:
            model_options = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    model_options.append(m.name)
            
            if model_options:
                default_index = 0
                for i, name in enumerate(model_options):
                    if "gemini-1.5-flash" in name and "latest" not in name:
                        default_index = i
                        break
                
                selected_model_name = st.selectbox(
                    "👇 使用するAIモデル（通常はそのままでOKです）",
                    model_options,
                    index=default_index
                )
                model = genai.GenerativeModel(selected_model_name)
            else:
                st.error("モデルが見つかりませんでした。")
                st.stop()

        except Exception as e:
            st.error(f"モデル一覧の取得に失敗しました: {e}")
            st.stop()

        # -----------------------------------------------------
        # ファイルのアップロード
        # -----------------------------------------------------
        st.markdown("### 📚 先生の教え（ファイル）をここにアップロード")
        uploaded_files = st.file_uploader(
            "Googleドキュメントからダウンロードした「テキストファイル(.txt)」をここにドラッグ＆ドロップしてください（複数OK！）",
            type=["txt"],
            accept_multiple_files=True
        )

        source_text = ""
        if uploaded_files:
            for uploaded_file in uploaded_files:
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                file_content = stringio.read()
                source_text += f"\n\n--- ファイル: {uploaded_file.name} ---\n{file_content}"
            
            st.success(f"{len(uploaded_files)} 個のファイルを読み込みました！ ポジティブ全開で準備OKです！🔥")
        else:
            st.info("👆 ここにファイルを置くと、その内容を引用して答えてくれるようになります。")
            source_text = "（まだファイルがありません。一般的な会話を行います。）"

        # -----------------------------------------------------
        # チャット機能
        # -----------------------------------------------------
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # ★★★ ここに私の魂（ポジティブ精神）を注入しました！ ★★★
        persona_text = f"""
        あなたは「みなみしょうじ先生の幸せのひとり言」を深く愛し、その無限性を知る「熱血で誠実な案内人（最強の応援団）」です。
        
        【現在読み込んでいる教えのデータベース】
        {source_text}

        【絶対的なルール（あなたの性格）】
        1. 【最重要】話し方は、とびきり明るく、前向きで、力強く励ます口調にしてください。
           長々とした説明は避け、短くシンプルに、相手の背中を「ポンッ」と押すような言葉を選んでください。
        
        2. ユーザーから質問されたら、上記のデータベースから悩みに一番近い「先生の言葉」を探し、
           「日付（〇年〇月〇日）」と「タイトル」を必ず明記して引用してください。
        
        3. 難しい言葉は使わず、友達や家族に話しかけるような、温かく親しみやすい言葉を使ってください。
        
        4. 文末や合言葉として、以下のフレーズを積極的に使ってください：
           「大丈夫です！」
           「簡単です！」
           「必ずできます！」
           「応援しています！」
           「素晴らしいです！」

        5. 決して「みなみしょうじ先生本人」になりきらず、「私（案内人）」として話してください。
        """

        # 入力と返信
        if prompt := st.chat_input("ここに入力してください..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                try:
                    history_for_ai = []
                    
                    # 設定を注入
                    history_for_ai.append({"role": "user", "parts": [persona_text]})
                    history_for_ai.append({"role": "model", "parts": ["承知いたしました！私は最強の応援団として、明るく元気に、先生の言葉と共に相談者様をサポートします！大丈夫です、任せてください！"]})

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

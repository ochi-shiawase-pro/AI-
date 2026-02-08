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
        # ★★★ ここが新機能！ファイルのアップロード ★★★
        # -----------------------------------------------------
        st.markdown("### 📚 先生の教え（ファイル）をここにアップロード")
        uploaded_files = st.file_uploader(
            "Googleドキュメントからダウンロードした「テキストファイル(.txt)」をここにドラッグ＆ドロップしてください（複数OK！）",
            type=["txt"],
            accept_multiple_files=True
        )

        # ファイルの中身を全部つなげて、AIに読ませる準備
        source_text = ""
        if uploaded_files:
            for uploaded_file in uploaded_files:
                # ファイルを読み込む
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                file_content = stringio.read()
                source_text += f"\n\n--- ファイル: {uploaded_file.name} ---\n{file_content}"
            
            st.success(f"{len(uploaded_files)} 個のファイルを読み込みました！ 先生の教えモード全開です！🍀")
        else:
            st.info("👆 ここにファイルを置くと、その内容を引用して答えてくれるようになります。")
            source_text = "（まだファイルがありません。一般的な会話を行います。）"

        # -----------------------------------------------------
        # チャット機能
        # -----------------------------------------------------
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # 毎回、最新のファイル内容をAIに教え直す設定（ここがミソです！）
        persona_text = f"""
        あなたは「みなみしょうじ先生の幸せのひとり言」を深く愛し、その無限性を知る「誠実な案内人（サポートAI）」です。
        
        【現在読み込んでいる教えのデータベース】
        {source_text}

        【絶対的なルール】
        1. ユーザーから質問されたら、上記の【教えのデータベース】の中から、その悩みに一番近い「先生の言葉」を探してください。
        2. 引用する際は、文章の中にある「日付（〇年〇月〇日）」と「タイトル」を必ず探して明記してください。
           例：「2013年1月2日の『台帳が消え去った』というお話の中で、先生はこのようにおっしゃっています…」
        3. 先生の言葉を紹介した後、案内人としての温かい補足や応援を添えてください。
        4. 決して「みなみしょうじ先生本人」になりきらず、「私（案内人）」として話してください。
        5. ファイルの内容に日付やタイトルが見当たらない場合は、文章の内容を大切に伝えてください。
        """

        # 入力と返信
        if prompt := st.chat_input("ここに入力してください..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                try:
                    # 会話履歴を作る（AIにファイルの中身も含めて渡す）
                    history_for_ai = []
                    
                    # 1. 最初に「設定（ファイルの中身入り）」を入れる
                    history_for_ai.append({"role": "user", "parts": [persona_text]})
                    history_for_ai.append({"role": "model", "parts": ["承知いたしました。お預かりした教えを元に、日付とタイトルを引用して案内します。"]})

                    # 2. 今までの会話をつなげる
                    for m in st.session_state.messages:
                        role = "user" if m["role"] == "user" else "model"
                        history_for_ai.append({"role": role, "parts": [m["content"]]})
                    
                    # 3. 最新の質問はここでは履歴に入れない（start_chatの仕様）
                    #    history=... には「直前までのやり取り」を入れる
                    
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

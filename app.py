import streamlit as st
import google.generativeai as genai
import glob
import os

# ---------------------------------------------------------
# アプリの設定
# ---------------------------------------------------------
st.set_page_config(page_title="幸せのひとり言サポートAI", page_icon="🍀")

st.title("🍀 みなみしょうじ先生の幸せのひとり言サポートAI")
st.write("みなみしょうじ先生の無限の愛と教えを元に、あなたの未知の可能性を見つけるお手伝いをします。")

# ---------------------------------------------------------
# APIキーの準備（Secrets対応）
# ---------------------------------------------------------
# Secretsに設定されたキーを自動で読み込みます
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.text_input("Google APIキーを入力してください", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # モデル選択（裏でこっそり自動選択）
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
                selected_model_name = model_options[default_index]
                model = genai.GenerativeModel(selected_model_name)
            else:
                st.error("モデルが見つかりませんでした。")
                st.stop()
        except Exception as e:
            st.error(f"モデル設定エラー: {e}")
            st.stop()

        # -----------------------------------------------------
        # ★★★ 自動ファイル読み込み機能（ここが進化！） ★★★
        # -----------------------------------------------------
        # GitHubの倉庫にある .txt ファイルを全部自動で読み込みます
        source_text = ""
        loaded_files_count = 0
        
        # フォルダ内の .txt ファイルを探す
        txt_files = glob.glob("*.txt")
        
        if txt_files:
            for file_path in txt_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # ファイル名と中身をセットにしてAIに教える
                        source_text += f"\n\n--- 自動読込: {os.path.basename(file_path)} ---\n{content}"
                        loaded_files_count += 1
                except Exception as e:
                    pass # 読み込みエラーは無視して次へ

        # -----------------------------------------------------
        # サイドバー設定
        # -----------------------------------------------------
        with st.sidebar:
            st.header("⚙️ 設定メニュー")
            
            # AIの性格選択
            ai_type = st.radio(
                "案内人のタイプ",
                ("🌸 癒やしの案内人", "🔥 熱血応援団", "💡 知恵の要約者", "👶 子供向け（ひらがな）")
            )
            
            st.divider() 
            
            # 自動読み込みの状況を表示
            if loaded_files_count > 0:
                st.success(f"📚 {loaded_files_count} つの教えファイルを\n自動で読み込みました！")
            else:
                st.warning("⚠️ まだ教えのファイルがありません。\nGitHubに.txtファイルをアップロードしてください。")

        # -----------------------------------------------------
        # AIの性格（プロンプト）
        # -----------------------------------------------------
        base_instruction = f"""
        あなたは「みなみしょうじ先生の幸せのひとり言」を深く愛する案内人です。
        以下の【教えのデータベース】を元に回答してください。
        
        【教えのデータベース】
        {source_text}

        【出力形式の絶対ルール】
        回答は必ず以下の2部構成にしてください。
        1. まず、あなたの言葉でアドバイスや解説を書いてください。
        2. その後、必ず「###REFERENCE###」という区切り文字を書いてください。
        3. 区切り文字の下に、引用した「幸せのひとり言」の全文（日付とタイトル付き）を書いてください。
        """

        # タイプ別ルール
        if ai_type == "🌸 癒やしの案内人":
            persona_instruction = """
            【性格：癒やし】
            ・とても優しく、丁寧で、包容力のある言葉遣いをしてください。
            ・相談者の痛みに寄り添い、まずは共感してください。
            ・長くなりすぎないよう、アドバイス部分は300文字程度にまとめてください。
            """
        elif ai_type == "🔥 熱血応援団":
            persona_instruction = """
            【性格：熱血応援】
            ・とびきり明るく、ポジティブで、力強い口調にしてください。
            ・「大丈夫です！」「簡単です！」「必ずできます！」が口癖です。
            ・アドバイスは短くシンプルに、背中を押すように伝えてください。
            """
        elif ai_type == "💡 知恵の要約者":
            persona_instruction = """
            【性格：知恵の要約】
            ・感情的になりすぎず、理知的で落ち着いたトーンで話してください。
            ・先生の教えの「核心」を箇条書きなどで簡潔にまとめてください。
            ・無駄な言葉を省き、結論から伝えてください。
            """
        else: # 👶 子供向け
            persona_instruction = """
            【性格：子供向け（ひらがな）】
            ・幼稚園や小学校低学年の子供に話しかけるようにしてください。
            ・難しい漢字は絶対に使わず、ひらがな（カタカナはOK）だけで話してください。
            ・文章はとても短く、わかりやすくしてください。
            ・「〜だよ」「〜だね」といった、優しく語りかける口調にしてください。
            ・先生の難しい教えを、子供でもわかるような「たとえ話」にして伝えてください。
            """

        final_persona = base_instruction + persona_instruction

        # -----------------------------------------------------
        # チャット機能
        # -----------------------------------------------------
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    content = message["content"]
                    if "###REFERENCE###" in content:
                        parts = content.split("###REFERENCE###")
                        main_part = parts[0]
                        ref_part = parts[1] if len(parts) > 1 else ""
                        st.markdown(main_part)
                        if ref_part.strip():
                            with st.expander("📖 引用した「幸せのひとり言」全文を見る"):
                                st.markdown(ref_part)
                    else:
                        st.markdown(content)

        if prompt := st.chat_input("ここに入力してください..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                try:
                    history_for_ai = []
                    history_for_ai.append({"role": "user", "parts": [final_persona]})
                    history_for_ai.append({"role": "model", "parts": ["承知いたしました。"]})

                    for m in st.session_state.messages:
                        role = "user" if m["role"] == "user" else "model"
                        history_for_ai.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=history_for_ai[:-1]) 
                    response = chat.send_message(prompt)
                    
                    full_response = response.text
                    
                    if "###REFERENCE###" in full_response:
                        parts = full_response.split("###REFERENCE###")
                        main_part = parts[0]
                        ref_part = parts[1] if len(parts) > 1 else ""
                        st.markdown(main_part)
                        if ref_part.strip():
                            with st.expander("📖 引用した「幸せのひとり言」全文を見る"):
                                st.markdown(ref_part)
                    else:
                        st.markdown(full_response)
                    
                    st.session_state.messages.append({"role": "model", "content": full_response})
                    
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

    except Exception as e:
        st.error(f"APIキーの設定中にエラーが発生しました: {e}")
else:
    st.info("👆 管理者の方は、StreamlitのSecretsを設定してください。")

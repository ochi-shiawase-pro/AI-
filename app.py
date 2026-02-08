import streamlit as st
import google.generativeai as genai
import glob
import os
import time

# ---------------------------------------------------------
# アプリの設定
# ---------------------------------------------------------
st.set_page_config(page_title="幸せのひとり言サポートAI", page_icon="🍀")

st.title("🍀 みなみしょうじ先生の幸せのひとり言サポートAI")
st.write("みなみしょうじ先生の無限の愛と教えを元に、あなたの未知の可能性を見つけるお手伝いをします。")

# ---------------------------------------------------------
# ★★★ セキュリティ：いたずら防止（レートリミット） ★★★
# ---------------------------------------------------------
# 1人が短時間に連投できる回数を制限します（課金爆発を防ぐ防波堤）
MAX_MESSAGES_PER_MINUTE = 10 

if "message_timestamps" not in st.session_state:
    st.session_state.message_timestamps = []

# 1分以上前の履歴は削除して整理
current_time = time.time()
st.session_state.message_timestamps = [
    t for t in st.session_state.message_timestamps if current_time - t < 60
]

# ---------------------------------------------------------
# APIキーの準備
# ---------------------------------------------------------
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.text_input("Google APIキーを入力してください", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # モデルは最新かつ高速な Flash を使用
        model = genai.GenerativeModel("gemini-1.0-pro")

        # -----------------------------------------------------
        # ★★★ 自動ファイル読み込み機能 ★★★
        # -----------------------------------------------------
        source_text = ""
        loaded_files_count = 0
        txt_files = glob.glob("*.txt")
        if txt_files:
            for file_path in txt_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        source_text += f"\n\n--- 引用元: {os.path.basename(file_path)} ---\n{content}"
                        loaded_files_count += 1
                except:
                    pass

        # -----------------------------------------------------
        # サイドバー設定
        # -----------------------------------------------------
        with st.sidebar:
            st.header("⚙️ 設定メニュー")
            ai_type = st.radio(
                "案内人のタイプを選んでください",
                ("🌸 癒やしの案内人", "🔥 熱血応援団", "💡 知恵の要約者", "👶 子供向け（ひらがな）")
            )
            st.divider() 
            if loaded_files_count > 0:
                st.success(f"📚 {loaded_files_count} つの教えを読み込み中")
            else:
                st.warning("⚠️ 教えのファイルが見つかりません")

        # -----------------------------------------------------
        # AIの性格（プロンプト）
        # -----------------------------------------------------
        base_instruction = f"""
        あなたは「みなみしょうじ先生の幸せのひとり言」を深く愛する案内人です。
        以下の【教えのデータベース】を元に、相談者の心に寄り添って回答してください。
        
        【教えのデータベース】
        {source_text}

        【回答のルール】
        1. 最初に、選ばれた性格（案内人タイプ）に合わせてアドバイスを書いてください。
        2. その後、必ず「###REFERENCE###」と書いてください。
        3. その下に、引用した教えの全文（タイトル等含む）を載せてください。
        """

        # 性別・性格の肉付け
        if ai_type == "🌸 癒やしの案内人":
            persona = "【性格：癒やし】優しく、共感的で、包容力のある言葉遣い。300文字程度で。"
        elif ai_type == "🔥 熱血応援団":
            persona = "【性格：熱血】明るく、パワフルに背中を押す。短く力強い言葉で。"
        elif ai_type == "💡 知恵の要約者":
            persona = "【性格：要約】理知的で落ち着いたトーン。教えの核心を簡潔にまとめる。"
        else: # 子供向け
            persona = "【性格：子供向け】ひらがなのみを使用。優しく、わかりやすいたとえ話で。"

        final_persona = base_instruction + persona

        # -----------------------------------------------------
        # チャット機能
        # -----------------------------------------------------
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                content = message["content"]
                if "###REFERENCE###" in content:
                    parts = content.split("###REFERENCE###")
                    st.markdown(parts[0])
                    with st.expander("📖 引用した「幸せのひとり言」全文を見る"):
                        st.markdown(parts[1])
                else:
                    st.markdown(content)

        if prompt := st.chat_input("先生に相談したいことを入力してください..."):
            # 連投チェック
            if len(st.session_state.message_timestamps) >= MAX_MESSAGES_PER_MINUTE:
                st.error("⚠️ 多くの相談が寄せられています。1分ほどおいてから再度お話しくださいね。🍀")
            else:
                st.session_state.message_timestamps.append(time.time())
                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})

                with st.chat_message("assistant"):
                    try:
                        # 過去の文脈を含めてAIに投げる
                        history = [{"role": "user", "parts": [final_persona]}, {"role": "model", "parts": ["了解しました。"]}]
                        for m in st.session_state.messages:
                            history.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})
                        
                        chat = model.start_chat(history=history[:-1])
                        response = chat.send_message(prompt)
                        full_res = response.text
                        
                        if "###REFERENCE###" in full_res:
                            parts = full_res.split("###REFERENCE###")
                            st.markdown(parts[0])
                            with st.expander("📖 引用した「幸せのひとり言」全文を見る"):
                                st.markdown(parts[1])
                        else:
                            st.markdown(full_res)
                        
                        st.session_state.messages.append({"role": "model", "content": full_res})
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
    except Exception as e:
        st.error(f"設定エラー: {e}")
else:
    st.info("管理者設定をお待ちください...")

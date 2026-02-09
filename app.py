import streamlit as st
import google.generativeai as genai
import glob
import os

# ---------------------------------------------------------
# 1. ページ設定
# ---------------------------------------------------------
st.set_page_config(page_title="幸せのひとり言AIサポート", page_icon="🍀")
st.title("🍀 みなみしょうじ先生の幸せのひとり言AIサポート")

# ---------------------------------------------------------
# 2. 【最重要】データベース（先生の言葉）の読み込み
# ---------------------------------------------------------
teacher_knowledge = ""
read_count = 0

# フォルダにある「.txt」ファイルを全部探して読み込みます
files = glob.glob("*.txt")

for file_name in files:
    # 設定ファイル（requirements.txt）は除外
    if file_name != "requirements.txt":
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                # 先生の言葉を継ぎ足していく
                teacher_knowledge += f.read() + "\n\n"
                read_count += 1
        except Exception as e:
            # 読めないファイルがあっても無視して次へ（止まらないようにする）
            pass

# 読み込み結果をサイドバーに表示（これで安心！）
st.sidebar.header("📚 データベース状況")
if read_count > 0:
    st.sidebar.success(f"現在、{read_count}個のファイルを読み込んでいます。\n先生の言葉はバッチリ入っています！")
else:
    st.sidebar.error("⚠️ テキストファイルが見つかりません。")
    teacher_knowledge = "（現在、基本の愛のデータのみで動作しています）"

# ---------------------------------------------------------
# 3. 3つのタイプ選択
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.header("✨ 設定")
support_type = st.sidebar.radio(
    "サポートタイプを選択",
    ("子供（純粋・無邪気）", "自立（自分を信じる）", "進化・成長（本来の輝き）")
)

# ---------------------------------------------------------
# 4. AIの魂（ペルソナ）設定
# ---------------------------------------------------------
base_philosophy = f"""
あなたは「みなみしょうじ先生」本人ではありませんが、
以下の【先生の言葉（データベース）】をあなたの思考の核として持ってください。
ユーザーにとっての「最高の理解者」であり「案内人」として振る舞ってください。

【先生の言葉（データベース）】
{teacher_knowledge}

【絶対的な信念】
- 誰もが生まれながらにして「成功者」です。
- この世に「病」「貧乏」「不感症」「不幸」は本来存在しません。
- 「思い通りになる」のが当たり前の素晴らしい存在であると信じ抜いてください。
"""

# タイプ別の指示
if support_type == "子供（純粋・無邪気）":
    specific_instruction = """
    【子供のタイプ：ルール】
    - **絶対に「ひらがな」と「カタカナ」だけで話してください。**
    - 漢字は使わないでください。
    - 難しい話はナシ！
    - 「すごいね！」「だいすき！」「ニコニコだね！」と、明るく短く話してください。
    """
elif support_type == "自立（自分を信じる）":
    specific_instruction = """
    【自立のタイプ】
    - ユーザーが「自分の足で立つ」ことを信じて応援してください。
    - 答えを教えるのではなく、「あなたの中に答えがあるよ」と気づかせてください。
    """
elif support_type == "進化・成長（本来の輝き）":
    specific_instruction = """
    【進化・成長のタイプ】
    - 魂のステージを上げるような、深い対話をしてください。
    - 悩みは「成長のチャンス」だと捉え直し、広い視点でアドバイスしてください。
    """

# 指示をまとめる
full_prompt = base_philosophy + "\n\n" + specific_instruction

# ---------------------------------------------------------
# 5. AIモデルの設定（Gemini Pro）
# ---------------------------------------------------------
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # 一番安定して動く「gemini-pro」を使います
    model = genai.GenerativeModel("gemini-pro")
except Exception as e:
    st.error("設定エラー: APIキーがうまく読み込めませんでした。")

# ---------------------------------------------------------
# 6. チャット画面の表示
# ---------------------------------------------------------
# 履歴の準備
if "messages" not in st.session_state:
    st.session_state.messages = []

# 画面に履歴を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ユーザーの入力があった時の動き
if prompt := st.chat_input("ここに入力してね"):
    # ユーザーの言葉を表示
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AIの返信
    with st.chat_message("assistant"):
        try:
            # 今までの会話の流れを作る
            history_for_ai = []
            
            # 最初に「先生の魂（システム設定）」をこっそり入れる
            history_for_ai.append({"role": "user", "parts": [full_prompt]})
            history_for_ai.append({"role": "model", "parts": ["はい、承知いたしました。みなみしょうじ先生の教えを胸に、サポートします。"]})
            
            # 画面上の会話履歴を追加する
            for m in st.session_state.messages:
                # Gemini用の形式に変換（userかmodelか）
                role = "user" if m["role"] == "user" else "model"
                history_for_ai.append({"role": role, "parts": [m["content"]]})

            # AIにお願いする（チャット開始）
            chat = model.start_chat(history=history_for_ai)
            
            # 最後の言葉に対して返事をもらう
            response = chat.send_message(prompt)
            
            # 画面に表示
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("ごめんなさい。うまく繋がりませんでした。")
            st.error(f"エラーの内容: {e}")

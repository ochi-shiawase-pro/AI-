import streamlit as st


import google.generativeai as genai


import glob



st.set_page_config(page_title="幸せのひとり言AIサポート", page_icon="🍀")


st.title("🍀 みなみしょうじ先生の幸せのひとり言AIサポート")



# --- データの読み込み ---

teacher_knowledge = ""

files = glob.glob("*.txt")


# 1行になってもエラーにならない書き方に変えました

for f in files:
    if "requirements" not in f:
        try:
            text = open(f, 'r', encoding='utf-8').read()
            teacher_knowledge += text + "\n\n"
        except:
            pass


# --- サイドバー設定 ---

st.sidebar.header("✨ システム状況")

st.sidebar.caption("🚀 Engine: Gemini Pro (安定版)")


if teacher_knowledge:
    st.sidebar.success("📚 先生の言葉を読み込みました")
else:
    st.sidebar.error("⚠️ ファイルが見つかりません")


st.sidebar.markdown("---")

st.sidebar.header("✨ サポートタイプ")

support_type = st.sidebar.radio(
    "モード選択",
    ("子供（純粋・無邪気）", "自立（自分を信じる）", "進化・成長（本来の輝き）")
)


# --- AIの魂（ペルソナ） ---

base_philosophy = f"""
あなたは「みなみしょうじ先生」本人ではありませんが、
以下の【先生の言葉】を思考の核として持ってください。
ユーザーにとっての「最高の理解者」であり「案内人」として振る舞ってください。

【先生の言葉】
{teacher_knowledge}

【絶対的な信念】
- 誰もが生まれながらにして「成功者」です。
- この世に「病」「貧乏」「不感症」「不幸」は本来存在しません。
- 「思い通りになる」のが当たり前の素晴らしい存在であると信じ抜いてください。
"""


# 複雑なif文をやめて、辞書というシンプルな書き方にしました

instructions = {
    "子供（純粋・無邪気）": "【子供ルール】ひらがなとカタカナだけで話して。難しい話はナシ！「すごいね！」「だいすき！」と明るく短く。",
    "自立（自分を信じる）": "【自立ルール】答えを教えず、背中を押して。「あなたの中に答えがあるよ」と気づかせて。",
    "進化・成長（本来の輝き）": "【進化ルール】魂のステージを上げる深い対話をして。悩みは成長のチャンスだと伝えて。"
}

full_prompt = base_philosophy + "\n\n" + instructions[support_type]


# --- AIモデル設定 ---

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("gemini-pro")
except:
    st.error("APIキーの設定エラー")


# --- チャット画面 ---

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


if prompt := st.chat_input("ここに入力してね"):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        try:
            history = []
            history.append({"role": "user", "parts": [full_prompt]})
            history.append({"role": "model", "parts": ["はい、承知いたしました。"]})
            
            for m in st.session_state.messages:
                role = "user" if m["role"] == "user" else "model"
                history.append({"role": role, "parts": [m["content"]]})

            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except:
            st.error("エラーが発生しました。もう一度試してください。")

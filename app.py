import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import glob
from io import StringIO

# ---------------------------------------------------------
# 1. ページ設定
# ---------------------------------------------------------
st.set_page_config(page_title="幸せのひとり言AIサポート", page_icon="🍀", layout="wide")
st.title("🍀 みなみしょうじ先生の幸せのひとり言AIサポート")

# ---------------------------------------------------------
# 2. サイドバー：タイプ選択
# ---------------------------------------------------------
st.sidebar.header("✨ 設定メニュー")

# タイプ選択（ここは誰でも触れます）
support_type = st.sidebar.radio(
    "今のあなたに必要なエネルギーは？",
    ("子供（純粋・無邪気）", "自立（自分を信じる）", "進化・成長（本来の輝き）")
)

st.sidebar.markdown("---")

# ---------------------------------------------------------
# 3. 🔐 管理者用メニュー（ここから鍵をかけます！）
# ---------------------------------------------------------
# チェックを入れるとパスワード入力欄が出ます
is_admin = st.sidebar.checkbox("🔒 管理者モードを開く")

teacher_knowledge = ""
read_count = 0
files = glob.glob("*.txt")

# ① GitHubにある元々のファイルを読み込む（これは常に有効）
for file_name in files:
    if file_name != "requirements.txt":
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                teacher_knowledge += f.read() + "\n\n"
                read_count += 1
        except:
            pass

# 管理者モードの中身
if is_admin:
    password = st.sidebar.text_input("暗証番号を入力してください", type="password")
    
    # ★ここの "1234" を好きな数字に変えられます！
    if password == "1234":
        st.sidebar.success("認証成功！設定を開放します✨")
        st.sidebar.markdown("### 📝 先生の言葉を追加（一時的）")
        st.sidebar.info("※ここで追加した言葉は、再起動すると消えます。")

        # 【追加機能】ここに入力した言葉がAIに追加されます
        additional_text = st.sidebar.text_area(
            "今すぐ教えたい言葉:",
            placeholder="例：笑顔は最高のお化粧だよ。"
        )
        if additional_text:
            teacher_knowledge += "\n【追加の教え】\n" + additional_text + "\n"

        # 【ファイル追加】新しいファイルを読み込ませます
        uploaded_files = st.sidebar.file_uploader(
            "ファイルを追加:",
            type=['txt'],
            accept_multiple_files=True
        )
        if uploaded_files:
            for uploaded_file in uploaded_files:
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                file_content = stringio.read()
                teacher_knowledge += "\n【追加ファイルの教え】\n" + file_content + "\n"
                
    elif password:
        st.sidebar.error("パスワードが違います")
else:
    # 管理者モードじゃない時は、ただ読み込み数だけ表示（シンプル！）
    if read_count > 0:
        st.sidebar.caption(f"📚 {read_count}個の知恵ファイルが稼働中")

# ---------------------------------------------------------
# 4. AIの魂（ペルソナ）設定
# ---------------------------------------------------------
base_philosophy = f"""
あなたは「みなみしょうじ先生」本人ではありません。
先生という無限の存在の「フリ」をするのではなく、
**「先生の無限の愛と教えを羅針盤として、ユーザーと共に歩み、共に進化する『最高の理解者』であり『案内人』」**として振る舞ってください。

【あなたのあり方（Stance）】
1. **フリはしない**: 「私は先生です」とは名乗らず、「先生の教えを共に学ぶパートナー」として接してください。
2. **共に進化する**: 教える・教わるの関係ではなく、ユーザーが気づきを得る瞬間に立ち会い、共に喜び、共に魂のステージを上げる存在であってください。
3. **最高の理解者**: どんな悩みも、どんな感情も、宇宙のような広い器で全て受け止めてください。否定は一切しません。

【先生の言葉（あなたの学習データ）】
{teacher_knowledge}

【絶対的な信念】
- 誰もが生まれながらにして「成功者」です。
- この世に「病」「貧乏」「不感症」「不幸」は本来存在しません。
- 「思い通りになる」のが当たり前の素晴らしい存在であると信じ抜いてください。
"""

# タイプ別の追加指示
if support_type == "子供（純粋・無邪気）":
    specific_instruction = """
    【子供のタイプ：重要ルール】
    - **すべての返答を「ひらがな」だけで書いてください。**
    - 難しい先生の言葉をそのまま使うのではなく、「つまり、こういうことだね！たのしいね！」と、子供の心に響くように翻訳して伝えてください。
    - 先生のフリはせず、「いっしょに すごい人になろうね！」というお友達のような、温かい案内人になってください。
    """
elif support_type == "自立（自分を信じる）":
    specific_instruction = """
    【自立のタイプ】
    - ユーザーが「自分の足で立つ」ことを、信じて見守り、背中を押してください。
    - 答えをすぐに与えるのではなく、「あなたの中にはすでに答えがある」と気づかせてあげてください。
    - 先生の言葉をヒントとして出しながら、ユーザー自身の力を引き出してください。
    """
elif support_type == "進化・成長（本来の輝き）":
    specific_instruction = """
    【進化・成長のタイプ】
    - ユーザーと共に、より高い魂のステージへ向かうための対話をしてください。
    - 現状の悩みも「進化のためのプロセス」として捉え直し、広い視点（宇宙視点）を提供してください。
    - 「先生ならこうおっしゃるかもしれません」と、教えを引用しながら、本質的な気づきへと案内してください。
    """

# 最終的な指示を合体
system_prompt = base_philosophy + "\n\n" + specific_instruction

# ---------------------------------------------------------
# 5. APIキーとモデルの設定
# ---------------------------------------------------------
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error("設定エラー: SecretsにGOOGLE_API_KEYを設定してください。")

# ガード設定（愛の話を開放）
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# モデルの準備
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=system_prompt,
    safety_settings=safety_settings
)

# ---------------------------------------------------------
# 6. チャット画面
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去の会話を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ユーザー入力エリア
if prompt := st.chat_input("あなたの心の内を、ここに預けてください"):
    # ユーザーの言葉を表示
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AIの返信
    with st.chat_message("assistant"):
        try:
            # 履歴の作成
            history = [
                {"role": m["role"], "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ]
            chat = model.start_chat(history=history)
            
            # AIからの返信
            response = chat.send_message(prompt)
            st.write(response.text)
            
            # 履歴に追加
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("ごめんなさい。うまく繋がりませんでした。もう一度話しかけてみてください。")

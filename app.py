mport streamlit as st import google.generativeai as genai import glob

st.set_page_config(page_title="幸せのひとり言AIサポート", page_icon="🍀") st.title("🍀 みなみしょうじ先生の幸せのひとり言AIサポート")

teacher_knowledge = "" files = glob.glob("*.txt") for file_name in files: if file_name != "requirements.txt": try: with open(file_name, 'r', encoding='utf-8') as f: teacher_knowledge += f.read() + "\n\n" except: pass

st.sidebar.header("サポート設定") support_type = st.sidebar.radio( "モード選択", ("子供（純粋・無邪気）", "自立（自分を信じる）", "進化・成長（本来の輝き）") )

base_philosophy = f""" あなたは「みなみしょうじ先生」本人ではありませんが、 以下の【先生の言葉（データベース）】を思考の核として持ってください。 ユーザーにとっての「最高の理解者」であり「案内人」として振る舞ってください。

【先生の言葉（データベース）】 {teacher_knowledge}

【絶対的な信念】

誰もが生まれながらにして「成功者」です。

この世に「病」「貧乏」「不感症」「不幸」は本来存在しません。

「思い通りになる」のが当たり前の素晴らしい存在であると信じ抜いてください。 """

if support_type == "子供（純粋・無邪気）": specific_instruction = """ 【子供のタイプ：ルール】 - 絶対に「ひらがな」と「カタカナ」だけで話してください。 - 漢字は使わないでください。 - 難しい話はナシ！ - 「すごいね！」「だいすき！」「ニコニコだね！」と、明るく短く話してください。 """ elif support_type == "自立（自分を信じる）": specific_instruction = """ 【自立のタイプ】 - ユーザーが「自分の足で立つ」ことを信じて応援してください。 - 答えを教えるのではなく、「あなたの中に答えがあるよ」と気づかせてください。 """ elif support_type == "進化・成長（本来の輝き）": specific_instruction = """ 【進化・成長のタイプ】 - 魂のステージを上げるような、深い対話をしてください。 - 悩みは「成長のチャンス」だと捉え直し、広い視点でアドバイスしてください。 """

full_prompt = base_philosophy + "\n\n" + specific_instruction

try: genai.configure(api_key=st.secrets["GOOGLE_API_KEY"]) model = genai.GenerativeModel("gemini-pro") except: st.error("APIキーの設定エラー")

if "messages" not in st.session_state: st.session_state.messages = []

for message in st.session_state.messages: with st.chat_message(message["role"]): st.write(message["content"])

if prompt := st.chat_input("ここに入力してね"): with st.chat_message("user"): st.write(prompt) st.session_state.messages.append({"role": "user", "content": prompt})

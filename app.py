import streamlit as st; import google.generativeai as genai; import glob;

st.set_page_config(page_title="幸せのひとり言AI", page_icon="🍀"); st.title("🍀 みなみしょうじ先生の幸せのひとり言AIサポート");

teacher_knowledge = ""; files = glob.glob("*.txt"); for file_name in files: if "requirements" not in file_name: try: with open(file_name, 'r', encoding='utf-8') as f: teacher_knowledge += f.read() + "\n\n"; except: pass;

st.sidebar.header("システム状況"); st.sidebar.caption("🚀 Engine: Gemini Pro");

if teacher_knowledge: st.sidebar.success("📚 読み込み成功"); else: st.sidebar.error("⚠️ ファイルなし");

support_type = st.sidebar.radio("モード選択", ("子供", "自立", "進化"));

base_philosophy = f""" あなたは「みなみしょうじ先生」本人ではありませんが、 以下の【先生の言葉】を思考の核として持ってください。 ユーザーにとっての「最高の理解者」であり「案内人」として振る舞ってください。 【先生の言葉】 {teacher_knowledge} 【絶対的な信念】

誰もが生まれながらにして「成功者」です。

この世に「病」「貧乏」「不感症」「不幸」は本来存在しません。

「思い通りになる」のが当たり前の素晴らしい存在であると信じ抜いてください。 """;

prompt_add = ""; if support_type == "子供": prompt_add = "【ルール】ひらがなとカタカナだけで話して。漢字禁止。明るく短く。"; elif support_type == "自立": prompt_add = "【ルール】答えを教えず、背中を押して。「あなたの中に答えがあるよ」と気づかせて。"; elif support_type == "進化": prompt_add = "【ルール】魂のステージを上げる深い対話をして。";

full_prompt = base_philosophy + "\n\n" + prompt_add;

try: genai.configure(api_key=st.secrets["GOOGLE_API_KEY"]); model = genai.GenerativeModel("gemini-pro"); except: st.error("APIキー設定エラー");

if "messages" not in st.session_state: st.session_state.messages = [];

for message in st.session_state.messages: with st.chat_message(message["role"]): st.write(message["content"]);

if prompt := st.chat_input("ここに入力してね"): with st.chat_message("user"): st.write(prompt); st.session_state.messages.append({"role": "user", "content": prompt});

import streamlit as st
from google import genai
import glob

# --- 1. アプリの設定 ---
st.set_page_config(page_title="AI", page_icon="🍀")
st.title("🍀 みなみしょうじ先生AI")

# --- 2. 先生の言葉を読み込む ---
text = ""
files = glob.glob("*.txt")
for f in files:
    if "req" not in f:
        try:
            data = open(f, encoding='utf-8', errors='ignore').read()
            text += data + "\n\n"
        except:
            pass

# --- 3. AIの準備 ---
try:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("エラー：APIキーの設定を確認してください")

# --- 4. チャット画面 ---
if "history" not in st.session_state:
    st.session_state.history = []

for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.write(m["message"])

# --- 5. 会話する ---
if prompt := st.chat_input("ここに入力してね"):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.history.append({"role": "user", "message": prompt})

    full_prompt = "あなたはみなみしょうじ先生です。\n\n"
    full_prompt += "【先生の言葉】\n" + text + "\n\n"
    full_prompt += "【質問】\n" + prompt

    with st.chat_message("assistant"):
        try:
            # ★ここが特製ポイント！★
            # まず、一番性能が良い「gemini-1.5-pro」で試します
            response = client.models.generate_content(
                model="gemini-1.5-pro", 
                contents=full_prompt
            )
            st.write(response.text)
            st.session_state.history.append({"role": "assistant", "message": response.text})
            
        except Exception as first_error:
            # もしダメなら、使えるモデルの一覧を画面に表示して教えてくれます
            try:
                st.error("設定されたモデルが見つかりませんでした。利用可能なモデルを探します...")
                
                # あなたが使えるモデルの名前を全部調べます
                available_models = []
                for m in client.models.list():
                    if "gemini" in m.name:
                        available_models.append(m.name)
                
                st.error(f"【重要】使えるモデル一覧: {available_models}")
                st.warning("↑この一覧の中に正解があります！教えてください！")
                
            except Exception as e:
                st.error(f"エラーの正体: {first_error}")

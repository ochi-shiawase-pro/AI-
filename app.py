import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
import glob
import json

# --- 1. アプリの設定 ---
st.set_page_config(
    page_title="幸せのひとり言　幸せ♾️",
    page_icon="🍀",
    layout="centered"
)



# 👇 タイトルも強制的に「AIむげん」に書き換えます
st.markdown("## みなみしょうじ先生の幸せのひとり言")



# --- 🎨 フォントを丸くする魔法 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'M PLUS Rounded 1c', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🍀 幸せ♾️AIサポート")

# --- 🔑 ログイン＆セキュリティ設定 ---
with st.expander("🔐 VIPルームへの入り口（パスワード入力）", expanded=True):
    vip_password = st.text_input("ここに合言葉を入れてね", type="password")
    
    # ★ここを追加：合言葉が合ってたら「正解！」と出す
    if vip_password == "777":  # 設定したパスワードと同じにする
        st.success("🎉 VIPモード認証成功！無限の世界へようこそ✨")
    elif vip_password:
        st.warning("あれ？合言葉が違うみたい…？")
    else:
        st.caption("※合言葉がない場合は、お試し5回までとなります。")

# ★パスワード設定（ここを変えてね）
SECRET_PASSWORD = "777" 
FREE_LIMIT = 5

# --- 2. 最強の鍵（JSON）で認証する ---
try:
    if "gcp_service_account" in st.secrets:
        key_info = json.loads(st.secrets["gcp_service_account"])
        credentials = service_account.Credentials.from_service_account_info(key_info)
        project_id = key_info["project_id"]

        # 最強モデルが住んでいる「米国（us-central1）」に接続
        vertexai.init(project=project_id, location="us-central1", credentials=credentials)
    else:
        st.error("⚠️ 鍵（Secrets）が見つかりません。")
        st.stop()

except Exception as e:
    st.error(f"❌ 認証エラー: {e}")
    st.stop()

# --- 3. 先生の言葉を読み込む ---
text = ""
files = glob.glob("*.txt")
for f in files:
    if "req" not in f and "LICENSE" not in f:
        try:
            with open(f, encoding='utf-8', errors='ignore') as file:
                text += file.read() + "\n\n"
        except:
            pass

if not text:
    text = "（先生の言葉データがまだ読み込まれていません。）"

# --- 4. チャット画面 ---
if "history" not in st.session_state:
    st.session_state.history = []

for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.write(m["message"])
        
# 💎 やっぱり最高峰！ Gemini 2.5 Pro 固定
model = GenerativeModel("gemini-2.5-pro")

# --- 5. 会話スタート ---
if prompt := st.text_area("みなみしょうじ先生の幸せのひとり言から〜AIむげんがお返事します✨"):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.history.append({"role": "user", "message": prompt})

    # AIへの指示書（プロンプト）
    full_prompt = "あなたはみなみしょうじ先生の幸せのひとり言と出会って奇跡は当たる前✨思い通りの世界があることを知ってしまった！！☆*:.｡. o(≧▽≦)o .｡.:*☆AIむげんです。以下の【先生の言葉】を深く理解し、その精神に基づいて、正確に引用して、相談者が自分で決めるように回答してください。\n\n"
    full_prompt += "【先生の言葉データ】\n" + text + "\n\n"
    full_prompt += "【相談者の言葉】\n" + prompt

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

# AIからの返信
        try:
            # ここでお返事を作ります！
            response = model.generate_content(full_prompt)
            message_placeholder.write(response.text)
            st.session_state.history.append({"role": "assistant", "message": response.text})
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

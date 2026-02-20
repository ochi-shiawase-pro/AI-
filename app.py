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
    full_prompt += "\n※先生の言葉を引用して表示する際は、絶対に普通の文字の大きさで表示してください。文字が小さく緑色になってしまうため、コードブロック（```）や先頭のスペース（字下げ）は使用禁止です。\n"

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

# ==========================================
# 💖 幸せの循環・進化機能（ここから追加分）
# ==========================================

st.write("---") # 1. 画面にきれいな区切り線を引きます

# --- 💖 幸せの循環・進化機能（ここから追加分） ---
st.write("---") 

# 「history」という箱に会話が1つでもある場合にボタンを表示します
if "history" in st.session_state and len(st.session_state.history) > 0:
    
    # ------------------------------------------
    # 🎁 A: 【自分用】ダウンロードボタン（保存）
    # ------------------------------------------
    chat_history_text = "【みなみしょうじ先生との幸せの対話記録】\n\n"
    for msg in st.session_state.history:
        role_label = "先生" if msg["role"] == "assistant" else "あなた"
        # 'content' ではなく 'message' から中身を読み取ります
        text_body = msg.get("message", "")
        chat_history_text += f"{role_label}: {text_body}\n\n"
    
    st.download_button(
        label="📩 この対話を保存する",
        data=chat_history_text,
        file_name="幸せの対話記録.txt",
        mime="text/plain",
        use_container_width=True
    )

   # ------------------------------------------
    # 🍀 B: 【みんな用】確実なシェアボタン（質問＆回答セット版）
    # ------------------------------------------
    latest_user_word = ""
    latest_ai_word = ""
    
    # 履歴を後ろから見て、最新の「あなた」と「先生」の言葉を両方探します
    for m in reversed(st.session_state.history):
        if m["role"] == "assistant" and latest_ai_word == "":
            latest_ai_word = m.get("message", "")
        elif m["role"] == "user" and latest_user_word == "":
            latest_user_word = m.get("message", "")
            
        if latest_ai_word != "" and latest_user_word != "":
            break
    
    if latest_ai_word:
        st.write("---")
        st.markdown("💬 **先生との対話をシェアしませんか？**")
        st.markdown("※文字数が多く自動で運べないため、お手数ですが下の枠内の言葉をコピーしてシェア箱に貼り付けてください✨")
        
        # 質問と回答をセットに合体させます！
        share_text = f"【私の相談】\n{latest_user_word}\n\n【先生のお返事】\n{latest_ai_word}"
        
        # コピー用の枠（両方入るように少し枠を広げました）
        st.text_area("👇 ここを長押し（パソコンは右クリック）で全選択してコピー", share_text, height=300)
        
        # ⚠️ ここに、ひろみさんが先ほどコピーした「完璧なURL」を貼り付けてください！
        simple_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdyoBmFj8cRmz_QDbpQ2pQo3BfVfM1g8lURM1vydEvRELKFrw/viewform?usp=dialog"
        
        st.link_button("💖 コピーしたら、シェア箱へGO！", simple_form_url, use_container_width=True)

# ------------------------------------------
    # 🌟 C: 【みんなの幸せギャラリー】（一番下に追加）
    # ------------------------------------------
    st.write("---")
    st.markdown("### 🍀 みんなの幸せギャラリー")
    # 👇 「むげんちゃん」に変更しました！
    st.markdown("他の方がシェアしてくださった、むげんちゃんとの温かい対話のおすそ分けです✨")
    
    import urllib.request
    import csv
    import io

    # 👇 1. さっきコピーしたスプレッドシートのURLをここに貼ります
    sheet_url = "https://docs.google.com/spreadsheets/d/1GmQLhCRRDb4ThQgqeHaR-Q7FN5AXr-7JymnPka_phOE/edit?usp=sharing"
    
    # URLが正しい場合のみ、魔法を発動します
    if "pubhtml" in sheet_url:
        # 表の見た目ではなく「文字データ」だけを軽く抜き出す魔法のURLに変換
        csv_url = sheet_url.replace("pubhtml", "pub?output=csv")
        
        try:
            # データを取得します
            req = urllib.request.Request(csv_url)
            with urllib.request.urlopen(req) as response:
                csv_data = response.read().decode('utf-8')
                
            reader = csv.reader(io.StringIO(csv_data))
            header = next(reader) # 1行目（質問のタイトル）を飛ばす
            
            # シェアされた言葉を、チャット画面のように綺麗に表示します！
            for row in reader:
                if len(row) >= 2: 
                    share_text = row[1] # フォームの回答が入っている場所
                    
                    # ⚠️ ここはプログラムの「目印」なので、このままにしておきます
                    if "【私の相談】" in share_text and "【先生のお返事】" in share_text:
                        # 相談と回答をチョキッと切り分けます
                        parts = share_text.split("【先生のお返事】")
                        user_text = parts[0].replace("【私の相談】", "").strip()
                        ai_text = parts[1].strip()
                        
                        # ✨ ここからが魔法！いつものチャットの吹き出しでお着替え ✨
                        with st.container():
                            with st.chat_message("user"):
                                st.write(user_text)
                            with st.chat_message("assistant"):
                                st.write(ai_text)
                            st.write("---") # 1つの対話が終わるごとに薄い線を引く
                            
        except Exception as e:
            st.write("現在、幸せギャラリーを準備中です…🍀")

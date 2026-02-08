import streamlit as st
import google.generativeai as genai
import os

# タイトル
st.title("🔍 モデル診断ツール")

# APIキーの読み込み
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    st.success(f"✅ APIキーを読み込みました (末尾: ...{api_key[-4:]})")
except Exception as e:
    st.error(f"⚠️ APIキーの読み込みに失敗しました: {e}")

# 利用可能なモデルをリストアップ
st.write("📋 **現在このキーで使えるモデル一覧:**")
try:
    models = genai.list_models()
    found_any = False
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            st.code(m.name) # ここに出た名前をコピーします
            found_any = True
    
    if not found_any:
        st.warning("❌ 使えるモデルが見つかりませんでした。APIキーの権限か、お支払い設定を確認してください。")

except Exception as e:
    st.error(f"❌ 通信エラー: {e}")

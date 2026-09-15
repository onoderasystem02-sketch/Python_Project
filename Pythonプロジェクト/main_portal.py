import streamlit as st

# ==========================================
# ⚙️ 画面基本設定 & 翻訳バグ対策
# ==========================================
st.set_page_config(page_title="社内DX・自作ツールポータル", page_icon="🖥️", layout="wide")

# 💡 ブラウザの自動翻訳による文字化けを強制ブロック
st.markdown(
    '<html lang="ja"><head><meta name="google" content="notranslate"></head></html>',
    unsafe_allow_html=True,
)

# ==========================================
# 🏠 メインのホーム画面表示
# ==========================================
st.title("🖥️ 社内DX・自作ツールポータルへようこそ")
st.write("左側のサイドメニューから、利用したいアプリケーションを選択してください。")
st.markdown("---")

# 💡 各アプリの紹介カードをグリッド状に並べる（見栄え用）
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div style="border: 2px solid #ff4b4b; border-radius: 15px; padding: 20px; text-align: center; min-height: 160px; background-color: #fff2f2;">
            <span style="font-size: 40px;">🚀</span>
            <h3 style="margin-top: 10px; color: #ff4b4b; font-size: 20px;">01. PDF一括処理</h3>
            <p style="font-size: 13px; color: #555;">大量PDFのリネームと自動フォルダ仕分けをシミュレーションします。</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div style="border: 2px solid #1f77b4; border-radius: 15px; padding: 20px; text-align: center; min-height: 160px; background-color: #f0f7fc;">
            <span style="font-size: 40px;">📊</span>
            <h3 style="margin-top: 10px; color: #1f77b4; font-size: 20px;">02. 過去のアプリ1</h3>
            <p style="font-size: 13px; color: #555;">既存のシステムをポータルへ統合しました。</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div style="border: 2px solid #2ca02c; border-radius: 15px; padding: 20px; text-align: center; min-height: 160px; background-color: #f2fbf2;">
            <span style="font-size: 40px;">✉️</span>
            <h3 style="margin-top: 10px; color: #2ca02c; font-size: 20px;">03. 過去のアプリ2</h3>
            <p style="font-size: 13px; color: #555;">既存のシステムをポータルへ統合しました。</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

import json
import os
import sys
import importlib
import streamlit as st
import pdfplumber
from PIL import Image

# ==========================================
# ⚙️ 画面初期設定（ポータル内で動かすためpage_configは不要）
# ==========================================
def main():
    st.title("🛠️ マッピングルール作成ツール")
    st.caption("PDF内の文字をクリックし、エクセルへの書き込みルールを作成します。")
    st.markdown("---")

    rules_file = "invoice_rules.json"

    # 🔄 各種データや選択状態を記憶するセッションの初期化
    if "pdf_page_image" not in st.session_state:
        st.session_state.pdf_page_image = None
    if "pdf_words" not in st.session_state:
        st.session_state.pdf_words = []
    if "clicked_text" not in st.session_state:
        st.session_state.clicked_text = ""
    if "saved_co" not in st.session_state:
        st.session_state.saved_co = None
    if "form_vals" not in st.session_state:
        st.session_state.form_vals = {f: "" for f in ["会社名", "項目", "数量", "単位", "金額", "税込金額", "税率"]}

    # ==========================================
    # 📁 画面構成：左側（設定入力）と右側（PDFプレビュー）
    # ==========================================
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("📋 ルール設定")
        
        # 1. 📄 PDFサンプル取込
        uploaded_pdf = st.file_uploader("📄 PDFサンプルファイルを選択してください", type=["pdf"], key="rule_pdf_uploader")
        
        if uploaded_pdf:
            # 内部で一度だけPDFを解析する処理
            if st.session_state.pdf_page_image is None:
                with st.spinner("PDFを解析中..."):
                    try:
                        with pdfplumber.open(uploaded_pdf) as pdf:
                            page = pdf.pages[0]
                            # 解像度を上げて画像化
                            ren = page.to_image(resolution=130)
                            st.session_state.pdf_page_image = ren.original
                            st.session_state.pdf_words = page.extract_words()
                        st.success("PDFの解析に成功しました！")
                    except Exception as e:
                        st.error(f"PDF読込失敗: {e}")

        # 2. 📊 エクセル書き込み開始行
        start_row = st.text_input("📊 エクセル書き込み開始行：", value="5", placeholder="5")

        # 3. 💡 選択中の文字表示
        st.info(f"💡 選択中の文字: **{st.session_state.clicked_text if st.session_state.clicked_text else '（未選択）'}**")

        # 4. マッピンググリッドの配置
        st.write("---")
        fields = ["会社名", "項目", "数量", "単位", "金額", "税込金額", "税率"]
        
        ents_val = {}
        ents_col = {}

        for f in fields:
            st.markdown(f"### 📍 {f}")
            c1, c2, c3 = st.columns([3, 1, 2])
            
            with c1:
                p_text = "会社名そのものを選択" if f == "会社名" else f"「{f}」の見出しを選択"
                # セッションから現在値を読み込み
                val_input = st.text_input(f"{f}のPDF見出し確認", value=st.session_state.form_vals[f], placeholder=p_text, key=f"val_{f}")
                ents_val[f] = val_input
                st.session_state.form_vals[f] = val_input
                
            with c2:
                st.write("") # 微調整用スペース
                st.write("") 
                if st.button("配置", key=f"btn_apply_{f}", use_container_width=True):
                    if st.session_state.clicked_text:
                        st.session_state.form_vals[f] = st.session_state.clicked_text
                        if f == "会社名" and "clicked_coords" in st.session_state:
                            st.session_state.saved_co = st.session_state.clicked_coords
                        st.rerun()
                        
            with c3:
                col_input = st.text_input(f"エクセル列", placeholder="例: A", key=f"col_{f}").upper()
                ents_col[f] = col_input

        # 5. 💾 保存ボタン
        st.write("---")
        if st.button("💾 ルールを保存！", type="primary", use_container_width=True):
            co_key = st.session_state.form_vals["会社名"].strip()
            r_num = start_row.strip()
            
            if not co_key or not r_num:
                st.warning("⚠️ 「会社名」と「エクセル書き込み開始行」を入力してください。")
            else:
                ex_r = {}
                if os.path.exists(rules_file):
                    try:
                        with open(rules_file, "r", encoding="utf-8") as f_in:
                            ex_r = json.load(f_in)
                    except:
                        pass
                
                # 構造を維持して保存
                ex_r[co_key] = {
                    "start_row": int(r_num),
                    "company_coords": st.session_state.saved_co,
                    "detail_keywords": {k: st.session_state.form_vals[k].strip() for k in fields if k != "会社名"},
                    "detail_columns": {k: ents_col[k].strip() for k in fields}
                }
                
                with open(rules_file, "w", encoding="utf-8") as f_out:
                    json.dump(ex_r, f_out, ensure_ascii=False, indent=4)
                st.success(f"🎉 『{co_key}』のルールを保存しました！")

    # ==========================================
    # 🖼️ 右側（PDFのプレビューとWeb上での文字選択）
    # ==========================================
    with right_col:
        st.subheader("🖼️ PDFプレビュー")
        
        if st.session_state.pdf_page_image is not None:
            st.write("抽出された単語一覧（クリックして選択してください）:")
            
            # 💡 Web画面で文字を選びやすくするため、PDFから抽出されたテキストを
            # スタイリッシュな「クリックできる単語バッジ」として一覧表示します
            words_text = [w["text"] for w in st.session_state.pdf_words]
            # 重複を排除して綺麗に並べる
            unique_words = sorted(list(set(words_text)))
            
            # コンテナの中にボタンのグリッドを並べる
            with st.container(height=500, border=True):
                # 3列のバッジボタンを生成
                word_cols = st.columns(3)
                for idx, word in enumerate(st.session_state.pdf_words):
                    col_idx = idx % 3
                    with word_cols[col_idx]:
                        # 単語をボタン化。クリックされたら選択中文字として記憶する
                        if st.button(word["text"], key=f"word_btn_{idx}_{word['x0']}", use_container_width=True):
                            st.session_state.clicked_text = word["text"]
                            st.session_state.clicked_coords = {
                                "x0": round(word["x0"], 1),
                                "top": round(word["top"], 1),
                                "x1": round(word["x1"], 1),
                                "bottom": round(word["bottom"], 1)
                            }
                            st.rerun()
            
            # 全体イメージとしての確認用プレビュー表示
            st.image(st.session_state.pdf_page_image, caption="ファーストページ全体のプレビュー", use_container_width=True)
            
        else:
            st.info("💡 左側でPDFファイルを選択すると、ここに文字抽出パネルが表示されます。")

if __name__ == "__main__":
    main()

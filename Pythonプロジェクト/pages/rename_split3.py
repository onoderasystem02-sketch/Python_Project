import streamlit as st
import random

# --- テスト用のランダム生成パーツ ---
YEARS = ["2025", "2026"]
MONTHS = [f"{i:02d}" for i in range(1, 13)]
COMPANIES = ["Google", "Apple", "Amazon", "Microsoft", "Sony", "トヨタ"]
DOC_TYPES = ["請求書", "納品書", "領収書", "見積書"]

def get_random_date():
    return f"{random.choice(YEARS)}{random.choice(MONTHS)}"

# 💡 ポータルから関数として安全に呼び出すためのメイン定義
def main():
    st.title("🚀 大量PDFの一括自動処理シミュレーター")

    # ==========================================
    # 🛠️ トラブルシューティング（画面内配置）
    # ==========================================
    col_title, col_reset = st.columns()
    with col_reset:
        if st.button("🔧 データを完全初期化", type="secondary", use_container_width=True, key="rename_top_reset_btn"):
            current_pg = st.session_state.current_page
            st.session_state.clear()
            st.session_state.current_page = current_pg
            st.rerun()

    st.write("※このデモは画面上だけで完結します。実際のファイルやフォルダは作成されません。")
    st.markdown("---")

    # --- セッション状態の初期化 ---
    if "step" not in st.session_state:
        st.session_state.step = 1
    if "virtual_files" not in st.session_state:
        st.session_state.virtual_files = [] 
    if "rename_format" not in st.session_state:
        st.session_state.rename_format = "[企業名]_[書類名]_[日付]"

    # ==========================================
    # 【ステップ1】PDFファイルの生成（画面上のみ）
    # ==========================================
    st.subheader("1️⃣ 実験用のテストPDFファイルを自動生成する")

    if st.session_state.step == 1:
        generate_btn = st.button("📄 テストPDFファイルを50個自動生成する", type="primary", key="gen_pdf_btn_unique")

        if generate_btn:
            generated_list = []
            while len(generated_list) < 50:
                date_str = get_random_date()
                company = random.choice(COMPANIES)
                doc = random.choice(DOC_TYPES) 
                
                file_data = {"date": date_str, "company": company, "doc": doc}
                if file_data not in generated_list:
                    generated_list.append(file_data)
                    
                st.session_state.virtual_files = generated_list
                st.session_state.step = 2
                st.rerun()
    else:
        st.success(f"✅ 画面上にテストPDFファイルを50個作成しました！")

    # ==========================================
    # 【ステップ2】リネームフォーマットと一括変更
    # ==========================================
    if st.session_state.step >= 2:
        st.markdown("---")
        st.subheader("2️⃣ 新しいファイル名の法則を入力して、一括変更する")
        
        original_names = []
        for f in st.session_state.virtual_files:
            parts = [f['date'], f['company'], f['doc']]
            random.shuffle(parts)
            original_names.append("-".join(parts) + ".pdf")
        
        if st.session_state.step == 2:
            with st.expander(f"📦 現在の元のファイル一覧 (50個) を見る"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div translate="no" style="line-height:1.8;">' + "<br>".join([f"📄 {name}" for name in original_names[:25]]) + '</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div translate="no" style="line-height:1.8;">' + "<br>".join([f"📄 {name}" for name in original_names[25:]]) + '</div>', unsafe_allow_html=True)
                
            st.session_state.rename_format = st.text_input(
                "新しいファイル名のフォーマットを入力してください：",
                value=st.session_state.rename_format,
                help="[企業名] [書類名] [日付] と区切り文字（_）を組み合わせてください。",
                key="rename_fmt_input_final"
            )
            
            rename_btn = st.button("📝 ファイル名を一括変更する", type="primary", key="rename_exec_btn_final")
            
            if rename_btn and st.session_state.rename_format:
                st.session_state.step = 3
                st.rerun()
        else:
            st.success(f"✅ すべてのファイル名を 「{st.session_state.rename_format}」 に一括変更しました！")

    # ==========================================
    # 【ステップ3・4】ファイル仕分けの実行
    # ==========================================
    if st.session_state.step >= 3:
        st.markdown("---")
        st.subheader("3️⃣ 自動フォルダ仕分けの構造を設定して、実行する")
        
        main_col1, main_col2 = st.columns(2)
        
        with main_col1:
            st.write("#### 🛠️ 階層のルールを選択")
            folder_layer1 = st.selectbox(
                "📁 第1階層（親フォルダになる要素）",
                ["企業名", "書類名", "日付"],
                index=0,
                key="layer1_select_final"
            )
            
            layer2_options = ["なし", "企業名", "書類名", "日付"]
            if folder_layer1 in layer2_options:
                layer2_options.remove(folder_layer1)
                
            folder_layer2 = st.selectbox(
                "┗ 📁 第2階層（その中に作る子フォルダ）",
                layer2_options,
                index=0,
                key="layer2_select_final"
            )
            
        with main_col2:
            st.write("#### 📂 完成するツリー構造（プレビュー）")
            sample_data = {"company": "Google", "doc": "請求書", "date": "202501"}
            
            def get_sample_value(label):
                if label == "企業名": return sample_data["company"]
                if label == "書類名": return sample_data["doc"]
                if label == "日付": return sample_data["date"]
                return ""
                
            p_val1 = get_sample_value(folder_layer1)
            p_val2 = get_sample_value(folder_layer2) if folder_layer2 != "なし" else None
            
            sample_filename = st.session_state.rename_format.replace("[企業名]", sample_data["company"]).replace("[書類名]", sample_data["doc"]).replace("[日付]", sample_data["date"]) + ".pdf"
            
            visual_tree = "📁 出力先フォルダ\n"
            visual_tree += f"┗ 📁 {p_val1} （{folder_layer1}フォルダ）\n"
            if p_val2:
                visual_tree += f"   ┗ 📁 {p_val2} （{folder_layer2}フォルダ）\n"
                visual_tree += f"      ┗ 📄 {sample_filename}\n"
                visual_tree += f"      ┗ 📄 ...（他の該当ファイル群）"
            else:
                visual_tree += f"   ┗ 📄 {sample_filename}\n"
                visual_tree += f"   ┗ 📄 ...（他の該当ファイル群）"
                
            st.info("選択肢を変更すると、以下の構造にリアルタイムで変化します：")
            st.code(visual_tree, language="text")

        # 階層ごとにファイルを分類する辞書を作成
        explorer_tree = {}
        just_names = []
        folder_log = {}
        
        for f in st.session_state.virtual_files:
            n = st.session_state.rename_format.replace("[企業名]", f["company"]).replace("[書類名]", f["doc"]).replace("[日付]", f["date"]) + ".pdf"
            just_names.append(f"📄 {n}")
            
            def get_value_by_label(label):
                if label == "企業名": return f["company"]
                if label == "書類名": return f["doc"]
                if label == "日付": return f["date"]
                return None

            val1 = get_value_by_label(folder_layer1)
            val2 = get_value_by_label(folder_layer2) if folder_layer2 != "なし" else None
            
            # グラフ用の集計文字列
            if val1 and val2:
                display_folder = f"{val1} ➔ {val2}"
            elif val1:
                display_folder = f"{val1}"
            else:
                display_folder = "その他"
            folder_log[display_folder] = folder_log.get(display_folder, 0) + 1

            # エクスプローラー用のデータ格納
            if val1 not in explorer_tree:
                explorer_tree[val1] = {}
            
            if val2:
                if val2 not in explorer_tree[val1]:
                    explorer_tree[val1][val2] = []
                explorer_tree[val1][val2].append(n)
            else:
                if "__files__" not in explorer_tree[val1]:
                    explorer_tree[val1]["__files__"] = []
                explorer_tree[val1]["__files__"].append(n)
        # --- ステップ3：仕分け実行前 ---
        if st.session_state.step == 3:
            st.markdown("---")
            with st.expander(f"✨ 名前が綺麗になったファイル一覧 (50個) を見る"):
                sorted_just_names = sorted(just_names)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div translate="no" style="line-height:1.8;">' + "<br>".join(sorted_just_names[:25]) + '</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div translate="no" style="line-height:1.8;">' + "<br>".join(sorted_just_names[25:]) + '</div>', unsafe_allow_html=True)
                
            sort_btn = st.button("🚀 このフォルダ構造で一括仕分けを実行する", type="primary", key="sort_run_btn_final")
            if sort_btn:
                st.session_state.step = 4
                st.rerun()

        # ==========================================
        # 👑 【ステップ4】仕分け完了・レポート表示（こだわりUI！）
        # ==========================================
        if st.session_state.step == 4:
            st.success(f"🎉 完璧です！計 50 個のPDFを画面上の仮想フォルダへ綺麗に仕分けました！")
            
            st.write("### 📂 仮想フォルダ・エクスプローラー")
            st.info("💡 フォルダをクリックすると、中に仕分けられたファイル一覧を展開して確認できます！")
            
            r_col1, r_col2 = st.columns([6, 4]) # エクスプローラー側を少し広めにする
            
            with r_col1:
                st.markdown('<div translate="no">', unsafe_allow_html=True)
                
                # 💡 親フォルダをループ
                for key1 in sorted(explorer_tree.keys()):
                    with st.expander(f"📁 {key1}"):
                        
                        # 第2階層（子フォルダ）がある場合
                        if folder_layer2 != "なし":
                            for key2 in sorted(explorer_tree[key1].keys()):
                                # 子フォルダをインデント付きの空間（入れ子）で表現
                                with st.container():
                                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;📂 **{key2}**")
                                    files = sorted(explorer_tree[key1][key2])
                                    # ファイル一覧を少し引っ込めて並べる
                                    file_text = "<br>".join([f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;📄 {f}" for f in files])
                                    st.markdown(f'<div style="line-height:1.6; color:#555;">{file_text}</div>', unsafe_allow_html=True)
                                    st.write("") # 隙間あけ
                                    
                        # 子フォルダがなく、親の直下にファイルがある場合
                        else:
                            files = sorted(explorer_tree[key1].get("__files__", []))
                            file_text = "<br>".join([f"&nbsp;&nbsp;&nbsp;&nbsp;📄 {f}" for f in files])
                            st.markdown(f'<div style="line-height:1.6; color:#555;">{file_text}</div>', unsafe_allow_html=True)
                            
                st.markdown('</div>', unsafe_allow_html=True)
                
            with r_col2:
                st.write("#### 📊 仕分け統計データ")
                st.bar_chart(folder_log)
                
            st.markdown("---")
            # 💡 keyの重複バグを防ぐ専用マーク付きボタン
            if st.button("🔄 もう一度最初から実験する", type="primary", key="rename_restart_btn_final"):
                st.session_state.step = 1
                st.session_state.virtual_files = []
                st.rerun()

if __name__ == "__main__":
    main()

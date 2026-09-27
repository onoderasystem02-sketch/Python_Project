import json
import os
import sys
import importlib
import streamlit as st
import openpyxl
import pdfplumber
import io

def main():
    st.title("📁 請求書一括データ転記")
    st.caption("転記先のエクセルファイルと、処理したいPDFファイルを選択して一括転記を実行します。")
    st.markdown("---")

    rules_file = "invoice_rules.json"

    # ==========================================
    # ① 転記先エクセルのアップロード
    # ==========================================
    st.subheader("1. 転記先エクセルの選択")
    uploaded_excel = st.file_uploader(
        "転記先のエクセルファイル(.xlsx / .xlsm)を選択してください", 
        type=["xlsx", "xlsm"], 
        key="transfer_excel_uploader"
    )

    sheet_names = ["シートを選択してください"]
    selected_sheet = "シートを選択してください"

    if uploaded_excel is not None:
        try:
            wb_temp = openpyxl.load_workbook(io.BytesIO(uploaded_excel.getvalue()), read_only=True, keep_vba=True)
            sheet_names = wb_temp.sheetnames
            wb_temp.close()
        except Exception as e:
            st.error(f"❌ エクセルファイルの解析に失敗しました: {e}")

    selected_sheet = st.selectbox("★ 書き込みシートを選択してください", options=sheet_names, key="transfer_sheet_select")

    # ==========================================
    # ② 処理するPDFファイルのアップロード（複数可）
    # ==========================================
    st.write("---")
    st.subheader("2. 処理するPDFファイルの選択")
    uploaded_pdfs = st.file_uploader(
        "処理するPDFファイルをすべて選択してください（複数選択可）", 
        type=["pdf"], 
        accept_multiple_files=True, 
        key="transfer_pdf_uploader"
    )

    if uploaded_pdfs:
        st.info(f"💡 現在 {len(uploaded_pdfs)} 個のPDFファイルが選択されています。")

    # ==========================================
    # 🚀 全自動転記の一括実行
    # ==========================================
    st.write("---")
    
    if st.button("🚀 全自動転記を一括実行する！", type="primary", use_container_width=True):
        if uploaded_excel is None:
            st.warning("⚠️ 転記先のエクセルファイルを選択してください。")
            return
        if not uploaded_pdfs:
            st.warning("⚠️ 処理するPDFファイルを1つ以上選択してください。")
            return
        if selected_sheet == "シートを選択してください":
            st.warning("⚠️ 書き込み対象のシートを選択してください。")
            return
        if not os.path.exists(rules_file):
            st.warning("⚠️ 転記ルールファイル(`invoice_rules.json`)が見つかりません。ルール作成パネルで先にルールを保存してください。")
            return

        with open(rules_file, "r", encoding="utf-8") as f:
            rules = json.load(f)

        ok = 0
        errs = []

        with st.spinner("🔄 PDFのデータを解析してエクセルへ転記中..."):
            try:
                # 💡 メモリ上でエクセルを開く
                excel_bytes = uploaded_excel.getvalue()
                wb = openpyxl.load_workbook(io.BytesIO(excel_bytes), keep_vba=True)
                sh = wb[selected_sheet]

                for p_file in uploaded_pdfs:
                    p_name = p_file.name
                    try:
                        with pdfplumber.open(io.BytesIO(p_file.getvalue())) as pdf:
                            first_page = pdf.pages[0]
                            co_nm, rd = None, None

                            for name, rdata in rules.items():
                                c = rdata.get("company_coords")
                                if c:
                                    txt = first_page.crop((c["x0"] - 5, c["top"] - 5, c["x1"] + 5, c["bottom"] + 5)).extract_text() or ""
                                    if name in txt: 
                                        co_nm, rd = name, rdata
                                        break
                            
                            if not co_nm:
                                errs.append(f"❌ {p_name}: 会社名または転記ルールがシステムに未登録です。")
                                continue

                            row_idx = rd["start_row"]
                            cols = rd["detail_columns"]
                            check_col = cols.get("項目")
                            if not check_col:
                                for c_val in cols.values():
                                    if c_val: 
                                        check_col = c_val
                                        break

                            if check_col:
                                col_num = openpyxl.utils.column_index_from_string(check_col)
                                while sh.cell(row=row_idx, column=col_num).value is not None:
                                    row_idx += 1

                            words = first_page.extract_words()
                            kws = rd["detail_keywords"]
                            h_y, x_pos = None, {}
                            base_kw = kws.get("項目", "")

                            for w in words:
                                if base_kw and base_kw in w["text"]: 
                                    h_y = w["top"]
                                    break
                            if h_y is None:
                                errs.append(f"❌ {p_name}: 見出し未検出")
                                continue

                            for f_key, kw in kws.items():
                                if not kw: 
                                    continue
                                for w in words:
                                    if abs(w["top"] - h_y) < 8 and kw in w["text"]: 
                                        x_pos[f_key] = (w["x0"], w["x1"])
                                        break

                            rows_data = {}
                            for w in words:
                                if (w["top"] - h_y) > 10 and not any(x in w["text"] for x in ["合計", "小計", "御中"]):
                                    found = False
                                    for sy in rows_data.keys():
                                        if abs(w["top"] - sy) < 5: 
                                            rows_data[sy].append(w)
                                            found = True
                                            break
                                    if not found: 
                                        rows_data[w["top"]] = [w]

                            col_indexes = {f_key: openpyxl.utils.column_index_from_string(c) for f_key, c in cols.items() if c}

                            for y in sorted(rows_data.keys()):
                                r_words = rows_data[y]
                                row_values = {}

                                for f_key, ex_c in cols.items():
                                    if f_key == "会社名": 
                                        continue
                                    if not ex_c or f_key not in x_pos: 
                                        continue
                                    k_x0, k_x1 = x_pos[f_key]
                                    pts = [rw["text"] for rw in r_words if (k_x0 - 3) <= rw["x0"] <= (k_x1 + 3) or (k_x0 - 3) <= rw["x1"] <= (k_x1 + 3)]
                                    if pts:
                                        text_val = "".join(pts).strip()
                                        if "▲" in text_val:
                                            text_val = text_val.replace("▲", "－")
                                        row_values[f_key] = text_val

                                qty_val = row_values.get("数量", "")
                                unit_val = row_values.get("単位", "")
                                unit_keyword = kws.get("単位", "")
                                if qty_val and unit_keyword and (unit_keyword in qty_val):
                                    row_values["模量"] = qty_val.replace(unit_keyword, "").strip()
                                    if not unit_val or unit_val == "": 
                                        row_values["単位"] = unit_keyword

                                if "会社名" in col_indexes:
                                    row_values["会社名"] = co_nm

                                wrote = False
                                for f_key, val in row_values.items():
                                    if f_key in col_indexes:
                                        sh.cell(row=row_idx, column=col_indexes[f_key]).value = val
                                        wrote = True
                                if wrote: 
                                    row_idx += 1
                            ok += 1
                    except Exception as e: 
                        errs.append(f"❌ {p_name}: エラー({e})")
                
                # 💡 メモリ上でデータをセーブしてストリームに落とし込む
                out_stream = io.BytesIO()
                wb.save(out_stream)
                wb.close()
                out_bytes = out_stream.getvalue()

            # 💡 【移植】エクセルが開きっぱなしの時のエラーハンドリング
            except PermissionError:
                st.error(f"📁 ファイルエラー: Excelファイルが現在サーバー側、またはローカル側で開かれている、もしくは書き込み権限がないため実行できません。")
                return
            
            # 💡 その他の全体的なエラーハンドリング
            except Exception as e:
                st.error(f"❌ 失敗: {e}")
                return

            # ==========================================
            # 📥 【移植】処理結果のメッセージレポート＆ダウンロード
            # ==========================================
            res = f"処理が完了しました。\n\n🎉 転記成功: {ok}件\n"
            
            if errs:
                # 一部エラーがあった場合の警告表示
                st.warning(f"⚠️ 処理完了（未登録・エラーあり）\n\n{res}")
                with st.expander("⚠️ 【未処理のファイル一覧はこちら】"):
                    for err in errs:
                        st.write(err)
            else:
                # すべて成功した場合の大成功表示
                st.success(f"🌟 大成功！\n\n{res}すべてのファイルを正常に処理しました。")

            # 💡 ダウンロードボタン（このボタンを押して手元に転記済みのエクセルを保存します）
            st.download_button(
                label="📥 転記済みのエクセルファイルをダウンロードする",
                data=out_bytes,
                file_name=f"転記完了_{uploaded_excel.name}",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

if __name__ == "__main__":
    main()

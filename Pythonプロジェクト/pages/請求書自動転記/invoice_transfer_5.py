import json, os, glob
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import openpyxl, pdfplumber

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class InvoiceAutoTransferApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("【その2】invoice_transfer.py - 一括転記システム")
        self.geometry("600x520")
        self.rules_file = "invoice_rules.json"
        self.excel_path = ""
        self.pdf_paths = []

        ctk.CTkLabel(self, text="📁 請求書一括データ転記", font=("Arial", 16, "bold"), text_color="black").pack(pady=20)
        ctk.CTkButton(self, text="① 転記先エクセル(.xlsx / .xlsm)を選択", fg_color="#1f538d", text_color="white", command=self.sel_ex).pack(pady=10)
        self.lbl_ex = ctk.CTkLabel(self, text="エクセル未選択", text_color="#555555")
        self.lbl_ex.pack()

        f_ex = ctk.CTkFrame(self, fg_color="#e0e0e0") 
        f_ex.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(f_ex, text="★ 書き込みシート:", font=("Arial", 11, "bold"), text_color="black").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.sel_sh = ctk.CTkComboBox(f_ex, values=["シートを選択してください"], width=220, fg_color="#ffffff", text_color="#888888", dropdown_fg_color="#ffffff", dropdown_text_color="#000000", font=("Arial", 12, "bold"), command=self.on_sh)
        self.sel_sh.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkButton(self, text="② 処理するPDFファイルを選択", fg_color="#1f538d", text_color="white", command=self.sel_pdfs).pack(pady=10)
        self.lbl_pdf = ctk.CTkLabel(self, text="PDF未選択", text_color="#555555")
        self.lbl_pdf.pack()

        ctk.CTkButton(self, text="🚀 全自動転記を一括実行する！", fg_color="green", hover_color="darkgreen", text_color="white", font=("Arial", 14, "bold"), height=40, command=self.run).pack(pady=25)

    def sel_ex(self):
        fp = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xlsm")])
        if fp:
            self.excel_path = os.path.normpath(fp)
            self.lbl_ex.configure(text=os.path.basename(fp), text_color="black")
            wb = openpyxl.load_workbook(self.excel_path, read_only=True, keep_vba=True)
            sn = wb.sheetnames
            wb.close()
            self.sel_sh.configure(values=sn)
            self.sel_sh.set("シートを選択してください")
            self.sel_sh.configure(text_color="#888888")

    def on_sh(self, val):
        self.sel_sh.configure(text_color="#888888" if "選択して" in val else "#000000")

    def sel_pdfs(self):
        fs = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if fs:
            self.pdf_paths = list(fs)
            self.lbl_pdf.configure(text=f"{len(fs)} 個のPDFを選択中", text_color="black")

    def run(self):
        sh_nm = self.sel_sh.get()
        if not self.excel_path or not self.pdf_paths or "選択して" in sh_nm or not os.path.exists(self.rules_file):
            messagebox.showwarning("警告", "必要なファイルを正しく選択してください。")
            return

        with open(self.rules_file, "r", encoding="utf-8") as f: rules = json.load(f)
        ok, errs = 0, []

        try:
            wb = openpyxl.load_workbook(self.excel_path, keep_vba=True)
            sh = wb[sh_nm]
            for p_path in self.pdf_paths:
                p_nm = os.path.basename(p_path)
                try:
                    with pdfplumber.open(p_path) as pdf:
                        first_page = pdf.pages[0]
                        co_nm, rd = None, None

                        for name, rdata in rules.items():
                            c = rdata.get("company_coords")
                            if c:
                                txt = first_page.crop((c["x0"] - 5, c["top"] - 5, c["x1"] + 5, c["bottom"] + 5)).extract_text() or ""
                                if name in txt: co_nm, rd = name, rdata; break
                        
                        if not co_nm:
                            errs.append(f"❌ {p_nm}: 会社名または転記ルールがシステムに未登録です。")
                            continue

                        row_idx = rd["start_row"]
                        cols = rd["detail_columns"]
                        check_col = cols.get("項目")
                        if not check_col:
                            for c_val in cols.values():
                                if c_val: check_col = c_val; break

                        # 自動追記のための空行探し
                        if check_col:
                            col_num = openpyxl.utils.column_index_from_string(check_col)
                            while sh.cell(row=row_idx, column=col_num).value is not None:
                                row_idx += 1

                        # 文字の縦列スキャン
                        words = first_page.extract_words()
                        kws = rd["detail_keywords"]
                        h_y, x_pos = None, {}
                        base_kw = kws.get("項目", "")

                        for w in words:
                            if base_kw and base_kw in w["text"]: h_y = w["top"]; break
                        if h_y is None:
                            errs.append(f"❌ {p_nm}: 見出し未検出")
                            continue

                        for f, kw in kws.items():
                            if not kw: continue
                            for w in words:
                                if abs(w["top"] - h_y) < 8 and kw in w["text"]: x_pos[f] = (w["x0"], w["x1"]); break

                        rows_data = {}
                        for w in words:
                            if (w["top"] - h_y) > 10 and not any(x in w["text"] for x in ["合計", "小計", "御中"]):
                                found = False
                                for sy in rows_data.keys():
                                    if abs(w["top"] - sy) < 5: rows_data[sy].append(w); found = True; break
                                if not found: rows_data[w["top"]] = [w]

                        # エクセル列を数値化
                        col_indexes = {f: openpyxl.utils.column_index_from_string(c) for f, c in cols.items() if c}

                        for y in sorted(rows_data.keys()):
                            r_words = rows_data[y]
                            row_values = {}

                            for f, ex_c in cols.items():
                                if f == "会社名": continue # 会社名は個別ループで後述
                                if not ex_c or f not in x_pos: continue
                                k_x0, k_x1 = x_pos[f]
                                pts = [rw["text"] for rw in r_words if (k_x0 - 3) <= rw["x0"] <= (k_x1 + 3) or (k_x0 - 3) <= rw["x1"] <= (k_x1 + 3)]
                                if pts:
                                    text_val = "".join(pts).strip()
                                    # ★★★【新設：文字置換ロジック】「▼」が含まれていたら「－」に自動変換 ★★★
                                    if "▲" in text_val:
                                        text_val = text_val.replace("▲", "－")
                                    row_values[f] = text_val

                                

                            # 数量と単位の分離ロジック
                            qty_val = row_values.get("数量", "")
                            unit_val = row_values.get("単位", "")
                            unit_keyword = kws.get("単位", "")
                            if qty_val and unit_keyword and (unit_keyword in qty_val):
                                row_values["数量"] = qty_val.replace(unit_keyword, "").strip()
                                if not unit_val or unit_val == "": row_values["単位"] = unit_keyword

                            # ★★★ 会社名を明細行の指定された列（例：A列）に毎行並べて書き込む ★★★
                            if "会社名" in col_indexes:
                                row_values["会社名"] = co_nm

                            wrote = False
                            for f, val in row_values.items():
                                if f in col_indexes:
                                    sh.cell(row=row_idx, column=col_indexes[f]).value = val
                                    wrote = True
                            if wrote: row_idx += 1
                        ok += 1
                except Exception as e: errs.append(f"❌ {p_name}: エラー({e})")
            wb.save(self.excel_path)
            wb.close()

        except PermissionError:
            #エクセルファイルが開きっぱなしの時に出現
            messagebox.showerror(
                "ファイルエラー",
                f"Excelファイル「{os.path.basename(self.excel_path)}」が現在開かれてるため、実行できません。\n\nお手数ですが、一度Excelファイルを閉じてから実行してください。",
          )
            return
        
        except Exception as e:
            messagebox.showerror("エラー", f"失敗: {e}")
            return

        res = f"処理が完了しました。\n\n🎉 転記成功: {ok}件\n"
        if errs:
            res += "\n⚠️ 【未処理のファイルがあります】\n" + "\n".join(errs)
            messagebox.showwarning("処理完了（未登録あり）", res)
        else:
            messagebox.showinfo("大成功！", res + "すべてのファイルを正常に処理しました。")

if __name__ == "__main__":
    InvoiceAutoTransferApp().mainloop()

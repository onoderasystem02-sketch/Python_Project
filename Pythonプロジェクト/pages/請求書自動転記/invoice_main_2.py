import json, os, glob
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import pdfplumber

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class InvoiceRuleMaker(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("【その1】invoice_main.py - ルール作成パネル")
        self.geometry("1400x800")
        self.pdf_path, self.clicked_text, self.clicked_coords = "", "", None
        self.tk_image, self.rules_file = None, "invoice_rules.json"

        # 操作バー
        self.top = ctk.CTkFrame(self, height=60)
        self.top.pack(side="top", fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.top, text="🛠️ マッピングルール作成ツール (invoice_main)", font=("Arial", 14, "bold")).pack(side="left", padx=15)
        ctk.CTkButton(self.top, text="ルールを保存！", fg_color="green", hover_color="darkgreen", text_color="white", command=self.save_rules).pack(side="right", padx=15)

        # メイン
        self.split = ctk.CTkFrame(self, fg_color="transparent")
        self.split.pack(fill="both", expand=True)
        self.left = ctk.CTkFrame(self.split, width=500, fg_color="#f5f5f5")
        self.left.pack(side="left", fill="both", padx=5, pady=5)

        # PDF選択
        f_pdf = ctk.CTkFrame(self.left, fg_color="#e0e0e0")
        f_pdf.pack(fill="x", padx=15, pady=10)
        ctk.CTkButton(f_pdf, text="📄 PDFサンプル取込", text_color="white", command=self.select_pdf).pack(side="left", padx=10, pady=10)
        self.lbl_pdf = ctk.CTkLabel(f_pdf, text="PDF未選択", text_color="#333333")
        self.lbl_pdf.pack(side="left", padx=5)

        # 行入力
        f_row = ctk.CTkFrame(self.left, fg_color="transparent")
        f_row.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(f_row, text="📊 エクセル書き込み開始行：", text_color="black").pack(side="left")
        self.ent_row = ctk.CTkEntry(f_row, width=60, placeholder_text="5", fg_color="white", text_color="black")
        self.ent_row.pack(side="left")

        # 選択中文字
        f_chk = ctk.CTkFrame(self.left, fg_color="#ffffff", border_width=1, border_color="#cccccc")
        f_chk.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(f_chk, text="💡 選択中:", text_color="black").pack(side="left", padx=10, pady=5)
        self.lbl_chk = ctk.CTkLabel(f_chk, text="（未選択）", text_color="#1f538d", font=("Arial", 13, "bold"))
        self.lbl_chk.pack(side="left", pady=5)

        # グリッド配置
        self.f_g = ctk.CTkFrame(self.left, fg_color="transparent")
        self.f_g.pack(fill="both", expand=True, padx=15, pady=10)
        headers = ["項目名", "PDF見出し確認", "エクセル列"]
        for c, h in enumerate(headers):
            ctk.CTkLabel(self.f_g, text=h, font=("Arial", 11, "bold"), text_color="black").grid(row=0, column=c if c < 2 else 3, padx=5, pady=2)

        self.fields = ["会社名", "項目", "数量", "単位", "金額", "税込金額", "税率"]
        self.ents_val, self.ents_col, self.saved_co = {}, {}, None

        for i, f in enumerate(self.fields, start=1):
            ctk.CTkLabel(self.f_g, text=f, width=70, anchor="w", text_color="black").grid(row=i, column=0, padx=5, pady=8, sticky="w")
            
            # ★ 会社名も他と同じデザイン・プレースホルダーに統一
            p_text = "会社名そのものを選択" if f == "会社名" else f"「{f}」の見出しを選択"
            v = ctk.CTkEntry(self.f_g, width=150, fg_color="white", text_color="black", placeholder_text=p_text)
            v.grid(row=i, column=1, padx=5, pady=8)
            self.ents_val[f] = v
            
            ctk.CTkButton(self.f_g, text="配置", width=45, fg_color="#333333", text_color="white", command=lambda nm=f: self.apply_f(nm)).grid(row=i, column=2, padx=2, pady=8)
            
            c = ctk.CTkEntry(self.f_g, width=80, placeholder_text="例: A", fg_color="white", text_color="black")
            c.grid(row=i, column=3, padx=5, pady=8)
            self.ents_col[f] = c

        # 右プレビュー
        self.right = ctk.CTkFrame(self.split)
        self.right.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        scr = ctk.CTkScrollableFrame(self.right)
        scr.pack(fill="both", expand=True)
        self.cv = tk.Canvas(scr, bg="#e0e0e0")
        self.cv.pack(fill="both", expand=True)

    def select_pdf(self):
        fp = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not fp: return
        self.pdf_path = fp
        self.lbl_pdf.configure(text=os.path.basename(fp), text_color="black")
        self.cv.delete("all")
        try:
            with pdfplumber.open(fp) as pdf:
                page = pdf.pages[0]
                ren = page.to_image(resolution=130)
                img = ren.original
                self.cv.config(width=img.width, height=img.height)
                self.tk_image = ImageTk.PhotoImage(img)
                self.cv.create_image(0, 0, anchor="nw", image=self.tk_image)
                sx, sy = img.width / float(page.width), img.height / float(page.height)
                for w in page.extract_words():
                    x0, y0, x1, y1 = w["x0"]*sx, w["top"]*sy, w["x1"]*sx, w["bottom"]*sy
                    r_id = self.cv.create_rectangle(x0, y0, x1, y1, outline="red", width=1, fill="red", stipple="gray12")
                    self.cv.tag_bind(r_id, "<Button-1>", lambda e, wd=w: self.click_w(wd))
            messagebox.showinfo("成功", "PDF解析完了！")
        except Exception as e:
            messagebox.showerror("エラー", f"読込失敗: {e}")

    def click_w(self, wd):
        self.clicked_text = wd["text"]
        self.clicked_coords = {"x0": round(wd["x0"], 1), "top": round(wd["top"], 1), "x1": round(wd["x1"], 1), "bottom": round(wd["bottom"], 1)}
        self.lbl_chk.configure(text=f"「 {wd['text']} 」", text_color="#1f538d")

    def apply_f(self, nm):
        if not self.clicked_text: return
        self.ents_val[nm].delete(0, tk.END)
        self.ents_val[nm].insert(0, self.clicked_text)
        if nm == "会社名": self.saved_co = self.clicked_coords

    def save_rules(self):
        co_key = self.ents_val["会社名"].get().strip()
        r_num = self.ent_row.get().strip()
        if not co_key or not r_num: return
        ex_r = {}
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, "r", encoding="utf-8") as f: ex_r = json.load(f)
            except: pass
        
        # ★ 会社名も他の項目と並列で保存するシンプルな構造にアップデート
        ex_r[co_key] = {
            "start_row": int(r_num),
            "company_coords": self.saved_co,
            "detail_keywords": {k: self.ents_val[k].get().strip() for k in self.fields if k != "会社名"},
            "detail_columns": {k: self.ents_col[k].get().strip().upper() for k in self.fields} # 会社名も含める
        }
        with open(self.rules_file, "w", encoding="utf-8") as f: json.dump(ex_r, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("成功", f"『{co_key}』のルールを保存しました！")

if __name__ == "__main__":
    InvoiceRuleMaker().mainloop()

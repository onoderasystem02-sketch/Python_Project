import os
import sys
import importlib
import streamlit as st

# ==========================================
# ⚙️ 画面基本設定 & 翻訳バグ対策
# ==========================================
st.set_page_config(page_title="社内DX・自作ツールポータル", page_icon="🖥️", layout="wide")

# 💡 翻訳バグブロック ＆ 左側サイドメニューを完全に消すCSS
st.markdown(
    """
    <html lang="ja"><head><meta name="google" content="notranslate"></head></html>
    <style>
        /* サイドメニューと開閉ボタンを強制非表示 */
        [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        /* メインコンテンツを横いっぱいに広げて綺麗に見せる */
        [data-testid="stMainBlockContainer"] {
            padding-left: 5rem;
            padding-right: 5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# 💡 写真の通り、pagesフォルダーからappsフォルダーへ名前変更した前提のパス設定
APPS_DIR = os.path.join(os.path.dirname(__file__), "apps")

# ==========================================
# 🔍 スクショのフォルダ構造を正確に自動検出するロジック
# ==========================================
def get_available_apps():
    apps_dict = {
        "01_請求書自動転記": {"module_name": "invoice_main_2", "folder_path": os.path.join(APPS_DIR, "01_請求書自動転記")},
        "02_Excel修復ツール": {"module_name": "excel_fixer_4", "folder_path": os.path.join(APPS_DIR, "02_Excel修復ツール")},
        "03_ファイル名変更": {"module_name": "rename_split3", "folder_path": os.path.join(APPS_DIR, "03_ファイル名変更")}
    }
    
    # 実際にフォルダが存在するものだけを有効化
    valid_apps = {}
    for display_name, info in apps_dict.items():
        if os.path.exists(info["folder_path"]):
            valid_apps[display_name] = info
    return valid_apps

apps_list = get_available_apps()

# ==========================================
# 🔄 画面の状態管理（Session State）
# ==========================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 ホーム"

# ==========================================
# 🏠 ホーム画面（サイドメニューなし・3つのカード形式）
# ==========================================
if st.session_state.current_page == "🏠 ホーム":
    st.title("🖥️ 社内DX・自作ツールポータルへようこそ")
    st.write("利用したいアプリケーションのカードをタップして起動してください。")
    st.markdown("---")

    # 💡 3つのカラムに写真を再現した色付きカードを配置
    col1, col2, col3 = st.columns(3)

    # --- 🟥 1つ目のカード：請求書自動転記 ---
    with col1:
        # ※背景画像を敷く場合は background-image: url('画像のURL'); を追加してください
        st.markdown(
            """
            <div style="border: 2px solid #ff4b4b; border-radius: 15px; padding: 20px; text-align: center; min-height: 160px; background-color: #fff2f2; background-size: cover; background-position: center;">
                <span style="font-size: 40px;">🚀</span>
                <h3 style="margin-top: 10px; color: #ff4b4b; font-size: 20px;">01. 請求書自動転記</h3>
                <p style="font-size: 13px; color: #555;">invoice_main_2 を起動し、請求データの自動転記を行います。</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("このアプリを起動 ➔", key="click_invoice", use_container_width=True):
            if "01_請求書自動転記" in apps_list:
                st.session_state.current_page = "01_請求書自動転記"
                st.rerun()
            else:
                st.error("フォルダ 『01_請求書自動転記』 が見つかりません。")

    # --- 🟦 2つ目のカード：Excel修復ツール ---
    with col2:
        st.markdown(
            """
            <div style="border: 2px solid #1f77b4; border-radius: 15px; padding: 20px; text-align: center; min-height: 160px; background-color: #f0f7fc; background-size: cover; background-position: center;">
                <span style="font-size: 40px;">📊</span>
                <h3 style="margin-top: 10px; color: #1f77b4; font-size: 20px;">02. Excel修復ツール</h3>
                <p style="font-size: 13px; color: #555;">excel_fixer_4 を起動し、破損ファイルの破損チェックを行います。</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("このアプリを起動 ➔", key="click_fixer", use_container_width=True):
            if "02_Excel修復ツール" in apps_list:
                st.session_state.current_page = "02_Excel修復ツール"
                st.rerun()
            else:
                st.error("フォルダ 『02_Excel修復ツール』 が見つかりません。")

    # --- 🟩 3つ目のカード：ファイル名変更 ---
    with col3:
        st.markdown(
            """
            <div style="border: 2px solid #2ca02c; border-radius: 15px; padding: 20px; text-align: center; min-height: 160px; background-color: #f2fbf2; background-size: cover; background-position: center;">
                <span style="font-size: 40px;">✉️</span>
                <h3 style="margin-top: 10px; color: #2ca02c; font-size: 20px;">03. ファイル名変更</h3>
                <p style="font-size: 13px; color: #555;">rename_split3 を起動し、PDF等の一括リネームを行います。</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("このアプリを起動 ➔", key="click_rename", use_container_width=True):
            if "03_ファイル名変更" in apps_list:
                st.session_state.current_page = "03_ファイル名変更"
                st.rerun()
            else:
                st.error("フォルダ 『03_ファイル名変更』 が見つかりません。")

# ==========================================
# 🚀 各アプリケーションの安全な動的呼び出し
# ==========================================
else:
    # 💡 サイドメニューが無いため、最上部に戻るボタンを大きく配置
    if st.button("🏠 ポータルホーム（メニュー選択）に戻る", use_container_width=True):
        st.session_state.current_page = "🏠 ホーム"
        st.rerun()
        
    st.markdown("---")
    
    # 選択されたアプリのパス情報を取得
    app_info = apps_list[st.session_state.current_page]
    target_folder = app_info["folder_path"]
    target_module = app_info["module_name"]
    
    # 💡 パス問題の完全解決：Excel、JSON、サブファイルの読み込み迷子を防ぐ
    if target_folder not in sys.path:
        sys.path.insert(0, target_folder)
        
    old_cwd = os.getcwd()
    os.chdir(target_folder)
        
    try:
        # プログラムを読み込んで実行
        imported_module = importlib.import_module(target_module)
        importlib.reload(imported_module)
        imported_module.main()
        
    except AttributeError:
        st.error(f"❌ `{target_module}.py` 内に `def main():` が定義されていません。")
    except Exception as e:
        st.error(f"❌ プログラムの実行中にエラーが発生しました:\n{e}")
    finally:
        # ディレクトリ基準を元に戻す
        os.chdir(old_cwd)

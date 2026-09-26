import os
import sys
import importlib
import streamlit as st

# ==========================================
# ⚙️ 画面基本設定 & 翻訳バグ対策
# ==========================================
st.set_page_config(page_title="社内DX・自作ツールポータル", page_icon="🖥️", layout="wide")

# 💡 翻訳バグブロック ＆ 「pages」フォルダ特有の標準サイドメニューを跡形もなく完全に消し去るCSS
st.markdown(
    """
    <html lang="ja"><head><meta name="google" content="notranslate"></head></html>
    <style>
        /* 左側のサイドバー領域と開閉ボタンを完全に強制非表示にします */
        [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        /* メイン画面を横いっぱいに広げてカードを綺麗に並べます */
        [data-testid="stMainBlockContainer"] {
            padding-left: 5rem;
            padding-right: 5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# 💡 今の構成のまま「pages」フォルダの絶対パスを指定
PAGES_DIR = os.path.join(os.path.dirname(__file__), "pages")

# ==========================================
# 🔍 スクショのファイル・フォルダ構成を固定でマッピング
# ==========================================
apps_list = {
    "01_請求書自動転記": {
        "module_name": "invoice_main_2", 
        "folder_path": os.path.join(PAGES_DIR, "請求書自動転記")
    },
    "02_Excel修復ツール": {
        "module_name": "excel_fixer_4", 
        "folder_path": PAGES_DIR
    },
    "03_ファイル名変更": {
        "module_name": "rename_split3", 
        "folder_path": PAGES_DIR
    }
}

# ==========================================
# 🔄 画面の状態管理（Session State）
# ==========================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 ホーム"

# ==========================================
# 🏠 ホーム画面（色付き四角をダイレクトクリック！）
# ==========================================
if st.session_state.current_page == "🏠 ホーム":
    st.title("🖥️ 社内DX・自作ツールポータルへようこそ")
    st.write("利用したいアプリケーションの四角いカードを直接クリックして起動してください。")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    
    # 💡 共通の透明ボタン用スタイル（HTMLカードの真上に重ねるための設定）
    st.markdown(
        """
        <style>
            div.stButton > button { 
                height: 180px; 
                background-color: transparent; 
                border: none; 
                color: transparent; 
                width: 100%; 
                position: relative; 
                z-index: 2; 
            } 
            div.stButton > button:hover { 
                background-color: rgba(0,0,0,0.03); 
                border: none; 
                color: transparent; 
            }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # --- 🟥 1つ目の四角：請求書自動転記 ---
    with col1:
        st.markdown(
            """
            <div style="border: 2px solid #ff4b4b; border-radius: 15px; padding: 20px; text-align: center; min-height: 180px; background-color: #fff2f2; margin-bottom: -225px; position: relative; z-index: 1; pointer-events: none;">
                <span style="font-size: 40px;">🚀</span>
                <h3 style="margin-top: 10px; color: #ff4b4b; font-size: 20px;">01. 請求書自動転記</h3>
                <p style="font-size: 13px; color: #555; margin-top: 10px;">invoice_main_2 を起動し、請求データの自動転記を行います。</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button(" ", key="click_invoice", use_container_width=True):
            st.session_state.current_page = "01_請求書自動転記"
            st.rerun()

    # --- 🟦 2つ目の四角：Excel修復ツール ---
    with col2:
        st.markdown(
            """
            <div style="border: 2px solid #1f77b4; border-radius: 15px; padding: 20px; text-align: center; min-height: 180px; background-color: #f0f7fc; margin-bottom: -225px; position: relative; z-index: 1; pointer-events: none;">
                <span style="font-size: 40px;">📊</span>
                <h3 style="margin-top: 10px; color: #1f77b4; font-size: 20px;">02. Excel修復ツール</h3>
                <p style="font-size: 13px; color: #555; margin-top: 10px;">excel_fixer_4 を起動し、破損ファイルの破損チェックを行います。</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("  ", key="click_fixer", use_container_width=True):
            st.session_state.current_page = "02_Excel修復ツール"
            st.rerun()

    # --- 🟩 3つ目の四角：ファイル名変更 ---
    with col3:
        st.markdown(
            """
            <div style="border: 2px solid #2ca02c; border-radius: 15px; padding: 20px; text-align: center; min-height: 180px; background-color: #f2fbf2; margin-bottom: -225px; position: relative; z-index: 1; pointer-events: none;">
                <span style="font-size: 40px;">✉️</span>
                <h3 style="margin-top: 10px; color: #2ca02c; font-size: 20px;">03. ファイル名変更</h3>
                <p style="font-size: 13px; color: #555; margin-top: 10px;">rename_split3 を起動し、PDF等の一括リネームを行います。</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("   ", key="click_rename", use_container_width=True):
            st.session_state.current_page = "03_ファイル名変更"
            st.rerun()

# ==========================================
# 🚀 各アプリケーションの安全な動的呼び出し
# ==========================================
else:
    # 戻るボタンを画面上部に大きく配置
    if st.button("🏠 ポータルホーム（メニュー選択）に戻る", use_container_width=True):
        # 💡 ホームに戻る際、子画面が使っていた古いkey情報を一斉にクリアする（エラー再発防止）
        for key in list(st.session_state.keys()):
            if key not in ["current_page"]:
                del st.session_state[key]
        st.session_state.current_page = "🏠 ホーム"
        st.rerun()
        
    st.markdown("---")
    
    app_info = apps_list[st.session_state.current_page]
    target_folder = app_info["folder_path"]
    target_module = app_info["module_name"]
    
    # 💡 パス問題の解決：実行するフォルダのシステムパスを追加
    if target_folder not in sys.path:
        sys.path.insert(0, target_folder)
    if PAGES_DIR not in sys.path:
        sys.path.insert(0, PAGES_DIR)
        
    # カレントディレクトリをそのプログラムの場所に変更
    old_cwd = os.getcwd()
    os.chdir(target_folder)
        
    try:
        # 💡 【重要】リロードする前に、すでにセッションに残ってしまっている
        # 重複原因となるkey（'template'など）を一度強制削除してエラーを封じ込めます
        # ただしポータルの現在地を示す 'current_page' だけは残します
        for key in list(st.session_state.keys()):
            if key not in ["current_page"]:
                # ホーム画面用のボタン以外の古いコンポーネントキーを掃除
                if not key.startswith("click_"):
                    del st.session_state[key]

        # プログラムをインポートして実行
        imported_module = importlib.import_module(target_module)
        importlib.reload(imported_module)
        imported_module.main()
        
    except AttributeError:
        st.error(f"❌ `pages` の中にある `{target_module}.py` 内に `def main():` が定義されていません。")
    except Exception as e:
        st.error(f"❌ プログラムの実行中にエラーが発生しました:\n{e}")
    finally:
        # 他のアプリに影響が出ないよう、ディレクトリ基準を元のルートに戻す
        os.chdir(old_cwd)

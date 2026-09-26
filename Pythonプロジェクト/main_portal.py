import os
import sys
import importlib
import streamlit as st
import streamlit.components.v1 as components  # 💡 クリック検知用の機能

# ==========================================
# ⚙️ 画面基本設定 & 翻訳バグ対策
# ==========================================
st.set_page_config(page_title="社内DX・自作ツールポータル", page_icon="🖥️", layout="wide")

st.markdown(
    '<html lang="ja"><head><meta name="google" content="notranslate"></head></html>',
    unsafe_allow_html=True,
)

APPS_DIR = os.path.join(os.path.dirname(__file__), "apps")

# ==========================================
# 🔍 apps内の各フォルダから自動検出
# ==========================================
def get_available_apps():
    if not os.path.exists(APPS_DIR):
        os.makedirs(APPS_DIR)
    apps_dict = {}
    for folder_name in os.listdir(APPS_DIR):
        folder_path = os.path.join(APPS_DIR, folder_name)
        if os.path.isdir(folder_path):
            py_files = [f for f in os.listdir(folder_path) if f.endswith(".py") and not f.startswith("__")]
            if not py_files:
                continue
            main_file = None
            for f in py_files:
                if "main" in f.lower():
                    main_file = f
                    break
            if not main_file:
                main_file = py_files[0]
            module_name = main_file[:-3]
            apps_dict[folder_name] = {
                "module_name": module_name,
                "folder_path": folder_path
            }
    return apps_dict

apps_list = get_available_apps()
page_options = ["🏠 ホーム"] + list(apps_list.keys())

# ==========================================
# 🔄 画面の状態管理
# ==========================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 ホーム"

if st.session_state.current_page not in page_options:
    st.session_state.current_page = "🏠 ホーム"

# ==========================================
# 🗺️ サイドナビゲーション
# ==========================================
st.sidebar.title("メニュー")
page = st.sidebar.radio(
    "アプリケーションを選択",
    page_options,
    key="sb_page",
    index=page_options.index(st.session_state.current_page)
)
st.session_state.current_page = page

# ==========================================
# 🏠 ホーム画面（デザインされたHTMLカードをクリック可能に）
# ==========================================
if st.session_state.current_page == "🏠 ホーム":
    st.title("🖥️ 社内DX・自作ツールポータルへようこそ")
    st.write("下のカード、または左側のサイドメニューから、利用したいアプリケーションを選択してください。")
    st.markdown("---")

    if not apps_list:
        st.info("💡 `apps` フォルダの中に各アプリのフォルダを入れると、ここに自動で追加されます。")
    else:
        # 💡 ユーザーさんのカードを並べるための3カラム
        col1, col2, col3 = st.columns(3)
        
        # 検出されたフォルダ名をリスト化
        folders = list(apps_list.keys())

        # --- 🟥 カード1枚目 (01_請求書自動転記 など) ---
        with col1:
            if len(folders) > 0:
                # 💡 背景画像にする場合は、url('画像のURLやパス') に書き換えられます
                st.markdown(
                    f"""
                    <div style="border: 2px solid #ff4b4b; border-radius: 15px; padding: 20px; text-align: center; min-height: 160px; background-color: #fff2f2; background-size: cover; background-position: center;">
                        <span style="font-size: 40px;">🚀</span>
                        <h3 style="margin-top: 10px; color: #ff4b4b; font-size: 20px;">{folders[0]}</h3>
                        <p style="font-size: 13px; color: #555;">請求書の自動転記プログラムを起動します。</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                # 見えない透明なクリックボタンをカードの下に配置して、クリックを検知します
                if st.button("このアプリを起動 ➔", key="click_0", use_container_width=True):
                    st.session_state.current_page = folders[0]
                    st.rerun()

        # --- 🟦 カード2枚目 (02_Excel修復ツール など) ---
        with col2:
            if len(folders) > 1:
                st.markdown(
                    f"""
                    <div style="border: 2px solid #1f77b4; border-radius: 15px; padding: 20px; text-align: center; min-height: 160px; background-color: #f0f7fc; background-size: cover;">
                        <span style="font-size: 40px;">📊</span>
                        <h3 style="margin-top: 10px; color: #1f77b4; font-size: 20px;">{folders[1]}</h3>
                        <p style="font-size: 13px; color: #555;">Excelの破損やエラーを自動修復します。</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                if st.button("このアプリを起動 ➔", key="click_1", use_container_width=True):
                    st.session_state.current_page = folders[1]
                    st.rerun()

        # --- 🟩 カード3枚目 (03_ファイル名変更 など) ---
        with col3:
            if len(folders) > 2:
                st.markdown(
                    f"""
                    <div style="border: 2px solid #2ca02c; border-radius: 15px; padding: 20px; text-align: center; min-height: 160px; background-color: #f2fbf2; background-size: cover;">
                        <span style="font-size: 40px;">✉️</span>
                        <h3 style="margin-top: 10px; color: #2ca02c; font-size: 20px;">{folders[2]}</h3>
                        <p style="font-size: 13px; color: #555;">大量のファイル名を一括でリネームします。</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                if st.button("このアプリを起動 ➔", key="click_2", use_container_width=True):
                    st.session_state.current_page = folders[2]
                    st.rerun()

# ==========================================
# 🚀 各アプリケーションの動的呼び出し
# ==========================================
else:
    app_info = apps_list[st.session_state.current_page]
    target_folder = app_info["folder_path"]
    target_module = app_info["module_name"]
    
    if st.button("← ポータルホームに戻る", key="back_common"):
        st.session_state.current_page = "🏠 ホーム"
        st.rerun()
        
    st.markdown("---")
    
    if target_folder not in sys.path:
        sys.path.insert(0, target_folder)
        
    old_cwd = os.getcwd()
    os.chdir(target_folder)
        
    try:
        imported_module = importlib.import_module(target_module)
        importlib.reload(imported_module)
        imported_module.main()
        
    except AttributeError:
        st.error(f"❌ `{target_module}.py` 内に `def main():` が見つかりません。")
    except Exception as e:
        st.error(f"❌ アプリの実行中にエラーが発生しました:\n{e}")
    finally:
        os.chdir(old_cwd)

import streamlit as st
import openai
import os
import json

# --- 1. APIキーと基本設定 ---
client = openai.OpenAI(api_key="client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])")

st.set_page_config(page_title="NocoLde メッセージ自動生成SYSTEM", layout="wide")

# --- 2. テンプレートの定義 ---
TEMPLATE_HINTS = {
    "Instagramキャプション": "【メニュー名】：\n【価格】：\n【魅力・こだわり】：\n【期間・限定性】：",
    "スレッズ投稿": "【今日伝えたい想い】：\n【仕込みの裏側など】：",
    "公式LINE": "【イベント名】：\n【特典内容】：\n【期限】：\n【来店時に必要なこと】：",
    "Google口コミへの返信": "【お客様の褒めてくれた点】：\n【今回特に伝えてほしい感謝】：",
    "Googleビジネス": "【店舗の強み】：\n【ターゲット客層】：\n【営業時間やアクセス】：",
    "InstagramDM": "【相手との関係性】：\n【伝えたい要件】：",
    "営業向けLINE": "【相手の店名/名前】：\n【提案したい内容】：\n【メリット】：",
    "営業向けメール": "【会社名】：\n【担当者名】：\n【件名イメージ】：\n【提案内容】：",
}

# --- 3. セッション状態の初期化 (管理者情報を更新) ---
if "credentials" not in st.session_state:
    st.session_state.credentials = {
        "rapita.souhonten@gmail.com": "rapita2026", 
        "nocolde.reishin@gmail.com": "nocolde0000" # ★管理者の新しい情報
    }
if "mapping" not in st.session_state:
    st.session_state.mapping = {
        "rapita.souhonten@gmail.com": "ramen_lapita", 
        "nocolde.reishin@gmail.com": "ramen_lapita"   # 管理者もデフォルトでラピタを見れる設定
    }
if "user_input_val" not in st.session_state:
    st.session_state.user_input_val = ""

# --- 4. 認証ロジック ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 NocoLde AI SaaS Portal")
    u_id = st.text_input("店舗ID（Email）")
    u_pw = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        if u_id in st.session_state.credentials and st.session_state.credentials[u_id] == u_pw:
            st.session_state.authenticated = True
            st.session_state.user_id = u_id
            st.session_state.client_name = st.session_state.mapping[u_id]
            st.rerun()
        else:
            st.error("IDまたはパスワードが違います")
    st.stop()

# --- 5. 管理者画面 (nocolde.reishin@gmail.comのみ) ---
if st.session_state.user_id == "nocolde.reishin@gmail.com":
    st.title("🛠️ NocoLde Master Control")
    with st.expander("📝 【STEP1】新規店舗・プロンプト登録", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("🔑 アカウント情報登録")
            reg_email = st.text_input("ログイン用Email")
            reg_pass = st.text_input("ログイン用パスワード")
            reg_file = st.text_input("ファイル識別名(半角英数)", placeholder="sasaki_farm")
            reg_name = st.text_input("店舗正式名称")

        with col_b:
            st.subheader("🧠 プロンプト生成用データ")
            ref_url = st.text_input("参考URL (HPや食べログなど)")
            ref_file_upload = st.file_uploader("参考書類 (PDF/TXT等)", type=["pdf", "txt", "docx"])
            ref_manual = st.text_area("手動入力 (こだわり・店主の想いなど)", height=100)

        if st.button("🚀 店舗登録 ＆ AIプロンプト自動生成"):
            if reg_email and reg_file:
                with st.spinner("AIが提供データを分析してプロンプトを作成中..."):
                    # 簡易的なコンテクスト構築
                    context = f"店名:{reg_name}\nURL:{ref_url}\n想い:{ref_manual}"
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role":"user","content": f"{context}\n上記情報を元に、この店舗専用のSNS集客用システムプロンプトを作成してください。"}]
                    )
                    gen_p = res.choices[0].message.content
                    if not os.path.exists("prompts"): os.makedirs("prompts")
                    with open(f"prompts/{reg_file}.txt", "w", encoding="utf-8") as f: f.write(gen_p)
                    
                    st.session_state.credentials[reg_email] = reg_pass
                    st.session_state.mapping[reg_email] = reg_file
                    st.success(f"店舗「{reg_name}」の登録が完了しました！")
            else:
                st.error("Emailとファイル識別名は必須です。")
    st.markdown("---")

# --- 6. メイン利用者画面 ---
st.title(f"✨ {st.session_state.client_name} AIコンサル")
c1, c2 = st.columns([2, 1])

with c1:
    category = st.radio("カテゴリー", ["投稿内容作成", "プロフィール作成", "メッセージ作成", "メッセージ返信"], horizontal=True)
    sub_options = {
        "投稿内容作成": ["①Instagramキャプション", "②スレッズ投稿", "③X投稿", "④TikTokキャプション"],
        "プロフィール作成": ["①Instagram", "②スレッズ", "③X", "④TikTok", "⑤Googleビジネス"],
        "メッセージ作成": ["①公式LINE", "②InstagramDM", "③スレッズDM", "④営業向けLINE", "⑤営業向けメール"],
        "メッセージ返信": ["①公式LINE", "②InstagramDM", "③スレッズ", "④営業向けLINE", "⑤営業向けメール", "⑥Google口コミへの返信"]
    }
    mode = st.selectbox("詳細形式", sub_options[category])

    # テンプレボタンのロジック
    t_key = mode.strip("①②③④⑤⑥")
    if st.button("📋 マーケティング用テンプレを呼び出す"):
        st.session_state.user_input_val = TEMPLATE_HINTS.get(t_key, "")

    received_msg = st.text_area("📩 届いているメッセージ", height=100) if category == "メッセージ返信" else ""
    user_input = st.text_area("📝 生成したい内容", value=st.session_state.user_input_val, height=200)
    st.session_state.user_input_val = user_input

    if st.button("AIメッセージを生成", type="primary"):
        p_path = f"prompts/{st.session_state.client_name}.txt"
        sys_p = open(p_path, "r", encoding="utf-8").read() if os.path.exists(p_path) else "優秀なアシスタントです。"
        
        # 最終指示にマーケティング指示を強制追加
        final_q = f"{sys_p}\n\n形式:{mode}\n依頼:{user_input}\n相手メッセージ:{received_msg}\n\n※投稿のフックを3案出し、最後は必ず来店を促す強力なCTAで締めてください。"
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":final_q}]
        )
        st.subheader("✅ AI提案")
        st.write(res.choices[0].message.content)

with c2:
    st.subheader("📜 最新の生成結果")
    st.info("生成ボタンを押すとここに結果が表示されます。")

st.sidebar.button("ログアウト", on_click=lambda: st.session_state.update({"authenticated": False}))
import streamlit as st
import pandas as pd
import plotly.express as px
from itertools import combinations
import qrcode
from io import BytesIO

# === PAGE CONFIG ===
st.set_page_config(
    page_title="TTC Protein Optimizer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === INITIAL DATA & SESSION STATE ===
if 'custom_food' not in st.session_state:
    st.session_state.custom_food = []

@st.cache_data
def load_base_data():
    try:
        df = pd.read_csv("smith_clean.csv")
        mapping = {"name": "商品名", "price": "値段", "prot": "タンパク", "cat": "カテゴリ", "cal": "カロリー", "unit": "内容量"}
        df = df.rename(columns=lambda x: mapping.get(x, x))
        if "内容量" not in df.columns:
            df["内容量"] = "100g"
    except FileNotFoundError:
        rows = [
            ("ごはん(茶碗1杯)","150g",30,168,2.5,0.3,37.1,"サミット","主食"),
            ("食パン 1枚","60g",40,158,5.6,2.5,28.0,"サミット","主食"),
            ("鶏むね肉(皮なし)","100g",80,105,23.3,1.2,0.0,"サミット","タンパク質"),
            ("鶏卵 1個","60g",25,76,6.2,5.2,0.2,"サミット","タンパク質"),
            ("木綿豆腐 半丁","150g",50,72,6.6,4.2,1.6,"サミット","タンパク質"),
            ("納豆 1パック","50g",40,100,8.3,5.0,5.4,"サミット","タンパク質"),
            ("サバ缶(水煮)","150g",198,190,20.9,10.7,0.2,"サミット","タンパク質"),
            ("サラダチキン","115g",218,114,24.5,1.5,0.5,"FamilyMart","タンパク質"),
            ("ブロッコリー","100g",60,33,3.5,0.4,4.3,"サミット","野菜"),
        ]
        df = pd.DataFrame(rows, columns=["商品名","内容量","値段","カロリー","タンパク","fat","carb","store","カテゴリ"])
    return df

base_df = load_base_data()
if st.session_state.custom_food:
    custom_df = pd.DataFrame(st.session_state.custom_food)
    df = pd.concat([base_df, custom_df], ignore_index=True)
else:
    df = base_df

df["p/c_score"] = (pd.to_numeric(df["タンパク"], errors='coerce') / pd.to_numeric(df["値段"], errors='coerce') * 100).round(2)

# === GLOBAL CSS ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
html, body, [class*="css"], .stMarkdown, p, span, label, li, h1, h2, h3, h4, h5, h6 { 
    font-family: 'Noto Sans JP', sans-serif !important; 
    color: #1a4d2e !important;
}
.stApp { background: #f7f5f0; }
[data-testid="stSidebarNav"] + div, button[kind="headerNoPadding"] span, button[kind="headerNoPadding"] svg { display: none !important; }
button[kind="headerNoPadding"]::after { content: "☰"; font-size: 26px; color: #1a4d2e; font-weight: bold; visibility: visible; }
[data-testid="stSidebar"] { background-color: #f7f5f0 !important; border-right: 2px solid #1a4d2e; }
[data-testid="stSidebar"] * { color: #1a4d2e !important; }
.custom-card { background: white; padding: 20px; border-radius: 15px; border: 3px solid #1a4d2e; margin-bottom: 20px; }
.pairing-card { background: white; padding: 12px; border-radius: 10px; border: 2px solid #1a4d2e; margin-bottom: 10px; }
button[data-baseweb="tab"] * { color: #1a4d2e !important; font-weight: 700 !important; }

/* Analysis chart axis text color fix - EXTRA BOLD */
.js-plotly-plot .plotly .xtick text, .js-plotly-plot .plotly .ytick text, .js-plotly-plot .plotly .g-xtitle text, .js-plotly-plot .plotly .g-ytitle text {
    fill: #1a4d2e !important;
    font-weight: 900 !important;
    font-size: 16px !important;
}
</style>
""", unsafe_allow_html=True)

# === SIDEBAR ===
with st.sidebar:
    st.markdown("## ⚙️ 設定 / Settings")
    budget = st.slider("1日の予算 (¥)", 100, 2000, 1000, step=50)
    existing_categories = sorted(df["カテゴリ"].dropna().unique().tolist())
    category = st.selectbox("カテゴリーを選択", ["すべて"] + existing_categories)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.divider()
    st.markdown("### 📱 Share this App")
    app_url = "https://rjpdatasciece-garida-xp7g4qgsnimqdmeyqrepcu.streamlit.app/"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(app_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a4d2e", back_color="#f7f5f0")
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), use_container_width=True, caption="Scan to Open")

# === HEADER ===
st.markdown("# Team Data Chain")
st.caption("Protein Optimization Dashboard v4.7 | Final High-Contrast Edition")
st.divider()

# === BUDGET LOGIC ===
df_f = df.copy()
if category != "すべて":
    df_f = df_f[df_f["カテゴリ"] == category]
df_f = df_f[df_f["値段"] <= budget]

def find_best_plan(items_df, target_budget):
    pool = items_df.to_dict("records")
    best_combo = []
    max_prot = 0
    for n in range(1, 5):
        for combo in combinations(pool, n):
            total_price = sum(item["値段"] for item in combo)
            if (target_budget - 100) <= total_price <= target_budget:
                total_prot = sum(item["タンパク"] for item in combo)
                if total_prot > max_prot:
                    max_prot = total_prot
                    best_combo = combo
    return best_combo, max_prot

best_plan, plan_prot = find_best_plan(df_f, budget)

# === TABS ===
tab1, tab2, tab3, tab4 = st.tabs(["💰 予算プラン", "📋 食品リスト", "➕ 追加", "📊 分析"])

with tab1:
    st.markdown(f"### 🎯 {budget}円で購入可能な最適パッケージ組合せ")
    if best_plan:
        total_p = sum(item["値段"] for item in best_plan)
        st.markdown(f"""
        <div class="custom-card">
            <h2 style="margin:0;">合計タンパク質: {plan_prot:.1f}g</h2>
            <p style="margin:5px 0; font-weight:700; font-size:1.2rem;">合計金額: ¥{total_p} (予算内)</p>
        </div>
        """, unsafe_allow_html=True)
        for item in best_plan:
            unit_val = item.get("内容量", "100g")
            st.markdown(f"""
            <div class="pairing-card">
                <p style="font-weight:700; font-size:1.1rem; margin-bottom:5px;">{item['商品名']} ({unit_val})</p>
                <span>タンパク: {item['タンパク']}g | 価格: ¥{int(item['値段'])}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning(f"¥{budget} の予算内で最適な組み合わせを計算中...")

with tab2:
    st.markdown("### 📋 食品リスト")
    st.dataframe(df_f, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("### ➕ 食品を追加")
    with st.form("add_food_form", clear_on_submit=True):
        f_name = st.text_input("商品名")
        f_unit = st.text_input("内容量 (例: 150g, 1パック)", value="100g")
        f_cat = st.selectbox("カテゴリ", existing_categories + ["その他"])
        f_price = st.number_input("価格 (¥)", min_value=1, value=100)
        f_prot = st.number_input("タンパク質 (g)", min_value=0.0, value=10.0)
        submitted = st.form_submit_button("リストに追加")
        if submitted and f_name:
            new_item = {"商品名": f_name, "内容量": f_unit, "カテゴリ": f_cat, "値段": f_price, "タンパク": f_prot, "カロリー": 0, "store": "User"}
            st.session_state.custom_food.append(new_item)
            st.rerun()

with tab4:
    st.markdown("### 📊 分析 (Visual Analysis)")
    if not df_f.empty:
        # HIGH CONTRAST SETTINGS IN PLOTLY CALL
        fig = px.scatter(df_f, x="値段", y="タンパク", size="p/c_score", color="カテゴリ", 
                         hover_name="商品名", title="価格 vs タンパク質")
        
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a4d2e", size=18, family="Arial Black"), # Forced bold font
            xaxis=dict(
                title=dict(text="価格 (¥)", font=dict(size=20, color="#1a4d2e", family="Arial Black")),
                gridcolor="#d0d0d0", zerolinecolor="#1a4d2e",
                tickfont=dict(color="#1a4d2e", size=16, family="Arial Black")
            ),
            yaxis=dict(
                title=dict(text="タンパク質 (g)", font=dict(size=20, color="#1a4d2e", family="Arial Black")),
                gridcolor="#d0d0d0", zerolinecolor="#1a4d2e",
                tickfont=dict(color="#1a4d2e", size=16, family="Arial Black")
            ),
            legend=dict(font=dict(size=14, color="#1a4d2e"), bgcolor="rgba(255,255,255,0.7)")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("データがありません。")

st.divider()
st.markdown("<div style='text-align:center; font-size:0.8rem;'>© 2024 Team Data Chain</div>", unsafe_allow_html=True)

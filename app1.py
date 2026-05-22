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
    initial_sidebar_state="collapsed" # Mobile users often prefer it collapsed
)

# === INITIAL DATA & SESSION STATE ===
if 'custom_food' not in st.session_state:
    st.session_state.custom_food = []

@st.cache_data
def load_base_data():
    try:
        df = pd.read_csv("smith_clean.csv")
        mapping = {"name": "商品名", "price": "値段", "prot": "タンパク", "cat": "カテゴリ", "cal": "カロリー"}
        df = df.rename(columns=lambda x: mapping.get(x, x))
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
        df = pd.DataFrame(rows, columns=["商品名","unit","値段","カロリー","タンパク","fat","carb","store","カテゴリ"])
    return df

base_df = load_base_data()
if st.session_state.custom_food:
    custom_df = pd.DataFrame(st.session_state.custom_food)
    df = pd.concat([base_df, custom_df], ignore_index=True)
else:
    df = base_df

df["p/c_score"] = (pd.to_numeric(df["タンパク"], errors='coerce') / pd.to_numeric(df["値段"], errors='coerce') * 100).round(2)

# === MOBILE-FIRST GLOBAL CSS ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&display=swap');

/* Basic setup */
html, body, [class*="css"], .stMarkdown, p, span, label, li, h1, h2, h3, h4, h5, h6 { 
    font-family: 'Noto Sans JP', sans-serif !important; 
    color: #1a4d2e !important;
}

.stApp { 
    background: #f7f5f0; 
}

/* Reduce padding for mobile */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
}

/* Sidebar Toggle Icon Fix */
button[kind="headerNoPadding"] svg { display: none; }
button[kind="headerNoPadding"]::after { content: "☰"; font-size: 24px; color: #1a4d2e; font-weight: bold; }

/* Metrics adjustment for mobile */
[data-testid="stMetricValue"] { font-size: 1.5rem !important; color: #1a4d2e !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { font-size: 0.8rem !important; color: #1a4d2e !important; }

/* Custom Card for Mobile */
.custom-card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    border: 2px solid #1a4d2e;
    margin-bottom: 15px;
}

/* Pairing Card for Mobile */
.pairing-card {
    background: #ffffff;
    padding: 10px;
    border-radius: 10px;
    border: 2px solid #1a4d2e;
    margin-bottom: 8px;
}

/* Tab text size for mobile */
button[data-baseweb="tab"] {
    padding-left: 10px !important;
    padding-right: 10px !important;
}
button[data-baseweb="tab"] * {
    font-size: 0.85rem !important;
    font-weight: 700 !important;
}

/* Hide some elements on very small screens if needed */
@media (max-width: 480px) {
    h1 { font-size: 1.5rem !important; }
    .stMetric { margin-bottom: 10px !important; }
}

</style>
""", unsafe_allow_html=True)

# === SIDEBAR ===
with st.sidebar:
    st.markdown("## ⚙️ 設定 / Settings")
    budget = st.slider("1日の予算 (¥)", 100, 2000, 1000, step=50)
    category = st.selectbox("カテゴリ", ["すべて"] + sorted(df["カテゴリ"].dropna().unique().tolist()))
    
    st.divider()
    st.markdown("### 📱 Share this App")
    app_url = "https://rjpdatasciece-garida-xp7g4qgsnimqdmeyqrepcu.streamlit.app/"
    qr = qrcode.QRCode(version=1, box_size=5, border=2) # Smaller box_size for sidebar
    qr.add_data(app_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a4d2e", back_color="#f7f5f0")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), use_container_width=True)

# === HEADER ===


st.markdown("TTCの健康な学生へ")
st.caption("周辺スーパーから最適な食事を選ぼう")
st.divider()

# === BUDGET OPTIMIZER LOGIC ===
df_f = df.copy()
if category != "すべて":
    df_f = df_f[df_f["カテゴリ"] == category]
df_f = df_f[df_f["値段"] <= budget]

def find_best_plan(items_df, target_budget):
    pool = items_df.to_dict("records")
    best_combo = []
    max_prot = 0
    # For mobile performance and simplicity, limit combinations
    for n in range(2, 4): 
        for combo in combinations(pool, n):
            total_price = sum(item["値段"] for item in combo)
            if (target_budget - 100) <= total_price <= target_budget:
                total_prot = sum(item["タンパク"] for item in combo)
                if total_prot > max_prot:
                    max_prot = total_prot
                    best_combo = combo
    return best_combo, max_prot

best_plan, plan_prot = find_best_plan(df_f, budget)

# === MAIN DISPLAY ===
tab1, tab2, tab3, tab4 = st.tabs(["💰 予算", "📋 リスト", "➕ 追加", "📊 分析"])

with tab1:
    st.markdown(f"#### 🎯 {budget}円プラン")
    if best_plan:
        total_p = sum(item["値段"] for item in best_plan)
        st.markdown(f"""
        <div class="custom-card">
            <h3 style="margin:0;">タンパク質: {plan_prot:.1f}g</h3>
            <p style="margin:5px 0; font-weight:700;">合計: ¥{total_p}</p>
        </div>
        """, unsafe_allow_html=True)
        
        for item in best_plan:
            st.markdown(f"""
            <div class="pairing-card">
                <p style="font-weight:700; margin-bottom:2px;">{item['商品名']}</p>
                <span style="font-size:0.85rem;">{item['タンパク']}g | ¥{int(item['値段'])}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("組み合わせを計算中...")

with tab2:
    st.markdown("#### 📋 食品リスト")
    # Simplify dataframe for mobile
    st.dataframe(df_f[["商品名", "値段", "タンパク"]].sort_values("タンパク", ascending=False), 
                 use_container_width=True, hide_index=True)

with tab3:
    st.markdown("#### ➕ 食品を追加")
    st.info("😋 美味しい食品を教えてください！ ❤️")
    with st.form("add_food_form", clear_on_submit=True):
        f_name = st.text_input("食品名")
        f_cat = st.selectbox("カテゴリ", ["主食", "野菜", "乳製品", "その他"])
        f_price = st.number_input("価格 (¥)", min_value=1, value=100)
        f_prot = st.number_input("タンパク (g)", min_value=0.0, value=10.0)
        submitted = st.form_submit_button("追加")
        if submitted and f_name:
            new_item = {"商品名": f_name, "カテゴリ": f_cat, "値段": f_price, "タンパク": f_prot, "カロリー": 0, "store": "User", "unit": "-"}
            st.session_state.custom_food.append(new_item)
            st.rerun()

with tab4:
    st.markdown("#### 📊 分析")
    if not df_f.empty:
        # Smaller font and height for mobile charts
        fig = px.scatter(df_f, x="値段", y="タンパク", size="p/c_score", color="カテゴリ", 
                         hover_name="商品名")
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="#1a4d2e", size=10)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        top5_pc = df_f.nlargest(5, "p/c_score")
        fig2 = px.bar(top5_pc, x="p/c_score", y="商品名", orientation='h', color="タンパク")
        fig2.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=30, b=10),
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="#1a4d2e", size=10)
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

# === FOOTER ===
st.divider()
st.markdown("<div style='text-align:center; font-size:0.7rem;'>© 2024 Team Data Chain</div>", unsafe_allow_html=True)

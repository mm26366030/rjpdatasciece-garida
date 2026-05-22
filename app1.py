import streamlit as st
import pandas as pd
import plotly.express as px

# === PAGE CONFIG ===
st.set_page_config(
    page_title="TTC Team Data Chain | Protein Optimization",
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

# === GLOBAL CSS ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@600&family=Noto+Sans+JP:wght@300;400;500;700&display=swap');

html, body, [class*="css"], .stMarkdown, p, span, label, li, h1, h2, h3, h4, h5, h6 { 
    font-family: 'Noto Sans JP', sans-serif !important; 
    color: #1a4d2e !important;
}

.stApp { 
    background: #f7f5f0; 
}

/* Sidebar Toggle Icon Fix */
/* Hide the double arrow and show a hamburger-like icon or just cleaner look */
button[kind="headerNoPadding"] svg {
    display: none;
}
button[kind="headerNoPadding"]::after {
    content: "☰";
    font-size: 24px;
    color: #1a4d2e;
    font-weight: bold;
}

[data-testid="stMetricValue"] {
    color: #1a4d2e !important;
    font-weight: 800 !important;
}
[data-testid="stMetricLabel"] {
    color: #1a4d2e !important;
}

[data-testid="stSidebar"] * {
    color: #1a4d2e !important;
}

button[data-baseweb="tab"] * {
    color: #1a4d2e !important;
    font-weight: 700 !important;
}

.custom-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    border: 2px solid #1a4d2e;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

.pairing-card {
    background: #ffffff;
    padding: 15px;
    border-radius: 12px;
    border: 2px solid #1a4d2e;
    margin-bottom: 10px;
}

input, select, textarea {
    color: #1a4d2e !important;
}

.stDataFrame div {
    color: #1a4d2e !important;
}

.stAlert p {
    color: #1a4d2e !important;
}
</style>
""", unsafe_allow_html=True)

# === SIDEBAR ===
with st.sidebar:
    st.markdown("## ⚙️ 設定 / Settings")
    weight = st.number_input("体重 (kg)", min_value=30, max_value=150, value=65)
    activity = st.selectbox("活動レベル", ["低 (デスクワーク)", "中 (週3回の運動)", "高 (アスリート)"], index=1)
    st.divider()
    budget = st.slider("予算 (¥)", 100, 2000, 500, step=50)
    category = st.selectbox("カテゴリ", ["すべて"] + sorted(df["カテゴリ"].dropna().unique().tolist()))

# === HEADER ===
st.markdown("# データサイエンス＋AI科　**Team Data Chain** の作品")
st.caption("TTC Protein Optimization Dashboard v3.3 | UI/UX Refined")
st.divider()

# === CALCULATOR & METRICS ===
multiplier = 1.5 if "中" in activity else (2.0 if "高" in activity else 1.0)
target_protein = weight * multiplier

df_f = df[df["値段"] <= budget].copy()
if category != "すべて":
    df_f = df_f[df_f["カテゴリ"] == category]

c1, c2 = st.columns([1, 2])
with c1:
    st.markdown(f"""
    <div class="custom-card">
        <p style="margin:0; font-size:0.9rem;">あなたの1日の目標タンパク質</p>
        <h2 style="margin:10px 0;">{target_protein:.1f}g</h2>
        <p style="margin:0; font-size:0.8rem;">体重 {weight}kg × 係数 {multiplier}</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    m1, m2, m3 = st.columns(3)
    m1.metric("該当品目", f"{len(df_f)}品")
    m2.metric("平均タンパク", f"{df_f['タンパク'].mean():.1f}g" if not df_f.empty else "0g")
    m3.metric("最高コスパ", f"{df_f['p/c_score'].max():.1f}pt" if not df_f.empty else "0pt")

# === TABS ===
tab1, tab2, tab3, tab4 = st.tabs(["📋 食品・ランキング", "➕ 食品を追加", "🤝 おすすめ", "📊 分析"])

with tab1:
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("### 📋 食品リスト")
        st.dataframe(df_f.sort_values("タンパク", ascending=False), use_container_width=True, hide_index=True)
    with col_b:
        st.markdown("### 🏆 タンパク質 TOP 5")
        top5 = df_f.sort_values("タンパク", ascending=False).head(5)
        for i, row in top5.iterrows():
            st.markdown(f"**#{i+1} {row['商品名']}**  \n{row['タンパク']}g / ¥{int(row['値段'])}")
            st.divider()

with tab2:
    st.markdown("### ➕ 新しい食品をリストに追加")
    st.info("😋 美味しいと思う食品をここに追加してください！皆さんの協力に感謝します！ ❤️")
    with st.form("add_food_form", clear_on_submit=True):
        f_name = st.text_input("食品名", placeholder="例: プロテインバー")
        f_cat = st.selectbox("カテゴリ", ["タンパク質", "主食", "野菜", "乳製品", "その他"])
        f_price = st.number_input("価格 (¥)", min_value=1, value=100)
        f_prot = st.number_input("タンパク質 (g)", min_value=0.0, value=10.0, step=0.1)
        f_cal = st.number_input("カロリー (kcal)", min_value=0, value=100)
        submitted = st.form_submit_button("リストに追加する")
        if submitted:
            if f_name:
                new_item = {"商品名": f_name, "カテゴリ": f_cat, "値段": f_price, "タンパク": f_prot, "カロリー": f_cal, "store": "ユーザー追加", "unit": "-"}
                st.session_state.custom_food.append(new_item)
                st.success(f"「{f_name}」を追加しました！")
                st.rerun()

with tab3:
    st.markdown("### 🤝 おすすめの組み合わせ")
    pairings = [
        {"title": "定番！サラダチキンセット", "items": ["サラダチキン", "ブロッコリー", "ごはん"], "desc": "高タンパクの王道。ビタミンCが吸収を助けます。", "protein": "30.5g", "price": "¥328"},
        {"title": "朝のエネルギーチャージ", "items": ["納豆", "鶏卵", "ごはん"], "desc": "アミノ酸スコア100の完璧な組み合わせ。", "protein": "17.0g", "price": "¥95"},
    ]
    p_cols = st.columns(2)
    for i, p in enumerate(pairings):
        with p_cols[i]:
            st.markdown(f"""<div class="pairing-card"><h4>{p['title']}</h4><p>{' + '.join(p['items'])}</p><p style="font-size:0.8rem;">{p['desc']}</p><b>{p['protein']} | {p['price']}</b></div>""", unsafe_allow_html=True)

with tab4:
    st.markdown("### 📊 視覚的分析 (Visual Analysis)")
    if not df_f.empty:
        fig = px.scatter(df_f, x="値段", y="タンパク", size="p/c_score", color="カテゴリ", 
                         hover_name="商品名", 
                         title="価格 vs タンパク質含有量 (円 vs グラム)",
                         labels={"値段": "価格 (¥)", "タンパク": "タンパク質 (g)", "カテゴリ": "食品カテゴリ"})
        
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="#1a4d2e", size=14),
            title_font=dict(size=20, family="Noto Serif JP"),
            xaxis=dict(gridcolor="#e0e0e0", zerolinecolor="#1a4d2e", title_font=dict(size=16)),
            yaxis=dict(gridcolor="#e0e0e0", zerolinecolor="#1a4d2e", title_font=dict(size=16))
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        top10_pc = df_f.nlargest(10, "p/c_score")
        fig2 = px.bar(top10_pc, x="p/c_score", y="商品名", orientation='h', 
                      title="コスパスコア TOP 10 (100円あたりのタンパク質g)",
                      labels={"p/c_score": "コスパスコア (g/100円)", "商品名": "食品名"},
                      color="タンパク", color_continuous_scale="Greens")
        
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="#1a4d2e", size=14),
            title_font=dict(size=20, family="Noto Serif JP"),
            yaxis={'categoryorder':'total ascending'}
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("分析するデータがありません。フィルターを調整してください。")

# === FOOTER ===
st.divider()
st.markdown("<div style='text-align:center; font-size:0.8rem;'>© 2024 Team Data Chain | Tokyo Technical College</div>", unsafe_allow_html=True)
    else:
        st.warning("分析するデータがありません。フィルターを調整してください。")

# === FOOTER ===
st.divider()
st.markdown("<div style='text-align:center; font-size:0.8rem;'>© 2024 Team Data Chain | Tokyo Technical College</div>", unsafe_allow_html=True)

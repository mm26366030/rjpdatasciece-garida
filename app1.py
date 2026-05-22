import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# === PAGE CONFIG ===
st.set_page_config(
    page_title="TTC Team Data Chain | Protein Optimization",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === LOAD DATA ===
@st.cache_data
def load_data():
    try:
        # Try to load existing data
        df = pd.read_csv("smith_clean.csv")
        df["p/c_score"] = pd.to_numeric(df["p/c_score"], errors="coerce")
        df["タンパク"]   = pd.to_numeric(df["タンパク"],   errors="coerce")
        df["値段"]       = pd.to_numeric(df["値段"],       errors="coerce")
        # Ensure column names match expected logic
        if "商品名" not in df.columns and "name" in df.columns:
            df = df.rename(columns={"name": "商品名", "price": "値段", "prot": "タンパク", "cat": "カテゴリ"})
    except FileNotFoundError:
        # Use dummy data from reference app if file not found
        rows = [
            ("ごはん(茶碗1杯)","150g",30,168,2.5,0.3,37.1,"サミット","主食"),
            ("食パン 1枚","60g",40,158,5.6,2.5,28.0,"サミット","主食"),
            ("鶏むね肉(皮なし)","100g",80,105,23.3,1.2,0.0,"サミット","タンパク質"),
            ("鶏卵 1個","60g",25,76,6.2,5.2,0.2,"サミット","タンパク質"),
            ("木綿豆腐 半丁","150g",50,72,6.6,4.2,1.6,"サミット","タンパク質"),
            ("納豆 1パック","50g",40,100,8.3,5.0,5.4,"サミット","タンパク質"),
            ("サバ缶(水煮)","150g",198,190,20.9,10.7,0.2,"サミット","タンパク質"),
            ("サラダチキン","115g",218,114,24.5,1.5,0.5,"FamilyMart","タンパク質"),
            ("ゆで卵 1個","60g",78,76,6.5,5.1,0.3,"FamilyMart","タンパク質"),
            ("ブロッコリー","100g",60,33,3.5,0.4,4.3,"サミット","野菜"),
        ]
        df = pd.DataFrame(rows, columns=["商品名","unit","値段","cal","タンパク","fat","carb","store","カテゴリ"])
        df["p/c_score"] = (df["タンパク"] / df["値段"] * 100).round(2)
    return df

df = load_data()

# === GLOBAL CSS (Reference Style) ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@600&family=Noto+Sans+JP:wght@300;400;500;700&display=swap');

html, body, [class*="css"] { 
    font-family: 'Noto Sans JP', sans-serif; 
}

.stApp { 
    background: #f7f5f0; 
}

h1, h2, h3 { 
    font-family: 'Noto Serif JP', serif !important; 
    color: #1a4d2e !important;
}

/* Custom Card Style */
.custom-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    border-left: 5px solid #1a4d2e;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

.pairing-card {
    background: #ffffff;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    margin-bottom: 10px;
    transition: transform 0.2s;
}
.pairing-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    border-color: #1a4d2e;
}

.highlight-text {
    color: #1a4d2e;
    font-weight: 700;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e0e0e0;
}
</style>
""", unsafe_allow_html=True)

# === SIDEBAR (Settings) ===
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/protein.png", width=80)
    st.markdown("## ⚙️ 設定 / Settings")
    
    st.markdown("### 👤 User Profile")
    weight = st.number_input("体重 (kg)", min_value=30, max_value=150, value=65)
    activity = st.selectbox("活動レベル", 
                            ["低 (デスクワーク)", "中 (週3回の運動)", "高 (アスリート)"],
                            index=1)
    
    st.divider()
    
    st.markdown("### 🔍 Filters")
    budget = st.slider("予算 (¥)", 100, 2000, 500, step=50)
    
    cat_options = ["すべて"] + sorted(df["カテゴリ"].dropna().unique().tolist())
    category = st.selectbox("カテゴリ", cat_options)

# === HEADER ===
st.markdown("# データサイエンス＋AI科　**Team Data Chain** の作品")
st.caption("専門学校東京テクニカルカレッジ (TTC) · プロテイン最適化ダッシュボード v2.0")
st.divider()

# === CALCULATOR SECTION ===
multiplier = 1.0
if "中" in activity: multiplier = 1.5
elif "高" in activity: multiplier = 2.0
target_protein = weight * multiplier

c1, c2 = st.columns([1, 2])

with c1:
    st.markdown(f"""
    <div class="custom-card">
        <p style="margin:0; font-size:0.9rem; color:#666;">あなたの1日の目標タンパク質</p>
        <h2 style="margin:10px 0; color:#1a4d2e;">{target_protein:.1f}g</h2>
        <p style="margin:0; font-size:0.8rem; color:#999;">体重 {weight}kg × 係数 {multiplier}</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    # Quick metrics from filtered data
    df_f = df[df["値段"] <= budget].copy()
    if category != "すべて":
        df_f = df_f[df_f["カテゴリ"] == category]
    
    m1, m2, m3 = st.columns(3)
    m1.metric("該当品目", f"{len(df_f)}品")
    m2.metric("平均タンパク", f"{df_f['タンパク'].mean():.1f}g" if not df_f.empty else "0g")
    m3.metric("最高コスパ", f"{df_f['p/c_score'].max():.1f}pt" if not df_f.empty else "0pt")

# === TABS ===
tab1, tab2, tab3 = st.tabs(["🍱 食品・ランキング", "🤝 おすすめの組み合わせ", "📊 データ分析"])

with tab1:
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.markdown("### 📋 食品リスト")
        st.dataframe(df_f.sort_values("タンパク", ascending=False), use_container_width=True, hide_index=True)
        
    with col_b:
        st.markdown("### 🏆 タンパク質 TOP 5")
        top5 = df_f.sort_values("タンパク", ascending=False).head(5)
        for i, row in top5.iterrows():
            st.markdown(f"""
            <div style="padding:10px; border-bottom:1px solid #eee;">
                <span style="font-weight:700; color:#1a4d2e;">#{i+1} {row['商品名']}</span><br>
                <span style="font-size:0.85rem; color:#666;">{row['タンパク']}g / ¥{int(row['値段'])}</span>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.markdown("### 🤝 一緒に食べるともっと美味しい！ (おすすめの組み合わせ)")
    st.write("栄養バランスと味の相性を考えた、最強のコンビネーションをご提案します。")
    
    pairings = [
        {
            "title": "定番！サラダチキンセット",
            "items": ["サラダチキン", "ブロッコリー", "ごはん"],
            "desc": "高タンパクの王道。ブロッコリーのビタミンCがタンパク質の吸収を助けます。",
            "protein": "30.5g",
            "price": "¥328"
        },
        {
            "title": "朝のエネルギーチャージ",
            "items": ["納豆", "鶏卵", "ごはん"],
            "desc": "日本の伝統的な朝食。アミノ酸スコア100の完璧な組み合わせです。",
            "protein": "17.0g",
            "price": "¥95"
        },
        {
            "title": "手軽に最強バルクアップ",
            "items": ["サバ缶(水煮)", "木綿豆腐"],
            "desc": "良質な脂質(EPA/DHA)と植物性タンパク質を同時に摂取。コスパも最強。",
            "protein": "27.5g",
            "price": "¥248"
        }
    ]
    
    p_cols = st.columns(3)
    for i, p in enumerate(pairings):
        with p_cols[i % 3]:
            st.markdown(f"""
            <div class="pairing-card">
                <h4 style="color:#1a4d2e; margin-top:0;">{p['title']}</h4>
                <p style="font-size:0.85rem; color:#444;">{' + '.join(p['items'])}</p>
                <hr style="margin:10px 0; border:0; border-top:1px solid #eee;">
                <p style="font-size:0.8rem; font-style:italic; color:#666;">{p['desc']}</p>
                <div style="display:flex; justify-content:space-between; margin-top:10px;">
                    <span class="highlight-text">{p['protein']}</span>
                    <span style="font-weight:700;">{p['price']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.markdown("### 📊 視覚的分析")
    c_left, c_right = st.columns(2)
    
    with c_left:
        # Scatter chart: Price vs Protein
        fig = px.scatter(df_f, x="値段", y="タンパク", 
                         size="p/c_score", color="カテゴリ",
                         hover_name="商品名",
                         title="価格 vs タンパク質含有量 (サイズの大きさはコスパ)")
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        
    with c_right:
        # Bar chart: Top 10 Cost Performance
        top10_pc = df_f.nlargest(10, "p/c_score")
        fig2 = px.bar(top10_pc, x="p/c_score", y="商品名", 
                      orientation='h', color="タンパク",
                      title="コスパスコア TOP 10 (100円あたりのタンパク質g)")
        fig2.update_layout(yaxis={'categoryorder':'total ascending'},
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

# === FOOTER ===
st.divider()
st.markdown("""
<div style="text-align:center; color:#888; font-size:0.8rem; padding:20px;">
    © 2024 Team Data Chain | Data Science + AI Division | Tokyo Technical College<br>
    Built with Streamlit & ❤️ for Healthy Students
</div>
""", unsafe_allow_html=True)

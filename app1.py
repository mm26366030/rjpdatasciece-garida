import streamlit as st
import pandas as pd
import altair as alt

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Protein Tracker | Team Data Chain",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# === LOAD DATA ===
try:
    df = pd.read_csv("smith_clean.csv")
    df["p/c_score"] = pd.to_numeric(df["p/c_score"], errors="coerce")
    df["タンパク"]   = pd.to_numeric(df["タンパク"],   errors="coerce")
    df["値段"]       = pd.to_numeric(df["値段"],       errors="coerce")
except FileNotFoundError:
    # Create dummy data if file not found for demonstration
    data = {
        "商品名": ["サラダチキン", "プロテインバー", "納豆", "卵", "豆腐"],
        "カテゴリ": ["惣菜", "お菓子", "日配", "日配", "日配"],
        "タンパク": [25.0, 15.0, 8.0, 6.0, 5.0],
        "値段": [250, 160, 100, 200, 80],
        "p/c_score": [10.0, 9.3, 8.0, 3.0, 6.2]
    }
    df = pd.DataFrame(data)

# === GLOBAL CSS ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --primary: #00f2fe;
    --secondary: #4facfe;
    --bg-dark: #0f172a;
    --card-bg: rgba(30, 41, 59, 0.7);
    --text-main: #f1f5f9;
    --text-dim: #94a3b8;
    --accent: #10b981;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-dark);
    color: var(--text-main);
}

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 2rem 1rem !important;
    max-width: 550px !important;
}

/* === HEADER === */
.app-header {
    text-align: center;
    margin-bottom: 2.5rem;
    padding: 2rem;
    background: linear-gradient(135deg, rgba(79, 172, 254, 0.1), rgba(0, 242, 254, 0.1));
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}
.app-sub {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--primary);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.app-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(to right, #00f2fe, #4facfe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
    margin: 0;
}

/* === CALCULATOR BOX === */
.calc-box {
    background: var(--card-bg);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
.calc-result {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--accent);
    text-align: center;
    margin: 1rem 0;
}
.calc-label {
    text-align: center;
    color: var(--text-dim);
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* === STAT CARDS === */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 2rem;
}
.stat-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 15px 10px;
    text-align: center;
    transition: transform 0.2s;
}
.stat-card:hover {
    transform: translateY(-2px);
    border-color: var(--primary);
}
.stat-val {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-main);
    font-family: 'JetBrains Mono', monospace;
}
.stat-lbl {
    font-size: 0.7rem;
    color: var(--text-dim);
    margin-top: 5px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* === RANK ITEMS === */
.rank-item {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 16px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    margin-bottom: 10px;
    transition: all 0.2s;
}
.rank-item:hover {
    background: rgba(79, 172, 254, 0.08);
    border-color: rgba(79, 172, 254, 0.3);
    transform: scale(1.01);
}
.rank-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--text-dim);
    width: 30px;
}
.rank-name {
    flex: 1;
    font-size: 1rem;
    font-weight: 600;
}
.rank-meta {
    text-align: right;
}
.rank-protein {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--primary);
    font-family: 'JetBrains Mono', monospace;
}

/* Section Title */
.section-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin: 2rem 0 1rem;
    padding-left: 10px;
    border-left: 3px solid var(--primary);
}

/* Custom Slider/Selectbox */
div[data-testid="stSlider"] label, div[data-testid="stSelectbox"] label {
    color: var(--text-dim) !important;
    font-weight: 600 !important;
}

</style>
""", unsafe_allow_html=True)

# === HEADER ===
st.markdown("""
<div class="app-header">
    <p class="app-sub">データサイエンス＋AI科</p>
    <h1 class="app-title">TEAM DATA CHAIN</h1>
    <p style="margin-top:10px; color:#94a3b8; font-size:0.9rem;">Protein Optimization Dashboard</p>
</div>
""", unsafe_allow_html=True)

# === PROTEIN CALCULATOR ===
st.markdown("<p class='section-title'>Daily Protein Calculator</p>", unsafe_allow_html=True)
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Weight (kg)", min_value=30, max_value=150, value=65)
    with col2:
        activity = st.selectbox("Activity Level", 
                                ["Low (Sedentary)", "Moderate (Exercise 3x/week)", "High (Athlete)"],
                                index=1)
    
    # Calculate multiplier
    multiplier = 1.0
    if "Moderate" in activity: multiplier = 1.5
    elif "High" in activity: multiplier = 2.0
    
    target_protein = weight * multiplier
    
    st.markdown(f"""
    <div class="calc-box">
        <p class="calc-label">Your Daily Target</p>
        <p class="calc-result">{target_protein:.1f}g</p>
        <p style="text-align:center; font-size:0.8rem; color:#64748b;">Based on {multiplier}g per kg of body weight</p>
    </div>
    """, unsafe_allow_html=True)

# === FILTER SECTION ===
st.markdown("<p class='section-title'>Optimization Filters</p>", unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])
with c1:
    budget = st.slider("Budget Limit (¥)", 100, 1000, 400, step=10)
with c2:
    cat_options = ["All"] + sorted(df["カテゴリ"].dropna().unique().tolist())
    category = st.selectbox("Category", cat_options)

# Apply filter
df_f = df[df["値段"] <= budget].copy()
if category != "All":
    df_f = df_f[df_f["カテゴリ"] == category]

df_f = df_f.sort_values("タンパク", ascending=False).reset_index(drop=True)

# === STATS ===
count     = len(df_f)
avg_prot  = f"{df_f['タンパク'].mean():.1f}g"  if not df_f.empty else "0g"
min_price = f"¥{int(df_f['値段'].min())}"       if not df_f.empty else "¥0"

st.markdown(f"""
<div class="stat-grid">
    <div class="stat-card">
        <span class="stat-val">{count}</span>
        <span class="stat-lbl">Items</span>
    </div>
    <div class="stat-card">
        <span class="stat-val">{avg_prot}</span>
        <span class="stat-lbl">Avg Protein</span>
    </div>
    <div class="stat-card">
        <span class="stat-val">{min_price}</span>
        <span class="stat-lbl">Min Price</span>
    </div>
</div>
""", unsafe_allow_html=True)

# === RANKING ===
st.markdown("<p class='section-title'>Top Protein Sources</p>", unsafe_allow_html=True)

if df_f.empty:
    st.warning("No items match your criteria.")
else:
    top5 = df_f.head(5)
    for i, row in top5.iterrows():
        st.markdown(f"""
        <div class="rank-item">
            <span class="rank-num">#0{i+1}</span>
            <div class="rank-name">
                {row['商品名']}
                <div style="font-size:0.7rem; color:#64748b; font-weight:400;">{row['カテゴリ']} | ¥{int(row['値段'])}</div>
            </div>
            <div class="rank-meta">
                <span class="rank-protein">{row['タンパク']}g</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# === FOOTER ===
st.markdown("""
<div style="text-align:center; margin-top:3rem; padding:1rem; border-top:1px solid rgba(255,255,255,0.05);">
    <p style="color:#475569; font-size:0.75rem;">© 2024 Team Data Chain | Data Science + AI Division</p>
</div>
""", unsafe_allow_html=True)

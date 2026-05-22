import streamlit as st
import pandas as pd
import altair as alt

# === PAGE CONFIG ===
st.set_page_config(
    page_title="いい食事取ろう！",
    page_icon="🍱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# === LOAD DATA ===
df = pd.read_csv("smith_clean.csv")
df["p/c_score"] = pd.to_numeric(df["p/c_score"], errors="coerce")
df["タンパク"]   = pd.to_numeric(df["タンパク"],   errors="coerce")
df["値段"]       = pd.to_numeric(df["値段"],       errors="coerce")

# === GLOBAL CSS ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 1.2rem 1rem 2rem 1rem !important;
    max-width: 480px !important;
}

/* === HEADER === */
.app-header {
    margin-bottom: 1.4rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.app-title {
    font-size: 1.55rem;
    font-weight: 600;
    color: #E2F5F1;
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin: 0 0 4px 0;
}
.app-sub {
    font-size: 0.78rem;
    color: #64a89f;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin: 0;
}

/* === STAT CARDS === */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 1.2rem;
}
.stat-card {
    background: rgba(13, 148, 136, 0.08);
    border: 1px solid rgba(13, 148, 136, 0.18);
    border-radius: 12px;
    padding: 10px 10px 8px;
    text-align: center;
}
.stat-val {
    font-size: 1.25rem;
    font-weight: 600;
    color: #5EEAD4;
    line-height: 1.1;
    display: block;
    font-family: 'DM Mono', monospace;
}
.stat-lbl {
    font-size: 0.65rem;
    color: #64a89f;
    margin-top: 3px;
    display: block;
    letter-spacing: 0.03em;
}

/* === SECTION TITLE === */
.section-title {
    font-size: 0.7rem;
    font-weight: 600;
    color: #64a89f;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 1.2rem 0 0.6rem;
}

/* === RANK ITEMS === */
.rank-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    margin-bottom: 6px;
    transition: background 0.15s;
}
.rank-item:hover { background: rgba(13,148,136,0.08); }
.rank-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    color: #64a89f;
    width: 18px;
    flex-shrink: 0;
    text-align: center;
}
.rank-num.gold   { color: #F59E0B; }
.rank-num.silver { color: #94A3B8; }
.rank-num.bronze { color: #92765A; }
.rank-name {
    flex: 1;
    font-size: 0.88rem;
    font-weight: 500;
    color: #E2F5F1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.rank-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    flex-shrink: 0;
    gap: 2px;
}
.rank-protein {
    font-size: 0.85rem;
    font-weight: 600;
    color: #5EEAD4;
    font-family: 'DM Mono', monospace;
}
.rank-price {
    font-size: 0.7rem;
    color: #64a89f;
}
.pc-badge {
    font-size: 0.62rem;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.02em;
}
.pc-hi  { background: rgba(13,148,136,0.25); color: #5EEAD4; }
.pc-mid { background: rgba(245,158,11,0.2);  color: #F59E0B; }
.pc-lo  { background: rgba(239,68,68,0.15);  color: #F87171; }

/* === PC INFO BOX === */
.pc-box {
    background: rgba(13,148,136,0.06);
    border: 1px solid rgba(13,148,136,0.15);
    border-radius: 14px;
    padding: 14px 16px;
    margin-top: 1.2rem;
}
.pc-formula {
    font-family: 'DM Mono', monospace;
    font-size: 0.88rem;
    color: #5EEAD4;
    text-align: center;
    padding: 10px;
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
    margin: 8px 0 12px;
}
.pc-levels {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
}
.pc-level-item {
    text-align: center;
    padding: 7px 4px;
    border-radius: 8px;
}
.pc-level-val {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    font-weight: 600;
    display: block;
}
.pc-level-lbl {
    font-size: 0.62rem;
    color: #64a89f;
    display: block;
    margin-top: 2px;
}

/* === SLIDER & SELECT override === */
div[data-testid="stSlider"] label,
div[data-testid="stSelectbox"] label {
    font-size: 0.75rem !important;
    color: #64a89f !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}

/* Altair chart bg */
.vega-embed { border-radius: 12px; overflow: hidden; }

/* Divider */
.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# === HEADER ===
st.markdown("""
<div class="app-header">
    <p class="app-sub">スミス東中野 × TTC</p>
    <h1 class="app-title">いい食事取ろう！🍱</h1>
</div>
""", unsafe_allow_html=True)

# === FILTER ===
budget = st.slider("予算 (¥)", 100, 600, 300, step=10)

cat_options = ["すべて"] + sorted(df["カテゴリ"].dropna().unique().tolist())
category = st.selectbox("カテゴリ", cat_options)

# Apply filter
df_f = df[df["値段"] <= budget].copy()
if category != "すべて":
    df_f = df_f[df_f["カテゴリ"] == category]

df_f = df_f.sort_values("タンパク", ascending=False).reset_index(drop=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# === STAT CARDS ===
count     = len(df_f)
avg_prot  = f"{df_f['タンパク'].mean():.1f}g"  if not df_f.empty else "ー"
min_price = f"¥{int(df_f['値段'].min())}"       if not df_f.empty else "ー"

st.markdown(f"""
<div class="stat-grid">
    <div class="stat-card">
        <span class="stat-val">{count}</span>
        <span class="stat-lbl">対象品目</span>
    </div>
    <div class="stat-card">
        <span class="stat-val">{avg_prot}</span>
        <span class="stat-lbl">平均タンパク</span>
    </div>
    <div class="stat-card">
        <span class="stat-val">{min_price}</span>
        <span class="stat-lbl">最安値</span>
    </div>
</div>
""", unsafe_allow_html=True)

# === RANKING TOP 5 ===
st.markdown("<p class='section-title'>たんぱく質 ランキング</p>", unsafe_allow_html=True)

if df_f.empty:
    st.info("該当する商品がありません")
else:
    rank_icons = {0: "gold", 1: "silver", 2: "bronze"}
    top5 = df_f.head(5)

    for i, row in top5.iterrows():
        score = row["p/c_score"]
        if score >= 5.0:
            badge_cls, badge_txt = "pc-hi",  f"P/C {score:.1f} ✅"
        elif score >= 2.0:
            badge_cls, badge_txt = "pc-mid", f"P/C {score:.1f} 🔶"
        else:
            badge_cls, badge_txt = "pc-lo",  f"P/C {score:.1f} ❌"

        num_cls = rank_icons.get(i, "rank-num")
        num_str = ["①","②","③","④","⑤"][i] if i < 5 else f"{i+1}"

        st.markdown(f"""
        <div class="rank-item">
            <span class="rank-num {num_cls}">{num_str}</span>
            <span class="rank-name">{row['商品名']}</span>
            <div class="rank-meta">
                <span class="rank-protein">{row['タンパク']}g</span>
                <span class="rank-price">¥{int(row['値段'])}</span>
                <span class="pc-badge {badge_cls}">{badge_txt}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# === BAR CHART コスパ ===
st.markdown("<p class='section-title'>コスパ上位 (g/¥100)</p>", unsafe_allow_html=True)

if not df_f.empty:
    bar_df = df_f.head(6)[["商品名", "p/c_score"]].copy()
    bar_df.columns = ["商品名", "score"]

    
    def get_level(s):
        if s >= 5.0:   return "High"
        elif s >= 2.0: return "Mid"
        else:          return "Low"
    bar_df["level"] = bar_df["score"].apply(get_level)

    bar = (
        alt.Chart(bar_df)
        .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
        .encode(
            y=alt.Y("商品名:N", sort="-x", title=None,
                    axis=alt.Axis(labelFontSize=12, labelColor="#94A3B8")),
            x=alt.X("score:Q", title="g / ¥100",
                    axis=alt.Axis(labelFontSize=11, labelColor="#64a89f")),
            color=alt.Color("level:N",
                scale=alt.Scale(
                    domain=["High", "Mid", "Low"],
                    range=["#0D9488", "#F59E0B", "#EF4444"]
                ),
                legend=None
            ),
            tooltip=["商品名", alt.Tooltip("score:Q", title="P/C Score", format=".2f")]
        )
        .properties(height=190)
        .configure_view(strokeWidth=0, fill="#0F1923")
        .configure_axis(grid=False, domain=False)
        .configure(background="#0F1923")
    )
    st.altair_chart(bar, use_container_width=True)
# === P/C INFO ===
st.markdown("""
<div class="pc-box">
    <p class="section-title" style="margin-top:0">P/Cスコアとは？</p>
    <div class="pc-formula">P/C = タンパク (g) ÷ 価格 (¥) × 100</div>
    <div class="pc-levels">
        <div class="pc-level-item" style="background:rgba(13,148,136,0.12)">
            <span class="pc-level-val" style="color:#5EEAD4">> 5.0</span>
            <span class="pc-level-lbl">High ✅</span>
        </div>
        <div class="pc-level-item" style="background:rgba(245,158,11,0.1)">
            <span class="pc-level-val" style="color:#F59E0B">2 〜 5</span>
            <span class="pc-level-lbl">Mid 🔶</span>
        </div>
        <div class="pc-level-item" style="background:rgba(239,68,68,0.1)">
            <span class="pc-level-val" style="color:#F87171">< 2.0</span>
            <span class="pc-level-lbl">Low ❌</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

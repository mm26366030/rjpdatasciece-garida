import streamlit as st
import pandas as pd
import altair as alt

import streamlit as st
import pandas as pd
import altair as alt
from itertools import combinations

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

# カテゴリ列がなければ空文字で補完
if "カテゴリ" not in df.columns:
    df["カテゴリ"] = "その他"

# 相性ルール（ジャンル列 or カテゴリ列を使用）
PAIRING = {
    "主食":     {"pairs": ["肉類","魚介","卵","大豆","野菜","乳製品"], "reason": "主食＋タンパク質でバランスUP"},
    "肉類":     {"pairs": ["主食","野菜","卵"],                        "reason": "肉料理には主食と野菜が相性◎"},
    "魚介":     {"pairs": ["主食","野菜","乳製品"],                    "reason": "魚＋野菜でDHA吸収アップ"},
    "卵":       {"pairs": ["主食","野菜","肉類"],                      "reason": "卵は万能食材。何でも合う"},
    "大豆":     {"pairs": ["主食","野菜","肉類"],                      "reason": "大豆＋主食で植物性タンパク補給"},
    "野菜":     {"pairs": ["肉類","魚介","卵","大豆","主食"],          "reason": "野菜でビタミン・食物繊維を補給"},
    "乳製品":   {"pairs": ["主食","果物","野菜"],                      "reason": "カルシウムを効率よく摂取"},
    "果物":     {"pairs": ["乳製品","主食"],                           "reason": "ビタミンCで鉄分吸収アップ"},
    "惣菜":     {"pairs": ["主食","野菜"],                             "reason": "惣菜＋主食でボリューム満点"},
    "飲料":     {"pairs": ["主食","果物","惣菜"],                      "reason": "食事のお供に"},
}

# === GLOBAL CSS ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
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
    background: rgba(13,148,136,0.08);
    border: 1px solid rgba(13,148,136,0.18);
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
.rank-price { font-size: 0.7rem; color: #64a89f; }
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

/* === PROTEIN GUIDE === */
.prot-guide-box {
    background: rgba(37,99,235,0.08);
    border: 1px solid rgba(37,99,235,0.2);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 1rem;
}
.prot-guide-title {
    font-size: 0.68rem;
    font-weight: 600;
    color: #93C5FD;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.prot-target-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
    font-size: 0.72rem;
    color: #94A3B8;
}
.prot-bar-bg {
    background: rgba(255,255,255,0.08);
    border-radius: 99px;
    height: 8px;
    margin-bottom: 10px;
    overflow: hidden;
    position: relative;
}
.prot-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.4s;
}
.male-fill   { background: linear-gradient(90deg,#3B82F6,#60A5FA); }
.female-fill { background: linear-gradient(90deg,#EC4899,#F472B6); }
.prot-note {
    font-size: 0.62rem;
    color: #475569;
    margin-top: 6px;
    text-align: right;
}

/* === PAIRING CARDS === */
.pairing-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 8px;
}
.pairing-for {
    font-size: 0.62rem;
    color: #64a89f;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.pairing-selected {
    font-size: 0.9rem;
    font-weight: 600;
    color: #E2F5F1;
    margin-bottom: 4px;
}
.pairing-reason {
    font-size: 0.7rem;
    color: #64a89f;
    font-style: italic;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.pairing-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0;
    border-bottom: 1px dotted rgba(255,255,255,0.05);
    font-size: 0.78rem;
}
.pairing-item:last-child { border: none; }
.pairing-item-name { color: #CBD5E1; }
.pairing-item-right {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-shrink: 0;
}
.pairing-prot { color: #5EEAD4; font-family: 'DM Mono', monospace; font-size: 0.75rem; }
.pairing-price { color: #64a89f; font-family: 'DM Mono', monospace; font-size: 0.72rem; }

/* === COMBO TABLE === */
.combo-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.75rem;
    margin-top: 4px;
}
.combo-table th {
    text-align: left;
    padding: 6px 8px;
    font-size: 0.62rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64a89f;
    font-weight: 600;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.combo-table th:not(:first-child) { text-align: right; }
.combo-table td {
    padding: 8px 8px;
    color: #CBD5E1;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    vertical-align: top;
}
.combo-table td:not(:first-child) {
    text-align: right;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
}
.combo-table tr:first-child td { color: #E2F5F1; }
.combo-rank { color: #F59E0B; font-weight: 700; margin-right: 4px; }
.combo-foods-cell { line-height: 1.5; }
.combo-food-tag {
    display: inline-block;
    font-size: 0.68rem;
    padding: 1px 6px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px;
    margin: 1px 2px 1px 0;
    color: #94A3B8;
}
.prot-ok  { color: #5EEAD4; font-weight: 600; }
.prot-low { color: #F87171; }

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
.pc-levels { display: grid; grid-template-columns: repeat(3,1fr); gap: 6px; }
.pc-level-item { text-align: center; padding: 7px 4px; border-radius: 8px; }
.pc-level-val { font-family: 'DM Mono', monospace; font-size: 0.82rem; font-weight: 600; display: block; }
.pc-level-lbl { font-size: 0.62rem; color: #64a89f; display: block; margin-top: 2px; }

/* Slider & Select */
div[data-testid="stSlider"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label {
    font-size: 0.75rem !important;
    color: #64a89f !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}
.vega-embed { border-radius: 12px; overflow: hidden; }
.divider { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# === HEADER ===
st.markdown("""
<div class="app-header">
    <p class="app-sub">スミス東中野 × TTC</p>
    <h1 class="app-title">いい食事取ろう！🍱</h1>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# === PROTEIN GUIDE（体重 → 男女別目標）===
# ─────────────────────────────────────────────────────────
weight = st.number_input("体重 (kg)", min_value=40, max_value=120, value=60, step=1)
male_target   = round(weight * 1.1)   # 男性：体重×1.1g（厚労省2025年版）
female_target = round(weight * 0.85)  # 女性：体重×0.85g

st.markdown(f"""
<div class="prot-guide-box">
    <div class="prot-guide-title">🥩 1日のタンパク質目安（厚労省 食事摂取基準2025）</div>

    <div class="prot-target-row">
        <span>👨 男性（{weight}kg）</span>
        <span style="color:#60A5FA;font-family:'DM Mono',monospace;font-weight:600">{male_target}g/日</span>
    </div>
    <div class="prot-bar-bg">
        <div class="prot-bar-fill male-fill" style="width:100%"></div>
    </div>

    <div class="prot-target-row">
        <span>👩 女性（{weight}kg）</span>
        <span style="color:#F472B6;font-family:'DM Mono',monospace;font-weight:600">{female_target}g/日</span>
    </div>
    <div class="prot-bar-bg">
        <div class="prot-bar-fill female-fill" style="width:{int(female_target/male_target*100)}%"></div>
    </div>

    <div class="prot-note">体重 × 1.0〜1.2g が目安（普通活動量の場合）</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# === FILTERS ===
# ─────────────────────────────────────────────────────────
budget = st.slider("予算 (¥)", 100, 600, 300, step=10)

cat_options = ["すべて"] + sorted(df["カテゴリ"].dropna().unique().tolist())
category = st.selectbox("カテゴリ", cat_options)

df_f = df[df["値段"] <= budget].copy()
if category != "すべて":
    df_f = df_f[df_f["カテゴリ"] == category]
df_f = df_f.sort_values("タンパク", ascending=False).reset_index(drop=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# === STAT CARDS ===
# ─────────────────────────────────────────────────────────
count     = len(df_f)
avg_prot  = f"{df_f['タンパク'].mean():.1f}g" if not df_f.empty else "ー"
min_price = f"¥{int(df_f['値段'].min())}"      if not df_f.empty else "ー"

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

# ─────────────────────────────────────────────────────────
# === RANKING TOP 5 ===
# ─────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────
# === BAR CHART ===
# ─────────────────────────────────────────────────────────
st.markdown("<p class='section-title'>コスパ上位 (g/¥100)</p>", unsafe_allow_html=True)

if not df_f.empty:
    bar_df = df_f.head(6)[["商品名","p/c_score"]].copy()
    bar_df.columns = ["商品名","score"]
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
                scale=alt.Scale(domain=["High","Mid","Low"],
                                range=["#0D9488","#F59E0B","#EF4444"]),
                legend=None),
            tooltip=["商品名", alt.Tooltip("score:Q", title="P/C Score", format=".2f")]
        )
        .properties(height=190)
        .configure_view(strokeWidth=0, fill="#0F1923")
        .configure_axis(grid=False, domain=False)
        .configure(background="#0F1923")
    )
    st.altair_chart(bar, use_container_width=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# === 一緒に食べると美味しい（相性テーブル）===
# ─────────────────────────────────────────────────────────
st.markdown("<p class='section-title'>🍱 一緒に食べると美味しい</p>", unsafe_allow_html=True)

if df_f.empty:
    st.info("予算内の商品がありません")
else:
    # 予算内の上位3品を基準に相性提案
    anchor_items = df_f.head(3)

    for _, anchor in anchor_items.iterrows():
        anchor_cat = anchor["カテゴリ"]
        rule = PAIRING.get(anchor_cat, {"pairs": [], "reason": "相性情報なし"})

        # 全データから相性のいいカテゴリの品を検索（予算内）
        matches = df[
            (df["カテゴリ"].isin(rule["pairs"])) &
            (df["値段"] <= budget) &
            (df["商品名"] != anchor["商品名"])
        ].sort_values("タンパク", ascending=False).head(3)

        if matches.empty:
            continue

        items_html = "".join([
            f"""<div class="pairing-item">
                <span class="pairing-item-name">{r['商品名']}</span>
                <div class="pairing-item-right">
                    <span class="pairing-prot">{r['タンパク']}g</span>
                    <span class="pairing-price">¥{int(r['値段'])}</span>
                </div>
            </div>"""
            for _, r in matches.iterrows()
        ])

        st.markdown(f"""
        <div class="pairing-card">
            <div class="pairing-for">合わせるなら</div>
            <div class="pairing-selected">{anchor['商品名']}</div>
            <div class="pairing-reason">{rule['reason']}</div>
            {items_html}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# === 組み合わせランキング表 ===
# ─────────────────────────────────────────────────────────
st.markdown("<p class='section-title'>📊 おすすめ組み合わせ ランキング</p>", unsafe_allow_html=True)

min_prot_target = st.slider(
    "タンパク質目標 (g)",
    min_value=10, max_value=80,
    value=min(female_target, 50),
    step=5,
    help=f"男性目安: {male_target}g / 女性目安: {female_target}g"
)

if df_f.empty:
    st.info("予算内の商品がありません")
else:
    pool = df_f.to_dict("records")
    combo_results = []

    for combo in combinations(pool, 3):
        total_cost = sum(c["値段"]  for c in combo)
        total_prot = sum(c["タンパク"] for c in combo)
        total_score= sum(c["p/c_score"] for c in combo)
        if total_cost <= budget:
            combo_results.append({
                "foods":      [c["商品名"] for c in combo],
                "cost":       total_cost,
                "protein":    round(total_prot, 1),
                "score":      round(total_score, 2),
                "prot_ok":    total_prot >= min_prot_target,
            })

    combo_results.sort(key=lambda x: -x["score"])
    top_combos = combo_results[:5]

    if not top_combos:
        st.info("予算内で3品の組み合わせが見つかりません")
    else:
        medals = ["🥇","🥈","🥉","4位","5位"]
        rows_html = ""
        for i, r in enumerate(top_combos):
            tags = "".join(f'<span class="combo-food-tag">{f}</span>' for f in r["foods"])
            prot_cls = "prot-ok" if r["prot_ok"] else "prot-low"
            prot_icon = "✅" if r["prot_ok"] else "❌"
            rows_html += f"""
            <tr>
                <td class="combo-foods-cell">
                    <span class="combo-rank">{medals[i]}</span>{tags}
                </td>
                <td>¥{int(r['cost'])}</td>
                <td class="{prot_cls}">{r['protein']}g {prot_icon}</td>
                <td>¥{int(budget - r['cost'])}</td>
                <td>{r['score']}</td>
            </tr>"""

        st.markdown(f"""
        <table class="combo-table">
            <thead>
                <tr>
                    <th>組み合わせ（3品）</th>
                    <th>合計</th>
                    <th>タンパク</th>
                    <th>残予算</th>
                    <th>P/Cスコア</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        <div style="font-size:0.62rem;color:#475569;margin-top:6px;text-align:right">
            目標 {min_prot_target}g以上 ✅ / 未達 ❌ &nbsp;·&nbsp; {len(combo_results)}通りから上位5件
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# === P/C INFO BOX ===
# ─────────────────────────────────────────────────────────
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

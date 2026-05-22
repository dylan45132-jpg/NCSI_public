import streamlit as st

def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500&family=Inter:wght@300;400;500&display=swap');

/* ── base ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif;
    font-size: 13px;
}
.stApp {
    background-color: #ffffff;
}

/* ── sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #fafafa !important;
    border-right: 1px solid #e2e4e9 !important;
}
section[data-testid="stSidebar"] .stMarkdown p {
    font-size: 11px;
    color: #9ca3af;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    font-weight: 500;
    margin-bottom: 4px;
}

/* ── header bar ── */
.ncsi-header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    padding: 0 0 16px 0;
    border-bottom: 1px solid #e2e4e9;
    margin-bottom: 24px;
}
.ncsi-wordmark {
    font-family: 'Roboto Mono', monospace;
    font-size: 14px;
    font-weight: 500;
    color: #1e3a5f;
    letter-spacing: 0.12em;
}
.ncsi-subtitle {
    font-size: 12px;
    color: #9ca3af;
    letter-spacing: 0.01em;
}
.ncsi-meta-tag {
    font-family: 'Roboto Mono', monospace;
    font-size: 10px;
    color: #9ca3af;
    background: #f3f4f6;
    border: 1px solid #e2e4e9;
    border-radius: 2px;
    padding: 3px 8px;
    margin-left: auto;
    letter-spacing: 0.04em;
}

/* ── section labels ── */
.section-label {
    font-family: 'Roboto Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    color: #6b7280;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 14px;
    padding-bottom: 7px;
    border-bottom: 1px solid #e2e4e9;
}
.section-title {
    font-size: 12px;
    font-weight: 500;
    color: #1f2937;
    margin-bottom: 2px;
    letter-spacing: 0.01em;
}
.section-caption {
    font-size: 11px;
    color: #9ca3af;
    margin-bottom: 12px;
    line-height: 1.5;
}

/* ── metric cards ── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0;
    margin-bottom: 20px;
    border: 1px solid #e2e4e9;
}
.metric-card {
    background: #ffffff;
    padding: 14px 16px;
    border-right: 1px solid #e2e4e9;
}
.metric-card:last-child {
    border-right: none;
}
.metric-card-wide {
    background: #ffffff;
    padding: 14px 16px;
    border: 1px solid #e2e4e9;
}
.metric-label {
    font-size: 10px;
    color: #9ca3af;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    font-family: 'Roboto Mono', monospace;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 20px;
    font-weight: 400;
    color: #111827;
    font-family: 'Roboto Mono', monospace;
    line-height: 1.1;
}
.metric-unit {
    font-size: 11px;
    color: #9ca3af;
    font-weight: 400;
    margin-left: 2px;
}
.metric-sub {
    font-size: 10px;
    color: #b0b4be;
    margin-top: 5px;
    padding-top: 5px;
    border-top: 1px solid #f3f4f6;
    font-family: 'Roboto Mono', monospace;
}

/* ── quadrant badge ── */
.quadrant-badge {
    display: inline-block;
    font-family: 'Roboto Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 0;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}
.badge-danger   { background: #fee2e2; color: #991b1b; border-left: 3px solid #dc2626; }
.badge-nature   { background: #fef3c7; color: #92400e; border-left: 3px solid #d97706; }
.badge-climate  { background: #fef9c3; color: #854d0e; border-left: 3px solid #ca8a04; }
.badge-safe     { background: #dcfce7; color: #166534; border-left: 3px solid #16a34a; }

/* ── data table overrides ── */
.stDataFrame {
    font-size: 12px !important;
}
div[data-testid="stDataFrame"] table {
    font-family: 'Roboto Mono', monospace !important;
    font-size: 11px !important;
}

/* ── dividers ── */
hr {
    border: none;
    border-top: 1px solid #e2e4e9;
    margin: 24px 0;
}

/* ── expander ── */
details summary {
    font-size: 11px !important;
    color: #6b7280 !important;
    font-family: 'Roboto Mono', monospace !important;
    letter-spacing: 0.04em !important;
}

/* ── slider label ── */
.stSlider label {
    font-size: 11px !important;
    color: #6b7280 !important;
    font-family: 'Roboto Mono', monospace !important;
    letter-spacing: 0.04em !important;
}

/* ── radio ── */
.stRadio label {
    font-size: 12px !important;
    color: #6b7280 !important;
}

/* ── selectbox ── */
.stSelectbox label {
    font-size: 10px !important;
    color: #9ca3af !important;
    font-family: 'Roboto Mono', monospace !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
}

/* ── button ── */
.stButton > button {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    color: #374151 !important;
    font-size: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 400 !important;
    border-radius: 2px !important;
    padding: 7px 14px !important;
    letter-spacing: 0.02em !important;
    box-shadow: none !important;
    transition: border-color 0.1s ease, color 0.1s ease !important;
}
.stButton > button:hover {
    border-color: #1e3a5f !important;
    color: #1e3a5f !important;
    background: #f8fafc !important;
}

/* ── note block ── */
.method-note {
    background: #f8f9fb;
    border-left: 2px solid #d1d5db;
    border-radius: 0;
    padding: 10px 14px;
    font-size: 11px;
    color: #6b7280;
    line-height: 1.6;
    margin-top: 8px;
}
.method-note code {
    font-family: 'Roboto Mono', monospace;
    font-size: 10px;
    color: #374151;
    background: #f3f4f6;
    padding: 1px 4px;
    border-radius: 2px;
}

/* ── score bar ── */
.score-bar-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 5px;
}
.score-bar-label {
    font-family: 'Roboto Mono', monospace;
    font-size: 10px;
    color: #9ca3af;
    width: 130px;
    flex-shrink: 0;
}
.score-bar-track {
    flex: 1;
    height: 3px;
    background: #f3f4f6;
}
.score-bar-fill {
    height: 100%;
    background: #1e3a5f;
}
.score-bar-val {
    font-family: 'Roboto Mono', monospace;
    font-size: 10px;
    color: #374151;
    font-weight: 500;
    width: 36px;
    text-align: right;
    flex-shrink: 0;
}

/* ── gain site row ── */
.gain-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #f3f4f6;
}
.gain-rank {
    font-family: 'Roboto Mono', monospace;
    font-size: 10px;
    color: #1e3a5f;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 2px;
    padding: 2px 7px;
    flex-shrink: 0;
    margin-top: 1px;
    letter-spacing: 0.04em;
}
.gain-content {
    flex: 1;
}
.gain-action {
    font-size: 12px;
    color: #1f2937;
    margin-bottom: 3px;
}
.gain-meta {
    font-family: 'Roboto Mono', monospace;
    font-size: 10px;
    color: #9ca3af;
}
.gain-score {
    font-family: 'Roboto Mono', monospace;
    font-size: 12px;
    font-weight: 500;
    color: #6b7280;
    flex-shrink: 0;
}

/* ── sidebar ── */
.ncsi-sidebar-wordmark {
    font-family: 'Roboto Mono', monospace;
    font-size: 13px;
    font-weight: 500;
    color: #1e3a5f;
    letter-spacing: 0.12em;
    margin-bottom: 4px;
}
.sidebar-section-label {
    font-family: 'Roboto Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    color: #9ca3af;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 10px;
    margin-top: 16px;
    padding-bottom: 5px;
    border-bottom: 1px solid #e2e4e9;
}
</style>
""", unsafe_allow_html=True)

# ── Helper functions ──────────────────────────────────────────────
def quadrant_badge(quad):
    mapping = {
        "Danger Zone":            ("badge-danger",  "● Danger zone — 危險區"),
        "Warning Zone (Nature)":  ("badge-nature",  "● Warning — 自然警戒區"),
        "Warning Zone (Climate)": ("badge-climate", "● Warning — 氣候警戒區"),
        "Safe Zone":              ("badge-safe",    "● Safe zone — 安全區"),
    }
    cls, label = mapping.get(quad, ("badge-safe", quad))
    return f'<span class="quadrant-badge {cls}">{label}</span>'

def score_color(val):
    if val >= 70: return "#dc2626"
    if val >= 40: return "#d97706"
    return "#16a34a"

def gap_status_badge(ratio):
    if ratio < 1:    return ("badge-safe",    "已達中和 / Neutralized")
    if ratio <= 2:   return ("badge-climate", "接近中和 / Near neutral")
    if ratio <= 10:  return ("badge-nature",  "缺口中等 / Gap moderate")
    return ("badge-danger", "缺口嚴重 / Gap critical")

def score_bar_html(label, val, color="#1e3a5f"):
    pct = min(max(val, 0), 100)
    return f"""
<div class="score-bar-wrap">
  <span class="score-bar-label">{label}</span>
  <div class="score-bar-track">
    <div class="score-bar-fill" style="width:{pct}%;background:{color};"></div>
  </div>
  <span class="score-bar-val">{val:.1f}</span>
</div>"""

def metric_card_html(label, value, unit="", sub=""):
    sub_html = f"<div class='metric-sub'>{sub}</div>" if sub else ""
    return f"""
<div class="metric-card">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{value}<span class="metric-unit">{unit}</span></div>
  {sub_html}
</div>"""
import streamlit as st

def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

/* ── base ── */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', -apple-system, sans-serif;
}
.stApp {
    background-color: #f9f9f7;
}

/* ── sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #f4f4f1 !important;
    border-right: 1px solid #e5e4e0 !important;
}
section[data-testid="stSidebar"] .stMarkdown p {
    font-size: 11px;
    color: #9ca3af;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-weight: 500;
    margin-bottom: 4px;
}

/* ── header bar ── */
.ncsi-header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    padding: 0 0 20px 0;
    border-bottom: 1px solid #e5e4e0;
    margin-bottom: 24px;
}
.ncsi-wordmark {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 15px;
    font-weight: 500;
    color: #0d9488;
    letter-spacing: 0.08em;
}
.ncsi-subtitle {
    font-size: 12px;
    color: #9ca3af;
    letter-spacing: 0.02em;
}
.ncsi-meta-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #9ca3af;
    background: #f0efeb;
    border: 1px solid #e5e4e0;
    border-radius: 3px;
    padding: 2px 7px;
    margin-left: auto;
}

/* ── section labels ── */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    color: #4b5563;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid #e5e4e0;
}
.section-title {
    font-size: 13px;
    font-weight: 500;
    color: #374151;
    margin-bottom: 2px;
}
.section-caption {
    font-size: 11px;
    color: #9ca3af;
    margin-bottom: 14px;
    line-height: 1.5;
}

/* ── metric cards ── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin-bottom: 16px;
}
.metric-card {
    background: #ffffff;
    border: 1px solid #e5e4e0;
    border-radius: 4px;
    padding: 12px 14px;
}
.metric-card-wide {
    background: #ffffff;
    border: 1px solid #e5e4e0;
    border-radius: 4px;
    padding: 12px 14px;
}
.metric-label {
    font-size: 10px;
    color: #9ca3af;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 4px;
}
.metric-value {
    font-size: 22px;
    font-weight: 500;
    color: #111827;
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1.2;
}
.metric-unit {
    font-size: 11px;
    color: #6b7280;
    font-weight: 400;
    margin-left: 2px;
}
.metric-sub {
    font-size: 11px;
    color: #9ca3af;
    margin-top: 2px;
}

/* ── quadrant badge ── */
.quadrant-badge {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 3px;
    letter-spacing: 0.04em;
}
.badge-danger   { background:#fef2f2; color:#dc2626; border:1px solid #fca5a5; }
.badge-nature   { background:#fff7ed; color:#c2410c; border:1px solid #fdba74; }
.badge-climate  { background:#fefce8; color:#a16207; border:1px solid #fde047; }
.badge-safe     { background:#f0fdf4; color:#15803d; border:1px solid #86efac; }

/* ── data table overrides ── */
.stDataFrame {
    font-size: 12px !important;
}
div[data-testid="stDataFrame"] table {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important;
}

/* ── dividers ── */
hr {
    border: none;
    border-top: 1px solid #e5e4e0;
    margin: 20px 0;
}

/* ── expander ── */
details summary {
    font-size: 12px !important;
    color: #6b7280 !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

/* ── slider label ── */
.stSlider label {
    font-size: 11px !important;
    color: #6b7280 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    letter-spacing: 0.04em !important;
}

/* ── radio ── */
.stRadio label {
    font-size: 12px !important;
    color: #6b7280 !important;
}

/* ── selectbox ── */
.stSelectbox label {
    font-size: 11px !important;
    color: #6b7280 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
}

/* ── button ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid #d1d5db !important;
    color: #6b7280 !important;
    font-size: 12px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    border-radius: 3px !important;
    padding: 6px 14px !important;
    letter-spacing: 0.02em !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    border-color: #0d9488 !important;
    color: #0d9488 !important;
    background: rgba(13,148,136,0.05) !important;
}

/* ── note block ── */
.method-note {
    background: #f4f4f1;
    border-left: 2px solid #d1d5db;
    border-radius: 0 3px 3px 0;
    padding: 10px 14px;
    font-size: 11px;
    color: #6b7280;
    line-height: 1.6;
    margin-top: 8px;
}
.method-note code {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #374151;
    background: #e5e4e0;
    padding: 1px 4px;
    border-radius: 2px;
}

/* ── score bar ── */
.score-bar-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
}
.score-bar-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #9ca3af;
    width: 120px;
    flex-shrink: 0;
}
.score-bar-track {
    flex: 1;
    height: 4px;
    background: #e5e4e0;
    border-radius: 2px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 2px;
    background: #0d9488;
}
.score-bar-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #6b7280;
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
    border-bottom: 1px solid #e5e4e0;
}
.gain-rank {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #0d9488;
    background: rgba(13,148,136,0.07);
    border: 1px solid rgba(13,148,136,0.2);
    border-radius: 3px;
    padding: 2px 7px;
    flex-shrink: 0;
    margin-top: 1px;
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
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #9ca3af;
}
.gain-score {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    font-weight: 500;
    color: #9ca3af;
    flex-shrink: 0;
}

/* ── sidebar nav ── */
.nav-item {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #6b7280;
    padding: 5px 0;
    cursor: default;
    display: flex;
    align-items: center;
    gap: 8px;
}
.nav-item .step-num {
    color: #9ca3af;
    width: 14px;
}
</style>
""", unsafe_allow_html=True)

# ── Helper functions ──────────────────────────────────────────────
def quadrant_badge(quad):
    mapping = {
        "Danger Zone":            ("badge-danger",  "DANGER ZONE · 危險區"),
        "Warning Zone (Nature)":  ("badge-nature",  "WARNING · 自然警戒區"),
        "Warning Zone (Climate)": ("badge-climate", "WARNING · 氣候警戒區"),
        "Safe Zone":              ("badge-safe",    "SAFE ZONE · 安全區"),
    }
    cls, label = mapping.get(quad, ("badge-safe", quad))
    return f'<span class="quadrant-badge {cls}">{label}</span>'

def score_color(val):
    if val >= 70: return "#f87171"
    if val >= 40: return "#fb923c"
    return "#4ade80"

def gap_status_badge(ratio):
    if ratio < 1:    return ("badge-safe",    "已達中和 / Neutralized")
    if ratio <= 2:   return ("badge-climate", "接近中和 / Near neutral")
    if ratio <= 10:  return ("badge-nature",  "缺口中等 / Gap moderate")
    return ("badge-danger", "缺口嚴重 / Gap critical")

def score_bar_html(label, val, color="#2dd4bf"):
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
    return f"""
<div class="metric-card">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{value}<span class="metric-unit">{unit}</span></div>
  {"<div class='metric-sub'>" + sub + "</div>" if sub else ""}
</div>"""

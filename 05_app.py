"""
NCSI - Natural Capital Spatial Intelligence Dashboard
自然資本空間智慧平台 | TNFD 對齊生物多樣性與氣候風險評估
"""

import os
import pandas as pd
import geopandas as gpd
import streamlit as st

from app_styles import inject_css
from app_sidebar import render_sidebar
from app_views import render_main

# ── 頁面設定 ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="NCSI — Natural Capital Spatial Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 資料載入 ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = None
    gdf = None
    if os.path.exists("demo_data/results.parquet"):
        df = pd.read_parquet("demo_data/results.parquet")
    if os.path.exists("demo_data/heatmap.geojson"):
        gdf = gpd.read_file("demo_data/heatmap.geojson")
    # The second returned value is not used, but kept for potential future use
    # and to match the requested function signatures.
    return df, gdf

# ── 主流程 ────────────────────────────────────────────────────────

inject_css()

df_raw, percentile_stats = load_data()

if df_raw is None:
    st.error("找不到資料檔案，請先執行 pipeline 產生 demo_data/results.parquet。")
    st.stop()

df = df_raw.copy()

sidebar_params = render_sidebar(df, percentile_stats)

render_main(df, sidebar_params)

import streamlit as st
import pandas as pd
import sys
import os
import importlib
import traceback
from app_constants import ISIC_MENU
from app_styles import metric_card_html, quadrant_badge

# ── Dynamic Module Imports ──────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    pipeline = importlib.import_module("04_pipeline")
except ImportError:
    pipeline = None

try:
    encore_engine = importlib.import_module("03_encore_engine")
except ImportError:
    encore_engine = None

def render_sidebar(df, percentile_stats):
    with st.sidebar:
        st.markdown('<div class="ncsi-wordmark">NCSI</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:10px;color:#9ca3af;font-family:\'IBM Plex Mono\',monospace;letter-spacing:0.06em;margin-bottom:20px;">Natural Capital Spatial Intelligence</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">Analysis Flow</div>', unsafe_allow_html=True)
        for step, label in [
            ("0", "Overview"),
            ("1", "Inputs"),
            ("2", "Spatial Footprint"),
            ("3", "ENCORE Weights"),
            ("4", "NCIS / CRS / DMS"),
            ("5", "Quadrant Classification"),
            ("6", "Liability & Gap Ratio"),
            ("7", "Gain Site Recommendation"),
        ]:
            st.markdown(f'<div class="nav-item"><span class="step-num">{step}</span>{label}</div>', unsafe_allow_html=True)

        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Parameters</div>', unsafe_allow_html=True)

        alpha = st.slider("α — Natural capital weight", 0.0, 1.0, 0.6, 0.05,
            help="α = NCIS 權重；(1-α) = CRS 權重。DMS = α×NCIS + (1-α)×CRS")
        beta = st.slider("β — Heat stress weight (HWDI)", 0.0, 1.0, 0.5, 0.05,
            help="β = 熱浪 HWDI 的權重；(1-β) = 暴雨 RX5DAY 的權重")

        st.markdown('<div class="section-label" style="margin-top:14px;">Scenario Period</div>', unsafe_allow_html=True)
        time_horizon = st.radio(
            "",
            ("Near-term  2016–2035", "Mid-term  2046–2065", "Long-term  2081–2100"),
            index=1,
            label_visibility="collapsed"
        )

        if "Near" in time_horizon:
            crs_col, dms_col = "crs_near", "dms_near"
        elif "Mid" in time_horizon:
            crs_col, dms_col = "crs_mid", "dms_mid"
        else:
            crs_col, dms_col = "crs_long", "dms_long"

        st.markdown('<div class="section-label" style="margin-top:14px;">Map Score</div>', unsafe_allow_html=True)
        score_options = {
            "DMS — Dual materiality": dms_col,
            "NCIS — Natural capital impact": "ncis_score",
            "CRS — Climate risk": crs_col,
        }
        selected_score_label = st.radio("", list(score_options.keys()), label_visibility="collapsed")
        selected_score_col = score_options[selected_score_label]

        st.markdown('<hr>', unsafe_allow_html=True)

        with st.expander("New site analysis"):
            st.markdown('<div class="section-caption">輸入座標與產業，與現有廠區相對比較（約 10–30 秒）</div>', unsafe_allow_html=True)
            new_lat  = st.number_input("Latitude", value=24.0, format="%.5f")
            new_lon  = st.number_input("Longitude", value=121.5, format="%.5f")
            new_area = st.number_input("Area (km²)", value=1.0, format="%.2f")

            selected_section   = st.selectbox("Industry sector", list(ISIC_MENU.keys()))
            division_options   = list(ISIC_MENU[selected_section].keys())
            selected_divisions = st.multiselect("Sub-sector", division_options, default=[division_options[0]] if division_options else [])

            selected_isic_codes = []
            for div in selected_divisions:
                selected_isic_codes.extend(ISIC_MENU[selected_section][div])
            selected_isic_codes = list(set(selected_isic_codes))

            if selected_isic_codes:
                st.markdown(f'<div class="method-note">ISIC: {", ".join(selected_isic_codes[:4])}{"..." if len(selected_isic_codes)>4 else ""}</div>', unsafe_allow_html=True)

            if st.button("Run analysis"):
                if not selected_isic_codes:
                    st.warning("請至少選擇一個產業細項。")
                elif not pipeline or not encore_engine:
                    st.error("分析模組 03_encore_engine.py 或 04_pipeline.py 載入失敗，無法執行。")
                else:
                    with st.spinner("Computing scores..."):
                        try:
                            available_layers = pipeline.get_available_layers(pipeline.RASTER_PATHS)
                            encore_df        = pd.read_csv("data/encore_dependency.csv")
                            new_footprint    = pipeline.make_footprint(new_lat, new_lon, new_area)
                            new_weights      = encore_engine.get_mandle_weights(selected_isic_codes, encore_df)

                            new_density = {}
                            for layer_name in available_layers:
                                path      = pipeline.RASTER_PATHS[layer_name]
                                total_sum = pipeline.zonal_sum(path, new_footprint)
                                new_density[layer_name] = (total_sum / new_area) if (total_sum is not None and new_area > 0) else None

                            existing_densities = {}
                            for fname in df["factory_name"].tolist():
                                frow = df[df["factory_name"] == fname].iloc[0]
                                existing_densities[fname] = {l: frow.get(f"zscore_{l}") for l in available_layers}

                            all_zscores  = pipeline.compute_zscore_table({**existing_densities, "__新廠址__": new_density})
                            new_zscores  = all_zscores["__新廠址__"]
                            ncis, _      = pipeline.compute_ncis(new_zscores, new_weights)
                            crs_near, crs_mid, crs_long, _ = pipeline.compute_crs(new_zscores)

                            crs_val  = {"crs_near": crs_near, "crs_mid": crs_mid, "crs_long": crs_long}[crs_col]
                            dms_val  = alpha * ncis + (1 - alpha) * crs_val
                            quadrant = pipeline.classify_quadrant(ncis, crs_mid)

                            st.markdown(f"""
<div class="metric-row" style="grid-template-columns:repeat(3,1fr);">
  {metric_card_html("NCIS", f"{ncis:.1f}")}
  {metric_card_html("CRS", f"{crs_val:.1f}")}
  {metric_card_html("DMS", f"{dms_val:.1f}")}
</div>
{quadrant_badge(quadrant)}
<div class="method-note" style="margin-top:8px;">
  Near {crs_near:.1f} · Mid {crs_mid:.1f} · Long {crs_long:.1f}
</div>
""", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"分析失敗：{e}")
                            st.code(traceback.format_exc())

    return {
        "alpha": alpha,
        "beta": beta,
        "time_horizon": time_horizon,
        "crs_col": crs_col,
        "dms_col": dms_col,
        "selected_score_label": selected_score_label,
        "selected_score_col": selected_score_col,
    }

import streamlit as st
import pandas as pd
import sys
import os
import importlib
import traceback
from app_constants import ISIC_MENU
from app_styles import metric_card_html, quadrant_badge

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    pipeline = importlib.import_module("04_pipeline")
except ImportError:
    pipeline = None

try:
    encore_engine = importlib.import_module("03_encore_engine")
except ImportError:
    encore_engine = None


def render_sidebar(df):
    with st.sidebar:
        # ── Wordmark ─────────────────────────────────────────────
        st.markdown(
            '<div class="ncsi-sidebar-wordmark">NCSI</div>'
            '<div style="font-size:10px;color:#9ca3af;font-family:\'Roboto Mono\',monospace;'
            'letter-spacing:0.06em;margin-bottom:20px;">Natural Capital Spatial Intelligence</div>',
            unsafe_allow_html=True,
        )

        # ── Parameters ───────────────────────────────────────────
        st.markdown('<div class="sidebar-section-label">Parameters</div>', unsafe_allow_html=True)

        beta = st.slider(
            "β — Heat stress weight (HWDI)",
            0.0, 1.0, 0.5, 0.05,
            help="β = 熱浪 HWDI 的權重；(1-β) = 暴雨 RX5DAY 的權重",
        )

        st.markdown('<div class="sidebar-section-label">Scenario period</div>', unsafe_allow_html=True)
        time_horizon = st.radio(
            "",
            ("Near-term  2016–2035", "Mid-term  2046–2065", "Long-term  2081–2100"),
            index=1,
            label_visibility="collapsed",
        )

        if "Near" in time_horizon:
            crs_col = "crs_near"
        elif "Mid" in time_horizon:
            crs_col = "crs_mid"
        else:
            crs_col = "crs_long"

        st.markdown('<div class="sidebar-section-label">Map score</div>', unsafe_allow_html=True)
        score_options = {
            "NCIS — Natural capital impact": "ncis_score",
            "CRS — Climate risk": crs_col,
        }
        selected_score_label = st.radio("", list(score_options.keys()), label_visibility="collapsed")
        selected_score_col = score_options[selected_score_label]

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── New site analysis ────────────────────────────────────
        with st.expander("New site analysis"):
            st.markdown(
                '<div class="section-caption">輸入座標與產業，與現有廠區相對比較（約 10–30 秒）</div>',
                unsafe_allow_html=True,
            )
            new_lat  = st.number_input("Latitude",  value=24.0, format="%.5f")
            new_lon  = st.number_input("Longitude", value=121.5, format="%.5f")
            new_area = st.number_input("Area (km²)", value=1.0, format="%.2f")

            selected_section   = st.selectbox("Industry sector", list(ISIC_MENU.keys()))
            division_options   = list(ISIC_MENU[selected_section].keys())
            selected_divisions = st.multiselect(
                "Sub-sector", division_options,
                default=[division_options[0]] if division_options else [],
            )

            selected_isic_codes = []
            for div in selected_divisions:
                selected_isic_codes.extend(ISIC_MENU[selected_section][div])
            selected_isic_codes = list(set(selected_isic_codes))

            if selected_isic_codes:
                st.markdown(
                    f'<div class="method-note">ISIC: {", ".join(selected_isic_codes[:4])}'
                    f'{"..." if len(selected_isic_codes) > 4 else ""}</div>',
                    unsafe_allow_html=True,
                )

            if st.button("Run analysis"):
                if not selected_isic_codes:
                    st.warning("請至少選擇一個產業細項。")
                elif not pipeline or not encore_engine:
                    st.error("分析模組載入失敗，無法執行。")
                else:
                    with st.spinner("Computing scores..."):
                        try:
                            available_layers = pipeline.get_available_layers(pipeline.RASTER_PATHS)
                            encore_df        = pd.read_csv("data/encore_dependency.csv")
                            new_footprint    = pipeline.make_footprint(new_lat, new_lon, new_area)
                            new_weights      = encore_engine.get_mandle_weights(selected_isic_codes, encore_df)

                            percentile_stats = pipeline.compute_raster_percentiles(pipeline.RASTER_PATHS)
                            new_norm_scores  = {}
                            for layer_name in available_layers:
                                path    = pipeline.RASTER_PATHS[layer_name]
                                density = pipeline.zonal_mean(path, new_footprint)
                                p_stats = percentile_stats.get(layer_name, {"p1": 0.0, "p99": 0.0})
                                new_norm_scores[layer_name] = pipeline.normalize_percentile(
                                    density, p_stats["p1"], p_stats["p99"]
                                )

                            ncis, _, _                     = pipeline.compute_ncis(new_norm_scores, new_weights)
                            crs_near, crs_mid, crs_long, _ = pipeline.compute_crs(new_norm_scores)
                            crs_val  = {"crs_near": crs_near, "crs_mid": crs_mid, "crs_long": crs_long}[crs_col]
                            quadrant = pipeline.classify_quadrant(ncis, crs_mid)

                            st.markdown(
                                f"""
<div class="metric-row" style="grid-template-columns:repeat(2,1fr);">
  {metric_card_html("NCIS", f"{ncis:.1f}", "/100")}
  {metric_card_html("CRS", f"{crs_val:.1f}", "/100")}
</div>
<div style="margin-bottom:10px;">{quadrant_badge(quadrant)}</div>
<div class="method-note">Near {crs_near:.1f} · Mid {crs_mid:.1f} · Long {crs_long:.1f}</div>
""",
                                unsafe_allow_html=True,
                            )
                        except Exception as e:
                            st.error(f"分析失敗：{e}")
                            st.code(traceback.format_exc())

    return {
        "beta": beta,
        "time_horizon": time_horizon,
        "crs_col": crs_col,
        "selected_score_label": selected_score_label,
        "selected_score_col": selected_score_col,
    }
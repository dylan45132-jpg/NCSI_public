import streamlit as st
import pandas as pd
import json
import folium
from folium import MacroElement
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from jinja2 import Template
from shapely import wkt as shapely_wkt
import sys
import os
import importlib

from app_styles import (
    quadrant_badge,
    score_color,
    gap_status_badge,
    score_bar_html,
    metric_card_html,
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    encore_engine = importlib.import_module("03_encore_engine")
except ImportError:
    encore_engine = None

# ── Layer label mapping (human-readable) ─────────────────────────
LAYER_LABELS = {
    "species_richness":  "Species richness",
    "red_list":          "Red list species",
    "endemic":           "Endemic species",
    "kba":               "Key biodiversity areas",
    "sediment":          "Sediment retention",
    "nitrogen":          "Nitrogen retention",
    "coastal":           "Coastal protection",
    "nature_access":     "Nature access",
}

def _layer_label(raw):
    return LAYER_LABELS.get(raw, raw.replace("_", " ").title())


def render_main(df, sidebar_params):
    beta                 = sidebar_params["beta"]
    time_horizon         = sidebar_params["time_horizon"]
    crs_col              = sidebar_params["crs_col"]
    selected_score_label = sidebar_params["selected_score_label"]
    selected_score_col   = sidebar_params["selected_score_col"]

    # ── Recalculate CRS with current β ───────────────────────────
    if "ncis_score" in df.columns and "norm_hwdi_near" in df.columns:
        for period, hw, rx in [
            ("near", "norm_hwdi_near", "norm_rx5day_near"),
            ("mid",  "norm_hwdi_mid",  "norm_rx5day_mid"),
            ("long", "norm_hwdi_long", "norm_rx5day_long"),
        ]:
            df[f"crs_{period}"] = (beta * df[hw] + (1 - beta) * df[rx]) * 100

    # ── Header ───────────────────────────────────────────────────
    st.markdown(
        f'<div class="ncsi-header">'
        f'<span class="ncsi-wordmark">NCSI</span>'
        f'<span class="ncsi-subtitle">Natural Capital Spatial Intelligence · 自然資本空間智慧平台</span>'
        f'<span class="ncsi-meta-tag">TNFD LEAP · RCP 8.5 · {len(df)} sites · {time_horizon}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════════════════════
    # §0  Executive Overview
    # ════════════════════════════════════════════════════════════
    st.markdown('<div class="section-label">§0 — Executive overview</div>', unsafe_allow_html=True)

    n_danger  = (df["quadrant"] == "Danger Zone").sum()
    n_warning = df["quadrant"].str.startswith("Warning").sum()
    avg_ncis  = df["ncis_score"].mean()
    avg_crs   = df[crs_col].mean()
    total_loss = df["liability_twd"].sum() if "liability_twd" in df.columns else 0

    st.markdown(
        f'<div class="metric-row" style="grid-template-columns:repeat(4,1fr);">'
        f'{metric_card_html("Avg NCIS", f"{avg_ncis:.1f}", "/100")}'
        f'{metric_card_html("Avg CRS", f"{avg_crs:.1f}", "/100")}'
        f'{metric_card_html("Sites at risk", f"{n_danger + n_warning}", f"/{len(df)}", f"{n_danger} danger · {n_warning} warning")}'
        f'{metric_card_html("Total monetised loss", f"{total_loss/1e8:.2f}", " 億/yr")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ════════════════════════════════════════════════════════════
    # §1–2 Spatial Footprint  ·  §5 Quadrant Classification
    # ════════════════════════════════════════════════════════════
    st.markdown(
        '<div class="section-label">§1–2 Spatial footprint  ·  §5 Quadrant classification</div>',
        unsafe_allow_html=True,
    )

    col_map, col_scatter = st.columns([13, 10])

    with col_map:
        st.markdown(
            f'<div class="section-title">Site locations — {selected_score_label}</div>'
            '<div class="section-caption">Click marker for site detail</div>',
            unsafe_allow_html=True,
        )

        m = folium.Map(location=[24.1, 121.5], zoom_start=8, tiles="CartoDB Positron")

        for _, row in df.iterrows():
            sv  = row.get(selected_score_col, 0) or 0
            col_hex = score_color(sv)
            # Radius proportional to score (6–14px range)
            radius = 6 + int((min(sv, 100) / 100) * 8)
            popup_html = (
                f'<div style="font-family:\'Roboto Mono\',monospace;font-size:11px;line-height:1.8;">'
                f'<b style="font-size:12px;color:#111827;">{row.get("factory_name","")}</b><br>'
                f'<span style="color:#9ca3af;">NCIS</span> {row.get("ncis_score",0):.1f} &nbsp;'
                f'<span style="color:#9ca3af;">CRS</span> {row.get(crs_col,0):.1f}<br>'
                f'<span style="color:#9ca3af;">Quadrant</span> {row.get("quadrant","")}'
                f'</div>'
            )
            folium.CircleMarker(
                location=[row.get("latitude", 24.1), row.get("longitude", 121.5)],
                radius=radius,
                color=col_hex, fill=True, fill_color=col_hex, fill_opacity=0.85,
                tooltip=row.get("factory_name", ""),
                popup=folium.Popup(popup_html, max_width=260),
            ).add_to(m)

        legend_html = """
        {% macro html(this, kwargs) %}
        <div style="position:fixed;bottom:20px;left:20px;
            background:#ffffff;border:1px solid #e2e4e9;
            padding:10px 14px;font-family:'Roboto Mono',monospace;font-size:10px;
            color:#6b7280;z-index:9999;letter-spacing:.04em;">
            <div style="margin-bottom:5px;color:#9ca3af;letter-spacing:.08em;">SCORE RANGE</div>
            <div><span style="color:#dc2626;margin-right:6px;">●</span>&ge; 70 &nbsp; High</div>
            <div><span style="color:#d97706;margin-right:6px;">●</span>40–69 &nbsp; Moderate</div>
            <div><span style="color:#16a34a;margin-right:6px;">●</span>&lt; 40 &nbsp; Low</div>
        </div>
        {% endmacro %}"""
        macro = MacroElement()
        macro._template = Template(legend_html)
        m.get_root().add_child(macro)

        st_folium(m, use_container_width=True, height=400, key=f"map_{selected_score_col}_{beta}")

    with col_scatter:
        st.markdown(
            '<div class="section-title">Risk quadrant matrix</div>'
            '<div class="section-caption">X = CRS · Y = NCIS · bubble = capacity scale</div>',
            unsafe_allow_html=True,
        )

        plot_df = df.copy()
        if "ecs_score" not in plot_df.columns:
            plot_df["ecs_score"] = 10

        quadrant_labels_map = {
            "Danger Zone":            "Danger Zone",
            "Warning Zone (Nature)":  "Warning — Nature",
            "Warning Zone (Climate)": "Warning — Climate",
            "Safe Zone":              "Safe Zone",
        }
        plot_df["q_label"] = plot_df["quadrant"].map(lambda x: quadrant_labels_map.get(x, x))
        color_map_plot = {
            "Danger Zone":       "#dc2626",
            "Warning — Nature":  "#d97706",
            "Warning — Climate": "#ca8a04",
            "Safe Zone":         "#16a34a",
        }

        fig = px.scatter(
            plot_df, x=crs_col, y="ncis_score",
            size="ecs_score", color="q_label",
            color_discrete_map=color_map_plot,
            hover_name="factory_name",
            hover_data={"ncis_score": ":.1f", crs_col: ":.1f", "q_label": False, "ecs_score": False},
            height=400,
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#ffffff",
            font=dict(family="Roboto Mono, monospace", size=11, color="#9ca3af"),
            xaxis=dict(
                range=[0, 100], title="CRS — Climate risk score",
                gridcolor="#f3f4f6", zerolinecolor="#e2e4e9",
                showline=True, linecolor="#e2e4e9",
            ),
            yaxis=dict(
                range=[0, 100], title="NCIS — Natural capital impact",
                gridcolor="#f3f4f6", zerolinecolor="#e2e4e9",
                showline=True, linecolor="#e2e4e9",
            ),
            legend=dict(title="", font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        fig.add_hline(y=50, line_dash="dot", line_color="#9ca3af", line_width=1)
        fig.add_vline(x=50, line_dash="dot", line_color="#9ca3af", line_width=1)
        for ax, ay, txt, c in [
            (88, 88, "DANGER",   "#dc2626"),
            (12, 88, "NAT WARN", "#d97706"),
            (88,  8, "CLM WARN", "#ca8a04"),
            (12,  8, "SAFE",     "#16a34a"),
        ]:
            fig.add_annotation(
                x=ax, y=ay, text=txt, showarrow=False,
                font=dict(color=c, size=9, family="Roboto Mono, monospace"),
            )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════
    # §3–4  Site Detail
    # ════════════════════════════════════════════════════════════
    st.markdown(
        '<div class="section-label">§3–4 ENCORE weights  ·  Site score detail</div>',
        unsafe_allow_html=True,
    )

    col_detail, col_weights = st.columns([11, 10])

    with col_detail:
        st.markdown('<div class="section-title">廠區詳情 / Site detail</div>', unsafe_allow_html=True)

        factory_list     = df["factory_name"].tolist()
        selected_factory = st.selectbox("", factory_list, label_visibility="collapsed", key="site_select")
        fac_data         = df[df["factory_name"] == selected_factory].iloc[0]

        ncis_v = fac_data.get("ncis_score", 0) or 0
        crs_v  = fac_data.get(crs_col, 0) or 0
        quad   = fac_data.get("quadrant", "Safe Zone")

        # Two metric cards + badge (ECS removed — no action value here)
        st.markdown(
            f'<div class="metric-row" style="grid-template-columns:repeat(2,1fr);">'
            f'{metric_card_html("NCIS", f"{ncis_v:.1f}", "/100")}'
            f'{metric_card_html("CRS", f"{crs_v:.1f}", "/100")}'
            f'</div>'
            f'<div style="margin-bottom:14px;">{quadrant_badge(quad)}</div>',
            unsafe_allow_html=True,
        )

        # Score bars — show top 3 by value, rest in expander
        norm_cols = sorted(
            [c for c in df.columns if c.startswith("norm_")
             and not c.startswith("norm_hwdi") and not c.startswith("norm_rx5")],
            key=lambda c: -(fac_data.get(c) or 0),
        )
        valid_cols = [(c, float(fac_data.get(c))) for c in norm_cols
                      if fac_data.get(c) is not None and not pd.isna(fac_data.get(c))]

        if valid_cols:
            st.markdown(
                '<div class="section-caption" style="margin-bottom:6px;">'
                'Normalised layer scores (P1–P99 percentile)</div>',
                unsafe_allow_html=True,
            )
            top_cols   = valid_cols[:3]
            extra_cols = valid_cols[3:]
            bars_top = "".join(score_bar_html(_layer_label(c.replace("norm_", "")), v * 100)
                               for c, v in top_cols)
            st.markdown(bars_top, unsafe_allow_html=True)

            if extra_cols:
                with st.expander(f"Show all {len(valid_cols)} layers"):
                    bars_extra = "".join(
                        score_bar_html(_layer_label(c.replace("norm_", "")), v * 100)
                        for c, v in extra_cols
                    )
                    st.markdown(bars_extra, unsafe_allow_html=True)

        # Monetisation — show Total only, detail in expander
        st.markdown(
            '<div class="section-caption" style="margin-top:14px;">§4C — Monetised ecosystem loss</div>',
            unsafe_allow_html=True,
        )
        coastal_val = fac_data.get("coastal_value_twd", 0.0) or 0.0
        nature_val  = fac_data.get("nature_access_value_twd", 0.0) or 0.0
        total_val   = coastal_val + nature_val

        st.markdown(
            f'<div class="metric-row" style="grid-template-columns:1fr;">'
            f'{metric_card_html("Total monetised loss", f"{total_val/1e4:.1f}", " 萬/yr", "Coastal protection + nature access")}'
            f'</div>',
            unsafe_allow_html=True,
        )
        with st.expander("Breakdown"):
            st.markdown(
                f'<div class="metric-row" style="grid-template-columns:repeat(2,1fr);">'
                f'{metric_card_html("Coastal protection", f"{coastal_val/1e4:.1f}", " 萬/yr", "替代成本法 82.2 TWD/person")}'
                f'{metric_card_html("Nature access", f"{nature_val/1e4:.1f}", " 萬/yr", "支付意願法 1,412 TWD/person")}'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="method-note">氮滯留與泥沙滯留為人口加權複合單位，貨幣化方法仍在研究中，維持實物量指數。</div>',
                unsafe_allow_html=True,
            )

    with col_weights:
        st.markdown(
            '<div class="section-title">ENCORE 依賴權重 / Dependency weights</div>'
            '<div class="section-caption">ISIC → ENCORE ecosystem service dependency → layer weight</div>',
            unsafe_allow_html=True,
        )

        # ENCORE table in expander by default (for methodology reviewers, not decision-makers)
        isic_val = fac_data.get("isic_codes", None)
        if isic_val and pd.notna(isic_val):
            try:
                encore_df  = pd.read_csv("data/encore_dependency.csv")
                isic_list  = str(isic_val).split(";")
                weights_dict = encore_engine.get_mandle_weights(isic_list, encore_df)

                weights_data = []
                for layer, weight in sorted(weights_dict.items(), key=lambda x: -x[1]):
                    norm_val = fac_data.get(f"norm_{layer}")
                    status   = "valid" if (norm_val is not None and not pd.isna(norm_val)) else "nodata"
                    weights_data.append({
                        "Layer":      _layer_label(layer),
                        "Weight":     round(weight, 3),
                        "Norm score": round(float(norm_val), 3) if (norm_val is not None and not pd.isna(norm_val)) else None,
                        "Status":     status,
                    })

                wdf = pd.DataFrame(weights_data)
                st.dataframe(wdf, hide_index=True, use_container_width=True)
                with st.expander("Methodology note"):
                    st.markdown(
                        f'<div class="method-note">ISIC codes: <code>{"; ".join(isic_list)}</code><br>'
                        f'Bio layers (species richness, red list, endemic, KBA) use fixed weight = 0.30 — '
                        f'ENCORE biodiversity mapping incomplete.</div>',
                        unsafe_allow_html=True,
                    )
            except Exception as e:
                st.error(f"載入權重失敗：{e}")
        else:
            st.markdown(
                '<div class="method-note">此廠區無 ISIC 代碼資料。</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════
    # §6  Liability & Neutralisation  ·  §7  Gain Site
    # ════════════════════════════════════════════════════════════
    st.markdown(
        '<div class="section-label">§6 Liability & neutralisation gap  ·  §7 Gain site recommendation</div>',
        unsafe_allow_html=True,
    )

    has_neutralization = all(
        c in df.columns for c in [
            "liability_index", "gain_quality_index",
            "max_conservation_area", "area_needed",
            "liability_twd", "gain_sites_json",
        ]
    )

    if not has_neutralization:
        st.markdown(
            '<div class="method-note">中和模組欄位不存在，請重新執行 pipeline。</div>',
            unsafe_allow_html=True,
        )
        return

    total_liability_twd = df["liability_twd"].sum()
    total_liability_idx = df["liability_index"].sum()
    avg_gain_quality    = df["gain_quality_index"].mean()

    st.markdown(
        f'<div class="metric-row" style="grid-template-columns:repeat(3,1fr);margin-bottom:20px;">'
        f'{metric_card_html("Total liability index", f"{total_liability_idx:.2f}", " km²", "Σ (NCIS/100) × area")}'
        f'{metric_card_html("Total monetised loss", f"{total_liability_twd/1e8:.2f}", " 億/yr", "Coastal + nature access")}'
        f'{metric_card_html("Avg gain quality", f"{avg_gain_quality:.3f}", "", "Portfolio-wide 0–1")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Portfolio liability table ─────────────────────────────
    st.markdown(
        '<div class="section-title">企業負債排序 / Portfolio liability ranking</div>',
        unsafe_allow_html=True,
    )

    lt = df[[
        "factory_name", "ncis_score",
        "liability_index", "liability_twd",
        "gain_quality_index", "area_needed",
    ]].copy()
    lt = lt.sort_values("liability_index", ascending=False)
    lt["liability_twd_萬"]  = (lt["liability_twd"] / 1e4).round(1)
    lt["liability_index"]   = lt["liability_index"].round(3)
    lt["gain_quality_index"] = lt["gain_quality_index"].round(3)
    lt["area_needed"]       = lt["area_needed"].round(1)
    lt["ncis_score"]        = lt["ncis_score"].round(1)
    lt = lt.rename(columns={
        "factory_name":      "Site",
        "ncis_score":        "NCIS",
        "liability_index":   "Liability index",
        "liability_twd_萬":  "Loss 萬TWD/yr",
        "gain_quality_index": "Gain quality",
        "area_needed":       "Area needed km²",
    })
    st.dataframe(
        lt[["Site", "NCIS", "Liability index", "Loss 萬TWD/yr", "Gain quality", "Area needed km²"]],
        hide_index=True,
        use_container_width=True,
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Site-level neutralisation detail ─────────────────────
    st.markdown(
        '<div class="section-title">廠區缺口詳情 / Site neutralisation detail</div>',
        unsafe_allow_html=True,
    )

    col_detail2, col_gain_map = st.columns([9, 13])

    with col_detail2:
        neutral_factory = st.selectbox(
            "", df["factory_name"].tolist(),
            key="neutral_select", label_visibility="collapsed",
        )
        fac_n = df[df["factory_name"] == neutral_factory].iloc[0]

        li          = fac_n["liability_index"]
        gqi         = fac_n["gain_quality_index"]
        max_ca      = fac_n["max_conservation_area"]
        area_needed = fac_n["area_needed"]
        lib_twd     = fac_n["liability_twd"]
        gain_sites  = json.loads(fac_n["gain_sites_json"])

        # Consolidated: 2 cards instead of 4
        st.markdown(
            f'<div class="metric-row" style="grid-template-columns:repeat(2,1fr);margin-bottom:12px;">'
            f'{metric_card_html("Liability index", f"{li:.3f}", " km²", f"Monetised {lib_twd/1e4:.1f} 萬/yr")}'
            f'{metric_card_html("Gain quality index", f"{gqi:.3f}", "", f"Max site {max_ca:.1f} km²")}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Simulation slider
        st.markdown(
            '<div class="section-caption">模擬保育面積 / Simulate conservation area</div>',
            unsafe_allow_html=True,
        )
        default_ca = round(max_ca * 0.5, 3) if max_ca > 0 else 0.0
        step_val   = max(1e-4, float(max_ca) / 100) if max_ca > 0 else 0.1
        sim_ca = st.slider(
            "",
            min_value=0.0,
            max_value=float(max_ca) if max_ca > 0 else 1.0,
            value=float(default_ca),
            step=step_val,
            format="%.3f km²",
            key=f"sim_ca_{neutral_factory}",
            label_visibility="collapsed",
        )

        gain_offset          = gqi * sim_ca
        neutralization_ratio = (gain_offset / li) if li > 0 else 0.0
        pct                  = min(neutralization_ratio * 100, 999.9)

        if neutralization_ratio >= 1.0:
            ratio_cls, ratio_txt = "badge-safe",    "✓ 可達自然資本中和"
        elif neutralization_ratio >= 0.5:
            ratio_cls, ratio_txt = "badge-climate", "接近中和，建議擴大保育"
        elif neutralization_ratio >= 0.2:
            ratio_cls, ratio_txt = "badge-nature",  "中和缺口中等"
        else:
            ratio_cls, ratio_txt = "badge-danger",  "中和缺口嚴重"

        st.markdown(
            f'<div class="metric-row" style="grid-template-columns:repeat(2,1fr);margin-top:12px;margin-bottom:10px;">'
            f'{metric_card_html("Gain offset", f"{gain_offset:.3f}", " km²", f"GQI × {sim_ca:.1f} km²")}'
            f'{metric_card_html("Neutralisation ratio", f"{pct:.1f}", "%", "gain offset ÷ liability")}'
            f'</div>'
            f'<div style="margin-bottom:12px;">'
            f'<span class="quadrant-badge {ratio_cls}">{ratio_txt}</span>'
            f'</div>'
            f'<div class="method-note">'
            f'完全中和所需保育面積：<b>{area_needed:.1f} km²</b>（若 GQI 不變）<br>'
            f'neutralisation ratio = GQI × conservation area ÷ liability index'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Gain site list
        st.markdown(
            '<div class="section-caption" style="margin-top:16px;">增益選址摘要 / Gain site summary</div>',
            unsafe_allow_html=True,
        )
        gain_colors_list = ["#1e3a5f", "#1d4ed8", "#2563eb"]
        for site in gain_sites:
            gc = gain_colors_list[min(site["rank"] - 1, 2)]
            layers_str = " · ".join(_layer_label(l) for l in site["dominant_layers"])
            # gain_score displayed as integer percentage (0–100), not raw 0–1 float
            gain_pct = round(site["gain_score"] * 100, 1)
            st.markdown(
                f'<div class="gain-row">'
                f'<span class="gain-rank">R{site["rank"]}</span>'
                f'<div class="gain-content">'
                f'<div class="gain-action">{site["suggested_action"]}</div>'
                f'<div class="gain-meta">{layers_str} · {site["area_km2"]:.1f} km²</div>'
                f'</div>'
                f'<div class="gain-score" style="color:{gc};">{gain_pct}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with col_gain_map:
        st.markdown(
            '<div class="section-caption">周邊 10km 增益潛力選址 / Gain sites within 10km radius</div>',
            unsafe_allow_html=True,
        )
        fac_lat = fac_n["latitude"]
        fac_lon = fac_n["longitude"]

        m_gain = folium.Map(location=[fac_lat, fac_lon], zoom_start=11, tiles="CartoDB Positron")

        folium.CircleMarker(
            location=[fac_lat, fac_lon], radius=9,
            color="#dc2626", fill=True, fill_color="#dc2626", fill_opacity=0.9,
            tooltip=f"Site: {neutral_factory}",
        ).add_to(m_gain)

        gc_map = ["#1e3a5f", "#1d4ed8", "#2563eb"]

        for site in gain_sites:
            gc = gc_map[min(site["rank"] - 1, 2)]
            gain_pct = round(site["gain_score"] * 100, 1)
            folium.Marker(
                location=[site["center_lat"], site["center_lon"]],
                icon=folium.DivIcon(
                    html=f'<div style="font-size:18px;color:{gc};text-shadow:0 0 3px rgba(255,255,255,.9);">★</div>',
                    icon_size=(20, 20), icon_anchor=(10, 10),
                ),
                tooltip=f'Rank {site["rank"]} · score {gain_pct} · {site["area_km2"]:.1f} km²',
                popup=folium.Popup(
                    f'<div style="font-family:\'Roboto Mono\',monospace;font-size:11px;line-height:1.7;">'
                    f'<b>Gain site rank {site["rank"]}</b><br>'
                    f'Score: {gain_pct}<br>'
                    f'Area: {site["area_km2"]:.1f} km²<br>'
                    f'Dominant layers: {", ".join(_layer_label(l) for l in site["dominant_layers"])}<br>'
                    f'Action: {site["suggested_action"]}</div>',
                    max_width=260,
                ),
            ).add_to(m_gain)

            try:
                poly_geom = shapely_wkt.loads(site["polygon_wkt"])
                polys = [poly_geom] if poly_geom.geom_type == "Polygon" else list(poly_geom.geoms)
                for part in polys:
                    coords = [[lat, lon] for lon, lat in part.exterior.coords]
                    folium.Polygon(
                        locations=coords, color=gc, weight=1.5,
                        fill=True, fill_color=gc, fill_opacity=0.15,
                        tooltip=f'Gain zone rank {site["rank"]} · {site["area_km2"]:.1f} km²',
                    ).add_to(m_gain)
            except Exception:
                pass

        st_folium(m_gain, use_container_width=True, height=480, key=f"gain_map_{neutral_factory}")
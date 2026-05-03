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

def render_main(df, sidebar_params):
    alpha = sidebar_params['alpha']
    beta = sidebar_params['beta']
    time_horizon = sidebar_params['time_horizon']
    crs_col = sidebar_params['crs_col']
    dms_col = sidebar_params['dms_col']
    selected_score_label = sidebar_params['selected_score_label']
    selected_score_col = sidebar_params['selected_score_col']

    # ── 重算動態參數 ──────────────────────────────────────────────────
    if "ncis_score" in df.columns and "norm_hwdi_near" in df.columns:
        for period, hw, rx in [
            ("near", "norm_hwdi_near", "norm_rx5day_near"),
            ("mid",  "norm_hwdi_mid",  "norm_rx5day_mid"),
            ("long", "norm_hwdi_long", "norm_rx5day_long"),
        ]:
            df[f"crs_{period}"] = (beta * df[hw] + (1 - beta) * df[rx]) * 100
        df[dms_col] = alpha * df["ncis_score"] + (1 - alpha) * df[crs_col]

    # ── Header ────────────────────────────────────────────────────────
    st.markdown(f'''
    <div class="ncsi-header">
      <span class="ncsi-wordmark">NCSI</span>
      <span class="ncsi-subtitle">Natural Capital Spatial Intelligence · 自然資本空間智慧平台</span>
      <span class="ncsi-meta-tag">TNFD LEAP · RCP 8.5 · {len(df)} sites · {time_horizon}</span>
    </div>
    ''', unsafe_allow_html=True)

    # ── §0 Executive Overview ─────────────────────────────────────────
    st.markdown('<div class="section-label">§0 — Executive Overview</div>', unsafe_allow_html=True)

    n_danger  = (df["quadrant"] == "Danger Zone").sum()
    n_warning = df["quadrant"].str.startswith("Warning").sum()
    n_safe    = (df["quadrant"] == "Safe Zone").sum()
    avg_ncis  = df["ncis_score"].mean()
    avg_crs   = df[crs_col].mean()
    avg_dms   = df[dms_col].mean()

    st.markdown(f'''
    <div class="metric-row">
      {metric_card_html("Avg NCIS", f"{avg_ncis:.1f}", "/100", "Natural capital impact")}
      {metric_card_html("Avg CRS", f"{avg_crs:.1f}", "/100", time_horizon.split()[0] + "-term scenario")}
      {metric_card_html("Avg DMS", f"{avg_dms:.1f}", "/100", f"α={alpha:.2f}")}
      {metric_card_html("Sites at risk", f"{n_danger + n_warning}", f"/{len(df)}", f"{n_danger} danger · {n_warning} warning")}
    </div>
    ''', unsafe_allow_html=True)

    # ── §1/2 Spatial Evidence + §5 Quadrant ──────────────────────────
    st.markdown('<div class="section-label">§1–2  Spatial Footprint  ·  §5  Quadrant Classification</div>', unsafe_allow_html=True)

    col_map, col_scatter = st.columns([13, 10])

    with col_map:
        st.markdown('<div class="section-title">Site locations — ' + selected_score_label + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-caption">CircleMarker radius proportional to score · click for detail</div>', unsafe_allow_html=True)

        m = folium.Map(location=[24.1, 121.5], zoom_start=8, tiles="CartoDB Positron")

        for _, row in df.iterrows():
            sv   = row.get(selected_score_col, 0) or 0
            col  = score_color(sv)
            popup_html = f'''
            <div style="font-family:monospace;font-size:12px;line-height:1.7;">
            <b style="font-size:13px;">{row.get('factory_name','')}</b><br>
            <span style="color:#6b7280;">NCIS</span> {row.get('ncis_score',0):.1f} &nbsp;
            <span style="color:#6b7280;">CRS</span> {row.get(crs_col,0):.1f} &nbsp;
            <span style="color:#6b7280;">DMS</span> {row.get(dms_col,0):.1f}<br>
            <span style="color:#6b7280;">Quadrant</span> {row.get('quadrant','')}
            </div>'''
            folium.CircleMarker(
                location=[row.get("latitude", 24.1), row.get("longitude", 121.5)],
                radius=10,
                color=col, fill=True, fill_color=col, fill_opacity=0.85,
                tooltip=row.get("factory_name", ""),
                popup=folium.Popup(popup_html, max_width=280)
            ).add_to(m)

        legend_html = '''
        {% macro html(this, kwargs) %}
        <div style="position:fixed;bottom:24px;left:24px;
            background:#ffffff;border:1px solid #e5e4e0;border-radius:4px;
            padding:10px 14px;font-family:monospace;font-size:11px;color:#6b7280;z-index:9999;">
            <div style="margin-bottom:5px;color:#9ca3af;letter-spacing:.06em;font-size:10px;">SCORE RANGE</div>
            <div><span style="color:#f87171;margin-right:6px;">●</span>&ge; 70 &nbsp; High impact</div>
            <div><span style="color:#fb923c;margin-right:6px;">●</span>40–69 &nbsp; Moderate</div>
            <div><span style="color:#4ade80;margin-right:6px;">●</span>< 40 &nbsp; Low impact</div>
        </div>
        {% endmacro %}'''
        macro = MacroElement()
        macro._template = Template(legend_html)
        m.get_root().add_child(macro)

        st_folium(m, use_container_width=True, height=400, key=f"map_{selected_score_col}_{alpha}_{beta}")

    with col_scatter:
        st.markdown('<div class="section-title">Risk quadrant matrix</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-caption">X = CRS · Y = NCIS · bubble size = ECS (capacity scale)</div>', unsafe_allow_html=True)

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
            "Danger Zone":       "#f87171",
            "Warning — Nature":  "#fb923c",
            "Warning — Climate": "#fbbf24",
            "Safe Zone":         "#4ade80",
        }

        fig = px.scatter(
            plot_df, x=crs_col, y="ncis_score",
            size="ecs_score", color="q_label",
            color_discrete_map=color_map_plot,
            hover_name="factory_name",
            hover_data={"ncis_score":":.1f", crs_col:":.1f", dms_col:":.1f", "q_label":False, "ecs_score":False},
            height=400,
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#ffffff",
            font=dict(family="IBM Plex Mono, monospace", size=11, color="#9ca3af"),
            xaxis=dict(range=[0,100], title="CRS — Climate risk score", gridcolor="#f0efeb", zerolinecolor="#e5e4e0"),
            yaxis=dict(range=[0,100], title="NCIS — Natural capital impact", gridcolor="#f0efeb", zerolinecolor="#e5e4e0"),
            legend=dict(title="", font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        fig.add_hline(y=50, line_dash="dot", line_color="#374151", line_width=1)
        fig.add_vline(x=50, line_dash="dot", line_color="#374151", line_width=1)
        for (ax, ay, txt, col) in [(92,92,"Danger",    "#f87171"),
                                    (8, 92,"Nat. warn", "#fb923c"),
                                    (92, 8,"Clim. warn","#fbbf24"),
                                    (8,  8,"Safe",      "#4ade80")]:
            fig.add_annotation(x=ax, y=ay, text=txt, showarrow=False,
                               font=dict(color=col, size=10, family="IBM Plex Mono, monospace"))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── §3/4 Site Detail ─────────────────────────────────────────────
    st.markdown('<div class="section-label">§3–4  ENCORE Weights  ·  Site Score Detail</div>', unsafe_allow_html=True)

    col_detail, col_weights = st.columns([11, 10])

    with col_detail:
        st.markdown('<div class="section-title">廠區詳情 / Site detail</div>', unsafe_allow_html=True)

        factory_list     = df["factory_name"].tolist()
        selected_factory = st.selectbox("", factory_list, label_visibility="collapsed", key="site_select")
        fac_data         = df[df["factory_name"] == selected_factory].iloc[0]

        ncis_v = fac_data.get("ncis_score", 0) or 0
        crs_v  = fac_data.get(crs_col, 0) or 0
        dms_v  = fac_data.get(dms_col, 0) or 0
        ecs_v  = fac_data.get("ecs_score", 0) or 0
        quad   = fac_data.get("quadrant", "Safe Zone")

        st.markdown(f'''
<div class="metric-row">
  {metric_card_html("NCIS", f"{ncis_v:.1f}", "/100")}
  {metric_card_html("CRS", f"{crs_v:.1f}", "/100")}
  {metric_card_html("DMS", f"{dms_v:.1f}", "/100")}
  {metric_card_html("ECS", f"{ecs_v:.1f}", "/100")}
</div>
<div style="margin-bottom:12px;">{quadrant_badge(quad)}</div>
''', unsafe_allow_html=True)

        # Score bars — normalised layer scores
        bars_html = ""
        norm_cols = [c for c in df.columns if c.startswith("norm_") and not c.startswith("norm_hwdi") and not c.startswith("norm_rx5")]
        for nc in sorted(norm_cols):
            val = fac_data.get(nc)
            if val is not None and not pd.isna(val):
                bars_html += score_bar_html(nc.replace("norm_", ""), float(val) * 100)

        if bars_html:
            st.markdown('<div class="section-caption" style="margin-bottom:6px;">Normalised layer scores (0–100, P1–P99 percentile)</div>', unsafe_allow_html=True)
            st.markdown(bars_html, unsafe_allow_html=True)

        # Monetisation
        st.markdown('<div class="section-caption" style="margin-top:14px;">§4.C — Ecosystem service loss (monetised)</div>', unsafe_allow_html=True)
        coastal_val = fac_data.get("coastal_value_twd", 0.0) or 0.0
        nature_val  = fac_data.get("nature_access_value_twd", 0.0) or 0.0
        total_val   = coastal_val + nature_val

        st.markdown(f'''
<div class="metric-row" style="grid-template-columns:repeat(3,1fr);">
  {metric_card_html("Coastal protection loss", f"{coastal_val/1e4:.1f}", " 萬/yr", "替代成本法 82.2 TWD/person")}
  {metric_card_html("Nature access loss", f"{nature_val/1e4:.1f}", " 萬/yr", "支付意願法 1,412 TWD/person")}
  {metric_card_html("Total monetised loss", f"{total_val/1e4:.1f}", " 萬/yr", "Coastal + nature access")}
</div>
<div class="method-note">氮滯留與泥沙滯留為人口加權複合單位，貨幣化方法仍在研究中，維持實物量指數。</div>
''', unsafe_allow_html=True)

    with col_weights:
        st.markdown('<div class="section-title">ENCORE 依賴權重 / Dependency weights</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-caption">ISIC → ENCORE ecosystem service dependency → Mandle layer weight</div>', unsafe_allow_html=True)

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
                        "Layer": layer,
                        "Weight": round(weight, 4),
                        "Norm score": round(float(norm_val), 4) if (norm_val is not None and not pd.isna(norm_val)) else None,
                        "Status": status,
                    })

                wdf = pd.DataFrame(weights_data)
                st.dataframe(wdf, hide_index=True, use_container_width=True)
                st.markdown(f'<div class="method-note">ISIC codes: <code>{"; ".join(isic_list)}</code><br>Bio layers (species_richness, red_list, endemic, kba) use fixed weight = 0.30 — ENCORE biodiversity mapping incomplete.</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"載入權重失敗：{e}")
        else:
            st.markdown('<div class="method-note">此廠區無 ISIC 代碼資料。</div>', unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── §6/7 Neutralisation Module ────────────────────────────────────
    st.markdown('<div class="section-label">§6  Liability & Neutralisation Gap  ·  §7  Gain Site Recommendation</div>', unsafe_allow_html=True)
    
    has_neutralization = all(c in df.columns for c in [
        'liability_index', 'gain_quality_index',
        'max_conservation_area', 'area_needed',
        'liability_twd', 'gain_sites_json'
    ])
    
    if not has_neutralization:
        st.markdown('<div class="method-note">中和模組欄位不存在，請重新執行 pipeline。</div>', unsafe_allow_html=True)
    else:
        total_liability_twd = df['liability_twd'].sum()
        total_liability_idx = df['liability_index'].sum()
        avg_gain_quality    = df['gain_quality_index'].mean()
    
        st.markdown(f'''
    <div class="metric-row" style="grid-template-columns:repeat(3,1fr);margin-bottom:20px;">
      {metric_card_html('Total liability index', f'{total_liability_idx:.2f}', ' km²', 'Σ (NCIS/100) × area')}
      {metric_card_html('Total monetised loss', f'{total_liability_twd/1e8:.2f}', ' 億/yr', 'Coastal + nature access')}
      {metric_card_html('Avg gain quality', f'{avg_gain_quality:.3f}', '', 'Portfolio-wide 0–1')}
    </div>
    ''', unsafe_allow_html=True)
    
        # Liability table
        st.markdown('<div class="section-title">企業負債排序 / Portfolio liability ranking</div>', unsafe_allow_html=True)
        lt = df[[
            'factory_name', 'ncis_score', 'area_km2',
            'liability_index', 'liability_twd',
            'gain_quality_index', 'area_needed'
        ]].copy()
        lt = lt.sort_values('liability_index', ascending=False)
        lt['liability_twd_萬'] = (lt['liability_twd'] / 1e4).round(1)
        lt['liability_index']   = lt['liability_index'].round(3)
        lt['gain_quality_index'] = lt['gain_quality_index'].round(3)
        lt['area_needed']       = lt['area_needed'].round(1)
        lt['ncis_score']        = lt['ncis_score'].round(1)
        lt = lt.rename(columns={
            'factory_name':      'Site',
            'ncis_score':        'NCIS',
            'area_km2':          'Area km²',
            'liability_index':   'Liability index',
            'liability_twd_萬':  'Loss 萬TWD/yr',
            'gain_quality_index': 'Gain quality',
            'area_needed':       'Area needed km²',
        })
        st.dataframe(
            lt[['Site','NCIS','Area km²','Liability index','Loss 萬TWD/yr','Gain quality','Area needed km²']],
            hide_index=True, use_container_width=True
        )
    
        st.markdown('<hr>', unsafe_allow_html=True)
    
        # Site-level detail
        st.markdown('<div class="section-title">廠區缺口詳情 / Site neutralisation detail</div>', unsafe_allow_html=True)
    
        col_detail, col_gain_map = st.columns([9, 13])
    
        with col_detail:
            neutral_factory = st.selectbox('', df['factory_name'].tolist(),
                                           key='neutral_select', label_visibility='collapsed')
            fac_n = df[df['factory_name'] == neutral_factory].iloc[0]
    
            li          = fac_n['liability_index']
            gqi         = fac_n['gain_quality_index']
            max_ca      = fac_n['max_conservation_area']
            area_needed = fac_n['area_needed']
            lib_twd     = fac_n['liability_twd']
            gain_sites  = json.loads(fac_n['gain_sites_json'])
    
            st.markdown(f'''
    <div class="metric-row" style="grid-template-columns:repeat(2,1fr);margin-bottom:12px;">
      {metric_card_html('Liability index', f'{li:.3f}', ' km²')}
      {metric_card_html('Gain quality index', f'{gqi:.3f}', '', '0–1')}
    </div>
    <div class="metric-row" style="grid-template-columns:repeat(2,1fr);margin-bottom:12px;">
      {metric_card_html('Monetised loss', f'{lib_twd/1e4:.1f}', ' 萬/yr')}
      {metric_card_html('Max conservation area', f'{max_ca:.1f}', ' km²', 'Top-1 gain site')}
    </div>
    ''', unsafe_allow_html=True)
    
            # 滑桿
            st.markdown('<div class="section-caption" style="margin-top:8px;">模擬保育面積 / Simulate conservation area</div>', unsafe_allow_html=True)
    
            default_ca = round(max_ca * 0.5, 1) if max_ca > 0 else 0.0
            sim_ca = st.slider(
                '',
                min_value=0.0,
                max_value=float(max_ca) if max_ca > 0 else 1.0,
                value=default_ca,
                step=round(max_ca / 100, 2) if max_ca > 0 else 0.1,
                format='%.1f km²',
                key=f'sim_ca_{neutral_factory}',
                label_visibility='collapsed'
            )
    
            # 即時計算
            gain_offset          = gqi * sim_ca
            neutralization_ratio = (gain_offset / li) if li > 0 else 0.0
            pct                  = min(neutralization_ratio * 100, 999.9)
    
            if neutralization_ratio >= 1.0:
                ratio_cls, ratio_txt = 'badge-safe',    '✅ 可達自然資本中和'
            elif neutralization_ratio >= 0.5:
                ratio_cls, ratio_txt = 'badge-warning', '🟡 接近中和，建議擴大保育'
            elif neutralization_ratio >= 0.2:
                ratio_cls, ratio_txt = 'badge-orange',  '🟠 中和缺口中等'
            else:
                ratio_cls, ratio_txt = 'badge-danger',  '🔴 中和缺口嚴重'
    
            st.markdown(f'''
    <div class="metric-row" style="grid-template-columns:repeat(2,1fr);margin-top:12px;margin-bottom:8px;">
      {metric_card_html('Gain offset', f'{gain_offset:.3f}', ' km²', f'GQI × {sim_ca:.1f} km²')}
      {metric_card_html('Neutralisation ratio', f'{pct:.1f}', '%', 'gain offset ÷ liability')}
    </div>
    <div style="margin-bottom:12px;"><span class="quadrant-badge {ratio_cls}">{ratio_txt}</span></div>
    <div class="method-note">
      完全中和所需保育面積：<b>{area_needed:.1f} km²</b>（若 GQI 不變）<br>
      neutralisation ratio = GQI × conservation area ÷ liability index
    </div>
    ''', unsafe_allow_html=True)
    
            # Gain site list
            st.markdown('<div class="section-caption" style="margin-top:16px;">增益選址摘要 / Gain site summary</div>', unsafe_allow_html=True)
            gain_colors_list = ['#0d9488', '#059669', '#65a30d']
            for site in gain_sites:
                gc = gain_colors_list[site['rank'] - 1]
                layers_str = ' · '.join(site['dominant_layers'])
                st.markdown(f'''
    <div class="gain-row">
      <span class="gain-rank">R{site["rank"]}</span>
      <div class="gain-content">
        <div class="gain-action">{site["suggested_action"]}</div>
        <div class="gain-meta">{layers_str} · {site["area_km2"]:.1f} km²</div>
      </div>
      <div class="gain-score" style="color:{gc};">{site["gain_score"]:.4f}</div>
    </div>
    ''', unsafe_allow_html=True)
    
        with col_gain_map:
            st.markdown('<div class="section-caption">周邊 10km 增益潛力選址 / Gain sites within 10km radius</div>', unsafe_allow_html=True)
            fac_lat = fac_n['latitude']
            fac_lon = fac_n['longitude']
    
            m_gain = folium.Map(location=[fac_lat, fac_lon], zoom_start=11, tiles='CartoDB Positron')
    
            folium.CircleMarker(
                location=[fac_lat, fac_lon], radius=9,
                color='#f87171', fill=True, fill_color='#f87171', fill_opacity=0.9,
                tooltip=f'Site: {neutral_factory}'
            ).add_to(m_gain)
    
            gc_map = ['#0d9488', '#059669', '#65a30d']
    
            for site in gain_sites:
                gc = gc_map[site['rank'] - 1]
                folium.Marker(
                    location=[site['center_lat'], site['center_lon']],
                    icon=folium.DivIcon(
                        html=f'<div style="font-size:18px;color:{gc};text-shadow:0 0 4px rgba(0,0,0,.8);">★</div>',
                        icon_size=(20, 20), icon_anchor=(10, 10),
                    ),
                    tooltip=f'Rank {site["rank"]} · gain score {site["gain_score"]:.4f} · {site["area_km2"]:.1f} km²',
                    popup=folium.Popup(
                        f'<div style="font-family:monospace;font-size:11px;line-height:1.7;">'
                        f'<b>Gain site rank {site["rank"]}</b><br>'
                        f'Score: {site["gain_score"]:.4f}<br>'
                        f'Area: {site["area_km2"]:.1f} km²<br>'
                        f'Dominant layers: {", ".join(site["dominant_layers"])}<br>'
                        f'Action: {site["suggested_action"]}</div>',
                        max_width=260
                    )
                ).add_to(m_gain)
    
                try:
                    poly_geom = shapely_wkt.loads(site['polygon_wkt'])
                    polys = [poly_geom] if poly_geom.geom_type == 'Polygon' else list(poly_geom.geoms)
                    for part in polys:
                        coords = [[lat, lon] for lon, lat in part.exterior.coords]
                        folium.Polygon(
                            locations=coords, color=gc, weight=1.5,
                            fill=True, fill_color=gc, fill_opacity=0.18,
                            tooltip=f'Gain zone rank {site["rank"]} · {site["area_km2"]:.1f} km²'
                        ).add_to(m_gain)
                except Exception:
                    pass
    
            st_folium(m_gain, use_container_width=True, height=480, key=f'gain_map_{neutral_factory}')

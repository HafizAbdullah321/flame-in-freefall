"""Evidence coverage map (REQ-E1): what our experiments cover in (pressure, oxygen) space versus planned mission atmospheres."""
import numpy as np, pandas as pd
import plotly.graph_objects as go
from scipy.spatial import ConvexHull, Delaunay

NEAR_SCALE = (10.0, 2.0)          # kPa, % oxygen: one 'unit' of distance for the nearest-experiment test
SYMBOL = {"none": "circle", "Aluminium": "diamond", "Stainless Steel": "triangle-up"}
COLORS = {"none": "#ffffff", "Aluminium": "#ffa726", "Stainless Steel": "#9aa4b8"}
STATUS_COLOR = {"INSIDE": "#66bb6a", "NEAR": "#ffa726", "OUTSIDE": "#ef5350"}
STATUS_TEXT = {"INSIDE": "Inside the tested band", "NEAR": "Near the tested band", "OUTSIDE": "Outside the tested band"}

def _pts(exp): return np.c_[exp["p_kpa"].to_numpy(float), exp["o2_pct"].to_numpy(float)]

def hull_polygon(exp):
    pts = _pts(exp); h = ConvexHull(pts); v = pts[h.vertices]; return np.vstack([v, v[:1]])

def ppo2_range(exp):
    pp = exp["o2_pct"] * exp["p_kpa"] / 100; return float(pp.min()), float(pp.max())

def ppo2_gap(p, o2, exp):
    lo, hi = ppo2_range(exp); pp = p * o2 / 100; return float(max(lo - pp, pp - hi, 0.0))

def atmosphere_status(p, o2, exp):
    """INSIDE (convex hull of tested conditions) | NEAR (close to an experiment and partial pressure within 0.5 kPa) | OUTSIDE."""
    pts = _pts(exp)
    if Delaunay(pts).find_simplex(np.array([p, o2])) >= 0: return "INSIDE"
    d = np.min(np.sqrt(((pts[:, 0] - p) / NEAR_SCALE[0]) ** 2 + ((pts[:, 1] - o2) / NEAR_SCALE[1]) ** 2))
    return "NEAR" if d <= 1.0 and ppo2_gap(p, o2, exp) <= 0.5 else "OUTSIDE"

def planned_points(scenarios):
    """Unique (pressure, oxygen) environments; several scenarios can share one atmosphere (they differ in gravity)."""
    pts = {}
    for s in scenarios.values():
        k = (round(s.pressure_kpa, 2), round(s.o2_pct, 2)); pts.setdefault(k, []).append(s)
    return pts

OVERLAY_COLOR = {"Ground (1g)": "#ba68c8", "Planned": "#ffb74d"}
def _overlay_entries(catalog, exclude_ids=("E07",)):
    return [e for e in (catalog or []) if e["id"] not in exclude_ids and e["o2_min"] is not None and e["pressure_kpa_min"] is not None]

def coverage_table(exp, scenarios, catalog=None):
    rows = []
    for _, r in exp.sort_values("o2_pct").iterrows():
        rows.append(dict(Type="Experiment", Name=r["exp"], Pressure_kPa=round(r["p_kpa"], 1), Oxygen_pct=round(r["o2_pct"], 1),
                         O2_partial_kPa=round(r["o2_pct"] * r["p_kpa"] / 100, 1), Status="Tested", Gap_kPa=0.0))
    for (p, o2), ss in planned_points(scenarios).items():
        st = atmosphere_status(p, o2, exp)
        rows.append(dict(Type="Planned environment", Name="; ".join(s.name for s in ss), Pressure_kPa=p, Oxygen_pct=o2,
                         O2_partial_kPa=round(p * o2 / 100, 1), Status=STATUS_TEXT[st], Gap_kPa=round(ppo2_gap(p, o2, exp), 1)))
    for e in _overlay_entries(catalog):
        rng = "" if (e["pressure_kpa_min"] == e["pressure_kpa_max"] and e["o2_min"] == e["o2_max"]) else f", range {e['pressure_kpa_min']:g} to {e['pressure_kpa_max']:g} kPa and {e['o2_min']:g} to {e['o2_max']:g}% O2 (lowest values listed)"
        rows.append(dict(Type="Other experiment", Name=f"{e['name']} ({e['type']}, {e['status']}{rng})", Pressure_kPa=float(e["pressure_kpa_min"]), Oxygen_pct=float(e["o2_min"]),
                         O2_partial_kPa=round(e["o2_min"] * e["pressure_kpa_min"] / 100, 1),
                         Status="Not microgravity-tested here" if (e["gravity_g_min"] or 0) >= 0.05 else "Microgravity", Gap_kPa=float("nan")))
    return pd.DataFrame(rows)

def coverage_figure(exp, scenarios, selected=None, catalog=None):
    fig = go.Figure(); poly = hull_polygon(exp)
    fig.add_trace(go.Scatter(x=poly[:, 0], y=poly[:, 1], mode="lines", fill="toself", name="Tested band (hull of our experiments)", fillcolor="rgba(102,187,106,0.20)",
                             line=dict(color="#66bb6a", width=2), hoverinfo="skip"))
    P = np.arange(40, 111, 1.0)
    for i, pp in enumerate((15, 19, 21, 25, 30)):                       # constant oxygen partial pressure lines
        o2 = 100 * pp / P; m = (o2 >= 14) & (o2 <= 42)
        fig.add_trace(go.Scatter(x=P[m], y=o2[m], mode="lines", line=dict(color="rgba(168,178,198,0.55)", width=1, dash="dot"), name="Constant O2 partial pressure",
                                 legendgroup="ppo2", showlegend=(i == 0), hovertemplate=f"{pp} kPa O2 partial pressure<extra></extra>"))
        k = np.where(m)[0]
        if len(k): fig.add_annotation(x=P[k[-1]], y=o2[k[-1]], text=f"{pp} kPa", showarrow=False, xanchor="left", font=dict(size=11, color="#a8b2c6"))
    for mat, d in exp.groupby("gap_material"):
        lab = "Experiment: continuous PMMA" if mat == "none" else f"Experiment: {mat} barriers"
        fig.add_trace(go.Scatter(x=d["p_kpa"], y=d["o2_pct"], mode="markers", name=lab, marker=dict(symbol=SYMBOL[mat], size=9, color=COLORS[mat], line=dict(width=1, color="#202940")),
                                 customdata=np.c_[d["exp"]], hovertemplate="%{customdata[0]}<br>%{x:.1f} kPa, %{y:.1f}% O2<extra></extra>"))
    shown = set()
    for e in _overlay_entries(catalog):                                   # other experiments: ground (1g) tests and planned platforms
        c = OVERLAY_COLOR.get(e["type"], "#4dd0e1"); grp = e["type"]; first = grp not in shown; shown.add(grp)
        lab = f"Other experiments: {'ground (1g) tests' if grp == 'Ground (1g)' else grp.lower()}"
        hov = f"{e['name']}<br>{e['type']}, {e['status']}<extra></extra>"
        if e["o2_min"] == e["o2_max"] and e["pressure_kpa_min"] == e["pressure_kpa_max"]:
            fig.add_trace(go.Scatter(x=[e["pressure_kpa_min"]], y=[e["o2_min"]], mode="markers", name=lab, legendgroup=grp, showlegend=first,
                                     marker=dict(symbol="square-open", size=13, color=c, line=dict(width=2.5, color=c)), hovertemplate=hov))
        else:
            x0, x1, y0, y1 = e["pressure_kpa_min"], e["pressure_kpa_max"], e["o2_min"], e["o2_max"]
            fig.add_trace(go.Scatter(x=[x0, x1, x1, x0, x0], y=[y0, y0, y1, y1, y0], mode="lines", name=lab, legendgroup=grp, showlegend=first,
                                     line=dict(color=c, width=2, dash="dash"), fill="toself", fillcolor="rgba(186,104,200,0.10)" if grp == "Ground (1g)" else "rgba(255,183,77,0.10)", hovertemplate=hov))
    for (p, o2), ss in planned_points(scenarios).items():
        st = atmosphere_status(p, o2, exp); sel = selected is not None and any(s.key == selected for s in ss)
        label = f"{p * 0.145038:.1f} psia, {o2:g}% O2"
        fig.add_trace(go.Scatter(x=[p], y=[o2], mode="markers+text", text=[label], textposition="top center", textfont=dict(size=12, color="#ffffff"),
                                 name=f"Planned: {STATUS_TEXT[st].lower()}", legendgroup=st, showlegend=False,
                                 marker=dict(symbol="star", size=24 if sel else 17, color=STATUS_COLOR[st], line=dict(width=2.5 if sel else 1, color="#ffffff")),
                                 hovertemplate="%{text}<br>" + "<br>".join(f"{s.name} ({s.g:g} g)" for s in ss) + f"<br>{STATUS_TEXT[st]}; O2 partial pressure {p * o2 / 100:.1f} kPa<extra></extra>"))
    for st, c in STATUS_COLOR.items():                                    # legend entries for the star states
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=f"Planned environment: {STATUS_TEXT[st].lower()}", marker=dict(symbol="star", size=14, color=c, line=dict(width=1, color="#fff"))))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=520,
                      font=dict(family="Roboto, Helvetica Neue, Arial, sans-serif", color="#dfe4ee", size=13), margin=dict(t=10, r=60),
                      xaxis=dict(title="Total pressure (kPa)", range=[40, 112], gridcolor="rgba(255,255,255,0.08)"),
                      yaxis=dict(title="Oxygen (%)", range=[15, 42], gridcolor="rgba(255,255,255,0.08)"), legend=dict(orientation="h", y=-0.22))
    return fig

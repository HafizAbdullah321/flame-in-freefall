"""Visual theme: deep navy surfaces, raised colored card headers, purple accent, Roboto / Roboto Slab.
Fonts are bundled in app/static (served by Streamlit static serving), so nothing is loaded from the internet."""
BG, CARD, INSET, SIDEBAR = "#1a2035", "#202940", "#141a2e", "#161c2e"
TEXT, MUTED, LINK, ACCENT = "#ffffff", "#a8b2c6", "#4dd0e1", "#ce93d8"
GRADIENTS = {                       # white text on every one of these meets 3:1 (large bold card titles); most meet 4.5:1
    "green":  ("#43a047", "#2e7d32", "76,175,80"),
    "orange": ("#ef6c00", "#e65100", "255,152,0"),
    "red":    ("#e53935", "#c62828", "244,67,54"),
    "purple": ("#9c27b0", "#8e24aa", "156,39,176"),
    "teal":   ("#0097a7", "#00838f", "0,188,212"),
}
FONT_SANS = "'Roboto','Helvetica Neue',Helvetica,Arial,sans-serif"
FONT_SLAB = "'Roboto Slab','Roboto',Georgia,serif"

def _face(family, weight, file):
    return f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};font-display:swap;src:url('app/static/{file}') format('woff2');}}"

def css():
    faces = "".join([_face("Roboto", w, f"roboto-{w}.woff2") for w in (300, 400, 500, 700)] + [_face("Roboto Slab", w, f"roboto-slab-{w}.woff2") for w in (400, 700)])
    grads = "".join(f".ff-{n}{{background:linear-gradient(60deg,{a},{b});--glow:rgba({g},.40);}}" for n, (a, b, g) in GRADIENTS.items())
    cards = '[class*="st-key-card_"]'
    return f"""<style>
{faces}
html, body, .stApp {{ font-family:{FONT_SANS}; }}
.stApp :is(p, li, label, button, input, textarea, select, td, th, a, small, [data-testid="stMarkdownContainer"], [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [role="tab"], [data-testid="stCaptionContainer"]):not([data-testid="stIconMaterial"]) {{ font-family:{FONT_SANS} !important; }}
.stApp :is(h1, h1 span, .ff-head h2) {{ font-family:{FONT_SLAB} !important; }}
.stApp {{ background:{BG}; color:{TEXT}; }}
[data-testid="stHeader"] {{ background:transparent; }}
[data-testid="stDecoration"], footer, [data-testid="stStatusWidget"] {{ display:none !important; }}
.block-container {{ padding-top:2.2rem; max-width:1400px; }}
h1, h1 * {{ font-weight:400; font-size:1.9rem; letter-spacing:.2px; color:{TEXT}; }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {{ color:{MUTED} !important; opacity:1 !important; }}

/* sidebar */
[data-testid="stSidebar"] {{ background:{SIDEBAR}; box-shadow:0 0 28px rgba(0,0,0,.35); }}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h2 * {{ font-size:.8rem; font-weight:500; text-transform:uppercase; letter-spacing:1.4px; color:{MUTED}; }}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p {{ font-size:.95rem; }}

/* tabs as pills */
[role="tablist"] {{ gap:8px; border-bottom:none !important; }}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{ display:none !important; }}
[role="tab"] {{ border-radius:6px; padding:8px 20px; color:{MUTED}; font-size:.9rem; font-weight:500; letter-spacing:.3px; }}
[role="tab"][aria-selected="true"] {{ color:#fff; background:linear-gradient(60deg,#9c27b0,#8e24aa); box-shadow:0 4px 20px 0 rgba(0,0,0,.14), 0 7px 10px -5px rgba(156,39,176,.4); }}

/* cards with raised colored headers */
{cards} {{ background:{CARD}; border-radius:6px; padding:0 20px 20px; margin-top:26px; box-shadow:0 1px 4px 0 rgba(0,0,0,.14); }}
.ff-head {{ border-radius:6px; padding:14px 18px; margin:-26px 0 10px; color:#fff; box-shadow:0 4px 20px 0 rgba(0,0,0,.14), 0 7px 10px -5px var(--glow); }}
.ff-head h2 {{ font-weight:400; font-size:1.3rem; line-height:1.3; margin:0; padding:0; color:#fff; }}
.ff-head p {{ margin:3px 0 0; font-size:.85rem; font-weight:300; color:#fff; }}
{grads}

/* stat cards with raised icon boxes */
.ff-stat {{ background:{CARD}; border-radius:6px; padding:12px 18px 12px 12px; margin-top:26px; min-height:88px; display:flex; align-items:flex-start; gap:12px; box-shadow:0 1px 4px 0 rgba(0,0,0,.14); }}
.ff-icon {{ width:62px; height:62px; flex:none; margin-top:-26px; border-radius:6px; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 20px 0 rgba(0,0,0,.14), 0 7px 10px -5px var(--glow); }}
.ff-icon svg {{ width:30px; height:30px; fill:none; stroke:#fff; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }}
.ff-stat-body {{ margin-left:auto; text-align:right; }}
.ff-stat-label {{ font-size:.85rem; color:{MUTED}; font-weight:400; }}
.ff-stat-value {{ font-size:1.75rem; font-weight:300; line-height:1.25; color:#fff; }}
.ff-stat-value small {{ font-size:.9rem; color:{MUTED}; font-weight:400; margin-left:3px; }}

/* metrics, alerts, expander, chat */
[data-testid="stMetricLabel"] * {{ color:{MUTED}; font-size:.9rem; }}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * {{ font-size:2.6rem; font-weight:300; line-height:1.15; }}
[data-testid="stAlert"] {{ border-radius:6px; border:none; }}
[data-testid="stAlertContentInfo"], [data-testid="stAlertContentInfo"] * {{ color:#d6ebff !important; }}
[data-testid="stAlertContentSuccess"], [data-testid="stAlertContentSuccess"] * {{ color:#d2f4d6 !important; }}
[data-testid="stAlertContentWarning"], [data-testid="stAlertContentWarning"] * {{ color:#ffe9b8 !important; }}
[data-testid="stAlertContentError"], [data-testid="stAlertContentError"] * {{ color:#ffd3d3 !important; }}
[data-testid="stExpander"] {{ border:1px solid rgba(255,255,255,.08); border-radius:6px; background:transparent; }}
[data-testid="stChatMessage"] {{ background:{INSET}; border-radius:6px; }}
[data-baseweb="input"], [data-baseweb="base-input"], .stTextInput input {{ background:{INSET} !important; border-radius:6px; }}
[data-baseweb="input"] {{ border:1px solid rgba(255,255,255,.18) !important; }}
/* risk cards */
.ff-risk-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(290px,1fr)); gap:16px; margin-top:6px; }}
.ff-risk {{ background:{INSET}; border-radius:6px; padding:14px 16px; border-left:4px solid var(--c); }}
.ff-risk h3 {{ font-family:{FONT_SLAB} !important; font-size:1.05rem; font-weight:400; margin:0 0 2px; padding:0; color:#fff; }}
.ff-badge {{ font-size:.82rem; font-weight:500; letter-spacing:.3px; color:var(--t); }}
.ff-risk p {{ font-size:.88rem; line-height:1.45; color:#d6dbe8; margin:8px 0 0; }}
.ff-risk p.note {{ color:{MUTED}; font-style:italic; }}
.ff-risk a {{ color:{LINK}; }}
a {{ color:{LINK}; }}
hr {{ border-color:rgba(255,255,255,.08); }}
</style>"""

def card_head(title, subtitle="", color="green"):
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    return f'<div class="ff-head ff-{color}"><h2>{title}</h2>{sub}</div>'

ICONS = {   # simple outline icons, decorative (aria-hidden)
    "pressure": '<circle cx="12" cy="13" r="8"/><path d="M12 13l4-4M7 13h1M12 8v1M16 13h1"/>',
    "flow": '<path d="M3 8h11a3 3 0 1 0-3-3M3 13h15a3 3 0 1 1-3 3M3 18h7"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5 9-5zM3 13l9 5 9-5"/>',
    "status": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>',
    "alert": '<circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 16.5v.5"/>',
}

def stat_card(label, value, unit="", color="orange", icon="pressure"):
    u = f"<small>{unit}</small>" if unit else ""
    return (f'<div class="ff-stat"><div class="ff-icon ff-{color}"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS[icon]}</svg></div>'
            f'<div class="ff-stat-body"><div class="ff-stat-label">{label}</div><div class="ff-stat-value">{value}{u}</div></div></div>')


import html as _html
RISK_STYLE = {"PREDICTED": ("#66bb6a", "#a5d6a7"), "MEASURED": ("#66bb6a", "#a5d6a7"), "INDIRECT": ("#ffa726", "#ffcc80"),
              "NO_PREDICTION": ("#ffa726", "#ffcc80"), "NONE": ("#ef5350", "#ef9a9a")}
RISK_SYMBOLS = {"PREDICTED": "●", "MEASURED": "●", "INDIRECT": "▲", "NO_PREDICTION": "▲", "NONE": "■"}

def risk_cards_html(cards, state_text):
    """cards: output of insights.risk_cards.build_cards; state_text: dict state -> label. Returns one HTML grid (all text escaped)."""
    e = _html.escape; out = ['<div class="ff-risk-grid">']
    for c in cards:
        col, txt = RISK_STYLE[c["state"]]
        sym = RISK_SYMBOLS.get(c["state"], "●")
        body = ""
        if c["numbers"]:
            n = c["numbers"]; body += f"<p><strong>{n['rate']:.2f} mm/s</strong> (90% interval {n['lo']:.2f} to {n['hi']:.2f})</p>"
        for f in c["findings"]:
            short = f["finding"] if len(f["finding"]) <= 150 else f["finding"][:147].rstrip() + "..."
            tag = "" if f.get("verified") == "yes" else " (not yet verified)"
            body += f'<p>{e(f["id"])}: {e(short)} <a href="{e(f["source_url"])}">source</a>{e(tag)}</p>'
        if c["note"]: body += f'<p class="note">{e(c["note"])}</p>'
        out.append(f'<div class="ff-risk" style="--c:{col};--t:{txt}"><h3>{e(c["label"])}</h3><div class="ff-badge">{sym} {e(state_text[c["state"]])}</div>{body}</div>')
    out.append("</div>")
    return "".join(out)

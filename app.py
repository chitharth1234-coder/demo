import time

import streamlit as st

st.set_page_config(
    page_title="BOB AI Rescue",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------------------------------
# Flow definition — the whole app is one linear sequence of stages.
# --------------------------------------------------------------------------
STAGES = [
    ("Command center", "Baseline health"),
    ("Detection", "Incident opened"),
    ("Investigation", "Agents sweep evidence"),
    ("Root cause", "Failure chain"),
    ("Rescue plan", "Proposed remediation"),
    ("Simulation", "What-if and approval"),
    ("Recovery", "Deploy and verify"),
]
LAST = len(STAGES) - 1

DEFAULTS = {
    "stage": 0,
    "investigated": False,
    "simulated": False,
    "approved": False,
    "deployed": False,
    "note": "",
}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def go(delta):
    st.session_state.stage = max(0, min(LAST, st.session_state.stage + delta))
    st.session_state.note = ""
    st.rerun()


def restart():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
    st.rerun()


# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap');

:root {
    --ink:      #0a0d12;
    --panel:    #12161e;
    --panel-2:  #161c26;
    --line:     #262d3a;
    --line-2:   #333c4c;
    --text:     #edf0f4;
    --muted:    #8991a0;
    --accent:   #e2a23f;
    --accent-2: #7d97b3;
    --good:     #5cbf8e;
    --bad:      #e25b52;
    --warn:     #d9b04a;
}

header[data-testid="stHeader"],
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
footer { display: none !important; }

.stApp {
    background:
        linear-gradient(180deg, #0d1119 0%, var(--ink) 340px),
        repeating-linear-gradient(180deg, rgba(255,255,255,.012) 0px, rgba(255,255,255,.012) 1px, transparent 1px, transparent 34px),
        var(--ink);
    color: var(--text);
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
}

.block-container {
    max-width: 1080px;
    padding: 2.4rem 1.4rem 4rem;
}

h1, h2, h3, h4 { font-family: 'Fraunces', Georgia, serif; font-weight: 600; letter-spacing: -0.01em; }

/* ---------- masthead ---------- */
.masthead {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 22px;
    padding-bottom: 18px;
    border-bottom: 1px solid var(--line);
}
.masthead .glyph { flex-shrink: 0; }
.masthead .id { display: flex; flex-direction: column; gap: 1px; }
.masthead .mark {
    font-family: 'Fraunces', Georgia, serif;
    font-weight: 600;
    font-size: 22px;
    line-height: 1.15;
    color: var(--text);
}
.masthead .tag { color: var(--muted); font-size: 13px; }

/* ---------- status strip ---------- */
.strip {
    position: relative;
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 22px;
    border-radius: 10px;
    border: 1px solid var(--line);
    background: var(--panel);
    margin-bottom: 28px;
}
.strip::before {
    content: '';
    position: absolute; left: 0; top: 12px; bottom: 12px; width: 3px;
    background: var(--good); border-radius: 0 2px 2px 0;
}
.strip.alert::before { background: var(--bad); }
.strip .dot {
    width: 9px; height: 9px; border-radius: 50%;
    background: var(--good);
    box-shadow: 0 0 0 4px rgba(92, 191, 142, .16);
}
.strip.alert .dot {
    background: var(--bad);
    box-shadow: 0 0 0 4px rgba(226, 91, 82, .18);
    animation: pulse 1.7s ease-in-out infinite;
}
@keyframes pulse {
    50% { box-shadow: 0 0 0 10px rgba(226, 91, 82, 0); }
}
.strip .headline { font-family: 'Fraunces', Georgia, serif; font-weight: 600; font-size: 17px; }
.strip .sub {
    color: var(--muted); font-size: 12.5px; margin-left: auto;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.01em;
}

/* ---------- progress rail ---------- */
.rail { display: flex; margin-bottom: 38px; }
.rail .node {
    flex: 1; min-width: 0; position: relative;
    display: flex; flex-direction: column; align-items: center;
    padding-top: 8px;
}
.rail .track {
    position: absolute; top: 15px; left: -50%; width: 100%; height: 2px;
    background: var(--line); z-index: 0;
}
.rail .node:first-child .track { display: none; }
.rail .node.done .track, .rail .node.now .track { background: var(--accent-2); }
.rail .circle {
    width: 16px; height: 16px; border-radius: 50%;
    border: 2px solid var(--line-2); background: var(--ink);
    display: flex; align-items: center; justify-content: center;
    position: relative; z-index: 1;
}
.rail .circle svg { width: 8px; height: 8px; }
.rail .node.now .circle {
    border-color: var(--accent); background: var(--accent);
    box-shadow: 0 0 0 4px rgba(226, 162, 63, .2);
}
.rail .node.done .circle { border-color: var(--accent-2); background: var(--accent-2); }
.rail .label { margin-top: 9px; text-align: center; line-height: 1.4; }
.rail .idx {
    display: block; font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; color: #4c5361;
}
.rail .t {
    font-size: 11.5px; color: #5b6373; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis;
}
.rail .node.done .t, .rail .node.done .idx { color: #838da0; }
.rail .node.now .t { color: var(--text); font-weight: 600; }
.rail .node.now .idx { color: var(--accent); }

/* ---------- stage heading ---------- */
.stage-h { margin-bottom: 6px; font-size: 28px; }
.stage-p { color: var(--muted); font-size: 15px; max-width: 66ch; margin-bottom: 26px; line-height: 1.55; }

/* ---------- readouts ---------- */
.grid { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 10px; }
.read {
    flex: 1 1 180px;
    border: 1px solid var(--line);
    border-radius: 9px;
    padding: 16px 18px;
    background: linear-gradient(165deg, #151b25, var(--panel));
    box-shadow: 0 1px 0 rgba(255,255,255,.02) inset, 0 6px 14px -10px rgba(0,0,0,.6);
}
.read .k {
    color: var(--muted); font-size: 11.5px; margin-bottom: 9px;
    text-transform: uppercase; letter-spacing: 0.05em;
}
.read .v {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px; font-weight: 500; color: var(--text);
}
.read .d { font-size: 12px; color: var(--muted); margin-top: 6px; }
.v.bad { color: var(--bad); }
.v.good { color: var(--good); }
.v.warn { color: var(--warn); }
.v.info { color: var(--accent-2); }

/* ---------- rows ---------- */
.row {
    display: flex; align-items: center; gap: 13px;
    border: 1px solid var(--line);
    border-left: 3px solid var(--line-2);
    border-radius: 9px;
    padding: 13px 16px;
    background: linear-gradient(165deg, #141a23, var(--panel));
    box-shadow: 0 6px 14px -12px rgba(0,0,0,.6);
    margin-bottom: 8px;
}
.row.ok { border-left-color: var(--good); }
.row.hot { border-left-color: var(--bad); }
.row .ic { flex-shrink: 0; width: 18px; height: 18px; color: var(--muted); }
.row.ok .ic { color: var(--good); }
.row.hot .ic { color: var(--bad); }
.row .name { font-weight: 600; font-size: 14.5px; }
.row .desc { color: var(--muted); font-size: 13px; margin-top: 1px; }
.row .state {
    margin-left: auto; font-size: 12px; color: var(--good); white-space: nowrap;
    font-family: 'IBM Plex Mono', monospace;
}
.row .state.idle { color: #565f6e; }
.row .state.bad { color: var(--bad); }
.row .state.warn { color: var(--warn); }

/* ---------- failure chain ---------- */
.chain { border-left: 2px solid var(--line-2); margin-left: 9px; padding-left: 22px; }
.chain .link { position: relative; padding: 11px 0; }
.chain .link::before {
    content: ''; position: absolute; left: -29px; top: 17px;
    width: 11px; height: 11px; border-radius: 50%;
    background: var(--ink); border: 2px solid var(--line-2);
}
.chain .link:last-child::before { border-color: var(--bad); background: var(--bad); }
.chain .link .lt { font-size: 15px; font-weight: 500; }
.chain .link .ld { color: var(--muted); font-size: 13px; margin-top: 2px; }

/* ---------- verdict panel ---------- */
.verdict {
    position: relative;
    border: 1px solid var(--line-2);
    border-radius: 10px;
    padding: 24px 26px;
    background: linear-gradient(155deg, #1a212d, var(--panel-2));
    box-shadow: 0 14px 30px -18px rgba(0,0,0,.7);
    margin-bottom: 22px;
}
.verdict::before, .verdict::after {
    content: ''; position: absolute; width: 14px; height: 14px;
    border: 1.5px solid var(--accent); opacity: .8;
}
.verdict::before { top: -1px; left: -1px; border-right: none; border-bottom: none; }
.verdict::after { bottom: -1px; right: -1px; border-left: none; border-top: none; }
.verdict .lead {
    color: var(--accent); font-size: 12px; margin-bottom: 10px;
    font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.02em;
}
.verdict h3 { margin: 0 0 10px; font-size: 21px; }
.verdict p { color: #c1c7d1; font-size: 14.5px; margin: 0; max-width: 70ch; line-height: 1.65; }

/* ---------- plan list ---------- */
.plan { counter-reset: s; }
.plan .item {
    display: flex; gap: 16px; align-items: flex-start;
    padding: 13px 0; border-bottom: 1px solid var(--line);
}
.plan .item:last-child { border-bottom: none; }
.plan .item .num {
    font-family: 'IBM Plex Mono', monospace; font-size: 12px;
    color: var(--accent); padding-top: 3px; min-width: 22px;
}
.plan .item .body .h { font-size: 15px; font-weight: 500; }
.plan .item .body .s { color: var(--muted); font-size: 13px; margin-top: 2px; }

/* ---------- diagrams ---------- */
.diagram {
    border: 1px solid var(--line-2);
    border-radius: 12px;
    padding: 20px 22px 8px;
    background: linear-gradient(165deg, #151b25, var(--panel));
    box-shadow: 0 14px 30px -18px rgba(0,0,0,.6);
    margin-bottom: 22px;
}
.diagram-label {
    color: var(--accent); font-size: 12px; margin-bottom: 6px;
    font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.02em;
}
.diagram svg { display: block; overflow: visible; }
.edge-hot { stroke-dasharray: 7 5; animation: dash 0.9s linear infinite; }
@keyframes dash { to { stroke-dashoffset: -24; } }
.pulse-ring {
    animation: ringpulse 1.7s ease-out infinite;
    transform-box: fill-box; transform-origin: center;
}
@keyframes ringpulse {
    0% { opacity: .55; transform: scale(1); }
    100% { opacity: 0; transform: scale(2.6); }
}

/* ---------- hero (command center only) ---------- */
.stage-h.hero { font-size: 40px; margin-bottom: 10px; }
.stage-p.hero { font-size: 16px; margin-bottom: 30px; }

/* ---------- buttons ---------- */
.stButton > button {
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 600;
    font-size: 14.5px;
    border-radius: 7px;
    padding: 11px 20px;
    border: 1px solid var(--line-2);
    background: var(--panel-2);
    color: var(--text);
    transition: background .15s ease, border-color .15s ease;
}
.stButton > button:hover {
    background: #1c2330; border-color: #445069; color: var(--text);
}
.stButton > button[kind="primary"] {
    background: var(--accent); border-color: var(--accent); color: #221403;
}
.stButton > button[kind="primary"]:hover {
    background: #edb35e; border-color: #edb35e; color: #221403;
}
.stButton > button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.stButton > button:disabled { opacity: .4; }

hr { border-color: var(--line); }
.foot {
    color: #565f6e; font-size: 12px; text-align: center; padding-top: 36px;
    font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.02em;
}

@media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; }
}
@media (max-width: 760px) {
    .rail .t { display: none; }
    .strip .sub { display: none; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Shared chrome
# --------------------------------------------------------------------------
stage = st.session_state.stage
incident_live = 1 <= stage <= 5 and not st.session_state.deployed

ICON_PATHS = {
    "check": '<path d="M3 8.5l3 3 7-7" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>',
    "alert": '<path d="M8 1.6L15 14H1L8 1.6z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/><path d="M8 6v3.4M8 11.6v.1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
    "dot": '<circle cx="8" cy="8" r="3" stroke="currentColor" stroke-width="1.4"/>',
    "code": '<path d="M5.5 4L1.5 8l4 4M10.5 4l4 4-4 4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>',
    "log": '<path d="M2 3.5h12M2 8h12M2 12.5h8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>',
    "pulse": '<path d="M1 8.5h3l1.5-5 3 9 1.5-4H15" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>',
    "nodes": '<circle cx="3" cy="4" r="1.8" stroke="currentColor" stroke-width="1.3"/><circle cx="13" cy="4" r="1.8" stroke="currentColor" stroke-width="1.3"/><circle cx="8" cy="12.5" r="1.8" stroke="currentColor" stroke-width="1.3"/><path d="M4.6 5l2.6 6M11.4 5l-2.6 6" stroke="currentColor" stroke-width="1.2"/>',
    "shield": '<path d="M8 1.5l5.5 2V8c0 4-2.4 5.8-5.5 6.5C4.9 13.8 2.5 12 2.5 8V3.5l5.5-2z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>',
    "test": '<rect x="2" y="2" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.3"/><path d="M5 8.2l2 2 4-4.4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>',
    "bolt": '<path d="M8.5 1.5L3 9h4l-1 5.5L13 7H9l-0.5-5.5z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>',
}
ICONS = {k: f'<svg viewBox="0 0 16 16" fill="none">{v}</svg>' for k, v in ICON_PATHS.items()}

CHECK_TICK = '<svg viewBox="0 0 16 16" fill="none"><path d="M3 8.3l3 3 7-7" stroke="#221403" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# palette mirrors the CSS custom properties, for use inside generated SVG
C_INK, C_PANEL, C_LINE, C_LINE2 = "#0a0d12", "#12161e", "#262d3a", "#333c4c"
C_TEXT, C_MUTED = "#edf0f4", "#8991a0"
C_ACCENT, C_ACCENT2 = "#e2a23f", "#7d97b3"
C_GOOD, C_BAD, C_WARN = "#5cbf8e", "#e25b52", "#d9b04a"

GLYPH = (
    '<svg class="glyph" width="30" height="30" viewBox="0 0 30 30" fill="none">'
    '<circle cx="15" cy="15" r="13" stroke="#333c4c" stroke-width="1.4"/>'
    '<path d="M4 15h5l2.4 6.5L15 7l3 12 2-4h6" stroke="#e2a23f" stroke-width="1.6" '
    'stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
    '</svg>'
)


def diagram(label, inner_svg, viewbox, height=220):
    return (
        f'<div class="diagram"><div class="diagram-label">{label}</div>'
        f'<svg viewBox="{viewbox}" style="width:100%;height:{height}px" '
        f'preserveAspectRatio="xMidYMid meet">{inner_svg}</svg></div>'
    )


def _node_box(cx, cy, label, sub, tone, w=118, h=48):
    stroke = {"neutral": C_LINE2, "hot": C_BAD, "good": C_GOOD}[tone]
    dot = {"neutral": C_GOOD, "hot": C_BAD, "good": C_GOOD}[tone]
    ring = f'<circle class="pulse-ring" cx="{cx - w/2 + 12}" cy="{cy - h/2 + 12}" r="4" fill="{dot}"/>' if tone == "hot" else ""
    return (
        f'<g>'
        f'<rect x="{cx - w/2}" y="{cy - h/2}" width="{w}" height="{h}" rx="9" '
        f'fill="{C_PANEL}" stroke="{stroke}" stroke-width="1.5"/>'
        f'<circle cx="{cx - w/2 + 12}" cy="{cy - h/2 + 12}" r="3.4" fill="{dot}"/>{ring}'
        f'<text x="{cx}" y="{cy - 2}" text-anchor="middle" fill="{C_TEXT}" '
        f'font-family="IBM Plex Sans" font-size="12.5" font-weight="600">{label}</text>'
        f'<text x="{cx}" y="{cy + 14}" text-anchor="middle" fill="{C_MUTED}" '
        f'font-family="IBM Plex Mono" font-size="10">{sub}</text>'
        f'</g>'
    )


def _edge(x1, y1, x2, y2, hot=False):
    cls = 'class="edge-hot"' if hot else ""
    color = C_BAD if hot else C_LINE2
    return f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{color}" stroke-width="1.6" {cls} fill="none"/>'


def svg_topology(mode):
    """mode: 'healthy' | 'incident' | 'recovered'"""
    hot = mode == "incident"
    api_tone = "hot" if hot else "good"
    db_tone = "hot" if hot else "good"
    ord_tone = "hot" if hot else "good"
    edges = (
        _edge(98, 100, 250, 100) +
        _edge(308, 100, 410, 100, hot=hot) +
        _edge(468, 100, 560, 66, hot=hot) +
        _edge(468, 100, 560, 140, hot=hot)
    )
    nodes = (
        _node_box(58, 100, "Client", "browser", "neutral", w=76) +
        _node_box(220, 100, "API Gateway", "edge", "neutral") +
        _node_box(410, 100, "Payment API", "payments-svc", api_tone) +
        _node_box(596, 66, "Database", "conn pool", db_tone, w=104) +
        _node_box(596, 140, "Order Service", "checkout", ord_tone)
    )
    return diagram("System map", edges + nodes, "0 0 656 200", height=190)


def svg_constellation(done):
    import math
    cx, cy, r = 260, 172, 118
    agents = [
        ("Code", "code"), ("Log", "log"), ("Telemetry", "pulse"),
        ("Dependency", "nodes"), ("Security", "shield"), ("Test", "test"),
    ]
    spoke_color = C_GOOD if done else C_LINE2
    spoke_cls = "" if done else 'class="edge-hot"'
    node_stroke = C_GOOD if done else C_LINE2
    icon_color = C_GOOD if done else C_MUTED
    spokes, nodes = "", ""
    for i, (name, icon) in enumerate(agents):
        ang = math.radians(-90 + i * 60)
        x, y = cx + r * math.cos(ang), cy + r * math.sin(ang)
        spokes += f'<path d="M{cx} {cy} L{x:.1f} {y:.1f}" stroke="{spoke_color}" stroke-width="1.4" {spoke_cls} fill="none"/>'
        nodes += (
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="27" fill="{C_PANEL}" stroke="{node_stroke}" stroke-width="1.6"/>'
            f'<svg x="{x-9:.1f}" y="{y-9:.1f}" width="18" height="18" viewBox="0 0 16 16" fill="none" '
            f'color="{icon_color}">{ICON_PATHS[icon]}</svg>'
            f'<text x="{x:.1f}" y="{y+42:.1f}" text-anchor="middle" fill="{C_MUTED if not done else C_TEXT}" '
            f'font-family="IBM Plex Sans" font-size="11" font-weight="500">{name}</text>'
        )
    hub_stroke = C_ACCENT if not done else C_GOOD
    hub_ring = (
        f'<circle class="pulse-ring" cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{C_ACCENT}" stroke-width="1.5"/>'
        if not done else ""
    )
    hub_check = f'<path d="M3 8.3l3 3 7-7" stroke="{C_INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    hub = (
        f'<circle cx="{cx}" cy="{cy}" r="34" fill="{C_ACCENT if not done else C_GOOD}" '
        f'stroke="{hub_stroke}" stroke-width="1.6"/>{hub_ring}'
        + (f'<svg x="{cx-9}" y="{cy-9}" width="18" height="18" viewBox="0 0 16 16">{hub_check}</svg>'
           if done else
           f'<text x="{cx}" y="{cy+5}" text-anchor="middle" fill="{C_INK}" font-family="IBM Plex Mono" '
           f'font-size="12" font-weight="700">BOB</text>')
    )
    return diagram("Agent network", spokes + nodes + hub, "0 0 520 340", height=260)


def svg_capacity():
    rows = [
        ("Configured after deploy", 100, 380, C_BAD, "100 total"),
        ("Peak checkout demand", 340, 380, C_ACCENT2, "340 concurrent"),
    ]
    bars = ""
    y = 30
    for label, value, scale, color, tag in rows:
        pct = value / scale * 100
        bars += (
            f'<text x="0" y="{y}" fill="{C_MUTED}" font-family="IBM Plex Sans" font-size="12.5">{label}</text>'
            f'<rect x="0" y="{y+10}" width="600" height="16" rx="8" fill="{C_LINE}"/>'
            f'<rect x="0" y="{y+10}" width="{pct*6:.0f}" height="16" rx="8" fill="{color}"/>'
            f'<text x="{pct*6+12:.0f}" y="{y+22}" fill="{C_TEXT}" font-family="IBM Plex Mono" font-size="12">{tag}</text>'
        )
        y += 58
    return diagram("Capacity vs demand", bars, "0 0 640 120", height=130)


def svg_recovery():
    pts = "20,134 90,132 140,30 230,28 340,26 420,24 480,70 540,118 600,136 620,134"
    area = f"20,150 {pts} 620,150"
    return diagram(
        "Recovery timeline",
        f'<defs><linearGradient id="rg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{C_ACCENT2}" stop-opacity=".35"/>'
        f'<stop offset="100%" stop-color="{C_ACCENT2}" stop-opacity="0"/></linearGradient></defs>'
        f'<polygon points="{area}" fill="url(#rg)"/>'
        f'<polyline points="{pts}" fill="none" stroke="{C_ACCENT2}" stroke-width="2"/>'
        f'<circle cx="140" cy="30" r="5" fill="{C_BAD}"/>'
        f'<text x="140" y="16" text-anchor="middle" fill="{C_BAD}" font-family="IBM Plex Mono" font-size="11">Detected</text>'
        f'<circle cx="620" cy="134" r="5" fill="{C_GOOD}"/>'
        f'<text x="620" y="152" text-anchor="end" fill="{C_GOOD}" font-family="IBM Plex Mono" font-size="11">Recovered · 6m12s</text>',
        "0 0 640 160", height=160,
    )

st.markdown(
    f'<div class="masthead">{GLYPH}'
    '<div class="id"><span class="mark">BOB Rescue</span>'
    '<span class="tag">Incident command, from detection to verified recovery</span></div></div>',
    unsafe_allow_html=True,
)

if stage == 0:
    strip_class, headline, sub = "", "All systems nominal", "Payments · Orders · Identity · Ledger"
elif st.session_state.deployed:
    strip_class, headline, sub = "", "Incident resolved", "Payment API restored · verified by BOB"
else:
    strip_class = "alert"
    headline = "Payment API degraded"
    sub = "INC-4471 · opened 00:02 ago · severity 1"

st.markdown(
    f'<div class="strip {strip_class}"><span class="dot"></span>'
    f'<span class="headline">{headline}</span><span class="sub">{sub}</span></div>',
    unsafe_allow_html=True,
)

rail = ['<div class="rail">']
for i, (name, _) in enumerate(STAGES):
    cls = "done" if i < stage else ("now" if i == stage else "")
    mark = CHECK_TICK.replace("#221403", "#0a0d12") if cls == "done" else ""
    rail.append(
        f'<div class="node {cls}"><div class="track"></div>'
        f'<div class="circle">{mark}</div>'
        f'<div class="label"><span class="idx">{i + 1:02d}</span>'
        f'<span class="t">{name}</span></div></div>'
    )
rail.append("</div>")
st.markdown("".join(rail), unsafe_allow_html=True)


def heading(title, blurb, hero=False):
    cls = " hero" if hero else ""
    st.markdown(f'<div class="stage-h{cls}">{title}</div><div class="stage-p{cls}">{blurb}</div>',
                unsafe_allow_html=True)


def readouts(items):
    cards = "".join(
        f'<div class="read"><div class="k">{k}</div>'
        f'<div class="v {tone}">{v}</div><div class="d">{d}</div></div>'
        for k, v, tone, d in items
    )
    st.markdown(f'<div class="grid">{cards}</div>', unsafe_allow_html=True)


def row(name, desc, state="", cls="", icon="dot", state_cls=""):
    return (
        f'<div class="row {cls}"><span class="ic">{ICONS[icon]}</span>'
        f'<div><div class="name">{name}</div><div class="desc">{desc}</div></div>'
        f'<div class="state {state_cls}">{state}</div></div>'
    )


# --------------------------------------------------------------------------
# Stages
# --------------------------------------------------------------------------
next_label, next_ready, next_action = "Continue", True, None

# 00 — Command center -------------------------------------------------------
if stage == 0:
    heading("Everything is quiet", "This is the steady state BOB watches around the clock. Continue "
                                   "to trigger a production incident and walk the rescue end to end.",
            hero=True)
    st.markdown(svg_topology("healthy"), unsafe_allow_html=True)
    readouts([
        ("Error rate", "0.4%", "good", "within 1% budget"),
        ("API latency p95", "210 ms", "info", "target 400 ms"),
        ("Database pool", "31 / 100", "good", "healthy headroom"),
        ("Open incidents", "0", "good", "last closed 9 days ago"),
    ])
    next_label = "Trigger production incident"

# 01 — Detection ------------------------------------------------------------
elif stage == 1:
    heading("BOB opened an incident", "Error rate crossed the payments budget within 40 seconds of a "
                                      "configuration deploy. BOB paged itself and captured a snapshot "
                                      "before anything was touched.")
    st.markdown(svg_topology("incident"), unsafe_allow_html=True)
    readouts([
        ("Error rate", "38%", "bad", "was 0.4% two minutes ago"),
        ("API latency p95", "4.8 s", "bad", "12× baseline"),
        ("Database pool", "100 / 100", "warn", "saturated, 214 waiting"),
        ("Failed payments", "1,204", "bad", "and climbing"),
    ])
    st.markdown(
        row("Payment API returning 503", "Upstream checkout and order services now timing out",
            "firing", cls="hot", icon="alert", state_cls="bad") +
        row("Deploy 8f2c1a landed 00:40 before first error", "Config-only change to payments-svc, no code diff",
            "suspect", cls="hot", icon="bolt", state_cls="warn"),
        unsafe_allow_html=True,
    )
    next_label = "Send in the agents"

# 02 — Investigation --------------------------------------------------------
elif stage == 2:
    heading("Six agents, one sweep", "Each agent owns a slice of the evidence and reports into a shared "
                                     "graph, so findings are cross-checked instead of guessed.")
    st.markdown(svg_constellation(st.session_state.investigated), unsafe_allow_html=True)
    agents = [
        ("Code", "Diffs the last deploy against the running config", "14 changes read", "code"),
        ("Log", "Clusters error signatures and orders the failure", "2.1M lines scanned", "log"),
        ("Telemetry", "Correlates latency, saturation and traffic", "340 series correlated", "pulse"),
        ("Dependency", "Maps blast radius across services", "9 services mapped", "nodes"),
        ("Security", "Rules out credential and access causes", "no anomalies", "shield"),
        ("Test", "Assembles the validation set for any fix", "5 suites selected", "test"),
    ]
    done = st.session_state.investigated
    rows = "".join(
        row(f"{n} agent", d, result if done else "standing by",
            cls="ok" if done else "", icon=ic, state_cls="idle" if not done else "")
        for n, d, result, ic in agents
    )
    st.markdown(rows, unsafe_allow_html=True)

    if done:
        st.markdown("")
        readouts([
            ("Evidence nodes", "1,847", "info", "linked in the graph"),
            ("Contradictions", "0", "good", "agents agree"),
            ("Sweep time", "38 s", "info", "vs 45 min manual median"),
        ])
        next_label = "See the root cause"
    else:
        next_label = "Run the sweep"

        def run_sweep():
            bar = st.progress(0)
            note = st.empty()
            phases = [
                (30, "Collecting evidence from logs, traces and the deploy record…"),
                (70, "Correlating findings across agents…"),
                (101, "Building the root-cause graph…"),
            ]
            done_to = 0
            for limit, text in phases:
                note.caption(text)
                for i in range(done_to, limit):
                    bar.progress(min(i + 1, 100))
                    time.sleep(0.012)
                done_to = limit
            st.session_state.investigated = True

        next_action = run_sweep

# 03 — Root cause -----------------------------------------------------------
elif stage == 3:
    heading("Root cause", "One change explains every symptom the agents found.")
    st.markdown(
        '<div class="verdict"><div class="lead">94% confidence · corroborated by 5 of 6 agents</div>'
        '<h3>The connection pool ceiling was cut, not raised</h3>'
        '<p>Deploy 8f2c1a set <code>db.pool.max</code> to 10 per instance instead of 100. '
        'With ten instances behind the load balancer the service could hold 100 connections '
        'total, which normal checkout traffic exhausts in under a minute. Every request after '
        'that waited on a free connection until it timed out.</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown(svg_capacity(), unsafe_allow_html=True)
    chain = [
        ("Config deploy 8f2c1a", "db.pool.max lowered from 100 to 10 per instance"),
        ("Pool ceiling drops 10×", "Effective capacity falls to 100 connections fleet-wide"),
        ("Connections exhausted", "214 requests queue for a free handle"),
        ("Requests time out at 5 s", "Gateway returns 503 to checkout"),
        ("Payments fail", "1,204 transactions rejected downstream"),
    ]
    links = "".join(
        f'<div class="link"><div class="lt">{t}</div><div class="ld">{d}</div></div>'
        for t, d in chain
    )
    st.markdown(f'<div class="chain">{links}</div>', unsafe_allow_html=True)
    st.markdown("")
    readouts([
        ("Confidence", "94%", "info", "evidence-weighted"),
        ("Blast radius", "3 services", "warn", "payments, checkout, orders"),
        ("Customer impact", "High", "bad", "1,204 failed payments"),
        ("Fix complexity", "Low", "good", "single config value"),
    ])
    next_label = "Build the rescue plan"

# 04 — Rescue plan ----------------------------------------------------------
elif stage == 4:
    heading("Proposed rescue", "Six steps, ordered so nothing reaches production before it has been "
                               "tested and signed off.")
    plan = [
        ("Restore db.pool.max to 100", "Reverts the single value changed by 8f2c1a"),
        ("Roll payments-svc instance by instance", "Keeps capacity online through the restart"),
        ("Run unit and integration suites", "5 suites selected by the test agent"),
        ("Verify pool and API health", "Watch saturation and p95 for 5 minutes"),
        ("Hold for human approval", "Nothing deploys without a sign-off"),
        ("Watch for regression", "Auto-rollback armed for 30 minutes"),
    ]
    items = "".join(
        f'<div class="item"><div class="num">{i:02d}</div>'
        f'<div class="body"><div class="h">{h}</div><div class="s">{s}</div></div></div>'
        for i, (h, s) in enumerate(plan, 1)
    )
    st.markdown(f'<div class="plan">{items}</div>', unsafe_allow_html=True)
    st.markdown("")
    readouts([
        ("Estimated recovery", "4 min", "info", "from approval"),
        ("Steps needing approval", "1", "warn", "the deploy itself"),
        ("Rollback", "Armed", "good", "one command, 40 s"),
    ])
    next_label = "Simulate this plan"

# 05 — Simulation and approval ---------------------------------------------
elif stage == 5:
    heading("Simulate, then decide", "BOB replays the plan against a shadow copy of production. "
                                     "You see the predicted outcome before anything real changes.")

    if not st.session_state.simulated:
        st.markdown(
            row("Shadow environment ready", "Mirrors live traffic shape from the last 15 minutes",
                "not yet run", icon="pulse", state_cls="idle"),
            unsafe_allow_html=True,
        )
        next_label = "Run the simulation"

        def simulate():
            with st.spinner("Replaying the plan against shadow traffic…"):
                time.sleep(1.6)
            st.session_state.simulated = True

        next_action = simulate
    else:
        readouts([
            ("Safety score", "92 / 100", "good", "threshold is 80"),
            ("Tests", "5 / 5", "good", "no failures"),
            ("Regression risk", "Low", "good", "no new error signatures"),
            ("Predicted p95", "190 ms", "info", "from 4.8 s"),
        ])
        st.markdown("")
        st.markdown(
            '<div class="verdict"><div class="lead">Decision required</div>'
            '<h3>BOB recommends deploying the rescue</h3>'
            '<p>The simulation cleared every threshold. Production changes stay under human '
            'control, so the deploy waits here until you approve it.</p></div>',
            unsafe_allow_html=True,
        )

        if st.session_state.approved:
            st.markdown(
                row("Approved for production", "Signed off by the on-call reviewer",
                    "ready to deploy", cls="ok", icon="check"),
                unsafe_allow_html=True,
            )
            next_label = "Deploy the rescue"
        else:
            a, b, _ = st.columns([1, 1, 2])
            if a.button("Approve rescue", type="primary", use_container_width=True):
                st.session_state.approved = True
                st.rerun()
            if b.button("Reject", use_container_width=True):
                st.session_state.note = "reject"
            if st.session_state.note == "reject":
                st.markdown(
                    row("Rescue rejected",
                        "Nothing was changed in production. The incident stays open and "
                        "BOB keeps monitoring.",
                        "no action taken", cls="hot", icon="alert", state_cls="bad"),
                    unsafe_allow_html=True,
                )
            next_label = "Deploy the rescue"
            next_ready = False

# 06 — Recovery -------------------------------------------------------------
elif stage == 6:
    if not st.session_state.deployed:
        heading("Deploying", "Instances roll one at a time so payments stay available throughout.")
        bar = st.progress(0)
        note = st.empty()
        steps = [
            (25, "Restoring db.pool.max to 100…"),
            (60, "Rolling payments-svc, 1 of 10…"),
            (85, "Running validation suites…"),
            (101, "Verifying pool and API health…"),
        ]
        done_to = 0
        for limit, text in steps:
            note.caption(text)
            for i in range(done_to, limit):
                bar.progress(min(i + 1, 100))
                time.sleep(0.018)
            done_to = limit
        st.session_state.deployed = True
        st.rerun()

    heading("Recovered and verified", "BOB watched every signal back to baseline before closing "
                                      "the incident.")
    st.markdown(svg_topology("recovered"), unsafe_allow_html=True)
    st.markdown(svg_recovery(), unsafe_allow_html=True)
    readouts([
        ("Error rate", "0.3%", "good", "down from 38%"),
        ("API latency p95", "180 ms", "good", "down from 4.8 s"),
        ("Database pool", "42 / 100", "good", "no queue"),
        ("Time to recovery", "6 min 12 s", "info", "detection to verified"),
    ])
    st.markdown("")
    for name, detail in [
        ("Payment API", "503s cleared, throughput back to baseline"),
        ("Database", "Pool steady at 42 of 100, no waiters"),
        ("Order service", "Downstream queue drained"),
        ("Failed payments", "1,204 queued for automatic retry"),
        ("Regression watch", "Auto-rollback armed for 30 minutes"),
    ]:
        st.markdown(
            row(name, detail, "verified", cls="ok", icon="check"),
            unsafe_allow_html=True,
        )

# --------------------------------------------------------------------------
# Footer navigation — one way forward
# --------------------------------------------------------------------------
st.markdown("<hr>", unsafe_allow_html=True)
left, right = st.columns([1, 1])

with left:
    if stage > 0:
        if st.button("Back", use_container_width=False):
            go(-1)

with right:
    slot = st.container()
    with slot:
        if stage == LAST:
            spacer, btn = st.columns([2, 1])
            with btn:
                if st.button("Start over", type="primary", use_container_width=True):
                    restart()
        else:
            spacer, btn = st.columns([1, 2])
            with btn:
                if st.button(next_label, type="primary", use_container_width=True,
                             disabled=not next_ready):
                    if next_action:
                        next_action()
                        st.rerun()
                    else:
                        go(1)
            if not next_ready:
                st.caption("Approve or reject the rescue to continue.")

st.markdown(
    '<div class="foot">BOB AI Rescue · detect, diagnose, rescue, recover</div>',
    unsafe_allow_html=True,
)

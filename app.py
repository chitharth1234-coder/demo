import time

import streamlit as st

st.set_page_config(
    page_title="BOB AI Rescue",
    page_icon="🚨",
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
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap');

:root {
    --ink:      #060f1a;
    --panel:    #0c1a2b;
    --panel-2:  #0f2136;
    --line:     #1b3450;
    --text:     #e6f0fb;
    --muted:    #8ba4bf;
    --cyan:     #56d6ff;
    --coral:    #ff6b7d;
    --mint:     #4fe0a4;
    --amber:    #ffc45c;
}

header[data-testid="stHeader"],
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
footer { display: none !important; }

.stApp {
    background:
        radial-gradient(1100px 520px at 12% -8%, #12304e 0%, transparent 62%),
        radial-gradient(900px 480px at 92% 0%, #0d2a44 0%, transparent 58%),
        var(--ink);
    color: var(--text);
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
}

.block-container {
    max-width: 1120px;
    padding: 2.2rem 1.4rem 4rem;
}

h1, h2, h3, h4 { font-family: 'Space Grotesk', system-ui, sans-serif; letter-spacing: -0.015em; }

/* ---------- masthead ---------- */
.masthead {
    display: flex;
    align-items: baseline;
    gap: 14px;
    margin-bottom: 20px;
}
.masthead .mark {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 26px;
    color: var(--text);
}
.masthead .tag { color: var(--muted); font-size: 14px; }

/* ---------- status strip ---------- */
.strip {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 20px;
    border-radius: 14px;
    border: 1px solid var(--line);
    background: linear-gradient(100deg, var(--panel), var(--panel-2));
    margin-bottom: 26px;
}
.strip .dot {
    width: 11px; height: 11px; border-radius: 50%;
    background: var(--mint);
    box-shadow: 0 0 0 5px rgba(79, 224, 164, .14);
}
.strip.alert { border-color: rgba(255, 107, 125, .5); }
.strip.alert .dot {
    background: var(--coral);
    box-shadow: 0 0 0 5px rgba(255, 107, 125, .18);
    animation: pulse 1.6s ease-in-out infinite;
}
@keyframes pulse {
    50% { box-shadow: 0 0 0 12px rgba(255, 107, 125, 0); }
}
.strip .headline { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 17px; }
.strip .sub { color: var(--muted); font-size: 14px; margin-left: auto; }

/* ---------- progress rail ---------- */
.rail { display: flex; gap: 6px; margin-bottom: 30px; }
.rail .node { flex: 1; min-width: 0; }
.rail .bar {
    height: 3px; border-radius: 2px; background: #16283d; margin-bottom: 10px;
}
.rail .node.done .bar { background: var(--mint); }
.rail .node.now  .bar { background: var(--cyan); }
.rail .n {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; color: #4d6885; margin-right: 6px;
}
.rail .t {
    font-size: 12.5px; color: #59748f; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis;
}
.rail .node.done .t, .rail .node.done .n { color: #7fa0bd; }
.rail .node.now .t { color: var(--text); font-weight: 600; }
.rail .node.now .n { color: var(--cyan); }

/* ---------- stage heading ---------- */
.stage-h { margin-bottom: 4px; font-size: 30px; font-weight: 700; }
.stage-p { color: var(--muted); font-size: 15px; max-width: 68ch; margin-bottom: 24px; }

/* ---------- readouts ---------- */
.grid { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }
.read {
    flex: 1 1 180px;
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 15px 17px;
    background: var(--panel);
}
.read .k { color: var(--muted); font-size: 12.5px; margin-bottom: 7px; }
.read .v {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 23px; font-weight: 500; color: var(--text);
}
.read .d { font-size: 12px; color: var(--muted); margin-top: 5px; }
.v.bad { color: var(--coral); }
.v.good { color: var(--mint); }
.v.warn { color: var(--amber); }
.v.info { color: var(--cyan); }

/* ---------- rows ---------- */
.row {
    display: flex; align-items: center; gap: 12px;
    border: 1px solid var(--line);
    border-left: 3px solid #23415f;
    border-radius: 10px;
    padding: 13px 16px;
    background: var(--panel);
    margin-bottom: 8px;
}
.row.ok { border-left-color: var(--mint); }
.row.hot { border-left-color: var(--coral); }
.row .name { font-weight: 600; font-size: 14.5px; }
.row .desc { color: var(--muted); font-size: 13px; }
.row .state { margin-left: auto; font-size: 13px; color: var(--mint); white-space: nowrap; }
.row .state.idle { color: #5d7894; }

/* ---------- failure chain ---------- */
.chain { border-left: 2px solid #23415f; margin-left: 9px; padding-left: 22px; }
.chain .link { position: relative; padding: 11px 0; }
.chain .link::before {
    content: ''; position: absolute; left: -29px; top: 17px;
    width: 12px; height: 12px; border-radius: 50%;
    background: var(--ink); border: 2px solid #3a6083;
}
.chain .link:last-child::before { border-color: var(--coral); background: var(--coral); }
.chain .link .lt { font-size: 15px; font-weight: 500; }
.chain .link .ld { color: var(--muted); font-size: 13px; margin-top: 2px; }

/* ---------- verdict panel ---------- */
.verdict {
    border: 1px solid rgba(86, 214, 255, .35);
    border-radius: 14px;
    padding: 22px 24px;
    background: linear-gradient(130deg, #0e2237, #10283f);
    margin-bottom: 20px;
}
.verdict .lead { color: var(--cyan); font-size: 13px; margin-bottom: 8px; }
.verdict h3 { margin: 0 0 8px; font-size: 22px; }
.verdict p { color: #b9cde2; font-size: 14.5px; margin: 0; max-width: 72ch; line-height: 1.6; }

/* ---------- plan list ---------- */
.plan { counter-reset: s; }
.plan .item {
    display: flex; gap: 14px; align-items: flex-start;
    padding: 12px 0; border-bottom: 1px solid #142638;
}
.plan .item:last-child { border-bottom: none; }
.plan .item .num {
    font-family: 'IBM Plex Mono', monospace; font-size: 12px;
    color: var(--cyan); padding-top: 3px; min-width: 22px;
}
.plan .item .body .h { font-size: 15px; font-weight: 500; }
.plan .item .body .s { color: var(--muted); font-size: 13px; margin-top: 2px; }

/* ---------- buttons ---------- */
.stButton > button {
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 600;
    font-size: 14.5px;
    border-radius: 10px;
    padding: 11px 20px;
    border: 1px solid #27466a;
    background: #10233a;
    color: var(--text);
    transition: background .15s ease, border-color .15s ease, transform .15s ease;
}
.stButton > button:hover {
    background: #16304c; border-color: #34618d; color: var(--text);
}
.stButton > button[kind="primary"] {
    background: var(--cyan); border-color: var(--cyan); color: #04121d;
}
.stButton > button[kind="primary"]:hover {
    background: #79e1ff; border-color: #79e1ff; color: #04121d;
}
.stButton > button:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }
.stButton > button:disabled { opacity: .4; }

hr { border-color: #142638; }
.foot { color: #4f6a86; font-size: 12.5px; text-align: center; padding-top: 34px; }

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

st.markdown(
    '<div class="masthead"><span class="mark">BOB AI Rescue</span>'
    '<span class="tag">Software incident command, from detection to verified recovery</span></div>',
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
    rail.append(
        f'<div class="node {cls}"><div class="bar"></div>'
        f'<span class="n">{i + 1:02d}</span><span class="t">{name}</span></div>'
    )
rail.append("</div>")
st.markdown("".join(rail), unsafe_allow_html=True)


def heading(title, blurb):
    st.markdown(f'<div class="stage-h">{title}</div><div class="stage-p">{blurb}</div>',
                unsafe_allow_html=True)


def readouts(items):
    cards = "".join(
        f'<div class="read"><div class="k">{k}</div>'
        f'<div class="v {tone}">{v}</div><div class="d">{d}</div></div>'
        for k, v, tone, d in items
    )
    st.markdown(f'<div class="grid">{cards}</div>', unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Stages
# --------------------------------------------------------------------------
next_label, next_ready, next_action = "Continue", True, None

# 00 — Command center -------------------------------------------------------
if stage == 0:
    heading("Everything is quiet", "This is the steady state BOB watches. Continue to trigger a "
                                   "production incident and walk the rescue end to end.")
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
    readouts([
        ("Error rate", "38%", "bad", "was 0.4% two minutes ago"),
        ("API latency p95", "4.8 s", "bad", "12× baseline"),
        ("Database pool", "100 / 100", "warn", "saturated, 214 waiting"),
        ("Failed payments", "1,204", "bad", "and climbing"),
    ])
    st.markdown(
        '<div class="row hot"><div><div class="name">Payment API returning 503</div>'
        '<div class="desc">Upstream checkout and order services now timing out</div></div>'
        '<div class="state" style="color:var(--coral)">firing</div></div>'
        '<div class="row hot"><div><div class="name">Deploy 8f2c1a landed 00:40 before first error</div>'
        '<div class="desc">Config-only change to payments-svc, no code diff</div></div>'
        '<div class="state" style="color:var(--amber)">suspect</div></div>',
        unsafe_allow_html=True,
    )
    next_label = "Send in the agents"

# 02 — Investigation --------------------------------------------------------
elif stage == 2:
    heading("Six agents, one sweep", "Each agent owns a slice of the evidence and reports into a shared "
                                     "graph, so findings are cross-checked instead of guessed.")
    agents = [
        ("Code", "Diffs the last deploy against the running config", "14 changes read"),
        ("Log", "Clusters error signatures and orders the failure", "2.1M lines scanned"),
        ("Telemetry", "Correlates latency, saturation and traffic", "340 series correlated"),
        ("Dependency", "Maps blast radius across services", "9 services mapped"),
        ("Security", "Rules out credential and access causes", "no anomalies"),
        ("Test", "Assembles the validation set for any fix", "5 suites selected"),
    ]
    done = st.session_state.investigated
    rows = "".join(
        f'<div class="row {"ok" if done else ""}"><div><div class="name">{n} agent</div>'
        f'<div class="desc">{d}</div></div>'
        f'<div class="state {"" if done else "idle"}">{result if done else "standing by"}</div></div>'
        for n, d, result in agents
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
            '<div class="row"><div><div class="name">Shadow environment ready</div>'
            '<div class="desc">Mirrors live traffic shape from the last 15 minutes</div></div>'
            '<div class="state idle">not yet run</div></div>',
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
                '<div class="row ok"><div><div class="name">Approved for production</div>'
                '<div class="desc">Signed off by the on-call reviewer</div></div>'
                '<div class="state">ready to deploy</div></div>',
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
                    '<div class="row hot"><div><div class="name">Rescue rejected</div>'
                    '<div class="desc">Nothing was changed in production. The incident stays '
                    'open and BOB keeps monitoring.</div></div>'
                    '<div class="state" style="color:var(--coral)">no action taken</div></div>',
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
            f'<div class="row ok"><div><div class="name">{name}</div>'
            f'<div class="desc">{detail}</div></div><div class="state">verified</div></div>',
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

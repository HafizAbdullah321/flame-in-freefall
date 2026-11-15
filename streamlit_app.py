"""Flame in Freefall: dashboard (steps 4-5: prediction card + charts).
Run from the repo root:  streamlit run app/streamlit_app.py"""
import os, sys
from pathlib import Path
import numpy as np, pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend")); sys.path.insert(0, str(ROOT))
from ffbackend.predict import Predictor            # noqa: E402
from ffbackend.config import DISCLAIMER             # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from components.flame3d import flame3d              # noqa: E402
from ui import theme                                 # noqa: E402
from insights.findings import load_findings, rank_findings, EVIDENCE_LABEL   # noqa: E402
from insights.scenarios import SCENARIOS, Scenario, evaluate                  # noqa: E402
from insights.brief import build_brief                                         # noqa: E402
from insights.catalog import load_catalog, filter_catalog, compare as compare_entries, evidence_matrix, gravity_class as cat_gravity, TYPES as CAT_TYPES, STATUSES as CAT_STATUSES, GEOMETRY_KEYWORDS, FUEL_CATEGORIES, SENSOR_CATEGORIES, _rng   # noqa: E402
from insights.si_brief import build_inputs as brief_inputs, generate_brief   # noqa: E402
from insights.risk_cards import build_cards, STATES as RISK_STATES   # noqa: E402
from insights.coverage_map import coverage_figure, coverage_table, atmosphere_status, ppo2_gap, STATUS_TEXT   # noqa: E402
from insights.synthesis import synthesize_topic, get_available_topics   # noqa: E402
from insights.nl_scenario import parse_scenario_nl   # noqa: E402
from rag.summaries import load_summaries, filter_summaries   # noqa: E402
from insights.terrestrial import get_terrestrial_spinoffs, filter_spinoffs, get_spinoff_comparison_dataframe   # noqa: E402
from insights.report_export import build_markdown_report, build_html_report   # noqa: E402
from insights.historic_incidents import get_historic_incidents, get_incident_comparison_table   # noqa: E402
from insights.persona import PERSONAS, calculate_combustion_physics, get_safety_officer_verdict, get_student_fundamentals   # noqa: E402
from domain.models import CatalogFilterCriteria                                  # noqa: E402
from services.simulation_service import SimulationService                       # noqa: E402
from services.mission_service import MissionService                             # noqa: E402
from services.catalog_service import CatalogService                             # noqa: E402
from services.document_service import DocumentService                           # noqa: E402
from services.audit_service import AuditService                                 # noqa: E402
from services.security_service import SecurityService                           # noqa: E402
from services.fault_tolerance_service import CircuitBreaker, CircuitBreakerOpenException  # noqa: E402

MODEL = Path(os.environ.get("FF_MODEL", ROOT / "backend/artifacts/ff_model.joblib"))
EXPERIMENTS = Path(os.environ.get("FF_EXPERIMENTS", ROOT / "phase0/raw/zarm_experiments_global.csv"))
FUEL, G0 = "PMMA", 0.0
CREDIT = ("Experimental data: ZARM drop-tower flame spread study, Zenodo record 18479713 (GPL-3.0-or-later). "
          "Reports: data provided by NASA Scientific and Technical Information Program "
          "(https://ntrs.nasa.gov/api/openapi/).")
PALETTE = dict(model="#26c6da", band="rgba(38,198,218,0.20)", user="#ce93d8", none="#ffffff", Aluminium="#ffa726", **{"Stainless Steel": "#9aa4b8"})
SYMBOL = {"none": "circle", "Aluminium": "diamond", "Stainless Steel": "triangle-up"}

RAG_DIR = Path(os.environ.get("FF_RAG_DIR", ROOT / "rag"))

st.set_page_config(page_title="Flame in Freefall", page_icon="🔥", layout="wide")

MIN_STREAMLIT = (1, 40)

def keyed_container(key):
    """st.container(key=...) needs Streamlit 1.39+; older versions get a plain container (no card styling) instead of an error."""
    try: return st.container(key=key)
    except TypeError: return st.container()

def show_plot(fig, key=None):
    try: st.plotly_chart(fig, width="stretch", key=key)
    except TypeError: st.plotly_chart(fig, use_container_width=True, key=key)

@st.cache_resource
def load_predictor():
    return Predictor.load(MODEL)

@st.cache_data
def load_experiments():
    d = pd.read_csv(EXPERIMENTS)
    d["o2_pct"] = d["o2_frac"] * 100
    return d

@st.cache_data(show_spinner=False)
def predict_cached(o2_r, f_r):
    return load_predictor().predict_on_line(FUEL, G0, o2_r, f_r)

@st.cache_data(show_spinner=False)
def curve(f_r, lo, hi):
    P = load_predictor(); xs = np.round(np.arange(lo, hi + 1e-9, 0.25), 2)
    rows = [(o, *(lambda r: (r["rate"], r["lo"], r["hi"]))(P.predict_on_line(FUEL, G0, o, f_r))) for o in xs]
    return pd.DataFrame(rows, columns=["o2", "rate", "lo", "hi"]).dropna()

@st.cache_resource
def get_llm():
    """OpenAI client if a key is configured (secrets or environment), else None. Every AI feature falls back without it."""
    key = None
    try: key = st.secrets["OPENAI_API_KEY"]
    except Exception: key = os.environ.get("OPENAI_API_KEY")
    if not key: return None
    from rag.llm import OpenAILLM, LLMError
    from rag.config import AssistantConfig
    try: return OpenAILLM(AssistantConfig(), api_key=key)
    except LLMError: return None

@st.cache_resource
def load_assistant():
    """Returns (assistant, None) or (None, reason). Works without an API key (cache / extractive answers only)."""
    idx, tau = RAG_DIR / "index", RAG_DIR / "tau.json"
    if not (idx / "faiss.index").exists():
        return None, "The assistant is not set up yet: build the document index first (`python scripts/setup_all.py`, then `make rag-index`)."
    if not tau.exists():
        return None, "The refusal threshold is not calibrated yet: run `make rag-calibrate` (see rag/questions.csv)."
    from rag.retrieve import Retriever
    from rag.answer import Assistant, Cache
    from rag.limits import DailyCap
    from rag.llm import OpenAILLM, LLMError
    from rag.config import AssistantConfig
    cfg = AssistantConfig()
    try:
        R = Retriever(idx); R.load_tau(tau)
    except Exception as e:
        return None, f"The assistant index needs rebuilding ({type(e).__name__}): re-run the index and calibration steps."
    llm = get_llm()
    cache = Cache(RAG_DIR / "cache.json", R.embedder, R.meta["corpus_signature"])
    return Assistant(R, llm, cache, cfg, daily=DailyCap(RAG_DIR / "daily_cap.json", cfg.daily_llm_cap),
                     log_path=RAG_DIR / "assistant_log.jsonl"), None

TIER_BADGE = {"LLM": "✔ AI answer grounded in NASA documents", "CACHE": "◷ Cached answer", "EXTRACTIVE": "≡ Passages only (no AI summary)",
              "REFUSED": "✖ Not answered", "RATE_LIMITED": "⏳ Slow down", "INVALID": "⚠ Check your question"}

def render_answer(m):
    st.markdown(m["answer"])
    st.caption(f"{TIER_BADGE.get(m['tier'], m['tier'])}" + (f": {m['label']}" if m.get("label") and m["tier"] in ("CACHE", "REFUSED", "EXTRACTIVE") else ""))
    for src in m.get("sources", []):
        au = ", ".join(a for a in (src.get("authors") or []) if a)
        st.markdown(f"[{src['n']}] [{src['title']}]({src['url']})" + (f", {au}" if au else ""))

def assistant_tab():
    A, why = load_assistant()
    if A is None:
        st.info(why); return
    from rag.limits import TokenBucket
    from rag.config import AssistantConfig
    if "limiter" not in st.session_state: st.session_state.limiter = TokenBucket(AssistantConfig().rate_per_minute)
    st.session_state.setdefault("chat", [])
    st.caption("Answers come only from NASA documents in this repository, with links to the sources. Questions outside them are declined." +
               ("" if A.llm else " AI summaries are off (no API key): you will see cached answers or the closest passages."))

    with st.expander("💡 Quick Question Starters (Click to Ask)", expanded=False):
        c_q1, c_q2 = st.columns(2)
        q_sel = None
        if c_q1.button("🔬 BASS findings on PMMA & fabrics", key="chip_q1"):
            q_sel = "What did the BASS experiments discover about solid polymers and fabrics in microgravity?"
        if c_q2.button("🌙 Lunar atmospheric ignition limits", key="chip_q2"):
            q_sel = "How does reduced pressure and increased oxygen affect material ignition in lunar exploration?"
        c_q3, c_q4 = st.columns(2)
        if c_q3.button("🚨 Mir 1997 oxygen candle fire", key="chip_q3"):
            q_sel = "What caused the 1997 Mir space station fire and what lessons were learned?"
        if c_q4.button("💧 Fine water mist spacecraft suppression", key="chip_q4"):
            q_sel = "Why is fine water mist effective for fire extinguishment in spacecraft cabins?"
        if q_sel:
            st.session_state["queued_chat_query"] = q_sel
            st.rerun()

    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            render_answer(m) if m["role"] == "assistant" else st.markdown(m["answer"])

    queued_prompt = st.session_state.pop("queued_chat_query", None)
    q = st.chat_input("Ask about microgravity combustion and spacecraft fire safety", max_chars=500)
    user_query = queued_prompt or q
    if user_query:
        clean_q = SecurityService.sanitize_text(user_query)
        is_safe, reason = SecurityService.detect_prompt_injection(clean_q)
        if not is_safe:
            st.session_state.chat.append(dict(role="user", answer=clean_q))
            with st.chat_message("user"): st.markdown(clean_q)
            res = dict(tier="REFUSED", answer=f"🛡 **Security Guardrail Active**: {reason}", sources=[], label="Security Filter")
            with st.chat_message("assistant"): render_answer(res)
            st.session_state.chat.append(dict(role="assistant", **res))
        else:
            st.session_state.chat.append(dict(role="user", answer=clean_q))
            with st.chat_message("user"): st.markdown(clean_q)
            with st.chat_message("assistant"), st.spinner("Searching the NASA documents..."):
                res = A.ask(clean_q, st.session_state.limiter); render_answer(res)
            st.session_state.chat.append(dict(role="assistant", **res))

# ---------------------------------------------------------------------------
# Performance & Data Memoization Layer (Optimized for Sub-100ms UI Latency)
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def findings_table():
    """Cached NASA verified findings table."""
    return load_findings()

@st.cache_data(show_spinner=False)
def catalog_rows():
    """Cached PSI experiment catalog entries via CatalogService."""
    return CatalogService.get_all_entries()

@st.cache_data(show_spinner=False)
def get_cached_summaries():
    """Cached executive summaries from harvested NASA STI publications via DocumentService."""
    return DocumentService.get_summaries()

@st.cache_data(show_spinner=False)
def get_cached_incidents():
    """Cached historic spaceflight fire emergency records via DocumentService."""
    return DocumentService.get_flight_incidents()

@st.cache_data(show_spinner=False)
def get_cached_spinoffs():
    """Cached terrestrial technology spin-off records via DocumentService."""
    return DocumentService.get_earth_spinoffs()

@st.cache_data(show_spinner=False)
def get_cached_spinoff_df():
    """Cached terrestrial technology comparison dataframe via DocumentService."""
    return DocumentService.get_spinoff_comparison_table()

@st.cache_data(show_spinner=False)
def get_cached_topic_synthesis(topic_choice):
    """Cached synthesis results per topic via DocumentService."""
    return DocumentService.get_topic_synthesis(topic_choice)

@st.cache_data(show_spinner=False)
def get_cached_evidence_matrix():
    """Cached evidence distribution matrix via CatalogService."""
    return CatalogService.get_evidence_matrix_dataframe(catalog_rows()).rename(index=GRAV_LABEL)

@st.cache_data(show_spinner=False)
def get_all_scenarios_dataframe():
    """Cached overview table of all standard exploration scenarios."""
    P = load_predictor()
    exp = load_experiments()
    findings = findings_table()
    rows = []
    for k, s in SCENARIOS.items():
        e = evaluate(s, P, exp)
        top = rank_findings(findings, s.g, s.o2_pct, s.pressure_kpa, s.tags)[0]
        rows.append(dict(Scenario=s.name, Gravity=f"{s.g:g} g", Pressure_kPa=s.pressure_kpa, Oxygen_pct=s.o2_pct, O2_partial_kPa=round(e["ppo2"], 1),
                         Support=VERDICT_STYLE[e["verdict"]][1], Predicted_mm_s=(round(e["prediction"]["rate"], 2) if e["prediction"] else None),
                         Most_relevant_finding=top["id"] + ": " + top["finding"][:90] + "...", _o=SUPPORT_ORDER[e["verdict"]]))
    return pd.DataFrame(rows).sort_values("_o").drop(columns="_o")

@st.cache_data(show_spinner=False)
def build_base_scatter_fig(f_r, lo, hi):
    """Pre-compute the complex multi-trace scatter plot base for 60fps slider dragging."""
    fig = go.Figure()
    cv = curve(f_r, lo, hi)
    fig.add_trace(go.Scatter(x=cv.o2, y=cv.hi, mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=cv.o2, y=cv.lo, mode="lines", line=dict(width=0), fill="tonexty",
                             fillcolor=PALETTE["band"], name="90% interval"))
    fig.add_trace(go.Scatter(x=cv.o2, y=cv.rate, mode="lines", name=f"Model (f*={f_r:.2f})",
                             line=dict(color=PALETTE["model"], width=3)))
    exp = load_experiments()
    for mat, d in exp.groupby("gap_material"):
        lab = "Continuous PMMA (f*=1)" if mat == "none" else f"{mat} barriers"
        fig.add_trace(go.Scatter(x=d.o2_pct, y=d.v_mm_s, mode="markers", name=lab,
                                 error_y=dict(type="data", array=d.v_sd_mm_s, visible=True),
                                 marker=dict(symbol=SYMBOL[mat], size=10, color=PALETTE[mat], line=dict(width=1, color=theme.CARD)),
                                 customdata=np.c_[d.exp, d.f_star], hovertemplate="%{customdata[0]}<br>O2 %{x:.1f}%<br>rate %{y:.2f} mm/s<br>f* %{customdata[1]:.2f}<extra></extra>"))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Roboto, Helvetica Neue, Arial, sans-serif", color="#dfe4ee", size=13),
                      xaxis=dict(title="Oxygen (%)", gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.12)"),
                      yaxis=dict(title="Flame spread rate (mm/s)", gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.12)"),
                      height=440, legend=dict(orientation="h", y=-0.25), margin=dict(t=10))
    return fig

@st.cache_data(show_spinner=False)
def cached_coverage_figure(selected_key, is_custom=False, custom_p=56.5, custom_o2=34.0):
    """Cached multi-trace coverage map avoiding expensive Plotly trace assembly on reruns."""
    exp = load_experiments()
    cat = catalog_rows()
    if is_custom:
        sc = Scenario("custom", "Custom environment", custom_p, custom_o2, 0.0, ("exploration-atmosphere",) if custom_o2 > 25 else (), "Environment set by you.")
        scen_all = {**SCENARIOS, "custom": sc}
        return coverage_figure(exp, scen_all, selected=sc.key, catalog=cat)
    return coverage_figure(exp, SCENARIOS, selected=selected_key, catalog=cat)

@st.cache_data(show_spinner=False)
def cached_coverage_table(selected_key, is_custom=False, custom_p=56.5, custom_o2=34.0):
    """Cached coverage table matching the evidence map."""
    exp = load_experiments()
    cat = catalog_rows()
    if is_custom:
        sc = Scenario("custom", "Custom environment", custom_p, custom_o2, 0.0, ("exploration-atmosphere",) if custom_o2 > 25 else (), "Environment set by you.")
        scen_all = {**SCENARIOS, "custom": sc}
        return coverage_table(exp, scen_all, catalog=cat)
    return coverage_table(exp, SCENARIOS, catalog=cat)

VERDICT_STYLE = {"COVERED": ("green", "Covered by our experiments"), "NEAR": ("orange", "Just outside our experiments"), "NOT_COVERED": ("red", "Not covered by our experiments")}
SUPPORT_ORDER = {"COVERED": 0, "NEAR": 1, "NOT_COVERED": 2}

def mission_tab(P, exp, persona="all"):
    st.caption("How do NASA's published findings and our microgravity experiments apply to the environments planned for human exploration? "
               "Pick a scenario: the dashboard checks what our data can and cannot say, ranks the most relevant NASA findings, and writes a sourced brief.")

    with st.expander("Describe scenario in natural language (e.g. 'lunar habitat at 8 psi and 30% oxygen')", expanded=False):
        nl_text = st.text_input("Describe environment", "", placeholder="e.g. lunar habitat at 8 psi and 30% oxygen, or Mars base at 56.5 kPa with 34% O2", key="nl_query")
        if st.button("Parse and validate scenario", key="btn_parse_nl"):
            clean_nl = SecurityService.sanitize_text(nl_text)
            is_safe, reason = SecurityService.detect_prompt_injection(clean_nl)
            if not is_safe:
                st.session_state["nl_active_scenario"] = None
                st.session_state["nl_active_result"] = {"ok": False, "errors": [reason]}
            else:
                res = parse_scenario_nl(clean_nl, llm=get_llm())
                if res["ok"]:
                    st.session_state["nl_active_scenario"] = res["scenario"]
                    st.session_state["nl_active_result"] = res
                else:
                    st.session_state["nl_active_scenario"] = None
                    st.session_state["nl_active_result"] = res

        if "nl_active_result" in st.session_state and st.session_state["nl_active_result"]:
            res = st.session_state["nl_active_result"]
            if res["ok"]:
                st.success(f"✔ **Parsed scenario ({res.get('method', 'REGEX')})**: {res['scenario'].name}")
                p1, p2, p3 = st.columns(3)
                p1.write(f"**Pressure**: {res['pressure_kpa']:.1f} kPa ({res.get('input_pressure')} {res.get('input_unit', 'kPa')})")
                p2.write(f"**Oxygen**: {res['o2_pct']:.1f}%")
                p3.write(f"**Gravity**: {res['gravity_name']}")
                if st.button("Activate this parsed scenario", key="btn_apply_nl"):
                    st.session_state["scenario_choice"] = "custom_nl"
                    st.rerun()
            else:
                if res.get("clarification_needed"):
                    st.warning(f"⚠ Clarification needed: {res['clarification_needed']}")
                for err in res.get("errors", []):
                    st.error(f"✖ {err}")

    names = {k: v.name for k, v in SCENARIOS.items()}
    scenario_options = list(names) + ["custom"] + (["custom_nl"] if st.session_state.get("nl_active_scenario") else [])
    def_sc_idx = 0
    if "scenario" in st.query_params and st.query_params["scenario"] in scenario_options:
        def_sc_idx = scenario_options.index(st.query_params["scenario"])
    choice = st.selectbox(
        "Mission scenario",
        scenario_options,
        index=def_sc_idx,
        format_func=lambda k: names.get(k, "Parsed: " + st.session_state["nl_active_scenario"].name if k == "custom_nl" and st.session_state.get("nl_active_scenario") else "Custom environment"),
        key="scenario_choice"
    )
    try:
        st.query_params["scenario"] = choice
    except Exception:
        pass
    if choice == "custom_nl" and st.session_state.get("nl_active_scenario"):
        sc = st.session_state["nl_active_scenario"]
    elif choice == "custom":
        c1, c2, c3 = st.columns(3)
        pk = c1.slider("Total pressure (kPa)", 40.0, 110.0, 56.5, 0.5, key="cus_p")
        ox = c2.slider("Oxygen (%)", 15.0, 40.0, 34.0, 0.5, key="cus_o")
        gg = c3.selectbox("Gravity", [0.0, 0.16, 0.38, 1.0], format_func=lambda g: {0.0: "0 g (microgravity)", 0.16: "0.16 g (Moon)", 0.38: "0.38 g (Mars)", 1.0: "1 g (Earth)"}[g], key="cus_g")
        sc = Scenario("custom", "Custom environment", pk, ox, gg, ("exploration-atmosphere",) if ox > 25 else (), "Environment set by you.")
    else:
        sc = SCENARIOS[choice]
    ev = evaluate(sc, P, exp); ranked = rank_findings(findings_table(), sc.g, sc.o2_pct, sc.pressure_kpa, sc.tags)
    gname = {0.0: "0 g", 0.16: "0.16 g", 0.38: "0.38 g", 1.0: "1 g"}.get(sc.g, f"{sc.g:g} g")
    a, b, c, d = st.columns(4)
    a.markdown(theme.stat_card("Total pressure", f"{sc.pressure_kpa:.1f}", "kPa", "orange", "pressure"), unsafe_allow_html=True)
    b.markdown(theme.stat_card("Oxygen", f"{sc.o2_pct:.1f}", "%", "teal", "flow"), unsafe_allow_html=True)
    c.markdown(theme.stat_card("O2 partial pressure", f"{ev['ppo2']:.1f}", "kPa", "green", "layers"), unsafe_allow_html=True)
    d.markdown(theme.stat_card("Gravity", gname, "", "purple", "status"), unsafe_allow_html=True)

    if persona in ("safety", "all"):
        v_safety = get_safety_officer_verdict(ev, sc.name)
        if persona == "safety":
            alert_fn = st.success if v_safety["badge_color"] == "green" else st.warning if v_safety["badge_color"] == "orange" else st.error
            alert_fn(f"🛡 **{v_safety['status_banner']}**  \n{v_safety['action']} (ppO₂: {v_safety['ppo2_kpa']:.1f} kPa, Δ from Earth: {v_safety['normoxic_delta']:+.1f} kPa)")

    color, title = VERDICT_STYLE[ev["verdict"]]
    with keyed_container("card_m_cover"):
        st.markdown(theme.card_head(title, "What our 22 microgravity experiments can say about this environment", color), unsafe_allow_html=True)
        if ev["verdict"] == "COVERED":
            p = ev["prediction"]; st.metric("Predicted flame spread rate (thin PMMA)", f"{p['rate']:.2f} mm/s",
                                             help="Flame front propagation velocity (mm/s), not physical flame dimension."); st.write(f"90% interval: **{p['lo']:.2f} to {p['hi']:.2f} mm/s**")
        else:
            st.markdown("No prediction is made for this environment." if ev["verdict"] != "NEAR" else "No prediction is made: the environment is just outside the tested range.")
            for r in ev["reasons"]: st.markdown(f"- {r}")
            cm = ev["comparator"]
            if cm: st.caption(f"For orientation only: at {cm['o2_pct']:.1f}% oxygen the nearest tested atmosphere ({cm['pressure_kpa']:.0f} kPa, microgravity) spread at about {cm['rate']:.1f} mm/s ({cm['lo']:.1f} to {cm['hi']:.1f}). Not a prediction for this scenario.")
    with keyed_container("card_m_map"):
        st.markdown(theme.card_head("Evidence map", "Green band: conditions our experiments cover. Stars: planned environments. Dotted lines: constant oxygen partial pressure", "teal"), unsafe_allow_html=True)
        stt = atmosphere_status(sc.pressure_kpa, sc.o2_pct, exp); gap = ppo2_gap(sc.pressure_kpa, sc.o2_pct, exp)
        st.markdown(f"**Selected atmosphere ({sc.pressure_kpa:.1f} kPa, {sc.o2_pct:.1f}% oxygen): {STATUS_TEXT[stt].lower()}.**" +
                    (f" Its oxygen partial pressure is {gap:.1f} kPa outside the tested range." if gap > 0 else ""))
        show_plot(cached_coverage_figure(sc.key, is_custom=(choice == "custom"), custom_p=sc.pressure_kpa, custom_o2=sc.o2_pct), key="cov_map_plot")
        with st.expander("Map data as a table (text alternative to the chart)"):
            st.dataframe(cached_coverage_table(sc.key, is_custom=(choice == "custom"), custom_p=sc.pressure_kpa, custom_o2=sc.o2_pct), hide_index=True)
        st.caption("Coverage is judged on pressure and oxygen only; gravity is handled separately: all of our experiments are microgravity. Dashed boxes mark other experiments from the catalog: ground (1g) tests and planned platforms, which are not microgravity tests in this range.")
    with keyed_container("card_m_risk"):
        st.markdown(theme.card_head("Risk cards by topic", "What the evidence says for this environment, topic by topic. A card with no evidence is a data gap, not a sign of safety", "red"), unsafe_allow_html=True)
        st.markdown(theme.risk_cards_html(build_cards(ev, ranked), RISK_STATES), unsafe_allow_html=True)
        st.caption("Only the spread card can show numbers, and only when the environment is covered by our experiments. Everything else is cited findings; items marked 'not yet verified' have not been checked against their sources.")
    with keyed_container("card_m_find"):
        st.markdown(theme.card_head("NASA findings, ranked", "Most relevant first: scored on gravity, atmosphere and topic match, weighted by strength of evidence", "purple"), unsafe_allow_html=True)
        for i, f in enumerate(ranked[:6], 1):
            st.markdown(f"**{i}. {f['finding']}**  \n{EVIDENCE_LABEL[f['evidence']]} · [{f['source_title']}]({f['source_url']}) · score {f['score']:.2f} (relevance {f['relevance']:.2f}, evidence {f['evidence_weight']:.2f})")
        with st.expander("How the ranking works"):
            st.markdown("Score = 0.7 × relevance + 0.3 × evidence strength. Relevance = 0.45 gravity match + 0.30 atmosphere match + 0.25 topic match. "
                        "Evidence strength: partial-gravity experiment 1.0, microgravity experiment 0.9, ground test 0.8, review 0.6, planning or context 0.4. "
                        "Findings are short paraphrases of the cited sources; verify wording against the source.")
    with keyed_container("card_m_brief"):
        st.markdown(theme.card_head("Insight brief", "Every statement traces to our model, our tested ranges, or a cited finding", "teal"), unsafe_allow_html=True)
        rule_brief = build_brief(ev, ranked); inputs = brief_inputs(ev, ranked, build_cards(ev, ranked)); shown = rule_brief
        import hashlib, json as _json
        sig = "ai_brief_" + hashlib.sha256(_json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:16]
        llm = get_llm()
        if llm is None:
            st.caption("AI-written briefs are off (no API key configured). The rule-based brief below is always available and fully sourced.")
        else:
            from rag.limits import TokenBucket, DailyCap
            from rag.config import AssistantConfig
            if st.button("Write with AI (verified)", key="brief_ai", help="A language model writes the brief from the facts above; the dashboard checks citations, numbers and structure before showing it."):
                lim = st.session_state.setdefault("brief_limiter", TokenBucket(5))
                if lim.allow():
                    st.session_state[sig] = generate_brief(llm, inputs, rule_brief, DailyCap(RAG_DIR / "daily_cap.json", AssistantConfig().daily_llm_cap))
                else:
                    st.session_state[sig] = dict(tier="RULE_BASED", text=rule_brief, reasons=["Too many AI requests in a short time; please wait a moment."], cached=False)
            res = st.session_state.get(sig)
            if res:
                shown = res["text"]
                if res["tier"] == "SI": st.success("✔ AI-written brief. Citations, numbers and structure were checked against the facts.")
                else: st.warning("Showing the rule-based brief. " + " ".join(res["reasons"]))
        st.markdown(shown)
        with st.expander("What the AI is given (the facts)"):
            st.json(inputs)
        full_md = build_markdown_report(sc, ev, ranked, build_cards(ev, ranked), shown)
        with st.expander("👁 In-App Executive Report Preview (Read Before Download)", expanded=False):
            st.markdown(full_md)
        col_dl1, col_dl2, col_dl3 = st.columns(3)
        col_dl1.download_button("Download brief (.md)", shown, file_name=f"insight_brief_{sc.key}.md", mime="text/markdown", key="dl_brief_md")
        col_dl2.download_button("Download full report (.md)", full_md, file_name=f"mission_safety_report_{sc.key}.md", mime="text/markdown", key="dl_report_md")
        full_html = build_html_report(sc, ev, ranked, build_cards(ev, ranked), shown)
        col_dl3.download_button("Download printable report (.html)", full_html, file_name=f"mission_safety_report_{sc.key}.html", mime="text/html", key="dl_report_html")
    with keyed_container("card_m_all"):
        st.markdown(theme.card_head("All scenarios at a glance", "Ranked by how directly our experiments cover them", "orange"), unsafe_allow_html=True)
        st.dataframe(get_all_scenarios_dataframe(), hide_index=True)

GRAV_LABEL = {"micro": "Microgravity", "lunar": "Lunar gravity", "mars": "Mars gravity", "earth": "Earth gravity (1g)", "unknown": "Not stated"}

def experiments_tab():
    rows = catalog_rows()
    st.caption("Find and compare the experiments and facilities behind NASA's microgravity fire research. Entries marked 'No' have not been checked against their sources yet.")
    with keyed_container("card_x_filter"):
        st.markdown(theme.card_head("Find experiments", "Filter by platform, gravity, status, fuel geometry, or diagnostic instrumentation", "purple"), unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        types = c1.multiselect("Platform", CAT_TYPES, key="x_types")
        grav = c2.multiselect("Gravity", list(GRAV_LABEL), format_func=lambda g: GRAV_LABEL[g], key="x_grav")
        stat = c3.multiselect("Status", CAT_STATUSES, key="x_stat")
        
        f1, f2, f3 = st.columns(3)
        geoms = f1.multiselect("Sample Geometry", list(GEOMETRY_KEYWORDS.keys()), key="x_geom", help="Filter by geometry: flat sheets, solid cylinders/rods, droplets, or porous burners.")
        fuel_cats = f2.multiselect("Fuel Material", list(FUEL_CATEGORIES.keys()), key="x_fuel_cat", help="Filter by fuel material: polymers (PMMA), fabrics, droplets, or gases.")
        sensor_cats = f3.multiselect("Diagnostic & Sensor Type", list(SENSOR_CATEGORIES.keys()), key="x_sensor_cat", help="Filter by instrumentation: image analysis, thermocouples, radiometers, or aerosol detectors.")
        
        c4, c5 = st.columns([3, 1])
        text = c4.text_input("Keyword (name, fuel, measurement, result)", key="x_text")
        vonly = c5.checkbox("Verified only", key="x_ver")
        criteria = CatalogFilterCriteria(
            types=types or None,
            gravity=grav or None,
            status=stat or None,
            text=text,
            verified_only=vonly,
            geometry=geoms or None,
            fuel_cat=fuel_cats or None,
            sensor_cat=sensor_cats or None,
        )
        hits = CatalogService.filter_experiments(criteria, rows)
        st.markdown(f"**{len(hits)} of {len(rows)} entries**")
        if hits:
            df = pd.DataFrame([dict(
                ID=r["id"],
                Name=r["name"],
                Platform=r["type"],
                Gravity=GRAV_LABEL[cat_gravity(r)],
                Geometry=r["geometry"] or "Not specified",
                Fuels=r["fuels"] or "Not specified",
                Diagnostics=r["measurements"] or "Not specified",
                Status=r["status"],
                Verified="Yes" if r["verified"] == "yes" else "No",
                Key_result=r["key_result"],
                Source=r["source_url"]
            ) for r in hits])
            st.dataframe(df, hide_index=True, column_config={"Source": st.column_config.LinkColumn("Source", display_text="open")})
        else:
            st.info("No entries match these filters.")
    with keyed_container("card_x_inspector"):
        st.markdown(theme.card_head("Investigation & apparatus deep dive", "Detailed engineering breakdown of burner geometry, instrumentation sensors, and test variables", "blue"), unsafe_allow_html=True)
        names = {r["id"]: f"{r['id']}: {r['name']}" for r in rows}
        sel_inv_id = st.selectbox("Select investigation to inspect", list(names), format_func=lambda i: names[i], key="x_inspect_choice")
        inv = [r for r in rows if r["id"] == sel_inv_id][0]
        
        ic1, ic2 = st.columns([1, 1])
        with ic1:
            st.markdown(f"#### 🔬 {inv['name']} ({inv['id']})")
            st.write(f"**Platform / Facility**: {inv['type']} ({inv['status']})")
            st.write(f"**Gravity Acceleration**: {_rng(inv['gravity_g_min'], inv['gravity_g_max'], 'g')}")
            st.write(f"**Atmospheric Conditions**: Oxygen {_rng(inv['o2_min'], inv['o2_max'], '%')}, Pressure {_rng(inv['pressure_kpa_min'], inv['pressure_kpa_max'], ' kPa')}")
            st.write(f"**Flow Velocity**: {_rng(inv['flow_cm_s_min'], inv['flow_cm_s_max'], ' cm/s')}")
            st.markdown("**Test Duration**:")
            st.write(f"{inv['duration_s']} s" if inv['duration_s'] else "Continuous orbital / facility dependent")
        with ic2:
            st.markdown("#### 🧪 Fuels, Geometry & Instrumentation")
            st.write(f"**Fuel Material(s)**: {inv['fuels'] or 'Not reported'}")
            st.write(f"**Sample / Burner Geometry**: {inv['geometry'] or 'Not reported'}")
            st.markdown("**Diagnostic Sensors & Measurements**:")
            st.info(inv['measurements'] or "Standard flammability pass/fail screening")
            st.markdown("**Primary Scientific Finding:**")
            st.success(inv['key_result'])
            st.caption(f"Source Document: [{inv['source_url']}]({inv['source_url']}) · Verified: {inv['verified']}")
    with keyed_container("card_x_compare"):
        st.markdown(theme.card_head("Compare experiments", "Choose two to four entries for a side-by-side view", "teal"), unsafe_allow_html=True)
        names = {r["id"]: f"{r['id']}: {r['name']}" for r in rows}
        pick = st.multiselect("Entries to compare", list(names), default=["E02", "E07"], format_func=lambda i: names[i], max_selections=4, key="x_pick")
        if len(pick) >= 2:
            st.dataframe(CatalogService.compare_investigations(pick, rows))
        else:
            st.info("Select at least two entries.")
    with keyed_container("card_x_matrix"):
        st.markdown(theme.card_head("Where is the evidence?", "Entries in this catalog by gravity and status", "orange"), unsafe_allow_html=True)
        m = get_cached_evidence_matrix()
        st.dataframe(m)
        n_lunar_flown = int(m.loc["Lunar gravity"].get("flown", 0)) if "Lunar gravity" in m.index else 0
        st.markdown("In this catalog, **no experiment has flown at lunar gravity with a published spread-rate dataset**, and the planned lunar-gravity platforms are still planned." if n_lunar_flown == 0 else "")
        st.caption("Counts reflect the entries in this catalog only, not everything NASA has done.")

def documents_tab():
    with keyed_container("card_d_synthesis"):
        st.markdown(theme.card_head("Topic synthesis", "What NASA's verified findings say about key fire-safety topics. Conflicting physical trends are highlighted", "purple"), unsafe_allow_html=True)
        available_topics = get_available_topics()
        default_idx = available_topics.index("flame-spread") if "flame-spread" in available_topics else 0
        topic_choice = st.selectbox("Select fire-safety topic to synthesize", available_topics, index=default_idx, key="syn_topic_choice")

        syn = get_cached_topic_synthesis(topic_choice)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Verified findings", syn["verified_count"])
        c2.metric("Unverified candidates", syn["unverified_count"])
        status_color = "green" if syn["consensus"] == "CONSENSUS" else "orange" if syn["consensus"] == "CONFLICT" else "teal" if syn["consensus"] == "NEUTRAL" else "red"
        c3.markdown(f"**Consensus status**  \n<span style='color:{theme.GRADIENTS.get(status_color, ('#fff',))[0]}; font-weight:700; font-size:1.1rem;'>{syn['consensus']}</span>", unsafe_allow_html=True)
        grav_str = ", ".join(syn["gravity_coverage"]) if syn["gravity_coverage"] else "None"
        c4.markdown(f"**Gravity coverage**  \n<span>{grav_str}</span>", unsafe_allow_html=True)

        if syn["consensus"] == "CONFLICT" and syn["conflict_note"]:
            st.warning(f"⚠ {syn['conflict_note']}")
        
        if syn["statements"]:
            st.markdown("#### Synthesized Takeaways")
            for stmt in syn["statements"]:
                st.markdown(f"- {stmt}")
        elif syn["status"] == "GAP":
            st.info(f"ℹ {syn['headline']}")

        if syn["evidence_counts"]:
            st.markdown("#### Evidence Breakdown")
            ev_cols = st.columns(len(syn["evidence_counts"]))
            for col, (ev_type, count) in zip(ev_cols, syn["evidence_counts"].items()):
                col.markdown(f"**{EVIDENCE_LABEL.get(ev_type, ev_type)}**: {count}")

        if syn["gaps"]:
            with st.expander("Identified data gaps and research needs", expanded=(syn["status"] == "GAP")):
                for g in syn["gaps"]:
                    st.markdown(f"• {g}")

    with keyed_container("card_d_explorer"):
        st.markdown(theme.card_head("Document explorer", "Browse harvested NASA reports with grounded executive summaries (120 words or fewer)", "teal"), unsafe_allow_html=True)
        summaries = get_cached_summaries()
        
        c_search, c_filter = st.columns([2, 1])
        search_query = c_search.text_input("Search reports (title, summary, authors)", "", key="doc_search_query")
        sti_types = ["All"] + sorted(list({r.get("sti_type", "REPORT") for r in summaries.values() if r.get("sti_type")}))
        type_choice = c_filter.selectbox("Publication type", sti_types, key="doc_type_filter")

        filtered = DocumentService.search_summaries(summaries, query=search_query, sti_type=type_choice)
        st.write(f"Showing **{len(filtered)}** of **{len(summaries)}** documents")

        for doc in filtered[:15]:
            with st.expander(f"{doc.get('title', 'NASA Report')} ({doc.get('id')})"):
                st.markdown(f"**Authors**: {', '.join(doc.get('authors', [])) or 'NASA STIP'}  \n"
                            f"**STI Type**: {doc.get('sti_type', 'REPORT')} | **Summary Method**: `{doc.get('method', 'EXTRACTIVE')}` ({doc.get('word_count', 0)} words)")
                st.markdown(f"**Summary**:  \n{doc.get('summary', '')}")
                if doc.get("citation_url"):
                    st.markdown(f"[View publication on NASA NTRS]({doc.get('citation_url')})")
        if len(filtered) > 15:
            st.caption("Showing first 15 results. Refine search query to see other documents.")

    with keyed_container("card_d_terrestrial"):
        st.markdown(theme.card_head("Terrestrial spin-offs & Earth safety", "How NASA microgravity fire research protects civilian lives and property on Earth", "green"), unsafe_allow_html=True)
        st.caption("NASA's low-gravity combustion and fire safety research directly powers critical life-saving technologies on Earth: fine-water-mist extinguishers, ultra-lightweight breathing air tanks, advanced firefighter turnout gear, and particle-discriminating smoke detectors.")
        
        c_cat, c_search = st.columns([1, 2])
        cats = ["All", "Suppression", "Life Support & Crew Safety", "Materials & Protection", "Early Detection"]
        cat_choice = c_cat.selectbox("Technology domain", cats, key="spinoff_cat")
        sp_search = c_search.text_input("Search spin-offs (keyword, application, science)", "", placeholder="e.g. water mist, firefighter gear, air tanks, smoke detector", key="spinoff_query")
        
        spinoffs = DocumentService.get_earth_spinoffs(category=cat_choice, query=sp_search)
        st.write(f"Showing **{len(spinoffs)}** verified Earth applications")
        
        for sp in spinoffs:
            with st.expander(f"{sp['icon']} {sp['title']} — {sp['category']}"):
                col_sp1, col_sp2 = st.columns([1, 1])
                with col_sp1:
                    st.markdown("**🚀 Spaceflight Origin (Microgravity / NASA Need)**")
                    st.write(sp["space_origin"])
                    st.markdown("**🔬 Microgravity & PSI Science Link**")
                    st.caption(sp["psi_connection"])
                with col_sp2:
                    st.markdown("**🌍 Terrestrial Earth Application**")
                    st.write(sp["terrestrial_app"])
                    st.markdown("**🛡 Civilian Safety Benefits**")
                    for b in sp["benefits"]:
                        st.markdown(f"• {b}")
                st.caption(f"Verified source: [{sp['source_citation']}]({sp['source_url']})")
        
        with st.expander("Compare spaceflight origin vs. Earth commercial impact (Table)"):
            st.dataframe(DocumentService.get_spinoff_comparison_table(), hide_index=True)

    with keyed_container("card_d_historic"):
        st.markdown(theme.card_head("Historic spaceflight fires & NASA lessons learned", "How disasters from Apollo 1 and Mir to deep-space false alarms shaped modern microgravity combustion research", "red"), unsafe_allow_html=True)
        st.caption("Decades of real spaceflight fire emergencies directly prompted NASA's microgravity combustion experiments (PSI/ISS). Each incident identified physical failure modes that our dashboard's rules and tests evaluate.")
        
        incidents = DocumentService.get_flight_incidents()
        inc_names = {inc["id"]: f"{inc['title']} ({inc['date'].split()[-1]})" for inc in incidents}
        selected_inc_id = st.selectbox("Select historic incident to inspect", list(inc_names), format_func=lambda i: inc_names[i], key="inc_choice")
        
        selected_inc = [inc for inc in incidents if inc["id"] == selected_inc_id][0]
        
        col_i1, col_i2 = st.columns([1, 1])
        with col_i1:
            st.markdown(f"#### 🚨 Incident: {selected_inc['title']}")
            st.write(f"**Mission / Date**: {selected_inc['mission']} — {selected_inc['date']}")
            st.write(f"**Atmosphere & Gravity**: {selected_inc['environment']} ({selected_inc['gravity']})")
            st.markdown("**Root Physical Cause:**")
            st.info(selected_inc["cause"])
            st.markdown("**Consequence:**")
            st.write(selected_inc["consequence"])
        with col_i2:
            st.markdown("#### 🔬 NASA Engineering Lessons & PSI Link")
            st.markdown("**Modern Spacecraft Safety Mitigation:**")
            for line in selected_inc["engineering_lessons"].split("\n"):
                if line.strip():
                    st.markdown(f"• {line.lstrip('1234. ')}")
            st.markdown("**Direct Connection to PSI Research:**")
            st.success(selected_inc["psi_connection"])
            st.caption(f"Official Investigation Report: [{selected_inc['source_citation']}]({selected_inc['source_url']})")
            
        with st.expander("Compare all historic spacecraft incidents side-by-side (Table)"):
            st.dataframe(get_incident_comparison_table(), hide_index=True)

def main():
    try:
        ver = tuple(int(x) for x in st.__version__.split(".")[:2])
        if ver < MIN_STREAMLIT:
            st.warning(f"Streamlit {st.__version__} is old; some styling and features need {'.'.join(map(str, MIN_STREAMLIT))} or newer. Run: pip install -U streamlit")
    except ValueError:
        pass
    st.markdown(theme.css(), unsafe_allow_html=True)
    st.title("Flame in Freefall")
    st.caption("Flame spread over thin PMMA in microgravity (ZARM drop tower). Research and educational tool.")

    with st.expander("🚀 New to Flame in Freefall? 60-Second Guided Tour", expanded=False):
        c_tour1, c_tour2, c_tour3 = st.columns(3)
        with c_tour1:
            st.markdown("#### 1. 🔥 Simulation")
            st.write("Adjust oxygen concentration and opposed flow to observe how zero-buoyancy diffusion flames propagate across solid materials. Contrast 0g vs 1g physics.")
        with c_tour2:
            st.markdown("#### 2. 🛡 Mission Insights")
            st.write("Select exploration environments (Artemis Lunar Base, Mars Rover) to check whether NASA data supports safe operations or leaves uncharacterized hazards.")
        with c_tour3:
            st.markdown("#### 3. 📚 Knowledge & AI")
            st.write("Investigate historic spacecraft fire emergencies (Apollo 1, Mir), explore civilian Earth spin-offs (water mist, turnout gear), and query harvested NASA reports.")

    try:
        P = load_predictor(); exp = load_experiments()
    except Exception as e:                                       # REQ-A5: clear setup error, not a traceback
        st.error(f"Setup problem: could not load the model or data ({type(e).__name__}). Run `make train` first.")
        st.stop()

    lo, hi = P.safe_o2_range(FUEL, G0, 1.0)
    
    # URL State Sync & Deep-Linking initialization
    qp = st.query_params
    if "preset_o2" in st.session_state:
        def_o2 = float(st.session_state.pop("preset_o2"))
    else:
        try:
            def_o2 = float(qp.get("o2", 28.0))
            if not (lo <= def_o2 <= hi): def_o2 = 28.0
        except (ValueError, TypeError):
            def_o2 = 28.0

    try:
        def_f = float(qp.get("f", 1.00))
        if not (0.72 <= def_f <= 1.00): def_f = 1.00
    except (ValueError, TypeError):
        def_f = 1.00

    def_persona_idx = 0
    if "persona" in qp:
        target_p = qp.get("persona")
        for idx, (p_label, p_code) in enumerate(PERSONAS.items()):
            if target_p in (p_code, p_label):
                def_persona_idx = idx
                break

    with st.sidebar:
        st.header("Conditions")
        st.markdown(f"**Fuel:** {FUEL} thin film, 75 µm")
        gravity = st.radio("Gravity", ["0g (microgravity)", "1g (Earth)"], index=0)
        reduce_motion = st.checkbox("Reduce motion", value=False)

        st.markdown("**1-Click Atmosphere Presets:**")
        pcol1, pcol2 = st.columns(2)
        if pcol1.button("🚀 ISS (21.8%)", key="preset_iss", help="Standard space station atmosphere"):
            st.session_state["preset_o2"] = 21.8
            st.rerun()
        if pcol2.button("🌙 Lunar (34%)", key="preset_lunar", help="Planned Artemis Lunar habitat atmosphere"):
            st.session_state["preset_o2"] = 34.0
            st.rerun()
        pcol3, pcol4 = st.columns(2)
        if pcol3.button("🔴 Mars (32%)", key="preset_mars", help="Exploration rover reduced pressure atmosphere"):
            st.session_state["preset_o2"] = 32.0
            st.rerun()
        if pcol4.button("🔥 CFI-G (36%)", key="preset_cfig", help="ACME CFI-G upper tested boundary in PSI"):
            st.session_state["preset_o2"] = 36.0
            st.rerun()

        o2 = st.slider("Oxygen (%)", float(round(lo + 0.05, 1)), float(round(hi - 0.05, 1)), def_o2, 0.5,
                       help="Pressure and flow in the experiments were tied to oxygen, so only oxygen is free.")
        f = st.slider("Fuel coverage f*", 0.72, 1.00, def_f, 0.01,
                      help="Fraction of the strip that is fuel; 1.0 is a continuous strip, lower values have metal barriers.")
        st.divider()
        st.header("Audience Mode")
        persona_choice = st.radio(
            "Target focus",
            list(PERSONAS.keys()),
            index=def_persona_idx,
            key="persona_choice",
            help="Adapts dashboard emphasis: Operational Go/No-Go limits for flight safety officers, dimensionless combustion physics for researchers, or foundational visual guides for students."
        )
        persona_key = PERSONAS[persona_choice]
        
        st.divider()
        with st.expander("📋 Shareable Link & Deep-Linking"):
            st.caption("Copy this URL to share the exact mission atmosphere & persona state:")
            st.code(f"?o2={o2:.1f}&f={f:.2f}&persona={persona_key}", language="text")

        with st.expander("🛡 System Provenance & Audit (SHA-256)"):
            prov = AuditService.get_provenance_report(ROOT)
            st.markdown(f"**Integrity**: `{prov['status']}`")
            st.caption(f"**Model SHA-256**: `{prov['model_sha256'][:16]}...`")
            st.caption(f"**Raw Dataset SHA-256**: `{prov['raw_dataset_sha256'][:16]}...`")
            st.caption(f"**DOI**: [{prov['primary_doi']}](https://doi.org/{prov['primary_doi']})")
            st.caption(f"**Model Family**: {prov['model_family']}")
            st.caption(f"**Python Runtime**: {prov['runtime_environment']['python_version']}")

    # Synchronize active parameters to URL query state
    try:
        st.query_params["o2"] = f"{o2:.1f}"
        st.query_params["f"] = f"{f:.2f}"
        st.query_params["persona"] = persona_key
    except Exception:
        pass
    cond = P.conditions_for(FUEL, G0, o2)
    is_1g = gravity.startswith("1g")
    res = None if is_1g else predict_cached(round(o2 * 2) / 2, round(f, 2))
    status = "n/a" if res is None else res["status"]

    tab1, tab_m, tab_x, tab_docs, tab2 = st.tabs(["Simulation and analytics", "Mission insights", "Experiments", "Documents & Synthesis", "AI assistant"])
    with tab1:
        banner = st.empty()      # fixed slot: inserting/removing a banner would shift the layout and remount the 3D iframe
        if is_1g:
            banner.warning("No 1g measurements in this dataset. The 1g view is an illustration only and shows no prediction.")
        else:
            banner.empty()
        s1, s2, s3, s4 = st.columns(4)
        s1.markdown(theme.stat_card("Pressure", f"{cond[0]:.0f}", "kPa", "orange", "pressure"), unsafe_allow_html=True)
        s2.markdown(theme.stat_card("Opposed flow", f"{cond[1]:.0f}", "mm/s", "teal", "flow"), unsafe_allow_html=True)
        s3.markdown(theme.stat_card("Fuel coverage", f"{f:.2f}", "", "green", "layers"), unsafe_allow_html=True)
        label, color, icon = {"IN": ("In range", "green", "status"), "SPARSE": ("Sparse data", "orange", "alert"), "OUT": ("Out of range", "red", "alert"),
                              "n/a": ("No 1g data", "purple", "alert")}.get(status, ("Unknown", "red", "alert"))
        s4.markdown(theme.stat_card("Data coverage", label, "", color, icon), unsafe_allow_html=True)

        c1, c2 = st.columns([1, 2])
        with c1:
            with keyed_container("card_pred"):
                st.markdown(theme.card_head("Predicted spread rate", "Model estimate with a 90% interval", "green"), unsafe_allow_html=True)
                if res is None:
                    st.info("Prediction available for 0g only.")
                elif res["status"] == "OUT":
                    st.error(f"✖ OUT: Experimental Bounds Exceeded. {res['message']}")
                else:
                    st.metric("Flame spread rate (propagation speed)", f"{res['rate']:.2f} mm/s",
                              help="Flame front propagation velocity along the PMMA fuel surface in millimeters per second (mm/s). This is spread speed, not physical flame size.")
                    st.write(f"90% interval: **{res['lo']:.2f} to {res['hi']:.2f} mm/s**")
                    if res["status"] == "IN":
                        st.success("✔ IN: within the tested envelope.")
                    else:
                        st.warning(f"⚠ SPARSE: {res['message']} Interval widened.")
                    
                    # Visual Flammability Risk Meter
                    if o2 < 23.5:
                        meter_col = "#43a047"
                        meter_txt = "Nominal Atmosphere (Near-Earth Flammability)"
                        meter_pct = max(min(int((o2 - 21.0) / 15.0 * 100), 100), 18)
                    elif o2 <= 30.0:
                        meter_col = "#ffa726"
                        meter_txt = "Elevated Spread Hazard (Caution Zone)"
                        meter_pct = max(min(int((o2 - 21.0) / 15.0 * 100), 100), 55)
                    else:
                        meter_col = "#e53935"
                        meter_txt = "High-Risk Exploration Atmosphere (NASA-STD-6001 Limit)"
                        meter_pct = max(min(int((o2 - 21.0) / 15.0 * 100), 100), 85)
                    
                    st.markdown(f"""
                    <div style="margin: 8px 0 10px 0; background: rgba(255,255,255,0.06); padding: 8px 10px; border-radius: 6px; border-left: 4px solid {meter_col};">
                        <div style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.5px; color: #a8b2c6; font-weight: 600;">Flammability Risk Meter</div>
                        <div style="font-size: 0.88rem; font-weight: 600; color: {meter_col}; margin: 2px 0 6px 0;">{meter_txt}</div>
                        <div style="background: rgba(0,0,0,0.3); border-radius: 4px; height: 7px; overflow: hidden;">
                            <div style="background: {meter_col}; width: {meter_pct}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.caption("Estimate from 22 experiments, one apparatus. " + DISCLAIMER)
        with c2:
            with keyed_container("card_flame"):
                st.markdown(theme.card_head("3D flame", "Speed follows the predicted spread rate", "purple"), unsafe_allow_html=True)
                ok = (not is_1g) and res is not None and res["status"] != "OUT"
                flame3d(rate=res["rate"] if ok else (4.0 if is_1g else None), gravity=1 if is_1g else 0, o2=o2, flow=cond[1],
                        status="IN" if is_1g else (res["status"] if res else "OUT"), reduce_motion=reduce_motion, illustration=is_1g)

        with keyed_container("card_chart"):
            st.markdown(theme.card_head("Prediction versus experiments", "Real experiments, the model curve and its 90% interval", "orange"), unsafe_allow_html=True)
            base_fig = build_base_scatter_fig(round(f, 2), float(round(lo, 2)), float(round(hi, 2)))
            fig = go.Figure(base_fig)
            if res is not None and res["status"] != "OUT":
                fig.add_trace(go.Scatter(x=[o2], y=[res["rate"]], mode="markers", name="Your selection",
                                         marker=dict(symbol="star", size=18, color=PALETTE["user"], line=dict(width=1.5, color="#FFFFFF"))))
            show_plot(fig, key="scatter_pred_vs_exp")
            with st.expander("Chart data as a table (text alternative to the chart)"):
                st.dataframe(exp[["exp", "o2_pct", "f_star", "gap_material", "v_mm_s", "v_sd_mm_s"]].rename(columns={"exp": "Experiment", "o2_pct": "Oxygen (%)", "f_star": "Fuel coverage", "gap_material": "Barrier", "v_mm_s": "Spread rate (mm/s)", "v_sd_mm_s": "Std (mm/s)"}), hide_index=True)
                if res is not None and res["status"] != "OUT":
                    st.write(f"Your selection: oxygen {o2:.1f} %, fuel coverage {f:.2f}, predicted {res['rate']:.2f} mm/s (90% interval {res['lo']:.2f} to {res['hi']:.2f}).")
            st.caption("Markers use different shapes per barrier material (not only color). Curve shows the model at the selected fuel coverage; real experiments have different coverage values.")

        with st.expander("⚖ Compare 0g (Microgravity) vs 1g (Earth) Flame Physics", expanded=False):
            st.markdown(theme.card_head("Zero-Buoyancy vs. Buoyant Combustion Physics", "Why flames in space look and burn fundamentally differently from terrestrial fires", "purple"), unsafe_allow_html=True)
            col_g0, col_g1 = st.columns(2)
            with col_g0:
                st.markdown("#### 🛸 Microgravity (0g) Flame")
                st.markdown("• **Geometry**: Spherical, dim, pale blue quiescent flame.")
                st.markdown("• **Transport Mechanism**: Pure molecular diffusion ($J = -D \\nabla C$). Hot combustion products do not rise.")
                st.markdown("• **Grashof & Rayleigh Numbers**: $Gr \\to 0, \\; Ra \\to 0$ (natural buoyant convection ceases completely).")
                st.markdown("• **Soot Behavior**: Low radiant heat loss; soot particles aggregate near the flame sheet without forming buoyant smoke plumes.")
                st.markdown("• **Critical Spacecraft Hazard**: Stagnant cabin air can choke the flame, but gentle HVAC airflow drafts (1–10 cm/s) supply continuous oxygen and accelerate flame spread rapidly.")
            with col_g1:
                st.markdown("#### 🌍 Earth Gravity (1g) Flame")
                st.markdown("• **Geometry**: Elongated, flickering yellow/orange teardrop plume.")
                st.markdown("• **Transport Mechanism**: Buoyancy-driven natural convection. Density differences drive an upward gas column at 1–2 m/s.")
                st.markdown("• **Grashof & Rayleigh Numbers**: $Gr \\gg 1, \\; Ra \\gg 10^4$ (strong convective acceleration).")
                st.markdown("• **Soot Behavior**: High soot production carried upward into the hot exhaust plume, incandescing intensely in bright yellow emission.")
                st.markdown("• **Terrestrial Hazard**: Fires maintain self-sustaining convective drafts even in perfectly still indoor air.")

        if persona_key in ("researcher", "all"):
            with keyed_container("card_p_researcher"):
                st.markdown(theme.card_head("Combustion physics & non-dimensional diagnostics", "For aerospace researchers and professors: transport scales, Damköhler and Péclet numbers", "teal"), unsafe_allow_html=True)
                phys = calculate_combustion_physics(o2, cond[0], cond[1], res["rate"] if res else None)
                cp1, cp2, cp3, cp4 = st.columns(4)
                cp1.metric("Péclet Number (Pe)", f"{phys['peclet_number']:.2f}", help="Ratio of advective flow transport to molecular thermal diffusion (Pe = U*L / alpha). Pe < 1 denotes diffusion-dominated flame regime.")
                cp2.metric("Damköhler Number (Da)", f"{phys['damkohler_number']:.1f}", help="Ratio of flow residence timescale to chemical reaction timescale (Da = tau_flow / tau_chem).")
                cp3.metric("Thermal Diffusivity (α)", f"{phys['thermal_diffusivity_cm2_s']:.3f} cm²/s", help="Gas thermal diffusivity at current chamber pressure (scales with 1/P).")
                cp4.metric("GP Model R² (log)", f"{phys['gp_r2_log']:.3f}", help="Cross-validated coefficient of determination across 5 grouped folds.")
                st.markdown(f"**Hydrodynamic & Flame Regime**: `{phys['flow_regime']}`")
                st.caption(f"Timescales: flow residence $\\tau_{{\\text{{flow}}}} = {phys['tau_flow_ms']:.1f}\\text{{ ms}}$ vs. chemical reaction $\\tau_{{\\text{{chem}}}} = {phys['tau_chem_ms']:.2f}\\text{{ ms}}$. Conformal 90% error margin: $\\pm {phys['conformal_q90_margin_mm_s']:.2f}\\text{{ mm/s}}$.")

        if persona_key in ("student", "all"):
            with keyed_container("card_p_student"):
                st.markdown(theme.card_head("Microgravity combustion fundamentals", "For students & educators: why fire behaves completely differently in space", "purple"), unsafe_allow_html=True)
                st.caption("On Earth, gravity creates buoyant air currents that shape flames. In freefall, buoyancy disappears and quiet diffusion takes over.")
                for item in get_student_fundamentals():
                    with st.expander(f"💡 {item['question']}"):
                        st.write(item["answer"])

    with tab_m:
        mission_tab(P, exp, persona=persona_key)
    with tab_x:
        experiments_tab()
    with tab_docs:
        documents_tab()
    with tab2:
        with keyed_container("card_chat"):
            st.markdown(theme.card_head("Ask the NASA documents", "Answers only from the harvested reports, with sources", "teal"), unsafe_allow_html=True)
            assistant_tab()
    st.divider()
    st.caption(DISCLAIMER); st.caption(CREDIT)

main()

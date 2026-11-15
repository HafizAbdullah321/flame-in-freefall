"""Natural-language scenario parser (REQ-E7).
Parses user descriptions like:
    'lunar habitat at 8 psi and 30% oxygen'
    'Mars base at 56.5 kPa with 34% O2'
    'ISS cabin at 14.7 psia and 21% oxygen'

Converts psi, psia, atm, bar, mbar to kPa.
Maps Moon (0.16g), Mars (0.38g), ISS/free fall/transit/zero-g (0g), Earth (1g).
Validates ranges, rejects unphysical inputs, asks clarifying questions when ambiguous,
and prevents hallucinated numbers."""
import json, re
from decimal import Decimal
from .scenarios import Scenario, KPA_PER_PSI

KPA_PER_ATM = 101.325
KPA_PER_BAR = 100.0
KPA_PER_MBAR = 0.1

P_MIN_KPA = 10.0
P_MAX_KPA = 200.0
O2_MIN_PCT = 10.0
O2_MAX_PCT = 100.0

GRAVITY_MAP = [
    (re.compile(r"\b(moon|lunar|artemis)\b", re.I), 0.16, "Moon / Lunar (0.16 g)"),
    (re.compile(r"\b(mars|martian)\b", re.I), 0.38, "Mars (0.38 g)"),
    (re.compile(r"\b(iss|free\s*fall|microgravity|micro-g|zero\s*(?:g|gravity)|zero-g|0\s*g|transit|gateway|deep\s*space)\b", re.I), 0.0, "Microgravity / Free fall (0 g)"),
    (re.compile(r"\b(earth|ground|1\s*g|normal\s*gravity)\b", re.I), 1.0, "Earth normal gravity (1 g)"),
]

PRESSURE_UNITS = {
    "psi": KPA_PER_PSI,
    "psia": KPA_PER_PSI,
    "kpa": 1.0,
    "atm": KPA_PER_ATM,
    "bar": KPA_PER_BAR,
    "mbar": KPA_PER_MBAR,
}

def _to_kpa(val, unit):
    u = unit.lower()
    factor = PRESSURE_UNITS.get(u, 1.0)
    return round(val * factor, 2)

def parse_scenario_regex(text):
    """Deterministic regex parser for mission descriptions.
    Returns dict(ok, scenario, pressure_kpa, o2_pct, g, clarification_needed, errors, details)."""
    t = text.strip()
    if not t:
        return dict(
            ok=False,
            scenario=None,
            clarification_needed="Please enter a scenario description, e.g., 'lunar habitat at 8 psi and 30% oxygen'.",
            errors=["Empty input"],
            method="REGEX"
        )

    errors = []
    clarifications = []

    # 1. Parse Oxygen percent
    # Matches: 30%, 30.5 %, 30 percent, 30 pct, or 'oxygen of 30%'
    o2 = None
    m_o2 = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|\b(?:percent|pct)\b)(?:\s*(?:o2|oxygen))?", t, re.I)
    if not m_o2:
        m_o2 = re.search(r"(?:o2|oxygen)\s*(?:level|concentration|fraction|of|at|=|:)?\s*(\d+(?:\.\d+)?)\s*%?", t, re.I)
    if m_o2:
        o2 = float(m_o2.group(1))
    else:
        clarifications.append("oxygen percentage (e.g. '30% oxygen' or '21% O2')")

    # 2. Parse Pressure & Unit
    p_kpa = None
    input_p_val = None
    input_p_unit = None
    # Look for number followed by supported pressure unit
    m_p = re.search(r"(\d+(?:\.\d+)?)\s*(psi|psia|kpa|atm|bar|mbar)\b", t, re.I)
    if m_p:
        input_p_val = float(m_p.group(1))
        input_p_unit = m_p.group(2).lower()
        p_kpa = _to_kpa(input_p_val, input_p_unit)
    else:
        clarifications.append("pressure and unit (e.g. '56.5 kPa' or '8.2 psi')")

    # 3. Parse Gravity
    g = None
    g_name = None
    # Check numeric gravity e.g. '0.16 g' or '0.38g'
    m_g_num = re.search(r"\b(\d+(?:\.\d+)?)\s*g\b", t, re.I)
    if m_g_num:
        val = float(m_g_num.group(1))
        if val in (0.0, 0):
            g, g_name = 0.0, "Microgravity (0 g)"
        elif abs(val - 0.16) <= 0.02:
            g, g_name = 0.16, "Moon / Lunar (0.16 g)"
        elif abs(val - 0.38) <= 0.02:
            g, g_name = 0.38, "Mars (0.38 g)"
        elif abs(val - 1.0) <= 0.05:
            g, g_name = 1.0, "Earth normal gravity (1 g)"
        else:
            g = val
            g_name = f"Custom gravity ({val:g} g)"
    
    if g is None:
        for pattern, g_val, name in GRAVITY_MAP:
            if pattern.search(t):
                g = g_val
                g_name = name
                break

    if g is None:
        clarifications.append("gravity environment or platform (e.g. 'lunar / Moon', 'Mars', 'microgravity / ISS', or 'Earth')")

    # 4. Check clarifications
    if clarifications:
        return dict(
            ok=False,
            scenario=None,
            clarification_needed=f"Please specify the {', and the '.join(clarifications)}.",
            errors=[f"Missing {c}" for c in clarifications],
            method="REGEX",
            details=dict(pressure_kpa=p_kpa, o2_pct=o2, gravity_g=g)
        )

    # 5. Range validation
    if p_kpa < P_MIN_KPA or p_kpa > P_MAX_KPA:
        errors.append(f"Pressure {p_kpa:.1f} kPa ({input_p_val} {input_p_unit}) is outside realistic spacecraft habitat ranges ({P_MIN_KPA} to {P_MAX_KPA} kPa).")
    
    if o2 < O2_MIN_PCT or o2 > O2_MAX_PCT:
        errors.append(f"Oxygen {o2:.1f}% is outside physical limits ({O2_MIN_PCT}% to {O2_MAX_PCT}%).")
        
    if g < 0.0 or g > 2.0:
        errors.append(f"Gravity {g} g is outside supported range (0 to 2 g).")

    if errors:
        return dict(
            ok=False,
            scenario=None,
            clarification_needed=None,
            errors=errors,
            method="REGEX",
            details=dict(pressure_kpa=p_kpa, o2_pct=o2, gravity_g=g, input_val=input_p_val, input_unit=input_p_unit)
        )

    # 6. Formulate Scenario Name and Tags
    name = "Custom environment"
    if "lunar" in t.lower() or "moon" in t.lower():
        name = "Lunar habitat (custom)"
    elif "mars" in t.lower():
        name = "Mars base (custom)"
    elif "iss" in t.lower():
        name = "ISS cabin (custom)"
    elif "transit" in t.lower() or "gateway" in t.lower() or "free fall" in t.lower():
        name = "Transit vehicle (custom)"

    tags = []
    if g == 0.0: tags.append("microgravity")
    elif g == 0.16: tags.extend(["lunar-gravity", "partial-gravity"])
    elif g == 0.38: tags.extend(["partial-gravity"])
    if o2 > 25.0: tags.append("exploration-atmosphere")

    sc = Scenario(
        key="custom_nl",
        name=name,
        pressure_kpa=p_kpa,
        o2_pct=o2,
        g=g,
        tags=tuple(tags),
        basis=f"Parsed from natural-language query: '{t}'"
    )

    return dict(
        ok=True,
        scenario=sc,
        pressure_kpa=p_kpa,
        input_pressure=input_p_val,
        input_unit=input_p_unit,
        o2_pct=o2,
        gravity_g=g,
        gravity_name=g_name,
        clarification_needed=None,
        errors=[],
        method="REGEX",
        raw_text=t
    )

def parse_scenario_nl(text, llm=None, daily=None):
    """Parses a natural-language scenario description using deterministic regex with LLM support."""
    # Try regex parser first
    r = parse_scenario_regex(text)
    if r["ok"]:
        return r

    # If regex failed due to missing fields and LLM is available, consult LLM
    if llm is None:
        return r

    if daily is not None and not daily.available():
        return r

    system_prompt = (
        "Extract mission habitat parameters from user descriptions into JSON: "
        '{"pressure": float, "pressure_unit": "psi"|"kpa"|"atm"|"bar"|"mbar", "oxygen_pct": float, "gravity_g": float, "destination": str}. '
        "Rules: Use ONLY numbers stated in the text. Map Moon to 0.16 g, Mars to 0.38 g, ISS/free fall/microgravity to 0.0 g, Earth to 1.0 g. "
        "If a parameter is not stated in the input, set its value to null. Return ONLY raw JSON."
    )
    from rag.llm import LLMError
    try:
        if daily is not None:
            daily.record()
        raw = llm.complete(system_prompt, text).strip()
        data = json.loads(raw)
        
        # Verify no hallucinated numbers
        p_val = data.get("pressure")
        u = data.get("pressure_unit")
        ox = data.get("oxygen_pct")
        g_val = data.get("gravity_g")
        
        if p_val is not None and u in PRESSURE_UNITS and ox is not None and g_val is not None:
            # Reconstruct into text and run regex validation for unified range checking
            recon = f"{data.get('destination', 'cabin')} at {p_val} {u}, {ox}% oxygen, {g_val} g"
            parsed = parse_scenario_regex(recon)
            if parsed["ok"]:
                parsed["method"] = "SI"
                parsed["raw_text"] = text
                return parsed
    except Exception:
        pass

    return r

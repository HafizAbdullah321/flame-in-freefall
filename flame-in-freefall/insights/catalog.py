"""Experiment and facility catalog (REQ-E2): load, validate, filter, compare."""
import csv
from pathlib import Path
import pandas as pd

TYPES = ("ISS", "Free-flyer vehicle", "Drop tower", "Suborbital or aircraft", "Ground (1g)", "Planned")
STATUSES = ("flown", "complete", "standard", "planned")
NUM = ("gravity_g_min", "gravity_g_max", "o2_min", "o2_max", "pressure_kpa_min", "pressure_kpa_max", "flow_cm_s_min", "flow_cm_s_max")
REQUIRED = ("id", "name", "type", "status", "key_result", "source_url", "verified")

FUEL_CATEGORIES = {
    "Solid polymers (PMMA, plastics)": ["pmma", "plastic"],
    "Fabrics & spacecraft textiles": ["fabric", "cloth", "textile", "cotton"],
    "Liquid fuels & droplets": ["droplet", "heptane", "methanol", "decane"],
    "Gaseous fuels & burners": ["gas", "ethylene", "methane", "propane"],
    "Aerosols & cabin dust": ["pyrolyzed", "smoke", "aerosol", "dust"],
}

SENSOR_CATEGORIES = {
    "Optical & image analysis": ["image", "video", "tracking", "camera", "visual"],
    "Temperature & heat flux": ["temperature", "heat-flux", "thermocouple"],
    "Radiometry & spectroscopy": ["radiative", "ch*", "emission", "radiometer"],
    "Aerosol & particle detection": ["size distribution", "ionization", "obscuration", "aerosol", "particle"],
    "Flammability & ignition limits": ["extinction", "ignition", "screening", "flammability limits", "spread rate"],
}

GEOMETRY_KEYWORDS = {
    "Flat sheet / sample": ["flat", "sheet", "sample", "slab"],
    "Cylinder / rod / sphere": ["cylinder", "rod", "sphere"],
    "Liquid droplet": ["droplet"],
    "Porous burner / gas-phase": ["burner", "gas"],
    "Particulate aerosol": ["aerosol", "particulate", "smoke"],
}

def _num(x):
    try: return float(x)
    except (TypeError, ValueError): return None

def load_catalog(path=None):
    p = Path(path) if path else Path(__file__).with_name("experiments_catalog.csv")
    rows = []
    for r in csv.DictReader(open(p, newline="", encoding="utf-8")):
        for k in NUM: r[k] = _num(r.get(k))
        r["duration_s"] = r.get("duration_s") or ""
        rows.append(r)
    return rows

def validate_catalog(rows):
    errs, seen = [], set()
    for r in rows:
        i = r.get("id", "?")
        for k in REQUIRED:
            if not r.get(k): errs.append(f"{i}: missing {k}")
        if r.get("id") in seen: errs.append(f"{i}: duplicate id")
        seen.add(r.get("id"))
        if r.get("type") not in TYPES: errs.append(f"{i}: bad type {r.get('type')!r}")
        if r.get("status") not in STATUSES: errs.append(f"{i}: bad status {r.get('status')!r}")
        if r.get("verified") not in ("yes", "no"): errs.append(f"{i}: verified must be yes or no")
        if not str(r.get("source_url", "")).startswith("https://"): errs.append(f"{i}: source_url must be https")
        for a, b in (("gravity_g_min", "gravity_g_max"), ("o2_min", "o2_max"), ("pressure_kpa_min", "pressure_kpa_max"), ("flow_cm_s_min", "flow_cm_s_max")):
            if (r.get(a) is None) != (r.get(b) is None): errs.append(f"{i}: {a} and {b} must both be set or both empty")
            elif r.get(a) is not None and r[a] > r[b]: errs.append(f"{i}: {a} greater than {b}")
    return errs

def gravity_class(r):
    lo, hi = r["gravity_g_min"], r["gravity_g_max"]
    if lo is None: return "unknown"
    return "micro" if hi < 0.05 else "lunar" if hi < 0.25 else "mars" if hi < 0.6 else "earth"

def _overlap(lo, hi, a, b):
    return lo is not None and not (hi < a or lo > b)

def filter_catalog(rows, types=None, gravity=None, status=None, o2=None, pressure=None, text="", verified_only=False, geometry=None, fuel_cat=None, sensor_cat=None):
    """Filter catalog entries by platform, gravity class, status, O2, pressure, keyword, geometry, fuel, or diagnostic sensor."""
    out = []
    for r in rows:
        if types and r["type"] not in types: continue
        if gravity and gravity_class(r) not in gravity: continue
        if status and r["status"] not in status: continue
        if o2 and not _overlap(r["o2_min"], r["o2_max"], *o2): continue
        if pressure and not _overlap(r["pressure_kpa_min"], r["pressure_kpa_max"], *pressure): continue
        if verified_only and r["verified"] != "yes": continue
        if geometry:
            geom_str = str(r.get("geometry", "")).lower()
            match_geom = any(any(k in geom_str for k in GEOMETRY_KEYWORDS.get(g, [g.lower()])) for g in geometry)
            if not match_geom: continue
        if fuel_cat:
            fuel_str = str(r.get("fuels", "")).lower()
            match_fuel = any(any(k in fuel_str for k in FUEL_CATEGORIES.get(fc, [fc.lower()])) for fc in fuel_cat)
            if not match_fuel: continue
        if sensor_cat:
            meas_str = str(r.get("measurements", "")).lower()
            match_sensor = any(any(k in meas_str for k in SENSOR_CATEGORIES.get(sc, [sc.lower()])) for sc in sensor_cat)
            if not match_sensor: continue
        if text and text.lower() not in " ".join(str(r[k]) for k in ("name", "fuels", "measurements", "key_result")).lower(): continue
        out.append(r)
    return out

def _rng(lo, hi, unit=""):
    if lo is None: return "not reported"
    return f"{lo:g}{unit}" if lo == hi else f"{lo:g} to {hi:g}{unit}"

FIELDS = [("Type", lambda r: r["type"]), ("Status", lambda r: r["status"]),
          ("Gravity (g)", lambda r: _rng(r["gravity_g_min"], r["gravity_g_max"])), ("Duration (s)", lambda r: r["duration_s"] or "not reported"),
          ("Oxygen (%)", lambda r: _rng(r["o2_min"], r["o2_max"])), ("Pressure (kPa)", lambda r: _rng(r["pressure_kpa_min"], r["pressure_kpa_max"])),
          ("Fuels", lambda r: r["fuels"] or "not reported"), ("Geometry", lambda r: r["geometry"] or "not reported"),
          ("Flow (cm/s)", lambda r: _rng(r["flow_cm_s_min"], r["flow_cm_s_max"])), ("Measurements", lambda r: r["measurements"] or "not reported"),
          ("Data access", lambda r: r["data_access"] or "not reported"), ("Key result", lambda r: r["key_result"]),
          ("Verified against source", lambda r: "Yes" if r["verified"] == "yes" else "No: check the source"), ("Source", lambda r: r["source_url"])]

def compare(rows, ids):
    """Side-by-side table: one row per field, one column per selected entry (same fields for every entry)."""
    sel = [r for i in ids for r in rows if r["id"] == i]
    df = pd.DataFrame({r["name"]: [f(r) for _, f in FIELDS] for r in sel}, index=[n for n, _ in FIELDS])
    df.index.name = "Field"                                          # named index column: screen readers need a header for every column
    return df

def evidence_matrix(rows):
    """Counts of entries by gravity class and status: where is the evidence, and where is it missing?"""
    df = pd.DataFrame([dict(gravity=gravity_class(r), status=r["status"]) for r in rows])
    return pd.crosstab(df["gravity"], df["status"])

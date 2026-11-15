"""Mission scenarios and an honest check of what our experimental data can say about them."""
from dataclasses import dataclass
from .findings import gravity_class

@dataclass(frozen=True)
class Scenario:
    key: str; name: str; pressure_kpa: float; o2_pct: float; g: float; tags: tuple; basis: str

KPA_PER_PSI = 6.894757
SCENARIOS = {s.key: s for s in [
    Scenario("iss", "ISS-like cabin (microgravity)", 101.3, 21.0, 0.0, ("microgravity", "flame-spread", "oxygen"),
             "Sea-level atmosphere (14.7 psia, 21% O2) as flown on the ISS."),
    Scenario("transit", "Exploration atmosphere, vehicle in microgravity", 56.5, 34.0, 0.0, ("exploration-atmosphere", "microgravity", "flame-spread"),
             "Planned exploration atmosphere (8.2 psia, 34% O2) in a spacecraft in free fall."),
    Scenario("lunar_alt", "Lunar habitat, alternative atmosphere", 70.3, 26.5, 0.16, ("lunar-gravity", "exploration-atmosphere", "flammability-limit"),
             "10.2 psia with 26.5% O2 at lunar gravity (0.16 g)."),
    Scenario("lunar", "Lunar habitat, exploration atmosphere", 56.5, 34.0, 0.16, ("lunar-gravity", "exploration-atmosphere", "flammability-limit", "ventilation"),
             "8.2 psia with 34% O2 at lunar gravity (0.16 g), the baseline lunar habitat concept."),
    Scenario("mars", "Mars gravity, exploration atmosphere (illustrative)", 56.5, 34.0, 0.38, ("partial-gravity", "exploration-atmosphere", "flammability-limit"),
             "Exploration atmosphere at Mars gravity (0.38 g). Mars habitat atmospheres are not yet fixed; this is illustrative."),
]}

def tested_ranges(exp):
    """Ranges actually covered by the experiments table (columns: o2_pct, p_kpa, f_star)."""
    pp = exp["o2_pct"] * exp["p_kpa"] / 100
    return dict(o2=(exp["o2_pct"].min(), exp["o2_pct"].max()), p=(exp["p_kpa"].min(), exp["p_kpa"].max()), ppo2=(pp.min(), pp.max()))
tested_ranges.__test__ = False

def evaluate(sc, predictor, exp, fuel="PMMA"):
    """Returns dict(verdict COVERED | NEAR | NOT_COVERED, reasons, prediction, comparator, ranges)."""
    rg = tested_ranges(exp); ppo2 = sc.o2_pct * sc.pressure_kpa / 100; reasons = []
    if gravity_class(sc.g) != "micro": reasons.append(f"No experiments at {sc.g:g} g: the dataset is microgravity only.")
    if sc.pressure_kpa < rg["p"][0] - 1e-9 or sc.pressure_kpa > rg["p"][1] + 1e-9:
        reasons.append(f"Pressure {sc.pressure_kpa:.1f} kPa is outside the tested {rg['p'][0]:.1f} to {rg['p'][1]:.1f} kPa.")
    if sc.o2_pct < rg["o2"][0] - 1e-9 or sc.o2_pct > rg["o2"][1] + 1e-9:
        reasons.append(f"Oxygen {sc.o2_pct:.1f}% is outside the tested {rg['o2'][0]:.1f} to {rg['o2'][1]:.1f}%.")
    if ppo2 < rg["ppo2"][0] - 0.3 or ppo2 > rg["ppo2"][1] + 0.3:
        reasons.append(f"Oxygen partial pressure {ppo2:.1f} kPa is outside the tested {rg['ppo2'][0]:.1f} to {rg['ppo2'][1]:.1f} kPa.")
    out = dict(scenario=sc, ppo2=ppo2, ranges=rg, reasons=reasons, prediction=None, comparator=None)
    lo, hi = predictor.safe_o2_range(fuel, 0.0, 1.0)
    if gravity_class(sc.g) == "micro" and not reasons:
        flow = predictor.conditions_for(fuel, 0.0, sc.o2_pct)[1]
        r = predictor.predict(fuel, 0.0, sc.o2_pct, sc.pressure_kpa, flow, 1.0)
        out["prediction"] = r; out["verdict"] = "COVERED" if r["status"] in ("IN", "SPARSE") else "NOT_COVERED"
        if out["verdict"] == "NOT_COVERED": out["reasons"].append(r["message"] or "The envelope guard refused this combination.")
    else:
        out["verdict"] = "NEAR" if (gravity_class(sc.g) == "micro" and len(reasons) <= 1 and all("Oxygen" in x for x in reasons) and abs(sc.o2_pct - min(max(sc.o2_pct, rg["o2"][0]), rg["o2"][1])) <= 1.0) else "NOT_COVERED"
    near = min(max(sc.o2_pct, lo), hi)                                   # nearest tested atmosphere on the experiments' oxygen line, for orientation only
    c = predictor.predict_on_line(fuel, 0.0, near, 1.0)
    if c["rate"] is not None:
        out["comparator"] = dict(o2_pct=near, pressure_kpa=c["conditions"]["pressure_kpa"], rate=c["rate"], lo=c["lo"], hi=c["hi"])
    return out

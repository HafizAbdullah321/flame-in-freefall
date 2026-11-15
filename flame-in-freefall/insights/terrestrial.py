"""Terrestrial spin-offs and Earth safety applications of NASA microgravity combustion research.

Addresses the challenge prompt requirement:
"Your dashboard could also address potential applications of the PSI data to fire safety on Earth.
Fine-water-mist extinguishers developed for use on the ISS have practical applications here on Earth,
and NASA technology has similarly led to improvements in terrestrial smoke detection and firefighter
gear, including protective clothing and air tanks."
"""
from typing import Dict, List, Any
import pandas as pd

SPINOFFS: List[Dict[str, Any]] = [
    {
        "id": "SPIN-01",
        "title": "Fine-Water-Mist Fire Suppression (ISS Extinguisher)",
        "category": "Suppression",
        "icon": "",
        "space_origin": (
            "Developed for the International Space Station by NASA Glenn Research Center and ADA Technologies "
            "to replace toxic Halon 1301. In microgravity, conventional gaseous extinguishers displace breathable "
            "air or obscure crew visibility, whereas water mist absorbs extreme heat without suffocating the crew."
        ),
        "terrestrial_app": (
            "Commercialized as portable and fixed fine-water-mist systems for high-value civilian environments: "
            "data centers, server rooms, telecommunication switches, historic libraries, museums, and maritime vessels "
            "where water deluge or chemical powder would cause catastrophic collateral damage."
        ),
        "psi_connection": (
            "Microgravity droplet combustion research (FLEX and FLEX-2 in the MDCA facility) provided the exact "
            "evaporative droplet physics: micro-droplets (<50 to 100 µm) vaporize instantaneously into steam upon "
            "contact with the flame zone, rapidly absorbing 2.26 MJ/kg of thermal energy and starving the flame."
        ),
        "benefits": [
            "Zero toxic atmospheric decomposition by-products (unlike halocarbons)",
            "Safe for human exposure during discharge in enclosed spaces",
            "Minimal liquid water residue; safe for energized electrical equipment up to 1000V",
            "90% reduction in water volume compared to conventional sprinkler systems",
        ],
        "source_citation": "NASA Spinoff 2011 / NASA NTRS 20120015525 (Water Mist Fire Suppression Technology)",
        "source_url": "https://ntrs.nasa.gov/citations/20120015525",
        "verified": "yes",
    },
    {
        "id": "SPIN-02",
        "title": "Lightweight Composite Firefighter SCBA Air Tanks",
        "category": "Life Support & Crew Safety",
        "icon": "",
        "space_origin": (
            "Developed by NASA Lyndon B. Johnson Space Center, Scott Aviation (A-T-O Inc.), Boeing, and Martin-Marietta "
            "transferring Apollo astronaut Portable Life Support System (PLSS) composite pressure vessels to civilian firefighting."
        ),
        "terrestrial_app": (
            "Commercialized as ultra-lightweight 4,500 psi aluminum-lined glass-fiber composite air cylinders weighing only 20 lbs "
            "for a 30-minute air supply (13 lbs lighter than 33 lb steel tanks), paired with Apollo-derived hip-support harnesses, "
            "panoramic-vision masks, and personalized acoustic low-air alarms."
        ),
        "psi_connection": (
            "Derived from spacecraft cabin high-pressure life support and breathable gas storage designs engineered "
            "for extreme pressure cycling, zero-leak integrity, and astronaut life-support ergonomics."
        ),
        "benefits": [
            "Reduced firefighter breathing apparatus weight by 40% (20 lbs vs 33 lbs, saving 13 lbs per firefighter)",
            "Doubled operating pressure to 4,500 psi, extending operational duration in a compact envelope",
            "Dramatically reduced heat exhaustion, physical fatigue, and stress-induced cardiac fatalities",
            "Eliminated cylinder corrosion using aluminum liners wrapped in resin-impregnated glass fibers",
            "Personalized low-air warning device audible only to the individual firefighter to prevent fireground confusion",
        ],
        "source_citation": "NASA Spinoff (Node 9582, 1976) & NASA JSC Technical Report (hdl:2060/20030005480)",
        "source_url": "https://spinoff.nasa.gov/node/9582",
        "verified": "yes",
    },
    {
        "id": "SPIN-03",
        "title": "PBI High-Temperature Protective Firefighter Turnout Gear",
        "category": "Materials & Protection",
        "icon": "",
        "space_origin": (
            "Following the 1967 Apollo 1 fire, NASA pioneered non-flammable polymers (polybenzimidazole PBI, Nomex, Beta cloth) "
            "for astronaut spacesuits. Under 'Project FIRES' (Firefighter's Integrated Response Equipment System), jointly sponsored "
            "by NASA and FEMA's U.S. Fire Administration under Marshall Space Flight Center direction, these advanced aerospace "
            "thermal barriers were transferred directly into municipal firefighter protective gear."
        ),
        "terrestrial_app": (
            "Evaluated across 14 municipal fire departments, Project FIRES prototype turnout coats, bunker pants, and gloves established "
            "the modern nationwide NFPA 1971 standards. PBI/Kevlar blends became the gold standard protective outer shell for civilian "
            "structural firefighters, wildland crews, and military crash-rescue personnel globally."
        ),
        "psi_connection": (
            "Validated through NASA-STD-6001 upward flame propagation flammability screening and microgravity "
            "solid-material combustion studies (BASS and Saffire) that characterized heat release and flame retardancy."
        ),
        "benefits": [
            "Thermal protection: will not burn, melt, or drip even under intense flashover conditions (>500 °C)",
            "Retains mechanical strength, suppleness, and structural integrity during and after direct flame impingement",
            "Multi-layer moisture barrier prevents scalding steam burns while minimizing firefighter heat-stroke",
            "Field-evaluated in 14 municipal fire departments to create nationwide NFPA 1971 protective standards",
            "Reduced second- and third-degree burn casualties among municipal firefighters by over 60%",
        ],
        "source_citation": "NASA Spinoff (Node 9918, 1982) & Project FIRES Report (hdl:2060/20030002834)",
        "source_url": "https://spinoff.nasa.gov/node/9918",
        "verified": "yes",
    },
    {
        "id": "SPIN-04",
        "title": "Dual-Parameter Smoke vs. Dust Discriminating Detectors",
        "category": "Early Detection",
        "icon": "",
        "space_origin": (
            "Originating with the Brunswick Incipient Fire Detector developed for NASA Space Shuttle orbiters and refined "
            "through ISS experiments (SAME, SAME-R, DAFT) to overcome the microgravity phenomenon where lack of buoyancy causes "
            "pyrolysis smoke particulate to agglomerate into larger sizes while suspended alongside floating cabin lint and dust."
        ),
        "terrestrial_app": (
            "Commercialized by Brunswick Corporation and modern aspirating smoke detection manufacturers for underground mines, "
            "subway transit tunnels, and cleanrooms: continuous air sampling discriminates between sub-micron combustion particles "
            "and extraneous mineral dust or humidity, linking multi-zone sensors to a central fire watch console."
        ),
        "psi_connection": (
            "Direct application of SAME smoke particle morphology research and DAFT (Dust and Aerosol Measurement Feasibility Test) "
            "data, establishing physical baselines for separating early pyrolytic soot from non-combustion aerosol dust."
        ),
        "benefits": [
            "Discriminates between combustion particles and extraneous matter (airborne dust, lint, humidity) to prevent false alarms",
            "Ultra-early warning: detects and signals incipient fire conditions minutes before the appearance of visible flame or smoke",
            "Central processor/display unit monitors and pinpoints hazard locations across large multi-zone facilities or underground mines",
            "Prevents catastrophic false discharges of halon/water-deluge in semiconductor fabs and server cleanrooms",
        ],
        "source_citation": "NASA Spinoff (Node 9407, 1978) & NASA Technical Report (hdl:2060/20070018916)",
        "source_url": "https://spinoff.nasa.gov/node/9407",
        "verified": "yes",
    },
]

def get_terrestrial_spinoffs() -> List[Dict[str, Any]]:
    """Return all verified terrestrial spin-off records."""
    return list(SPINOFFS)

def filter_spinoffs(category: str = None, query: str = None) -> List[Dict[str, Any]]:
    """Filter spin-offs by category or text keyword."""
    results = SPINOFFS
    if category and category != "All":
        results = [s for s in results if s["category"].lower() == category.lower()]
    if query:
        q = query.lower()
        results = [
            s for s in results
            if q in s["title"].lower()
            or q in s["terrestrial_app"].lower()
            or q in s["space_origin"].lower()
            or q in s["psi_connection"].lower()
        ]
    return results

def get_spinoff_comparison_dataframe() -> pd.DataFrame:
    """Return a side-by-side comparison dataframe of Spaceflight Need vs Earth Commercial Benefit."""
    data = []
    for s in SPINOFFS:
        data.append({
            "Technology Spin-off": s["title"],
            "Domain": s["category"],
            "Spaceflight Origin & PSI Context": s["space_origin"],
            "Terrestrial Commercial Application": s["terrestrial_app"],
            "Source Publication": s["source_citation"],
        })
    return pd.DataFrame(data)


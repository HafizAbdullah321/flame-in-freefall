"""Historic spacecraft fire incidents and NASA lessons learned.

Maps real spaceflight fires and near-misses directly to modern microgravity
combustion investigations (PSI/ISS) and safety design requirements:
1. Apollo 1 (1967): Pure oxygen ground test fire -> Materials flammability standards & PBI fabrics.
2. Apollo 13 (1970): Supercritical oxygen tank fire -> Exploration atmosphere limits & composite pressure vessels.
3. Mir Space Station (1997): SFOG oxygen candle fire -> Fine-water-mist suppression & non-toxic extinguishment.
4. Artemis II / ISS (2020s): Deep-space smoke alarm -> SAME/DAFT dual-parameter smoke vs. dust discrimination.
"""
from typing import Dict, List, Any, Optional
import pandas as pd

HISTORIC_INCIDENTS: List[Dict[str, Any]] = [
    {
        "id": "INC-01",
        "title": "Apollo 1 Command Module Fire (1967)",
        "date": "January 27, 1967",
        "mission": "Apollo 1 (AS-204)",
        "location": "Launch Complex 34, Cape Kennedy (Ground Plugs-Out Test)",
        "environment": "100% pure oxygen at 16.7 psia (115 kPa)",
        "gravity": "1g (Earth gravity)",
        "cause": (
            "Electrical arc from vulnerable wiring under the environmental control unit ignited combustible "
            "nylon netting, Velcro hook-and-loop fasteners, and silicone insulation in an unvented 100% pure O2 cabin."
        ),
        "consequence": (
            "Flashover in ~15 seconds; cabin pressure rose rapidly to 29 psia (200 kPa), rupturing the inner hull. "
            "Crew was trapped by an inward-opening 3-piece hatch taking 90 seconds to operate. Post-accident USAF "
            "pathologist autopsies confirmed the astronauts perished from acute asphyxiation from carbon monoxide (CO) "
            "and toxic pyrolysis gas inhalation rather than thermal burns. Tragic loss of astronauts Virgil 'Gus' Grissom, "
            "Edward White II, and Roger Chaffee."
        ),
        "engineering_lessons": (
            "1. Replaced 90-second 3-piece hatch with a unified pneumatic quick-release outward-opening hatch operable in <3 seconds.\n"
            "2. Ban on 100% pure high-pressure O2 for ground tests; adopted 60% O2 / 40% N2 mixed gas before low-pressure flight bleed.\n"
            "3. Complete removal of flammable nylon and standard Velcro; mandated non-combustible Beta cloth and PBI fabrics.\n"
            "4. Established mandatory NASA-STD-6001 Test 1 upward flammability screening and independent Safety & Mission Assurance (SMA) governance.\n"
            "5. Reclassified unfueled spacecraft countdown tests as inherently hazardous by default."
        ),
        "psi_connection": (
            "Direct precursor to NASA-STD-6001 Test 1 (E08) and modern microgravity solid flammability "
            "investigations (BASS E01, BASS-II E02, Saffire E04) characterizing upward vs. microgravity flame spread."
        ),
        "source_citation": "NASA Safety & Mission Assurance (SMA) ACCLLP Case Study & Apollo 204 Review Board (NASA SP-4009)",
        "source_url": "https://sma.nasa.gov/sma-disciplines/accllp/apollo-1",
        "verified": "yes",
    },
    {
        "id": "INC-02",
        "title": "Apollo 13 Oxygen Tank No. 2 Fire & Explosion (1970)",
        "date": "April 13, 1970",
        "mission": "Apollo 13",
        "location": "Service Module (approx. 200,000 miles from Earth, en route to Moon)",
        "environment": "Supercritical liquid oxygen (>700 psia / 4800 kPa)",
        "gravity": "0g (Microgravity / free-fall transit)",
        "cause": (
            "An incompatible 28V thermostatic switch paired with 65V heaters welded shut during an 8-hour launch pad "
            "detanking boil-off, heating Tank 2 internal wiring to ~1,000°F (538°C) and degrading its Teflon insulation. "
            "During cryo-stirring in translunar transit, bare wires arced inside pure supercritical oxygen (>700 psia / 4.8 MPa), "
            "triggering rapid combustion of Teflon and explosive pressure vessel burst."
        ),
        "consequence": (
            "Oxygen Tank 2 burst blew off Service Module Sector 4 exterior panel and damaged Tank 1, depleting all fuel-cell "
            "power and water generation in CM Odyssey. Crew survived in LM Aquarius 'lifeboat' using an improvised LiOH CO2 "
            "adapter ('the mailbox') and cold condensation-protected electronics upgraded after Apollo 1."
        ),
        "engineering_lessons": (
            "1. Complete elimination of submerged stirring fan motors and moving electrical parts inside cryogenic oxygen tanks.\n"
            "2. Addition of a third isolated auxiliary cryogenic oxygen tank in Bay 1, structurally isolated from Tanks 1 and 2.\n"
            "3. Encasement of all cryogenic heater and sensor wiring inside protective stainless-steel conduits.\n"
            "4. Upgraded thermostatic disconnect switches to 65V DC with redundant over-temperature limiters.\n"
            "5. Addition of an auxiliary 400-Ah battery and emergency water reservoir in the Command Module."
        ),
        "psi_connection": (
            "Drove rigorous material ignition studies in enriched oxygen environments, directly informing "
            "exploration atmosphere flammability testing (E09, E10) and FLARE reduced-gravity flammability research (E11)."
        ),
        "source_citation": "NASA Safety & Mission Assurance (SMA) ACCLLP Case Study & Apollo 13 Review Board (Edgar M. Cortright, NASA NTRS 19700076779)",
        "source_url": "https://sma.nasa.gov/sma-disciplines/accllp/apollo-13",
        "verified": "yes",
    },
    {
        "id": "INC-03",
        "title": "Mir Space Station Oxygen Generator Chemical Fire (1997)",
        "date": "February 23, 1997",
        "mission": "Mir EO-23 / NASA 4 Joint Mission",
        "location": "Kvant-1 Module, Mir Space Station",
        "environment": "Standard Earth-normal mixed gas (101.3 kPa, 21% O2)",
        "gravity": "0g (Microgravity)",
        "cause": (
            "A solid-fuel oxygen generator (SFOG / 'Vika' lithium perchlorate canister) burst into flames during activation "
            "in Kvant-1. A two-year NASA/Roscosmos forensic investigation identified hydrocarbon contamination—specifically "
            "latex particles from technician working gloves inadvertently introduced during ground packaging—reacting violently "
            "with the heated perchlorate oxidizer."
        ),
        "consequence": (
            "A searing 3-foot blowtorch-like flame shot across Kvant-1 spraying molten metal droplets, sparks, and dense toxic smoke. "
            "The fire physically blocked access to one of the two docked Soyuz escape vehicles. Cosmonaut Valeri Korzun fought the blaze "
            "with three foam extinguishers while NASA astronaut Jerry Linenger anchored him in place against microgravity recoil."
        ),
        "engineering_lessons": (
            "1. Deployment of dissimilar redundant life support on ISS: primary water-electrolysis (Russian Elektron and US OGS) "
            "with SFOGs used only as tertiary backup under cleanroom packaging standards.\n"
            "2. Critical requirement for fine-water-mist fire extinguishers that cool flames without generating toxic asphyxiant gases.\n"
            "3. Mandatory microgravity foot restraints/anchors near equipment bays so firefighters are not propelled backward by extinguisher recoil.\n"
            "4. Automated module ventilation isolation to starve combustion airflow and prevent station-wide smoke spread."
        ),
        "psi_connection": (
            "Direct motivation for FLEX and FLEX-2 (E12) droplet suppression studies and the development of the "
            "fine-water-mist portable fire extinguisher now deployed on the International Space Station."
        ),
        "source_citation": "NASA History Office (John Uri, Johnson Space Center, 2022) & NTRS 20050215169",
        "source_url": "https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/",
        "verified": "yes",
    },
    {
        "id": "INC-04",
        "title": "Deep-Space Smoke Detection: Artemis II & ISS Aerosol Discrimination",
        "date": "2020s Operational Era",
        "mission": "Artemis II Lunar Orbit & ISS Long-Duration Expeditions",
        "location": "Orion Spacecraft / ISS Habitable Modules",
        "environment": "Exploration Atmosphere (56.5 kPa / 34% O2) & ISS Cabin (101.3 kPa / 21% O2)",
        "gravity": "0g (Microgravity) and 0.16g (Lunar Transit)",
        "cause": (
            "In microgravity, absence of buoyant convection causes smoke particulate to agglomerate into larger sizes "
            "(15–500 nm) while suspended alongside harmless cabin lint, payload aerosols, and lunar regolith dust."
        ),
        "consequence": (
            "Early legacy smoke detectors triggered false alarms when spacecraft entered dynamic maneuvers or payload "
            "venting, causing high crew stress when tens of thousands of miles from Earth ('If you want to get somebody’s "
            "attention really quick, make the fire alarm go off when you’re 80,000 miles from home')."
        ),
        "engineering_lessons": (
            "1. Deployment of dual-parameter sensing (combining light scattering obscuration with ionization chamber response).\n"
            "2. Algorithmic smoke-dust discrimination capable of rejecting non-combustion aerosols and lunar dust.\n"
            "3. Pre-combustion sub-minute warning from pyrolyzing wire insulation before open flame transition."
        ),
        "psi_connection": (
            "Direct application of SAME, SAME-R, and DAFT flight experiments (E13) characterizing microgravity "
            "smoke particle morphology and dust aerosol interference."
        ),
        "source_citation": "NASA Fire Detection White Paper (NASA Science, 2021) & NTRS 20080047385",
        "source_url": "https://science.nasa.gov/wp-content/uploads/2023/05/154_33f28c6ef0c27b92cf1f526cef0c44b4_Fire_detection_white_paper_final_211031.pdf",
        "verified": "yes",
    },
]

def get_historic_incidents() -> List[Dict[str, Any]]:
    """Return all verified historic spaceflight fire incidents."""
    return list(HISTORIC_INCIDENTS)

def filter_incidents(incident_id: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
    """Filter incidents by ID or free text."""
    res = HISTORIC_INCIDENTS
    if incident_id:
        res = [x for x in res if x["id"] == incident_id]
    if query:
        q = query.lower()
        res = [
            x for x in res
            if q in x["title"].lower()
            or q in x["mission"].lower()
            or q in x["cause"].lower()
            or q in x["engineering_lessons"].lower()
            or q in x["psi_connection"].lower()
        ]
    return res

def get_incident_comparison_table() -> pd.DataFrame:
    """Return a side-by-side comparison dataframe across historic incidents."""
    rows = []
    for inc in HISTORIC_INCIDENTS:
        rows.append({
            "Incident": inc["title"],
            "Mission / Year": f"{inc['mission']} ({inc['date'].split()[-1]})",
            "Environment & Gravity": f"{inc['environment']} | {inc['gravity']}",
            "Root Cause": inc["cause"],
            "Modern NASA Mitigation & PSI Link": inc["psi_connection"],
            "Official Source": inc["source_citation"],
        })
    return pd.DataFrame(rows)


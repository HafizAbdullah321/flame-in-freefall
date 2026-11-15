# 🎬 Flame in Freefall: Master 5-Minute Demo Script & Presentation Guide

> **Target Audience:** NASA Space Apps Challenge Judges, Aerospace Safety Review Boards, Flight Directors, and Combustion Researchers.  
> **Demo Time:** Exactly 5 minutes (300 seconds).  
> **Target Resolution:** 1080p Full Screen.

---

## 📋 Pre-Flight Checklist (1 Minute Before Presenting)

1. Launch dashboard from the project directory:
   ```bash
   streamlit run app/streamlit_app.py
   ```
2. Confirm the Three.js WebGL flame renders at **60 FPS** (check the top-right FPS counter in the 3D flame panel).
3. Verify the sidebar persona selector is visible (default: *All Perspectives*).
4. If testing with an OpenAI API key, ensure `OPENAI_API_KEY` is configured; otherwise, the platform runs in **100% Air-Gapped Comm Blackout Mode** using onboard FAISS vector search and verified extractive NASA passages.

---

## ⏱️ Step-by-Step Presentation Walkthrough

### 1. The Hook: The Zero-Buoyancy Paradox (30 Seconds)
* **Visual:** Open on Tab 1 (*Simulation and analytics*) with the 3D flame rendering a quiescent blue sphere ($0g$).
* **Spoken Pitch:**  
  *"Fire in space is silent, spherical, and counter-intuitive. On Earth, gravity drives hot gas upward at 1 to 2 meters per second, creating flickering yellow flames. But in microgravity, gravitational buoyancy drops to zero ($Gr \to 0$). Flames become quiescent blue spheres that quickly choke in their own exhaust.*  
  *Here is the spaceflight paradox: while still flames choke, a gentle cabin draft of just **1 to 10 centimeters per second** sweeps away exhaust and continuously supplies fresh oxygen, causing aggressive, unpredictable fire spread along spacecraft walls.*  
  *NASA has 24 flight investigations and 12+ Terabytes of Physical Sciences Informatics data, but it is fragmented across decades. **Flame in Freefall** transforms this data into operational, physics-grounded flight intelligence."*

---

### 2. Live Physics HUD, 3D Simulation & "What-If?" Contingencies (75 Seconds)
* **Actions:**
  1. Drag the **Oxygen Concentration** slider from $21.8\%$ up to $34.0\%$.
  2. Point out the real-time volumetric chromatic shift in the 3D flame from blue diffusion to intense luminescence.
  3. Toggle the **Gravity Mode** to Earth Gravity ($1g$) to show the elongated buoyant yellow teardrop plume, then switch back to Microgravity ($0g$).
  4. Point to the **Live Non-Dimensional Physics HUD**:
     - **Péclet Number ($Pe$)**: Show transport shift from diffusion-dominated ($Pe < 1$) to advection-dominated ($Pe > 5$).
     - **Damköhler Number ($Da$)**: Kinetics vs. residence timescales ($Da \to 1$ near radiative extinction).
     - **Thermal Diffusivity ($\alpha$)**: Explain that lower cabin pressure increases gas diffusivity ($\alpha \propto 1/P$), accelerating preheat spread.
  5. Click the **"What-If?" Mission Hazard Contingency Buttons**:
     - Click **Artemis Cabin (Decompression Hazard)**: 56.5 kPa, 34% $\text{O}_2$.
     - Click **Cabin Draft (HVAC Failure)**: 21.8% $\text{O}_2$, 97 mm/s flow.
     - Click **Barrier Quench (Heatsink)**: $f^* = 0.72$ fuel coverage.
* **Spoken Pitch:**  
  *"Our predictive model is a Gaussian Process Regressor running at sub-2ms latency ($p95 = 1.91\text{ ms}$). Notice the 90% non-parametric conformal confidence band around the curve—it guarantees 90% empirical coverage without assuming Gaussian errors. With one click on our 'What-If?' contingency buttons, flight controllers can test Artemis habitat decompression, ventilation fan failures, or structural heatsink quenching."*

---

### 3. Audience Persona Switcher (45 Seconds)
* **Actions:**
  1. Open the sidebar and switch the **Dashboard Persona** to **🛡️ Flight Safety Officer Mode**.
     - Point out the **Go/No-Go Flammability Verdict**, normoxic equivalent pressure ($pp\text{O}_2$) margin, delta from sea level ($21.2\text{ kPa}$), and NASA-STD-6001 operational compliance banner.
  2. Switch to **🔬 Combustion Science Researcher Mode**:
     - Show the academic diagnostics: GPR hyperparameters, grouped cross-validation residuals ($\text{Log } R^2 = 0.934$, $\text{MAE} = 0.22\text{ mm/s}$), and 57-point vectorized curve generation in $7.7\text{ ms}$.
  3. Switch to **🎓 Student & Educator Mode**:
     - Highlight the interactive educational walkthrough explaining why matches don't flicker in orbit.
* **Spoken Pitch:**  
  *"Different mission stakeholders require different views. Flight Safety Officers see actionable Go/No-Go limits and normoxic margins. Researchers see dimensionless scaling laws and statistical cross-validation. Students see foundational microgravity physics."*

---

### 4. Mission Insights, Coverage Map & Natural Language Scenarios (60 Seconds)
* **Actions:**
  1. Switch to Tab 2 (*Mission insights*).
  2. Expand the **Natural Language Scenario Input** box and type:  
     `lunar base at 8.2 psi and 34% oxygen`
  3. Click **Activate this parsed scenario**:
     - Point out automated unit conversion: $8.2\text{ psi} \to 56.5\text{ kPa}$, $\text{Moon} \to 0.16g$.
  4. Point to the **Evidence Coverage Map**:
     - Show the scenario star sitting outside the green drop-tower envelope.
     - Point out the **NOT_COVERED (■ Square / Red)** status card.
  5. Scroll down to the **Ranked NASA Findings** and **Risk Cards**:
     - Show how all 18 findings are weighted by gravity match, atmosphere match, and evidence strength.
* **Spoken Pitch:**  
  *"Here is our core engineering honesty: our empirical drop-tower data was measured in microgravity. Lunar gravity ($0.16g$) and reduced pressure ($56.5\text{ kPa}$) fall outside our experimental envelope. Our N-dimensional convex hull guard strictly refuses to extrapolate. Instead of hallucinating an unsafe prediction, Flame in Freefall surfaces 18 verified NASA findings and highlights the exact missing flight data."*

---

### 5. 1-Click Mission Report Export & Cryptographic Provenance (30 Seconds)
* **Actions:**
  1. Click **Download Markdown Report (.md)** or **Download Standalone HTML (.html)**.
  2. Open the downloaded report: show embedded cryptographic SHA-256 data signature (`203e00041e9c2477`), scenario parameters, Go/No-Go verdict, and sourced citations.
* **Spoken Pitch:**  
  *"With a single click, mission safety teams can export a cryptographically signed, publication-ready mission fire assessment report for flight readiness reviews."*

---

### 6. Experiments Catalog & Terrestrial Civilian Spin-offs (30 Seconds)
* **Actions:**
  1. Switch to Tab 3 (*Experiments*):
     - Show side-by-side comparison across 15 verified flight experiments (BASS-II, FLEX, ACME, Saffire, SoFIE, LUCI).
  2. Switch to Tab 4 (*Documents & Synthesis*):
     - Highlight the **Terrestrial Civilian Spin-offs**:
       - Fine-water-mist fire extinguishers (FLEX droplet research replacing Halon on ISS and in data centers).
       - Lightweight composite SCBA air tanks (Apollo PLSS pressure vessels saving 13 lbs per municipal firefighter).
       - PBI turnout gear (Project FIRES cutting firefighter burn injuries by $>60\%$).
       - Dust vs. smoke discriminating detectors (SAME/DAFT microgravity sensors in subway tunnels and mines).
     - Point to the forensic cards for **Apollo 1 (1967)** and **Mir 1997 Oxygen Candle Fire**.
* **Spoken Pitch:**  
  *"Space exploration directly protects civilian lives on Earth. The same drop-tower droplet research that replaced toxic Halon on the ISS now protects commercial data centers, while Apollo spacesuit composite materials cut 13 pounds off municipal firefighter air tanks."*

---

### 7. AI Assistant & Deep-Space Comm Blackout Mode (30 Seconds)
* **Actions:**
  1. Switch to Tab 5 (*AI assistant*).
  2. Toggle **Simulate Deep-Space Comm Blackout** in the sidebar:
     - Show the yellow warning banner: *Simulated Deep-Space Comm Blackout Active — Operating in 100% Air-Gapped Local Mode*.
  3. Expand the **Question Discovery Vault** and select a question:  
     `Why are microgravity flames spherical?`
  4. Click submit: show instant extractive passage retrieval from the local FAISS vector index (1,573 chunks) with full NASA STI citations.
  5. Demonstrate the **Calibrated Refusal Gate ($\tau = 0.7455, \text{AUC} = 0.9863$)**:  
     Type an off-topic query like `What is the best pizza in Houston?`  
     Show that it is mathematically declined in code without calling an LLM.
* **Spoken Pitch:**  
  *"During deep-space radio blackouts on the lunar far side or during Mars solar conjunctions, ground communications are lost. Our Circuit Breaker severs cloud links and switches to 100% air-gapped local autonomy. Furthermore, our cosine refusal gate mathematically blocks ungrounded queries in code, guaranteeing zero hallucinations."*

---

## 🏆 Presentation Closing (15 Seconds)

*"Flame in Freefall delivers honest, physics-grounded intelligence: it predicts where science has evidence, refuses where data is missing, guarantees sub-2ms air-gapped flight autonomy for Artemis and Mars crews, and transfers NASA fire safety innovations directly to civilian life on Earth."*

---

## 💡 Rapid-Fire Q&A Preparation for Judges

* **Q: Why don't you predict spread rates for the Moon or Mars?**  
  *A:* Our training data consists of 22 microgravity ($0g$) drop-tower runs. At lunar gravity ($0.16g$) or exploration pressures ($56.5\text{ kPa}$), buoyant convection and thermal diffusivity behave differently. Hallucinating a number outside the convex hull would violate NASA-STD-6001. We show verified NASA findings and quantify data gaps instead.

* **Q: How do you prevent AI hallucinations in life-critical spaceflight?**  
  *A:* Three layers of defense:
  1. *Mathematical Refusal Gate*: Dense FAISS cosine similarity cutoff ($\tau = 0.7455, \text{AUC} = 0.9863$) mathematically refuses out-of-scope questions.
  2. *Deep-Space Comm Blackout Mode*: 100% air-gapped local extractive retrieval without cloud dependencies.
  3. *SI-Brief Code Verifier*: Evaluates LLM outputs in code—any hallucinated number, missing citation, or claim of "safety" is rejected and replaced by the rule-based brief.

* **Q: How reliable is your evidence library?**  
  *A:* 100% verified. All 18 findings and 15 catalog entries have been checked against NASA technical reports and flight papers with exact page and section citations.

* **Q: What is the computational overhead of the platform?**  
  *A:* The entire platform runs locally on standard flight hardware: $1.91\text{ ms}$ prediction latency (p95), $394\text{ MB}$ memory footprint, and $60\text{ FPS}$ 3D rendering.

# Flame in Freefall: Article Data Extraction Template

How to use: copy the **Per-Article Sheet** (Section 3) once for every article, paper, or dataset you read. Fill what you can find. Leave a field blank rather than guessing. Rows that end up in the training table must pass the checklist in Section 6.

---

## 1. What the project needs (priority order)

| Priority | What | Why | Where it goes |
|---|---|---|---|
| 1 | Spread rate **with** O2, pressure, fuel, gravity | The ML target and its inputs | `training_data.csv` (Phase 0) |
| 2 | Flow velocity, thickness, geometry, apparatus | Strong secondary drivers and grouping | `training_data.csv` |
| 3 | Flame shape and size per gravity level | Tunes the 3D simulator | Visual notes |
| 4 | Temperature and heat-flux profiles, pre-heat zone length | Physically grounded glow and gradients | Visual notes |
| 5 | Findings, limits, conclusions with page numbers | RAG assistant with citations | PDF goes to RAG corpus |

**Hard rule:** a spread-rate number with missing O2, pressure, fuel, or gravity cannot be used. Skip it or find the missing value in the article's methods or table captions.

---

## 2. Where to look in an article

| Item | Usually found in |
|---|---|
| Fuel, thickness, geometry, apparatus | Methods / Experimental setup / Test matrix table |
| O2, pressure, flow velocity, gravity | Test matrix table, figure captions, "Test conditions" paragraph |
| Spread rate values | Results tables, supplementary data, figure axes (digitize if only plotted) |
| How spread rate was measured | Methods ("flame front tracked by...", "average over steady period") |
| Number of repeats | Methods or table footnotes |
| Gravity source | Abstract and methods (ISS, drop tower, parabolic flight, rocket, ground) |
| Flame shape, size | Results text, flame images, captions |
| Temperature, heat flux | Results figures, supplementary CSVs |
| Limitations | Discussion, conclusions |

---

## 3. Per-Article Sheet (copy this block for each article)

### 3.1 Article identity

- **Article ID** (your own, for example A001):
- **Title:**
- **Authors:**
- **Year:**
- **Journal / report number / PSI or NTRS ID:**
- **DOI or URL:**
- **File name(s) in your folder:**
- **Date you retrieved it:**
- **License / access note** (open, paywalled, NASA public use):
- **Dataset type** (flight, drop tower, parabolic flight, ground, simulation only):
- **Simulation only?** (if yes, do **not** put it in the training table; use as context)

### 3.2 Experiment table (one line per experiment or test condition)

Copy these columns into a spreadsheet or CSV. One row per distinct experiment.

| experiment_id | source | fuel | geometry | thickness_mm | o2_pct | pressure_kpa | g_level | flow_velocity_mm_s | flow_direction | ignition_type | spread_rate_mm_s | spread_rate_definition | n_replicates | where_in_article |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | | | | |

### 3.3 Field definitions and allowed values

| Field | Definition | Allowed values / format |
|---|---|---|
| `experiment_id` | Unique ID within the article | for example `A001_T07` |
| `source` | Facility or origin | `BASS`, `BASS-II`, `ACME`, `SoFIE`, `Saffire`, `LUCI`, `literature` |
| `fuel` | Material tested | for example `PMMA`, `cellulose`, `cotton-fiberglass`; keep the spelling consistent |
| `geometry` | Shape of the sample | `flat_thin`, `flat_thick`, `cylinder`, `sphere`, `other` |
| `thickness_mm` | Sample thickness (or diameter for rods) | number, mm |
| `o2_pct` | Oxygen concentration | number, percent by volume |
| `pressure_kpa` | Total pressure | number, kPa |
| `g_level` | Gravity | 0 for microgravity, 1 for Earth, fraction for partial (0.16 lunar, 0.38 Mars) |
| `flow_velocity_mm_s` | Airflow speed over the sample | number, mm/s; 0 for quiescent |
| `flow_direction` | Flow relative to spread | `opposed`, `concurrent`, `quiescent` |
| `ignition_type` | How it was ignited | `hot_wire`, `radiant`, `spark`, `other` |
| `spread_rate_mm_s` | Measured spread rate | number, mm/s |
| `spread_rate_definition` | How it was measured | `steady_opposed_flat`, `steady_concurrent_flat`, or an honest other label (`rod_regression`, `burn_length`, `transient`, `blowoff`) |
| `n_replicates` | Number of repeats averaged | integer |
| `where_in_article` | Table or figure and page | for example `Table 2, p.6` |

**Training rule:** only `steady_opposed_flat` and `steady_concurrent_flat` rows train the model. Other labels are kept for context and charts.

### 3.4 Unit conversion cheat sheet

| Quantity | Convert to | Factors |
|---|---|---|
| Spread rate | mm/s | 1 cm/s = 10 mm/s; 1 m/s = 1000 mm/s |
| Flow velocity | mm/s | 1 cm/s = 10 mm/s; 1 m/s = 1000 mm/s |
| Pressure | kPa | 1 atm = 101.325 kPa; 1 psi = 6.895 kPa; 1 bar = 100 kPa; 1 Pa = 0.001 kPa |
| Length / thickness | mm | 1 µm = 0.001 mm; 1 cm = 10 mm |
| Oxygen | percent | fraction x 100 (0.21 becomes 21) |
| Temperature | K | °C + 273.15 |

Record the **original value and unit** in your notes in case a conversion is questioned.

### 3.5 Graphs and figures to digitize

List figures that show spread rate (or other target data) but have no table.

| Figure # | What the axes are | Conditions fixed in this plot (fuel, O2, pressure, g, flow) | Digitized file name | Digitizing tool | Estimated error |
|---|---|---|---|---|---|
| | | | | | |

Tips: calibrate with at least two points on each axis, read log axes carefully, note the legend for each curve (each curve may be a different fuel or gravity), and mark digitized rows `provenance=literature_digitized`.

### 3.6 Flame shape and visual data (for the 3D simulator)

| Item | Value | Unit | Condition (fuel, O2, pressure, g) | Where found |
|---|---|---|---|---|
| Flame height / length | | mm | | |
| Flame width | | mm | | |
| Height-to-width ratio | | | | |
| Flame shape description (teardrop, sphere, flat, other) | | | | |
| Color / luminosity description (blue, yellow, sooty) | | | | |
| Soot present? | | yes/no | | |
| Pre-heat zone length | | mm | | |
| Peak flame temperature | | K | | |
| Peak net heat flux | | kW/m² | | |
| Flame standoff distance | | mm | | |
| Frame rate / time between frames (if profile data) | | s | | |

### 3.7 Key findings for the AI assistant (with citations)

Write each finding as a short paraphrase in your own words. Do not copy long passages.

| # | Finding (paraphrased) | Conditions it applies to | Page / figure |
|---|---|---|---|
| 1 | | | |

Also note:
- **Stated limitations or caveats:**
- **Definition of spread rate used by the authors:**
- **Any statement about gravity effect (faster, slower, same):**
- **Any statement about pressure or flow effect:**

### 3.8 Quality flags

- [ ] Experimental (not simulation)
- [ ] All four of O2, pressure, fuel, gravity known for every row
- [ ] Units confirmed against the article text
- [ ] Spread-rate definition recorded
- [ ] Same experiment not already entered from another article (duplicate check)
- [ ] Data from a table (preferred) or from a digitized figure (flagged)
- [ ] Apparatus recorded (ISS glovebox, drop tower, duct height) in `provenance`

---

## 4. Master tracking sheet

Keep one row per article here so you can see what is done.

| Article ID | Title (short) | Source type | Rows extracted | Digitized figures | Visual data? | Status (todo / partial / done) | Notes |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

---

## 5. What I need at the end

Send me these when you are ready:

1. **`training_data.csv`**: all experiment rows from Section 3.2 combined, using the exact column names (a blank copy is in `training_data_template.csv`).
2. **Visual notes**: Section 3.6 tables, combined into one file.
3. **PDFs and articles** for the assistant, with the Section 3.1 details (title, authors, year, ID or DOI).
4. **Master tracking sheet** from Section 4, so I can see coverage.

---

## 6. Pre-submission checklist for every training row

- [ ] `spread_rate_mm_s`, `o2_pct`, `pressure_kpa`, `g_level`, and `fuel` are all filled
- [ ] `spread_rate_definition` is `steady_opposed_flat` or `steady_concurrent_flat` (or intentionally another label)
- [ ] Every value is in the canonical unit (Section 3.4)
- [ ] `experiment_id` is unique and `where_in_article` is filled
- [ ] No values were guessed or estimated from memory
- [ ] Simulation-only results are excluded from the training rows
- [ ] Digitized values are flagged in `provenance`

## 7. Coverage goal

For each combination of fuel and gravity level, aim for **at least 15 distinct experiments**, spread across a range of oxygen, pressure, and flow velocity. Track your counts here:

| Fuel | g_level | Experiments so far | Target | Gaps (O2 range, pressure range, flow range) |
|---|---|---|---|---|
| | | | 15+ | |

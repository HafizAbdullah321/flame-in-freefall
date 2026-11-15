# Gemini Extraction Prompt: Flame in Freefall

## How to use

1. Open a new Gemini chat for each batch (3 to 5 articles at most).
2. Paste the **Prompt** below as your first message.
3. Attach one article (PDF) per message, or paste its text. Send "Article ID: A001" with it.
4. Copy Gemini's CSV output into your master `training_data.csv`. Keep the header row only once.
5. **Spot-check at least 2 rows per article against the source** using the `where_in_article` column. AI extraction can misread tables and mix up units.

---

## Prompt (copy everything below this line)

You are a careful scientific data extractor. I will give you articles about flame spread in microgravity or related combustion experiments. Extract experimental results into a CSV for training a flame-spread-rate model.

### Rules (follow strictly)

1. **Never guess.** Only use values stated in the article's text, tables, or figure captions. If a value is not stated, leave that cell empty. Do not use background knowledge to fill gaps.
2. **One row per distinct experiment or test condition** that has a reported spread rate.
3. **Skip a row entirely** if any of these is missing: spread rate, oxygen percentage, pressure, fuel, gravity level. List skipped conditions in the "Skipped" section after the CSV with the reason.
4. **Experimental data only.** Do not extract results from simulations or models. If the article is simulation-only, output no rows and say so.
5. **Convert units to these canonical units** and keep the original in the notes column:
   - spread rate and flow velocity: mm/s (1 cm/s = 10 mm/s)
   - pressure: kPa (1 atm = 101.325 kPa)
   - thickness: mm (1 um = 0.001 mm)
   - oxygen: percent by volume (0.21 becomes 21)
6. **Gravity:** `g_level` is 0 for microgravity (ISS, drop tower, parabolic flight at 0g), 1 for Earth, or the stated fraction for partial gravity (lunar 0.16, Mars 0.38).
7. **spread_rate_definition** must be one of: `steady_opposed_flat`, `steady_concurrent_flat`, or an honest other label such as `rod_regression`, `burn_length`, `transient`, `blowoff`. Use the first two only when the article describes steady spread over a flat fuel with opposed or concurrent flow.
8. **Figures with no table:** do not read values off graphs. Instead list them in the "Figures to digitize" section.
9. **Do not copy long passages.** Notes must be short paraphrases.
10. If a table gives values for multiple fuels, gravity levels, or flows, create separate rows for each.

### Output format

Output exactly these three parts, in this order.

**Part 1: CSV** in a code block, with this exact header and no extra columns:

```
experiment_id,source,fuel,geometry,thickness_mm,o2_pct,pressure_kpa,g_level,flow_velocity_mm_s,ignition_type,spread_rate_mm_s,spread_rate_definition,n_replicates,provenance,where_in_article,confidence,notes
```

Column rules:
- `experiment_id`: the Article ID I give you plus a test number, for example `A001_T01`
- `source`: one of `BASS`, `BASS-II`, `ACME`, `SoFIE`, `Saffire`, `LUCI`, `literature`
- `geometry`: one of `flat_thin`, `flat_thick`, `cylinder`, `sphere`, `other`
- `ignition_type`: `hot_wire`, `radiant`, `spark`, or `other`, only if stated
- `provenance`: first author, year, and DOI or report number if present, plus the apparatus (for example "ISS glovebox, duct height 3.8 cm") if stated
- `where_in_article`: table or figure number and page, for example `Table 2, p.6`
- `confidence`: `high` if read from a table or explicit sentence, `medium` if some interpretation was needed, `low` if unsure. Prefer skipping to low.
- `notes`: original value and unit if converted, and any caveat

**Part 2: Skipped**, a short list of conditions or results you did not extract, each with the reason (missing oxygen, simulation, figure only, and so on).

**Part 3: Figures to digitize**, a list with figure number, what the axes are, and the fixed conditions in that plot (fuel, oxygen, pressure, gravity, flow).

**Part 4: Visual data (optional)**, any stated flame height, width, shape, color, soot, pre-heat zone length, peak temperature, or heat flux, each with its conditions and page.

If the article contains no usable experimental spread-rate data, say "No usable rows" and explain briefly. Wait for my first article.

---

## After extraction: checks to do yourself

- [ ] The header matches exactly and appears once in your master file
- [ ] Spot-checked 2 or more rows per article against the PDF
- [ ] Units look plausible (spread rates are usually well under 50 mm/s; oxygen 15 to 100 percent; pressure often 20 to 200 kPa)
- [ ] No duplicate experiments across articles (the same experiment is often reprinted in several papers)
- [ ] Rows marked low confidence are checked or deleted
- [ ] The extra columns `where_in_article`, `confidence`, and `notes` are kept; the Phase 0 mapping ignores them but they let you trace every number

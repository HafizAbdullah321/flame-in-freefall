"""Guided human verification of findings and catalog entries. Nothing is marked verified without an explicit 'y' from a person."""
import csv, datetime as dt, re, shutil
from pathlib import Path
from .catalog import load_catalog, validate_catalog

HERE = Path(__file__).parent
def _read(path):
    with open(path, newline="", encoding="utf-8") as f: r = csv.DictReader(f); return r.fieldnames, list(r)
def _write(path, fields, rows):
    shutil.copyfile(path, str(path) + ".bak")
    with open(path, "w", newline="", encoding="utf-8") as f: w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def _numbers(text): return sorted(set(re.findall(r"\d+(?:\.\d+)?", text)), key=lambda x: (len(x), x))

def verify_findings(path=None, ask=input, say=print, today=dt.date.today):
    path = Path(path or HERE / "findings_seed.csv"); fields, rows = _read(path); todo = [r for r in rows if r["verified"] != "yes"]
    say(f"{len(todo)} findings to check. For each: open the link, find the passage, compare.\n"); changed = 0
    for n, r in enumerate(list(todo), 1):
        say(f"--- {n}/{len(todo)}  {r['id']}  ({r['evidence']}, gravity {r['gravity']})\nCLAIM: {r['finding']}\nSOURCE: {r['source_title']}\nLINK: {r['source_url']}\nSEARCH THE SOURCE FOR: {', '.join(_numbers(r['finding'])) or 'key words'} and the main nouns of the claim")
        while True:
            a = ask("[y] matches the source  [e] edit wording  [n] cannot confirm  [d] delete  [s] skip  [q] save and quit > ").strip().lower()
            if a in ("y", "e", "n", "d", "s", "q"): break
        if a == "q": break
        if a == "s": continue
        if a == "d":
            if ask("Delete this finding? type DELETE to confirm > ").strip() == "DELETE": rows.remove(r); changed += 1
            continue
        if a == "n":
            r["note"] = (r["note"] + f" Checked {today()}: could not confirm in the source.").strip(); changed += 1; continue
        if a == "e":
            new = ask("Corrected wording (one line, at most 40 words; no long quotes) > ").strip()
            if not new or len(new.split()) > 40: say("Not changed: empty or over 40 words."); continue
            r["finding"] = new
            if ask("Does the corrected wording match the source exactly in meaning? [y/n] > ").strip().lower() != "y": changed += 1; continue
        page = ask("Page or section where you found it (optional) > ").strip()
        r["verified"], r["verified_on"], r["source_page"] = "yes", str(today()), page or r.get("source_page", ""); changed += 1
    if changed: _write(path, fields, rows); say(f"\nSaved {changed} change(s). Backup: {path}.bak")
    else: say("\nNo changes.")
    return changed

def verify_catalog(path=None, ask=input, say=print, today=dt.date.today):
    path = Path(path or HERE / "experiments_catalog.csv"); fields, rows = _read(path); todo = [r for r in rows if r["verified"] != "yes"]
    say(f"{len(todo)} catalog entries to check.\n"); touched = set(); backup = [dict(r) for r in rows]
    for n, r in enumerate(list(todo), 1):
        say(f"--- {n}/{len(todo)}  {r['id']}  {r['name']}\nLINK: {r['source_url']}")
        for k in ("type", "status", "gravity_g_min", "gravity_g_max", "duration_s", "o2_min", "o2_max", "pressure_kpa_min", "pressure_kpa_max", "fuels", "geometry", "flow_cm_s_min", "flow_cm_s_max", "measurements", "key_result"):
            say(f"  {k}: {r[k] if r[k] != '' else '(blank = not recorded)'}")
        say(f"  NOTE: {r['note']}")
        while True:
            a = ask("[y] all fields match the source (blank means 'not stated')  [e] edit a field  [n] cannot confirm  [d] delete  [s] skip  [q] save and quit > ").strip().lower()
            if a in ("y", "e", "n", "d", "s", "q"): break
        if a == "q": break
        if a == "s": continue
        if a == "d":
            if ask("type DELETE to confirm > ").strip() == "DELETE": rows.remove(r); touched.add(r['id'])
            continue
        if a == "n": r["note"] = (r["note"] + f" Checked {today()}: could not confirm.").strip(); touched.add(r["id"]); continue
        if a == "e":
            f = ask("Field name > ").strip(); 
            if f not in r or f in ("id", "verified"): say("Unknown or protected field."); continue
            r[f] = ask(f"New value for {f} (empty = blank) > ").strip(); touched.add(r["id"])
            if ask("Now matches the source for every field? [y/n] > ").strip().lower() != "y": continue
        r["verified"] = "yes"; r["note"] = (r["note"] + f" Verified {today()}.").strip(); touched.add(r["id"])
    changed = len(touched)
    if changed:
        errs = validate_catalog(load_catalog_from_rows(rows))
        if errs: say("Not saved. Problems found:\n  " + "\n  ".join(errs)); rows[:] = backup; return 0
        _write(path, fields, rows); say(f"\nSaved {changed} change(s). Backup: {path}.bak")
    else: say("\nNo changes.")
    return changed

def load_catalog_from_rows(rows):
    import tempfile, os
    fd, tmp = tempfile.mkstemp(suffix=".csv"); os.close(fd)
    with open(tmp, "w", newline="", encoding="utf-8") as f: w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    try: return load_catalog(tmp)
    finally: os.remove(tmp)

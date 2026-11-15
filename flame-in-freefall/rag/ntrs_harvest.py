"""Harvest NASA NTRS full text for the RAG corpus, following the NTRS OpenAPI terms.

  python ntrs_harvest.py harvest --query "flame spread microgravity" --max 200
  python ntrs_harvest.py sync        # run at least weekly: removes withdrawn documents

Rules from the NTRS documentation, enforced here:
  * rate limit 500 requests / 15 min  -> we sleep >= 2 s between calls and back off on 429
  * max 100 results per page, 10,000 records per query
  * redistributions must be checked weekly; withdrawn docs/records must be deleted locally
  * cite the record URL (ntrs.nasa.gov/citations/{id}), not a copied full-text link
  * only documents flagged DOCUMENT_AND_METADATA / PUBLIC are downloaded; records whose
    copyright determination is not PUBLIC_USE_PERMITTED are listed for manual review, not downloaded
"""
import argparse, json, time, datetime as dt
from pathlib import Path
import requests

BASE = "https://ntrs.nasa.gov"
API = BASE + "/api"
MIN_INTERVAL = 2.0          # 450 requests / 15 min, under the 500 limit
_last = [0.0]

def _req(method, url, **kw):
    for attempt in range(5):
        wait = MIN_INTERVAL - (time.time() - _last[0])
        if wait > 0: time.sleep(wait)
        _last[0] = time.time()
        r = requests.request(method, url, timeout=60, **kw)
        if r.status_code == 429:
            time.sleep(30 * (attempt + 1)); continue
        r.raise_for_status()
        return r
    raise RuntimeError("Rate limited repeatedly; wait 15 minutes and retry.")

def search(query, max_records=200, extra=None):
    out, offset = [], 0
    while len(out) < max_records:
        body = {"q": query, "disseminated": "DOCUMENT_AND_METADATA",
                "page": {"size": min(100, max_records - len(out)), "from": offset}}
        body.update(extra or {})
        res = _req("POST", f"{API}/citations/search", json=body).json().get("results", [])
        if not res: break
        out += res; offset += len(res)
    return out

def meta_row(rec, local_file, review):
    return {"id": rec["id"], "title": rec.get("title"), "abstract": rec.get("abstract"),
            "authors": [a.get("meta", {}).get("author", {}).get("name") for a in rec.get("authorAffiliations", [])],
            "sti_type": rec.get("stiType"), "center": (rec.get("center") or {}).get("name"),
            "citation_url": f"{BASE}/citations/{rec['id']}",
            "copyright": rec.get("copyright"), "review_copyright": review,
            "local_file": local_file, "retrieved_at": dt.datetime.utcnow().isoformat() + "Z"}

def pick_download(rec):
    for d in rec.get("downloads", []):
        links = d.get("links", {})
        if "fulltext" in links: return links["fulltext"]      # plain text: no PDF parsing needed
        if "pdf" in links: return links["pdf"]
    return None

def load_manifest(root):
    p = root / "manifest.jsonl"
    return {json.loads(l)["id"]: json.loads(l) for l in p.read_text().splitlines()} if p.exists() else {}

def save_manifest(root, m):
    (root / "manifest.jsonl").write_text("\n".join(json.dumps(v) for v in m.values()))

def harvest(query, root, max_records):
    (root / "docs").mkdir(parents=True, exist_ok=True)
    man = load_manifest(root)
    for rec in search(query, max_records):
        rid = rec["id"]
        if rid in man or rec.get("distribution") != "PUBLIC": continue
        permitted = (rec.get("copyright") or {}).get("determinationType") == "PUBLIC_USE_PERMITTED"
        link = pick_download(rec) if (rec.get("downloadsAvailable") and permitted) else None
        local = None
        if link:
            r = _req("GET", BASE + link)
            local = f"docs/{rid}{Path(link).suffix or '.txt'}"
            (root / local).write_bytes(r.content)
        man[rid] = meta_row(rec, local, review=not permitted)
        print(rid, "downloaded" if local else "metadata only", "| review copyright" if not permitted else "")
    save_manifest(root, man)

def sync(root):
    """Apply the Redistributions endpoint: delete anything NASA withdrew."""
    st = root / "state.json"
    since = json.loads(st.read_text())["last_sync"] if st.exists() else "2021"
    man, offset, removed = load_manifest(root), 0, 0
    while True:
        items = _req("GET", f"{API}/citations/redistributions",
                     params={"redistributedDate.gt": since, "page.size": 100, "page.from": offset}).json()
        items = items.get("results", items) if isinstance(items, dict) else items
        if not items: break
        for it in items:
            rid = it["id"]
            if rid not in man: continue
            gone_all = it["disseminated"] == "NONE" or it["distribution"] == "DO_NOT_DISTRIBUTE"
            if gone_all or it["disseminated"] == "METADATA_ONLY":
                f = man[rid].get("local_file")
                if f and (root / f).exists(): (root / f).unlink()
                man[rid]["local_file"] = None
                if gone_all: del man[rid]
                removed += 1
        offset += len(items)
    save_manifest(root, man)
    st.write_text(json.dumps({"last_sync": dt.date.today().isoformat()}))
    print(f"sync done, {removed} records affected")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["harvest", "sync"]); ap.add_argument("--query")
    ap.add_argument("--max", type=int, default=200); ap.add_argument("--root", default="corpus")
    a = ap.parse_args(); root = Path(a.root); root.mkdir(exist_ok=True)
    harvest(a.query, root, a.max) if a.cmd == "harvest" else sync(root)

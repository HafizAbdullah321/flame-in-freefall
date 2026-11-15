"""Tests for the guided verification tool with scripted answers (never touches the real files). Run: python -m insights.tests.test_verify"""
import csv, datetime as dt, shutil, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from insights.verify import verify_findings, verify_catalog
from insights.findings import load_findings
from insights.catalog import load_catalog, validate_catalog

def script(*answers):
    it = iter(answers); return lambda prompt="": next(it)

def test_all():
    tmp = Path(tempfile.mkdtemp()); f = tmp / "f.csv"; shutil.copy(ROOT / "insights/findings_seed.csv", f); day = lambda: dt.date(2026, 10, 22)
    before = {r["id"]: r for r in load_findings(f)}; todo = [i for i, r in before.items() if r["verified"] != "yes"]; assert len(todo) == 13
    # y, e (then confirm), n, d (typed DELETE), s, q
    out = []; n = verify_findings(f, script("y", "p. 6, Table 2", "e", "Corrected wording of the claim.", "y", "section 3", "n", "d", "DELETE", "s", "q"), out.append, day)
    after = {r["id"]: r for r in load_findings(f)}
    a, b, c, d_, e_ = todo[:5]
    assert after[a]["verified"] == "yes" and after[a]["verified_on"] == "2026-10-22" and after[a]["source_page"] == "p. 6, Table 2"
    assert after[b]["finding"] == "Corrected wording of the claim." and after[b]["verified"] == "yes" and after[b]["source_page"] == "section 3"
    assert after[c]["verified"] == "no" and "could not confirm" in after[c]["note"]
    assert d_ not in after and len(after) == len(before) - 1                                   # deleted
    assert after[e_]["verified"] == "no" and after[e_]["finding"] == before[e_]["finding"]     # skipped: untouched
    assert n == 4 and Path(str(f) + ".bak").exists() and any("SEARCH THE SOURCE FOR" in x for x in out)
    already = {i for i, r in before.items() if r["verified"] == "yes"}; assert all(after[i]["verified"] == "yes" and after[i]["finding"] == before[i]["finding"] for i in already)
    # a too-long edit is refused and nothing is marked verified
    g = tmp / "g.csv"; shutil.copy(ROOT / "insights/findings_seed.csv", g)
    verify_findings(g, script("e", " ".join(["word"] * 41), "q"), lambda *_: None, day); assert sum(r["verified"] == "yes" for r in load_findings(g)) == 3
    # no changes -> file untouched, no backup
    h = tmp / "h.csv"; shutil.copy(ROOT / "insights/findings_seed.csv", h); assert verify_findings(h, script("q"), lambda *_: None, day) == 0 and not Path(str(h) + ".bak").exists()
    # catalog: verify one, edit one, reject an invalid edit
    c1 = tmp / "c.csv"; shutil.copy(ROOT / "insights/experiments_catalog.csv", c1); cb = {r["id"]: r for r in load_catalog(c1)}
    ids = [i for i, r in cb.items() if r["verified"] != "yes"]; assert len(ids) == 9
    n = verify_catalog(c1, script("y", "e", "fuels", "PMMA, edited", "y", "q"), lambda *_: None, day); ca = {r["id"]: r for r in load_catalog(c1)}
    assert n == 2 and ca[ids[0]]["verified"] == "yes" and ca[ids[1]]["fuels"] == "PMMA, edited" and ca[ids[1]]["verified"] == "yes" and validate_catalog(list(ca.values())) == []
    c2 = tmp / "c2.csv"; shutil.copy(ROOT / "insights/experiments_catalog.csv", c2); orig = c2.read_text()
    out = []; n = verify_catalog(c2, script("e", "source_url", "http://not-https", "y", "q"), out.append, day)
    assert n == 0 and c2.read_text() == orig and any("https" in x for x in out), "invalid edits must not be saved"
    print("VERIFY TOOL TESTS PASSED | findings: verify/edit/cannot-confirm/delete/skip/quit; catalog: verify/edit/invalid edit refused; real files untouched")

if __name__ == "__main__":
    test_all()

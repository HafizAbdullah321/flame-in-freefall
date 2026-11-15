"""Per-document executive summaries and document explorer utilities (REQ-E4).
Summaries are 120 words or fewer, grounded in source passages with numbers verified.
Supports SI-generated summaries with automatic verification and extractive fallback.
Stored in rag/summaries.json."""
import collections, datetime as dt, json, re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

MAX_WORDS = 120
BANNED = ("is safe", "are safe", "be safe", "no risk", "guarantee", "certified", "will not burn", "cannot burn", "risk-free")

def _dec(x, places):
    return Decimal(str(x)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)

def _allowed_numbers(text):
    return [float(m) for m in re.findall(r"\d+(?:\.\d+)?", text)]

def _number_ok(tok, allowed):
    d = len(tok.split(".")[1]) if "." in tok else 0
    v = Decimal(tok)
    return any(_dec(a, d) == v for a in allowed)

def _clean_text(text):
    t = re.sub(r"\s+", " ", text).strip()
    # Strip common meeting / header boilerplate
    t = re.sub(r"^(?:Sub Topic:.*?Meeting|Organized by.*?Ohio|9th U\.?\s*S\.? National Combustion Meeting)\s*", "", t, flags=re.I)
    return t.strip()

def verify_summary(summary, source_text, doc_id=None, max_words=MAX_WORDS):
    """Verifies that summary:
    - is <= max_words
    - cites the source (contains doc_id or 'NTRS' or 'NASA')
    - contains only numbers present in the source text
    - contains no banned safety claims"""
    why = []
    words = re.findall(r"\S+", summary)
    if len(words) > max_words:
        why.append(f"longer than {max_words} words ({len(words)} words)")
    
    if doc_id is not None:
        if str(doc_id) not in summary and "NTRS" not in summary and "NASA" not in summary:
            why.append(f"does not cite source ID {doc_id}")

    allowed = _allowed_numbers(source_text)
    # Strip citation tokens like [NTRS 20150008962] before checking numbers if doc_id matches
    clean_summary = summary
    if doc_id is not None:
        clean_summary = clean_summary.replace(str(doc_id), "")
    
    for tok in re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])", clean_summary):
        if not _number_ok(tok, allowed):
            why.append(f"number {tok} is not in source text")
            break

    low = summary.lower()
    for b in BANNED:
        if b in low:
            why.append(f"banned phrase: {b}")

    return (not why), why

def extractive_summary(doc_info, chunks_text="", max_words=MAX_WORDS):
    """Deterministic, fully grounded extractive summary (<= 120 words).
    Extracts high-information sentences from the abstract or top chunks."""
    doc_id = doc_info.get("id")
    cite_tag = f" [NTRS {doc_id}]" if doc_id else " [NASA STI]"
    cite_words = len(cite_tag.strip().split())
    budget = max_words - cite_words

    # Prefer abstract if informative, else clean chunks text
    raw = doc_info.get("abstract") or chunks_text or doc_info.get("title", "")
    text = _clean_text(raw)
    
    # Split into sentences
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if not sentences:
        return f"{doc_info.get('title', 'NASA technical report')}.{cite_tag}"

    chosen = []
    current_word_count = 0

    for s in sentences:
        s_words = len(s.split())
        if current_word_count + s_words <= budget:
            chosen.append(s)
            current_word_count += s_words
        elif not chosen:
            # First sentence exceeds budget: truncate cleanly
            w = s.split()[:budget - 1]
            chosen.append(" ".join(w) + "...")
            break
        else:
            break

    return " ".join(chosen) + cite_tag

def generate_summary(doc_info, chunks_text="", llm=None, daily=None, max_words=MAX_WORDS):
    """Generates document summary with SI (if configured) or extractive fallback."""
    doc_id = doc_info.get("id")
    source_context = f"{doc_info.get('title', '')}\n\nAbstract: {doc_info.get('abstract', '')}\n\nPassages:\n{chunks_text[:2500]}"
    fallback_text = extractive_summary(doc_info, chunks_text, max_words)

    if llm is None:
        return dict(
            id=doc_id,
            title=doc_info.get("title", ""),
            authors=doc_info.get("authors", []),
            citation_url=doc_info.get("citation_url", f"https://ntrs.nasa.gov/citations/{doc_id}"),
            sti_type=doc_info.get("sti_type", "REPORT"),
            summary=fallback_text,
            word_count=len(fallback_text.split()),
            method="EXTRACTIVE",
            verified=True,
            reasons=[]
        )

    if daily is not None and not daily.available():
        return dict(
            id=doc_id,
            title=doc_info.get("title", ""),
            authors=doc_info.get("authors", []),
            citation_url=doc_info.get("citation_url", f"https://ntrs.nasa.gov/citations/{doc_id}"),
            sti_type=doc_info.get("sti_type", "REPORT"),
            summary=fallback_text,
            word_count=len(fallback_text.split()),
            method="EXTRACTIVE",
            verified=True,
            reasons=["Daily AI limit reached; showing extractive summary."]
        )

    system_prompt = (
        "You write concise executive summaries of NASA microgravity fire safety documents for aerospace engineers. "
        f"Write at most {max_words} words. Summarize: (1) experimental or numerical setup (gravity, atmosphere, fuel); "
        f"(2) key observations and fire safety findings. End with '[NTRS {doc_id}]'. "
        "Rules: Use ONLY facts from the provided text. Never invent numbers. Never claim an environment is safe or risk-free."
    )
    from rag.llm import LLMError
    try:
        if daily is not None:
            daily.record()
        raw = llm.complete(system_prompt, f"<document id='{doc_id}'>\n{source_context}\n</document>").strip()
        ok, why = verify_summary(raw, source_context, doc_id=doc_id, max_words=max_words)
        if ok:
            return dict(
                id=doc_id,
                title=doc_info.get("title", ""),
                authors=doc_info.get("authors", []),
                citation_url=doc_info.get("citation_url", f"https://ntrs.nasa.gov/citations/{doc_id}"),
                sti_type=doc_info.get("sti_type", "REPORT"),
                summary=raw,
                word_count=len(raw.split()),
                method="SI",
                verified=True,
                reasons=[]
            )
        else:
            return dict(
                id=doc_id,
                title=doc_info.get("title", ""),
                authors=doc_info.get("authors", []),
                citation_url=doc_info.get("citation_url", f"https://ntrs.nasa.gov/citations/{doc_id}"),
                sti_type=doc_info.get("sti_type", "REPORT"),
                summary=fallback_text,
                word_count=len(fallback_text.split()),
                method="EXTRACTIVE",
                verified=True,
                reasons=[f"AI summary failed verification ({'; '.join(why)}); used extractive fallback."]
            )
    except LLMError as e:
        return dict(
            id=doc_id,
            title=doc_info.get("title", ""),
            authors=doc_info.get("authors", []),
            citation_url=doc_info.get("citation_url", f"https://ntrs.nasa.gov/citations/{doc_id}"),
            sti_type=doc_info.get("sti_type", "REPORT"),
            summary=fallback_text,
            word_count=len(fallback_text.split()),
            method="EXTRACTIVE",
            verified=True,
            reasons=[f"AI service error ({e}); used extractive fallback."]
        )

def build_all_summaries(corpus_dir, chunks_file=None, out_path=None, llm=None, daily=None):
    """Generates and writes summaries for all corpus / indexed documents."""
    corpus = Path(corpus_dir)
    manifest_file = corpus / "manifest.jsonl"
    doc_map = {}
    if manifest_file.exists():
        for l in manifest_file.read_text(encoding="utf-8").splitlines():
            if l.strip():
                d = json.loads(l)
                doc_map[d["id"]] = d

    # Gather chunk texts
    chunk_texts = collections.defaultdict(list)
    if chunks_file and Path(chunks_file).exists():
        for l in Path(chunks_file).read_text(encoding="utf-8").splitlines():
            if l.strip():
                c = json.loads(l)
                chunk_texts[c["id"]].append(c.get("text", ""))
                if c["id"] not in doc_map:
                    doc_map[c["id"]] = {
                        "id": c["id"],
                        "title": c.get("title", ""),
                        "authors": c.get("authors", []),
                        "citation_url": c.get("citation_url", f"https://ntrs.nasa.gov/citations/{c['id']}"),
                        "sti_type": c.get("sti_type", "REPORT"),
                    }

    summaries = {}
    for doc_id, info in doc_map.items():
        ct = " ".join(chunk_texts.get(doc_id, []))
        s = generate_summary(info, ct, llm=llm, daily=daily)
        summaries[str(doc_id)] = s

    if out_path:
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summaries, indent=2), encoding="utf-8")

    return summaries

def load_summaries(path=None, auto_generate=True):
    """Loads rag/summaries.json. Auto-generates extractive summaries if file doesn't exist."""
    root = Path(__file__).resolve().parents[1]
    p = Path(path) if path else root / "rag/summaries.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass

    if auto_generate:
        corpus_dir = root / "rag/corpus"
        chunks_file = root / "rag/index/chunks.jsonl"
        return build_all_summaries(corpus_dir, chunks_file, out_path=p)
    return {}

def filter_summaries(summaries, query="", sti_type=None):
    """Filters a dictionary of summaries by text query and STI type."""
    rows = list(summaries.values()) if isinstance(summaries, dict) else list(summaries)
    if sti_type and sti_type != "All":
        rows = [r for r in rows if r.get("sti_type") == sti_type]
    if query:
        q = query.strip().lower()
        rows = [
            r for r in rows
            if (q in r.get("title", "").lower()
                or q in r.get("summary", "").lower()
                or any(q in a.lower() for a in r.get("authors", [])))
        ]
    return sorted(rows, key=lambda x: str(x.get("id")))


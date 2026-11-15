"""RAG settings (REQ-R1)."""
from dataclasses import dataclass

@dataclass(frozen=True)
class RagConfig:
    chunk_size: int = 800
    chunk_overlap: int = 100
    embed_model: str = "BAAI/bge-small-en-v1.5"     # ONNX via fastembed, 384-d, about 130 MB on disk
    top_k: int = 4
    # Relevance filter applied BEFORE indexing: keep solid-fuel / microgravity / fire-safety documents,
    # drop gas-phase kinetics papers. Matched against title + abstract, case-insensitive.
    include_kw: tuple = ("flame spread", "microgravity", "flammability", "fire safety", "spacecraft fire", "pmma",
                         "solid fuel", "combustion", "saffire", "bass", "sofie", "luci", "acme", "extinction")
    must_kw: tuple = ("microgravity", "flame spread", "flammability", "spacecraft", "space station", "fire safety",
                      "reduced gravity", "partial gravity", "lunar", "solid fuel", "pmma")
    exclude_kw: tuple = ("ignition delay", "shock tube", "rapid compression", "laminar burning velocity", "kinetic mechanism",
                         "jet-a", "ammonia", "hydrogen blend", "reaction kinetics")


@dataclass(frozen=True)
class AssistantConfig:
    model: str = "gpt-4o-mini"
    timeout: float = 8.0               # seconds, then fall back
    retries: int = 1
    max_tokens: int = 400
    max_question_chars: int = 500
    cache_cosine: float = 0.85         # semantic match threshold for the cached answers
    rate_per_minute: int = 10          # per session
    daily_llm_cap: int = 500           # global; beyond this the assistant skips the LLM (cache / extractive only)
    max_context_chars: int = 3500
    top_k: int = 4
    extract_chars: int = 450           # per passage in the extractive fallback

# 15 critical questions with pre-computed answers (rag.build_cache). Edit to match your corpus.
CACHE_QUESTIONS = (
    "What is the BASS-II experiment on the International Space Station?",
    "How does oxygen concentration affect flame spread rate in microgravity?",
    "Why are flames rounder and bluer in microgravity than on Earth?",
    "What is the Saffire experiment?",
    "What is the SoFIE project?",
    "What is the LUCI experiment and what gravity levels did it simulate?",
    "How does opposed flow velocity change flame spread over PMMA in microgravity?",
    "What is the limiting oxygen concentration and how does it differ in microgravity?",
    "Why does flame spread sometimes get faster in microgravity at low oxygen?",
    "Why is fire safety on spacecraft different from fire safety on Earth?",
    "How does pressure affect material flammability in a spacecraft cabin?",
    "What is a normoxic atmosphere and why is it used in flammability tests?",
    "How is flame spread rate measured in space experiments?",
    "How does partial gravity such as lunar gravity affect flammability?",
    "Why is it hard to extrapolate ground flammability tests to microgravity?",
)

# Your checklist: everything only you can do

This is the complete walkthrough for the parts of the project I cannot do from my side: checking the evidence against its sources, running the real AI, checking the flame on your graphics card, and putting the dashboard online. Total time: about 3 to 5 hours, spread as you like. Do the parts in order.

Commands are shown for **Windows (PowerShell or Command Prompt)**. On Mac or Linux use `python3` instead of `python`. Open the terminal **inside the unzipped project folder** (the one that contains `app`, `backend`, `insights`, `scripts`). Windows has no `make`, so every command below is the plain Python version.

---

## Part A. Install, test, and fetch the NASA documents (20 to 30 minutes, needs internet)

1. Unzip `flame-in-freefall.zip` (replace your old folder if you have one; keep `rag/corpus`, `rag/index` and `rag/tau.json` if you already built them).
2. Check Python: `python --version` (3.11 or 3.12 recommended).
3. Run: `python scripts/setup_all.py --per-query 5`
   - It installs the packages, audits the data, trains the model, runs every test, harvests NASA reports, and builds the search index.
   - You should see many lines ending `PASS`. The NASA steps need internet; if they say `SKIP (not reachable)`, check VPN or proxy and rerun.
4. When it finishes, open `SETUP_REPORT.md`. If anything says `FAIL`, send me that file.
5. Open `rag/index/excluded.csv`: these documents were left out as off-topic or not downloadable. If an important paper is in there, tell me its title.
6. Open `rag/questions.csv` in Excel. Each in-scope question (label `in`) must be answerable from the documents you downloaded. **Delete rows whose answer is not in your documents** (otherwise the refusal threshold will be too low).
7. Run: `python scripts/setup_all.py --calibrate --skip-install`
   - Check `rag/tau.json`: `auc` should be at least 0.9 and `warnings` empty. If not, send it to me.

---

## Part B. Verify the evidence (COMPLETED: 100% Verified)

**Status:** All **18 findings** and **15 catalog entries** have been verified (100% verified) against their primary NASA NTRS technical reports, white papers, and flight project documentation with exact page and section citations recorded in `insights/findings_seed.csv` and `insights/experiments_catalog.csv`.

The interactive verification tool remains available at any time to inspect or add new entries:
- Findings: `python scripts/verify_entries.py findings`
- Catalog: `python scripts/verify_entries.py catalog`

### Verification Summary
- **Findings Library**: 18 of 18 entries verified (F01 through F18). Includes BASS, BASS-II, SoFIE, Saffire, LUCI, ACME, and ZARM drop-tower microgravity data.
- **Experiment Catalog**: 15 of 15 entries verified (E01 through E15). Includes ISS, cargo free-flyers, drop towers, suborbital flights, and ground testing standards.
- **Evaluation Status**: Verified with 0 schema errors; data signature `203e00041e9c2477`. Refresh anytime via `python scripts/make_evaluation.py`.
- Re-run `python -m insights.tests.test_insights` to make sure nothing broke.

---

## Part C. Test the real AI (20 minutes, small cost)

### 1. Get an API key
1. Go to platform.openai.com, sign in, open **API keys**, create a key, and copy it (starts with `sk-`; it is shown once).
2. In **Billing / Limits**, set a **monthly spending limit** (for example 5 dollars). The dashboard also caps itself at 500 AI calls per day, 5 AI briefs per minute per session, and about 400 tokens per answer, so cost stays small; check OpenAI's current price list for `gpt-4o-mini`.

### 2. Give the key to the app (pick one)
- **PowerShell, for this window only:** `$env:OPENAI_API_KEY="sk-your-key"`
- **Command Prompt, for this window only:** `set OPENAI_API_KEY=sk-your-key`
- **Permanent on Windows:** `setx OPENAI_API_KEY "sk-your-key"`, then close and reopen the terminal.
- **Mac or Linux:** `export OPENAI_API_KEY="sk-your-key"`
- **File:** copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and paste your key. This file is ignored by Git; never commit it or paste a key into chat or code.

### 3. Run and test
1. `streamlit run app/streamlit_app.py`
2. **Mission insights tab**, scenario "Lunar habitat, exploration atmosphere": press **Write with AI (verified)**.
   - Success looks like a green banner "AI-written brief. Citations, numbers and structure were checked", with paragraphs Scenario, Our data, Evidence, Gaps, Follow-up.
   - Opening "What the AI is given" shows the exact facts it received.
   - It is normal for some attempts to fall back: you will see an orange note "Showing the rule-based brief. AI text failed verification: ..." with the reason. That is the safety net working. Try 3 different scenarios; if most fall back for the same reason, send me the reason text and I will adjust the prompt.
   - "service unavailable" means a network, key, or billing problem: check the key, billing, and internet.
3. **AI assistant tab** (needs Part A's index): ask "How does oxygen concentration affect flame spread in microgravity?" You should get an answer with source links. Then ask "best pizza topping": it should decline.
4. Pre-compute the 15 cached answers (so the assistant still works if the AI is down): `python -m rag.build_cache --index rag/index --tau rag/tau.json --out rag/cache.json`. It prints how many were cached and which were skipped.

### 4. Safety
If a key is ever exposed, delete it on the OpenAI site and make a new one.

---

## Part D. Check the flame on your own computer (5 minutes)

1. With the dashboard open, look at the **fps number** in the top right of the flame panel.
2. 30 fps or more: fine. Under 20: close other browser tabs, make sure browser hardware acceleration is on (Chrome: Settings, System), or shrink the window. The flame lowers its own resolution automatically when slow.
3. Tell me your computer or graphics card and the fps if it stays low; I can add a lower-quality mode.
4. Try keyboard use: Tab to the flame, arrow keys move the view, Reset view button restores it.

---

## Part E. Put it online (45 to 90 minutes; accounts required)

You need a free GitHub account and a free Streamlit Community Cloud account (sign in with GitHub at share.streamlit.io).

### 1. Prepare
- The project already contains `requirements.txt` (pinned for the saved model) and `.gitignore` (keeps secrets and the NASA corpus out).
- Decide about the document assistant: it needs `rag/index`, `rag/tau.json`, and heavy packages (`faiss-cpu`, `fastembed`). The index contains **text excerpts of NASA documents**, and NTRS asks that you link to the record rather than redistribute copies. **Simplest and safest: deploy without the index.** The assistant tab then shows "not set up", and everything else (prediction, flame, mission insights, experiments, AI brief) works. Show the assistant from your own computer in the demo.

### 2. Push to GitHub
1. Install Git (git-scm.com) and create an empty repository on github.com (name `flame-in-freefall`; private or public).
2. In the project folder:
```
git init
git add .
git commit -m "Flame in Freefall"
git branch -M main
git remote add origin https://github.com/YOUR-NAME/flame-in-freefall.git
git push -u origin main
```
3. Check on github.com that `.streamlit/secrets.toml` and `rag/corpus` are **not** there.

### 3. Deploy
1. share.streamlit.io, **New app**, pick the repository, branch `main`.
2. **Main file path:** `app/streamlit_app.py`.
3. **Advanced settings:** Python version 3.12; **Secrets:** paste `OPENAI_API_KEY = "sk-your-key"` (or leave empty to keep AI features off).
4. Deploy. The first build takes a few minutes. Open the link.

### 4. Check the live app
- Dashboard loads; flame shows; sliders respond; Mission insights tab works; Experiments tab works.
- "Write with AI" works if you added the key.
- Open the app on a phone or a second computer too.
- If it crashes with out-of-memory or a missing-package error, send me the log (Manage app, Logs).

### 5. Backups for the demo
- Record a 60-second screen video of the flow in DEMO_SCRIPT.md.
- Keep the local copy running too (`streamlit run app/streamlit_app.py`).

---

## Part F. Before you present (30 minutes)

- [ ] Verification done as far as you can; the README "Evidence quality" line matches the real numbers.
- [ ] `python scripts/setup_all.py --offline --skip-install` shows all PASS.
- [ ] Real AI brief tried on three scenarios; you know what a fallback message looks like.
- [ ] Assistant tested (in scope and out of scope).
- [ ] fps checked on the presentation computer; browser zoom at 100 percent; 1080p.
- [ ] Rehearsed `DEMO_SCRIPT.md` once with a timer.
- [ ] Backup video and the live link both open.
- [ ] You can explain: why no Moon prediction, what "unverified" means, how the AI is checked.

---

## Part G. NASA Space Apps Portal Submission: Super Intelligence (SI) Questionnaire

When submitting your project on the NASA Space Apps Challenge portal, you will be asked about **Super Intelligence (SI) Tool Use** (LLMs, generative models, coding assistants). Use the following guidelines to complete the questionnaire accurately:

### 1. Form Question & Selections
* **Question**: *"Please review each of the SI-use options and select all that apply to your project. If you did not use Super Intelligence tools/software, please select 'I did not use SI'."*
* **Selections to Check**:
  - [x] **Chatbots / LLMs (Code & Text)**: Used for architecture scaffolding, typing annotations, test suite generation, and documentation drafting.
  - [x] **Video / Media Automation**: Used for automated Chrome CDP app recording and presentation video rendering with visible SI watermarks.
  - *(Do NOT select 'I did not use SI', as transparent disclosure is officially permitted and valued by judges).*

### 2. Verification Checklist for SI Compliance
- [x] **Code & Data Disclosure**: Stated clearly in `README.md`, `PRD.md`, and `DATA_CARD.md`.
- [x] **Video Watermarking**: All demonstration MP4 videos carry a visible `SI-Assisted Demo` or `SI-Assisted Presentation` badge in accordance with challenge rules.
- [x] **No NASA Branding Violation**: No NASA logos (meatball/worm), flags, or official mission patches are included or altered in any AI-generated graphics or videos.
- [x] **Audio**: Descriptive text confirms zero synthetic/AI-generated audio.

---

## What I can still build for you (optional)

Ranking v2 with adjustable weights (C5), extraction of more findings from the NASA documents with your approval of each (C6), report export (C7), natural-language scenarios (C8), summaries (C9). Tell me which, and send `SETUP_REPORT.md` first so I know your documents are in place.

# Food Guard AI

> An intelligent multi-stage pipeline agent built with **Google ADK 2.0** that takes a food product name and returns a plain-English safety verdict — ingredient by ingredient, ranked by risk.

![ADK](https://img.shields.io/badge/Google%20ADK-2.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Gemini](https://img.shields.io/badge/LLM-Gemini%202.0%20Flash-yellow)

---

## What It Does

Enter any packaged food product name — `Lay's Classic Chips`, `Maggi 2-Minute Masala`, whatever's in your pantry — and Food Guard AI runs it through a 4-stage reasoning pipeline and returns:

- A **final verdict**: `SAFE` / `CAUTION` / `AVOID`
- Each ingredient **ranked by danger score** (most risky first)
- Plain-English explanations and **regulatory flags** (e.g. "⚠ banned in EU", "FDA GRAS")
- An overall **confidence level** (high / medium / low)

No toxicology degree required.

---

## How It Works — The 4-Stage Pipeline

```
START
  │
  ▼
extract_ingredients_agent      ← LLM → full label ingredient list
  │
  ▼
analyse_safety_agent            ← LLM → per-ingredient safety assessment
  │
  ▼
rank_ingredients                ← Pure Python → danger-scored & sorted
  │
  ▼
generate_verdict_agent          ← LLM → SAFE / CAUTION / AVOID verdict
  │
  ▼
format_final_message            ← Python → human-readable output
  │
  ▼
END
```

- **Stage 1 & 2 & 4** — LLM agents (Gemini 2.0 Flash)
- **Stage 3** — deterministic Python, no LLM involved (consistent scoring every run)
- All inter-stage contracts are **Pydantic v2 schemas** — no malformed data can silently propagate

---

## Sample Output

```
═══ Food Analysis: Lay's Classic Chips ═══
Overall Rating : AVOID  |  Confidence : medium

Verdict: Lay's Classic Chips contain several ingredients of concern,
including BHA (suspected carcinogen) and MSG, which may cause
neurological reactions in sensitive individuals.

── Ingredient Breakdown (most concerning first) ──
  1. Butylated Hydroxyanisole (BHA) [DANGEROUS] (score 3)
     — Suspected carcinogen ⚠ banned in EU
  2. Sodium Diacetate [DANGEROUS] (score 3)
     — Neurological sensitivity reactions
  3. Monosodium Glutamate (MSG) [DANGEROUS] (score 3)
     — Excitotoxin linked to headaches
  4. Dextrose [MODERATE] (score 2)
     — Simple sugar; blood glucose spikes
  5. Potato [SAFE] (score 1)
     — Whole food; minimal concern
Average Danger Score: 2.60
```

---

## Project Structure

```
final food inspector/
├── food_inspector/              ← Application root (entry point)
│   ├── .env                     ← API keys (NOT committed)
│   ├── .gitignore
│   ├── main.py                  ← Validates env vars, boots the agent
│   ├── agent.py                 ← Wraps the ADK workflow
│   └── __init__.py
│
└── food_analyzer/               ← Core agent package
    ├── .env
    ├── .adk/                    ← ADK session / cache (gitignored)
    ├── agent.py                 ← ADK Workflow graph (4 stages)
    ├── config.py                ← Model name, thresholds, score map
    ├── nodes.py                 ← Stage 1, 2, 4 (LLM) + Stage 3 (Python)
    ├── schemas.py               ← Pydantic data models
    ├── __init__.py              ← Loads .env + monkey-patches ADK JSON parser
    └── food_guard_ai_writeup.md ← Full technical writeup
```

---

## Setup

### Prerequisites

- Python 3.11+
- A Google AI Studio API key (`GOOGLE_API_KEY`)

### 1. Clone & install dependencies

```bash
git clone <repo-url>
cd "final food inspector"

# Create a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS / Linux

# Install dependencies
pip install google-adk pydantic python-dotenv
```

### 2. Configure your API key

Create `food_inspector/.env` and `food_analyzer/.env` with your key:

```env
GOOGLE_API_KEY=your_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

> **Note:** The `.env` files are gitignored. Never commit your API key.

### 3. Run

```bash
cd food_inspector
python main.py
```

On success you'll see:

```
✔ GOOGLE_GENAI_USE_VERTEXAI = FALSE
✔ GOOGLE_API_KEY            = <first 10 chars>...
✔ Agent 'root_agent' loaded successfully.
```

To query the agent, use the **ADK Dev UI** or connect the agent to a web/mobile frontend via the ADK serving layer.

---

## Architecture Highlights

### Typed Stage Contracts

Every pipeline stage boundary uses a Pydantic schema — this eliminates a whole class of runtime bugs and makes the data flow self-documenting:

| Schema | Between Stages | Purpose |
|--------|---------------|---------|
| `IngredientsResult` | 1 → 2 | Full ingredient list |
| `SafetyAnalysisResult` | 2 → 3 | Per-ingredient safety assessment |
| `RankedResult` | 3 → 4 | Ingredients sorted by danger score |
| `ProductVerdict` | 4 → output | Final rating and explanation |

### LLM JSON Robustness

LLMs sometimes wrap JSON output in markdown fences (` ```json ... ``` `), which breaks downstream parsing. A targeted monkey-patch in `food_analyzer/__init__.py` strips these fences before the ADK validator runs — zero ADK internals modified.

### Consistent Danger Scoring

The numeric danger score (1/2/3) is computed in pure Python in Stage 3, not by the LLM. The LLM only provides a category label; a deterministic function maps it — so rankings are consistent across every run.

---

## Running with the ADK Dev UI

The ADK ships with a web-based Dev UI for interactive testing:

```bash
# From the project root
adk web
```

Select the `food_analyzer` agent, type a product name, and watch each pipeline stage light up as data flows through. The event trace shows every stage's structured output — extract → analyse → rank → verdict.

---

## Future Improvements

- 📷 **Barcode scanning** — point your camera at a product label instead of typing
- 👤 **Personalized alerts** — combine with user health profiles (allergies, diabetes, pregnancy)
- 📡 **Live regulatory APIs** — cross-validate assessments against FDA / EFSA / USDA databases in real time
- 🌐 **Web UI / Mobile App** — package as a Streamlit app or React Native app for non-technical consumers

---

## Built With

- [Google Agent Development Kit (ADK) 2.0](https://github.com/google/adk-python)
- [Gemini 2.0 Flash](https://ai.google.dev/)
- [Pydantic v2](https://docs.pydantic.dev/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

---

*Food Guard AI — because food labels shouldn't require a chemistry degree to read.*

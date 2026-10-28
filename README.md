# ClearBrand

**Check content against approved brand rules before it is published.**

ClearBrand is a brand-governance web application built by team **ZeroDowntime** for **Codex 48** (We Code Coders), in response to the problem statement from Inkloom AI. It reviews a draft against a company's own approved guidelines, facts and glossary, explains each issue with its source, suggests a correction, and leaves the final decision to people.

- **Live app:** https://clearbrand-zerodowntime.streamlit.app/
- **Repository:** https://github.com/SanjanaSingh29/ClearBrand
- **Team:** ZeroDowntime (solo participant: Sanjana Singh, Bhagwan Parshuram Institute of Technology)

## The problem

Organisations publish content through employees, agencies and AI tools, which makes it hard to keep a consistent and trustworthy brand. Wrong claims, outdated facts and inconsistent wording are usually noticed only after publication.

## How to try it (no setup needed)

1. Open the live app. If it shows a "wake up" button, click it.
2. Use the **Your role** dropdown in the sidebar. Roles are a demo switcher so you can try each one (see Limitations).
3. **Manager:** open **Brand Setup**. Starter guidelines, approved facts and glossary entries are already loaded about ClearBrand itself. You can add or delete entries.
4. **Creator:** open **Review Draft**, submit a draft, and read the findings. Try this text:
   > Check out ClearBrand, the best tool ever! It is 100% accurate and rejected posts get an auto-fix, so users never make mistakes. Our AI decides what gets published!!
5. Accept or dismiss each finding (a dismissal needs a reason), edit the draft to save a new version and re-check, then press **Submit for review**.
6. **Reviewer:** open **Review Queue**, read the findings and revision history, comment, then **Request changes** or **Approve**.

## How it works

1. **Brand material:** a manager adds guidelines (R-), approved facts (F-) and glossary pairs (G-). Each entry gets a code that findings cite.
2. **Rule-based checks:** plain code finds glossary terms to avoid and risky claim words such as "best" or "guaranteed". A claim with no approved source is marked **unverified**, not declared false.
3. **Retrieval:** keyword matching selects the guideline and fact passages relevant to the draft.
4. **AI check (Google Gemini):** the model receives only those passages and must return JSON findings that cite a passage code and quote its exact wording.
5. **Verification:** a finding is kept only if the flagged text appears in the draft, the cited code is one of the supplied passages, and the quoted wording appears in that passage. Findings that fail are discarded and counted.
6. **Human review:** the creator accepts or dismisses each finding, and reviewers comment and approve. Nothing is rewritten or published automatically.
7. **Fallback:** if Gemini is unavailable, rule-based results still appear with a clear notice.

## Features completed

- Brand Setup: guidelines, approved facts and glossary, with coded entries, add, delete and .txt import
- Rule-based checks for glossary terms and unsupported claims
- Gemini-assisted checks for tone, terminology, fact mismatches and unverified claims
- Source and quote verification for AI findings
- Explanations, cited sources and suggested fixes for each finding
- Draft submission, highlighted text, accept and dismiss with a reason
- Revision history with versions and a line-by-line diff view
- Review workflow: Draft, In Review, Changes Requested, Approved
- Reviewer comments, request changes and approve
- Starter content that loads automatically on an empty database
- Findings labelled "Rule-based" or "AI-assisted"

## Technology

| Part | Choice |
|---|---|
| App and UI | Python, Streamlit |
| Database | SQLite |
| AI | Google Gemini through the `google-genai` library, with backup models |
| Retrieval | Keyword matching |
| Other | python-dotenv, difflib, re |
| Hosting | Streamlit Community Cloud, with a GitHub repository |

## Project structure

```
app.py                 Home page
pages/                 Brand Setup, Review Draft, Review Queue
core/db.py             Database tables and queries
core/rules.py          Rule-based checks
core/retrieval.py      Selects relevant passages
core/ai_check.py       Gemini call, with retries and backup models
core/verify.py         Source and quote verification
core/review.py         Combines rule and AI checks
core/seed.py           Starter brand material
core/ui.py, style.py   Shared layout and styling
```

## Changes from the Round 1 plan

- Keyword retrieval replaces embeddings and a vector index, to keep the build reliable within the time.
- Guidelines, facts and glossary are stored in one `sources` table with codes.
- Roles use a demo switcher instead of login.
- A rule-based fallback keeps the app useful when the AI is unavailable.

## AI use and disclosure

- **Inside the product:** Google Gemini performs part of the checks. The draft text and the retrieved brand passages are sent to Google's API.
- **In development:** Claude (Anthropic) helped write and explain the code. [Write one honest sentence about how you reviewed, ran and tested it.]
- **Libraries:** Streamlit, google-genai, python-dotenv and the Python standard library.

## Limitations

- The role switcher is a demo shortcut and not secure authentication. Anyone can change role.
- All visitors share one database, which may reset when the app restarts. Don't enter confidential material.
- Text content only. No image, document or video review yet.
- AI results are not always right. Verification proves that a finding's evidence exists, not that its reasoning is correct, which is why people make the final decision.

## Run locally

```
git clone https://github.com/SanjanaSingh29/ClearBrand.git
cd ClearBrand
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Create a `.env` file containing `GEMINI_API_KEY=your-key`, then run `streamlit run app.py`.

# ClearBrand

**Check content against approved brand rules before it is published.**

ClearBrand is a brand-governance web application built by team **ZeroDowntime** for **Codex 48** (We Code Coders), in response to the problem statement from Inkloom AI. It reviews a draft against a company's own approved guidelines, facts and glossary, explains each issue with its source, suggests a correction, and leaves the final decision to people.

- **Live app:** https://clearbrand-zerodowntime.streamlit.app/
- **Repository:** https://github.com/SanjanaSingh29/ClearBrand
- **Team:** ZeroDowntime (solo participant: Sanjana Singh, Bhagwan Parshuram Institute of Technology)

## The problem

Organisations publish content through employees, agencies and AI tools, which makes it hard to keep a consistent and trustworthy brand. Wrong claims, outdated facts, inconsistent wording and inaccessible content are usually noticed only after publication.

## Try it (no setup needed)

Open the live app. If it shows a "wake up" button, click it. Use a one-click demo button in the sidebar, or sign in with a demo account:

| Username | Password | Role |
|---|---|---|
| creator_demo | Creator#2026 | Creator |
| reviewer_demo | Reviewer#2026 | Reviewer |
| reviewer2_demo | Reviewer2#2026 | Reviewer |
| manager_demo | Manager#2026 | Manager |

These accounts are public and for demonstration only. Do not enter confidential material.

Suggested path:

1. **Manager** (`manager_demo`): open **Brand Setup**. Starter guidelines, approved facts and glossary entries are already loaded. Open **Users** to create accounts.
2. **Creator** (`creator_demo`): open **Review Draft**. Paste a draft, or import a `.docx`, `.pdf` or `.txt` file. Try:
   > Check out ClearBrand, the best tool ever! It is 100% accurate and rejected posts get an auto-fix, so users never make mistakes. Our AI decides what gets published!!
3. Accept or dismiss each finding (a dismissal needs a reason), edit the draft to save a new version, then **Submit for review**.
4. **Reviewer** (`reviewer_demo`): open **Review Queue**, read the findings and revision history, comment, then **Approve** or **Request changes**. A reviewer cannot decide on a draft they created; use `reviewer2_demo` to approve a draft made by `reviewer_demo`.
5. **Manager or Reviewer:** open **Insights** for recurring mistakes and rules that creators often dismiss, and **Audit Log** for who did what and when.

## How it works

1. **Brand material:** a manager adds guidelines (R-), approved facts (F-) and glossary pairs (G-). Each entry gets a code that findings cite.
2. **Import:** drafts can be typed, or imported from DOCX, PDF or TXT. An image can be attached with alt text.
3. **Rule-based checks:** glossary terms to avoid, and risky claim words such as "best" or "guaranteed". A claim with no approved source is marked **unverified**, not declared false.
4. **Accessibility checks:** missing or vague image alt text, vague link text, long runs of capital letters, lowercase hashtags, very long sentences and low reading ease.
5. **Retrieval:** keyword matching selects the guideline and fact passages relevant to the draft.
6. **AI check (Google Gemini):** the model sees only those passages and must return findings that cite a passage code and quote its exact wording.
7. **Verification:** an AI finding is kept only if the flagged text appears in the draft, the cited code is one of the supplied passages, and the quote appears in that passage. Others are discarded and counted.
8. **Human review:** creators accept or dismiss each finding, reviewers comment and approve. Nothing is rewritten or published automatically.
9. **Reliability:** the AI check has a 25-second budget and uses fast backup models. If it is unavailable, rule-based and accessibility results still appear with a notice.

## Features

- Brand Setup: guidelines, approved facts and glossary with coded entries, add, delete and `.txt` import
- Rule-based checks, accessibility checks and Gemini-assisted checks (tone, terminology, fact mismatches, unverified claims)
- Source and quote verification of AI findings
- Explanations, cited sources and suggested fixes; compliance score with a visible formula
- Multi-format import (DOCX, PDF, TXT) and image attachment with alt-text checks
- Draft versions, highlighted findings, accept and dismiss with a reason, revision history with diff view
- Review workflow: Draft, In Review, Changes Requested, Approved; reviewer comments
- Governance insights dashboard: repeated mistakes, most cited sources, dismissal rates and rules that may be unclear
- User accounts with salted PBKDF2 password hashes and one fixed role per user
- Creators see only their own drafts; only the creator can edit a draft; no self-approval (enforced in the server code)
- Audit log of sign-ins, drafts, revisions, decisions, brand changes and account changes, with filters and CSV download
- Manager account creation, and self-service account deletion for non-demo users
- Starter content and demo accounts created automatically on an empty database

## Technology

| Part | Choice |
|---|---|
| App and UI | Python, Streamlit |
| Database | SQLite |
| AI | Google Gemini via `google-genai`, with fast backup models and low thinking effort |
| Retrieval | Keyword matching |
| Documents | python-docx, pdfplumber |
| Data views | pandas |
| Passwords | `hashlib` PBKDF2-HMAC-SHA256 with a random salt |
| Hosting | Streamlit Community Cloud, GitHub |

## Project structure

```
app.py                    Home
pages/                    Brand Setup, Review Draft, Review Queue, Insights, Audit Log, Users
core/db.py                Tables and queries
core/auth.py              Password hashing, accounts, demo accounts
core/rules.py             Glossary and claim checks
core/accessibility.py     Accessibility checks
core/importers.py         DOCX, PDF and TXT import
core/retrieval.py         Selects relevant passages
core/ai_check.py          Gemini call, time budget, backup models
core/verify.py            Source and quote verification
core/review.py            Combines all checks
core/seed.py              Starter brand material
core/ui.py, style.py      Shared layout, sign-in, styling
```

## AI use and disclosure

- **Inside the product:** Google Gemini performs part of the checks. The draft text and the retrieved brand passages are sent to Google's API.
- **During development:** Claude (Anthropic) helped write and explain parts of the code. The author reviewed, ran and tested the code.
- **Libraries:** Streamlit, google-genai, python-dotenv, pandas, python-docx, pdfplumber and the Python standard library.

## Limitations

- There is one organisation. Accounts have roles, but there are no separate company workspaces.
- Demo passwords are public by design so every role can be tried. Sessions end on browser refresh.
- The database is a local SQLite file; on Streamlit Community Cloud it can reset after a restart. Demo accounts and starter content are recreated; drafts and created accounts are not.
- Image checks cover alt text only. PDFs are read as text; alt text cannot be read from PDFs and scanned PDFs are not supported.
- AI findings are not always right. Verification proves a finding's evidence exists, not that its reasoning is correct, which is why people make the final decision.
- Do not enter confidential material in the live app.

## Roadmap

- Separate organisation workspaces and a hosted database
- Image analysis for logos, colours and layout; OCR for scanned PDFs
- AI-suggested rewrites with a before-and-after diff and human approval
- Embedding-based retrieval
- Integrations with Google Docs, Slack and publishing tools
- Optional local model for organisations that cannot send content to an external service

## Run locally

```
git clone https://github.com/SanjanaSingh29/ClearBrand.git
cd ClearBrand
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Create a `.env` file containing `GEMINI_API_KEY=your-key`, then run `streamlit run app.py`.

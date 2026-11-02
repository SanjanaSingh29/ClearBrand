# ClearBrand

**Check content against approved brand rules before it is published.**

ClearBrand is an AI-assisted brand governance web application built by **Team ZeroDowntime** for **Codex 48 (We Code Coders)**, in response to the problem statement from **Inkloom AI**.

It reviews draft content against an organization's approved guidelines, facts, and glossary. It identifies potential issues, explains them with supporting sources, suggests corrections, and keeps the final decision under human control.

- **Live Application:** [ClearBrand](https://clearbrand-zerodowntime.streamlit.app/)
- **GitHub Repository:** [SanjanaSingh29/ClearBrand](https://github.com/SanjanaSingh29/ClearBrand)
- **Team:** ZeroDowntime
- **Team Leader & Developer:** Sanjana Singh
- **Institution:** Bhagwan Parshuram Institute of Technology

---

## 1. The Problem

Organizations publish content through employees, agencies, and AI tools. Maintaining consistent and trustworthy brand communication across these channels can be difficult.

Common problems include:

- Inconsistent brand voice and terminology.
- Unsupported promotional claims.
- Incorrect or outdated organizational information.
- Manual compliance reviews that slow down publishing.
- Difficulty identifying accessibility concerns.
- Lack of transparency about why content violates brand guidelines.

ClearBrand addresses these challenges through an explainable and human-supervised content review workflow.

## 2. How to Try ClearBrand

No local installation is required to explore the deployed application.

1. Open the [live application](https://clearbrand-zerodowntime.streamlit.app/).
2. If the application displays a wake-up message, click the wake-up button.
3. Sign in or use the available demo access options, if enabled.
4. Explore the available roles and features.

### Suggested Demo Workflow

**Manager**

- Open Brand Setup.
- Explore guidelines, approved facts, and glossary entries.
- Add or manage brand knowledge.

**Creator**

- Open Review Draft.
- Submit the following sample content:

> Check out ClearBrand, the best tool ever! It is 100% accurate and rejected posts get an auto-fix, so users never make mistakes. Our AI decides what gets published!!

- Review the generated findings.
- Accept or dismiss findings with an appropriate reason.
- Edit the draft and submit it for review.

**Reviewer**

- Open Review Queue.
- Examine submitted drafts and revision history.
- Add comments.
- Request changes or approve the submission, subject to the application's review permissions.

## 3. How It Works

ClearBrand combines deterministic validation, AI-assisted analysis, evidence verification, and human review.

### 1. Brand Knowledge Management

Managers maintain brand guidelines, approved facts, and glossary entries. Each entry receives a unique reference code.

### 2. Rule-Based Validation

Custom Python logic identifies terminology violations and potentially risky promotional claims.

For example, words such as "best" and "guaranteed" can trigger additional scrutiny.

A claim without an approved supporting source is marked as unverified rather than automatically declared false.

### 3. Context Retrieval

Keyword-based retrieval selects relevant guideline and fact passages from the brand knowledge repository.

### 4. AI-Assisted Analysis

Google Gemini analyzes the draft using the retrieved brand context and generates structured findings.

### 5. Evidence Verification

AI-generated findings are checked to ensure:

- The flagged text exists in the submitted draft.
- The cited source code belongs to the retrieved passages.
- The quoted wording exists in the cited passage.

Findings that fail these checks are discarded.

**Note:** Evidence verification confirms that references and quotations exist; it does not guarantee that an AI-generated interpretation is correct.

### 6. Human Review

Creators examine findings, revise content, and submit drafts for review. Reviewers evaluate the submission and decide whether to approve it or request changes.

### 7. Fallback Mechanism

If the Gemini API is unavailable, rule-based validation can still provide findings, subject to the implemented fallback behavior.

---

## 4. Features

### Brand Knowledge Management

- Manage brand guidelines.
- Maintain approved facts and glossary entries.
- Assign reference codes to knowledge entries.
- Import supported text files.
- Add and delete brand knowledge.

### Hybrid Content Validation

- Rule-based checks using Python and regular expressions.
- Gemini-assisted content analysis.
- Tone and terminology checks.
- Identification of potentially unsupported claims.
- Contextual explanations and suggested corrections.

### Source and Evidence Verification

- Verify flagged text against the original draft.
- Validate source reference codes.
- Verify quoted evidence against retrieved passages.
- Discard findings that fail verification.

### Accessibility and Document Processing

- Dedicated accessibility-checking module.
- Document import functionality for supported formats.
- PDF and DOCX processing through dedicated importer components.

### Review and Revision Management

- Draft submission and review workflow.
- Accept and dismiss findings.
- Dismissal reasons.
- Revision history.
- Line-by-line comparison using Python `difflib`.
- Reviewer comments.
- Approval and change-request actions.

### Account and Governance Features

- Account-related functionality.
- Role-based application workflows.
- Self-approval restrictions where enforced.
- Insights dashboard.
- Audit logging.

*The availability and completeness of individual features should be verified against the deployed application.*

---

## 5. Technology Stack

| Component              | Technology                  |
| ---------------------- | --------------------------- |
| Programming Language   | Python                      |
| Frontend and UI        | Streamlit                   |
| Database               | SQLite                      |
| AI Integration         | Google Gemini API           |
| AI Library             | `google-genai`              |
| Rule-Based Validation  | Python, Regular Expressions |
| Retrieval              | Keyword Matching            |
| Document Processing    | `python-docx`, `pdfplumber` |
| Revision Comparison    | `difflib`                   |
| Environment Management | `python-dotenv`             |
| Deployment             | Streamlit Community Cloud   |
| Version Control        | Git and GitHub              |

## 6. System Architecture

ClearBrand follows a modular architecture in which different components handle user interaction, validation, AI analysis, data management, and review operations.

```text
                  USER
                    |
                    v
             STREAMLIT UI
                    |
                    v
            APPLICATION LOGIC
                    |
          +---------+---------+
          |                   |
          v                   v
    RULE ENGINE          AI ANALYSIS
          |             (GOOGLE GEMINI)
          |                   |
          +---------+---------+
                    |
                    v
            EVIDENCE VERIFIER
                    |
                    v
            FINDINGS & FIXES
                    |
                    v
             CREATOR REVISION
                    |
                    v
             REVIEWER QUEUE
                    |
                    v
           APPROVAL / CHANGES
                    |
                    v
               SQLITE DB
```

## 7. Project Structure

```text
ClearBrand/
│
├── app.py
├── requirements.txt
├── README.md
├── speed_test.py
│
├── core/
│   ├── ai_check.py
│   ├── db.py
│   ├── review.py
│   ├── ui.py
│   ├── accessibility.py
│   ├── importers.py
│   └── auth.py
│
├── pages/
│   ├── 2_Review_Draft.py
│   ├── 4_Insights.py
│   └── ...
│

```

*This is a representative structure. Additional modules and pages may be present in the repository.*

## 8. Changes from the Round 2 Plan

The implementation evolved based on development time, reliability, and practical requirements.

- **Retrieval:** Keyword matching replaced the initially planned embedding-based retrieval and vector database.
- **Knowledge Management:** Guidelines, approved facts, and glossary entries are managed through a centralized database.
- **AI Integration:** Google Gemini was integrated for contextual brand analysis.
- **Evidence Verification:** A dedicated verification process was introduced to check AI-generated references and quotations.
- **Review Workflow:** Draft revision, history comparison, and reviewer approval functionality were developed.
- **Additional Capabilities:** Accessibility checks, document importers, account-related functionality, audit logging, and Insights were added as development progressed.

## 9. AI Use and Disclosure

Google Gemini is used for part of the content analysis process.

- Draft text and retrieved brand passages are sent to Google's Gemini API for AI-assisted analysis.
- The model generates structured findings based on the supplied context.
- The application verifies source references and quotations before retaining AI findings.
- Rule-based checks provide a separate validation mechanism.
- AI-generated recommendations do not automatically publish or approve content.

**Human oversight remains essential.** ClearBrand is designed to support editorial decisions, not replace them.

## 10. Testing

The following areas should be evaluated during local and deployed application testing.

| Area                  | Verification                                   |
| --------------------- | ---------------------------------------------- |
| Authentication        | Sign-in and available demo access              |
| Creator Workflow      | Draft submission and validation                |
| Reviewer Workflow     | Review, comments, and approval                 |
| Self-Approval         | Restrictions on approving one's own submission |
| Brand Validation      | Rule-based and AI-assisted findings            |
| Evidence Verification | Source codes and quoted text                   |
| Document Import       | PDF and DOCX extraction                        |
| Accessibility         | Accessibility findings                         |
| Insights              | Dashboard information                          |
| Audit Log             | Activity records and history                   |

Only tests actually completed successfully should be reported as passed.

## 11. Limitations

- AI-generated findings may be inaccurate or incomplete.
- Evidence verification does not establish the semantic correctness of every finding.
- Document extraction depends on the structure and quality of uploaded files.
- Accessibility checks do not replace a complete accessibility audit.
- The application requires human judgment for contextual interpretation.
- Production-grade security, authentication, and organization-level isolation must be assessed separately from demo functionality.
- Persistent storage and account isolation depend on the deployment configuration.

Do not submit confidential organizational information through a shared demonstration environment.

## 12. Future Scope

Potential improvements include:

- Advanced role-based access control and secure authentication.
- Organization-specific workspaces and tenant isolation.
- Expanded audit trails and governance analytics.
- More comprehensive accessibility validation.
- Multimodal content validation for images, audio, and video.
- Integrations with Google Docs, Notion, and other content platforms.
- Multilingual brand governance.
- On-premise deployment and locally hosted AI models.

## 13. Team

| Detail                     | Information                               |
| -------------------------- | ----------------------------------------- |
| Team Name                  | ZeroDowntime                              |
| Team Leader                | Sanjana Singh                             |
| Developer                  | Sanjana Singh                             |
| Institution                | Bhagwan Parshuram Institute of Technology |
| Hackathon                  | Codex 48 — We Code Coders                 |
| Problem Statement Provider | Inkloom AI                                |

## 14. Project Links

- **Live Application:** [https://clearbrand-zerodowntime.streamlit.app/](https://clearbrand-zerodowntime.streamlit.app/)
- **GitHub Repository:** [https://github.com/SanjanaSingh29/ClearBrand](https://github.com/SanjanaSingh29/ClearBrand)

---

## Conclusion

ClearBrand transforms static brand guidelines into an interactive editorial review system. By combining rule-based validation, Google Gemini AI, evidence verification, and human-supervised review workflows, it helps content teams identify potential brand inconsistencies before publication.

Rather than replacing human judgment, ClearBrand positions AI as an explainable assistant that supports creators and reviewers while keeping final approval under human control.

**ClearBrand — Build consistent brands. Publish with confidence.**

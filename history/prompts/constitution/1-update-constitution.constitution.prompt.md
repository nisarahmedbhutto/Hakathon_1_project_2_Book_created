---
id: 1
title: Update Constitution
stage: constitution
date: 2025-12-28
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: /sp.constitution
labels: [constitution,spec-driven,documentation]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```text
/sp.constitution

Project: AI-Spec-Driven Technical Book with Embedded RAG Chatbot

Core principles:
- Spec-driven development (all work must follow written specifications)
- Accuracy and faithfulness to source content
- Clear instructional writing for developers and technical learners
- Separation of concerns (book content, frontend, backend, AI systems)
- Reproducibility (entire project can be rebuilt from repository)
- Production-grade engineering standards

Book standards:
- Framework: Docusaurus (static site generation)
- Output: Deployed to GitHub Pages
- Writing style: Clear, structured, instructional
- Audience: Developers, AI engineers, software architects
- No hallucinated facts or unsupported claims
- All technical explanations must be internally consistent

AI/Spec-driven workflow:
- All tasks must originate from Spec-Kit Plus specifications
- No implementation without an approved spec
- Specs must be explicit, scoped, and testable
- Claude Code is the sole implementation agent
- No manual edits outside the defined workflow

RAG chatbot standards:
- Chatbot must answer questions strictly from book content
- Must support:
  - Full-book question answering
  - User-selected text–only question answering
- Architecture:
  - FastAPI backend
  - OpenAI Agents / ChatKit SDKs
  - Neon Serverless Postgres (metadata + conversations)
  - Qdrant Cloud (vector storage, free tier)
- No responses based on external or unstated knowledge
- Clear failure responses when information is not present

Frontend integration:
- Chatbot must be embedded inside the Docusaurus site
- UI must be minimal, accessible, and non-intrusive
- Book reading experience must remain primary
- No frontend logic leaks into backend responsibilities

Backend standards:
- Clean API boundaries
- Stateless endpoints where possible
- Environment-based configuration
- Secure handling of API keys and secrets
- Designed for future scalability

Constraints:
- Single unified repository
- Clear `/frontend` and `/backend` separation
- No unnecessary dependencies
- Free-tier compatible infrastructure only
- No breaking changes without spec updates

Quality controls:
- No code or content duplication
- No speculative features
- Every component must have a clear purpose
- All failures must be explicit and explainable
- Documentation must reflect actual behavior

Success criteria:
- Book builds successfully via Docusaurus
- Book is live on GitHub Pages
- Embedded RAG chatbot functions correctly
- Chatbot answers only from book content
- Selected-text-based answers work correctly
- Project is fully reproducible from repository
```

## Response snapshot

The constitution file `.specify/memory/constitution.md` has been successfully updated with project-specific principles for the AI-Spec-Driven Technical Book with Embedded RAG Chatbot project. The updated constitution includes:

- Core principles: Spec-driven development, accuracy and faithfulness to source content, separation of concerns, reproducibility and production-grade standards, free-tier compatible infrastructure, and quality controls
- Book and AI System Standards section
- Frontend and Backend Standards section
- Governance section
- Version tracking information

## Outcome

- ✅ Impact: New project constitution created with specific principles for AI-Spec-Driven Technical Book project
- 🧪 Tests: none
- 📁 Files: 1 file updated (.specify/memory/constitution.md)
- 🔁 Next prompts: Next steps would include creating specifications based on this constitution
- 🧠 Reflection: The constitution properly captures all the requirements and principles specified by the user

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create initial feature specifications based on this constitution
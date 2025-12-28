<!-- Sync Impact Report:
Version change: N/A → 1.0.0
Added sections: All principles and sections for AI-Spec-Driven Technical Book project
Removed sections: None (new constitution)
Modified principles: N/A (new constitution)
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated
- .specify/templates/spec-template.md ✅ updated
- .specify/templates/tasks-template.md ✅ updated
- .specify/templates/commands/*.md ⚠ pending
Follow-up TODOs:
- RATIFICATION_DATE: Original adoption date unknown
-->

# AI-Spec-Driven Technical Book with Embedded RAG Chatbot Constitution

## Core Principles

### Spec-driven development
All work must follow written specifications; No implementation without an approved spec; Specs must be explicit, scoped, and testable. This ensures that every feature and change is properly planned and documented before implementation begins.

### Accuracy and faithfulness to source content
No hallucinated facts or unsupported claims; All technical explanations must be internally consistent; Clear instructional writing for developers and technical learners. The book content must remain accurate and reliable at all times.

### Separation of concerns
Clear separation between book content, frontend, backend, and AI systems; Single unified repository with clear /frontend and /backend separation. This ensures maintainability and clear boundaries between different system components.

### Reproducibility and production-grade standards
Entire project can be rebuilt from repository; Production-grade engineering standards; No breaking changes without spec updates. The project must be fully reproducible from the repository and maintain high engineering standards.

### Free-tier compatible infrastructure
Infrastructure must work on free tiers; No unnecessary dependencies; Claude Code is the sole implementation agent. The project must remain cost-effective by utilizing free-tier services and minimizing dependencies.

### Quality controls
No code or content duplication; No speculative features; Every component must have a clear purpose; All failures must be explicit and explainable. Quality is maintained through strict controls on duplication and feature creep.

## Book and AI System Standards
Book standards: Framework: Docusaurus (static site generation), Output: Deployed to GitHub Pages, Writing style: Clear, structured, instructional, Audience: Developers, AI engineers, software architects. RAG chatbot standards: Chatbot must answer questions strictly from book content; Must support full-book question answering and user-selected text–only question answering; Architecture: FastAPI backend, OpenAI Agents / ChatKit SDKs, Neon Serverless Postgres (metadata + conversations), Qdrant Cloud (vector storage, free tier); No responses based on external or unstated knowledge; Clear failure responses when information is not present.

## Frontend and Backend Standards
Frontend integration: Chatbot must be embedded inside the Docusaurus site; UI must be minimal, accessible, and non-intrusive; Book reading experience must remain primary; No frontend logic leaks into backend responsibilities. Backend standards: Clean API boundaries; Stateless endpoints where possible; Environment-based configuration; Secure handling of API keys and secrets; Designed for future scalability.

## Governance
AI/Spec-driven workflow: All tasks must originate from Spec-Kit Plus specifications; No manual edits outside the defined workflow. Constraints: No breaking changes without spec updates; Free-tier compatible infrastructure only. Quality controls: Documentation must reflect actual behavior.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): Original adoption date unknown | **Last Amended**: 2025-12-28
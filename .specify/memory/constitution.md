<!--
SYNC IMPACT REPORT
Version change: 0.1.0 → 1.0.0 (MAJOR - initial complete constitution)
Added sections: Core Principles (6), Technology Standards, Development Workflow, Governance
Modified principles: None (new project)
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ updated
  - .specify/templates/spec-template.md ✅ updated
  - .specify/templates/tasks-template.md ✅ updated
Follow-up TODOs: None
-->

# AI-Spec Driven Book with RAG Chatbot Constitution

## Core Principles

### Spec-first development
Spec-first approach to all feature development. Every feature must be defined in a specification before implementation begins. Specifications must include clear acceptance criteria, test scenarios, and implementation requirements.

### Technical accuracy
All code examples and technical content must be accurate, tested, and validated. Technical claims must be verifiable and backed by working implementations. Documentation must reflect actual system behavior, not aspirational functionality.

### Clear, practical writing
All content must be written in clear, accessible language that serves both learning and reference purposes. Writing must be practical with actionable guidance rather than purely theoretical concepts. Examples should be immediately applicable to real-world scenarios.

### Reproducible workflows
All development and deployment workflows must be completely reproducible. Instructions must work consistently across different environments. Code examples must include complete setup procedures and dependency management.

### AI-native authoring
Leverage AI tools and workflows as primary authoring mechanisms. All content generation, editing, and review processes should incorporate AI assistance where appropriate. Maintain human oversight for quality and accuracy.

### Docusaurus book deployment
All documentation and code examples must be deployable via Docusaurus to GitHub Pages with clear deployment instructions. The book structure must follow Docusaurus conventions and be easily maintainable.

## Technology Standards
Docusaurus book deployed to GitHub Pages, Chapters generated from specs, Runnable, documented code only. RAG requirements: Answers grounded in book content, Full-book and selected-text queries, FastAPI backend, Qdrant Cloud (free tier), Neon Serverless Postgres, OpenAI Agents or ChatKit, Prompts documented. All technology choices must prioritize free-tier services and professional tone in the final output.

## Development Workflow
Spec-first approach, Technical accuracy verification, Clear, practical writing standards, Reproducible workflows, AI-native authoring tools. All changes must follow the Spec-Driven Development (SDD) methodology with proper documentation and validation at each stage.

## Governance

All code must be executable and tested, All documentation must be deployable, All RAG features must be grounded in book content, All workflows must be reproducible. This constitution supersedes all other practices and must be referenced in all development decisions.

**Version**: 1.0.0 | **Ratified**: 2025-12-30 | **Last Amended**: 2025-12-30
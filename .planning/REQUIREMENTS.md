# Requirements — Phase 1: AI Topic Decomposition Engine

## 🟢 Success Criteria
1. Given a subject name (e.g., "Machine Learning"), the AI can generate a list of 15-30 subtopics.
2. Each subtopic includes `name`, `difficulty`, `estimated_hours`, and `sort_order`.
3. Prerequisite mapping is extracted by the AI (stored in Topic metadata).
4. Subtopics can be "Ingested" into a subject with a single click.
5. UI shows a professional loading state ("Extracting Curriculum Architecture...") during generation.

## 🛠️ Technical Scope
- **Backend Service**: `DecompositionService` to handle LLM calls and DB ingestion.
- **AI Integration**: Update `AIClient` with structured output parsing (JSON Mode).
- **API Endpoint**: `POST /api/v1/topics/decompose/{subject_id}`.
- **Frontend Store**: `useSubjectStore` upgrade with `decomposeSubject` action.
- **UI**: Added "AI Curriculum Architect" section in `CurriculumPage.jsx`.

## 🧪 Verification Plan
- [ ] CURL test to hit the decomposition endpoint.
- [ ] Verify Topics are created in DB with correct `subject_id`.
- [ ] Manual UI test: Type subject → Click Decompose → See result.

# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for the IGDB Game Recommendation System.

## What are ADRs?

ADRs are short documents that capture important architectural decisions along with their context and consequences. They help preserve the "why" behind decisions, not just the "what".

## ADR Template

Each ADR follows this structure:

```markdown
# ADR-XXX: [Title]

## Status
[Proposed | Accepted | Rejected | Superseded]

## Context
[The issue motivating this decision]

## Decision
[The change that we're proposing or have made]

## Rationale
[Why this decision was made]

## Consequences
[What becomes easier or more difficult to do]
```

## Current ADRs

- [ADR-001: Project Structure](001-project-structure.md)
- [ADR-002: Development Workflow](002-development-workflow.md)
- [ADR-003: Documentation Strategy](003-documentation-strategy.md)
- [ADR-004: ML Strategy](004-ml-strategy.md)
- [ADR-005: Docker Strategy](005-docker-strategy.md)
- [ADR-006: Data Management](006-data-management.md)
- [ADR-007: ML Pipeline Implementation](007-ml-pipeline-implementation.md)
- [ADR-008: Option B Lite Implementation](008-option-b-lite-implementation.md)
- [ADR-009: Frontend Scalability Strategy](009-frontend-scalability-strategy.md)
- [ADR-010: Docker Deployment Lessons](010-docker-deployment-lessons.md) - **Superseded** by Cloud Run approach
- [ADR-011: App Engine Frontend Deployment](011-app-engine-frontend-deployment.md) - **Failed** (server.js not found)

## Related Documentation

- **[DEPLOYMENT.md](../DEPLOYMENT.md)** - Consolidated deployment guide
- **[LESSONS_LEARNED.md](../LESSONS_LEARNED.md)** - Centralized knowledge base
- **[CURRENT_STATUS.md](../CURRENT_STATUS.md)** - Current project status
- **[GCP_CURRENT_STATE.md](../GCP_CURRENT_STATE.md)** - GCP environment status

## Adding New ADRs

1. Create new file: `XXX-decision-name.md`
2. Use next sequential number
3. Follow the template above
4. Update this README with the new ADR
5. Commit with message: "Add ADR-XXX: [Title]"

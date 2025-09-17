# ADR-003: Documentation Strategy

## Status

Accepted

## Context

Need documentation that serves both humans and LLMs (like Cursor chat). Previous project lacked proper documentation, leading to confusion and duplicated work.

## Decision

Implement LLM-friendly documentation strategy:

### 1. Architecture Decision Records (ADRs)

- Short, structured documents explaining **WHY** decisions were made
- Located in `docs/decisions/`
- Template: Context → Decision → Rationale → Consequences

### 2. Context Files for LLMs

- `docs/CONTEXT.md`: Project overview for LLMs
- `docs/ARCHITECTURE.md`: System architecture
- `docs/API.md`: API endpoints and schemas
- `docs/DATA_FLOW.md`: Data flow between components

### 3. Code Documentation

- Docstrings with clear examples
- Type hints everywhere
- README in each directory explaining purpose

## Rationale

- **LLM efficiency**: Structured context helps AI understand project quickly
- **Human efficiency**: ADRs capture decision rationale, not just what was done
- **Maintenance**: Documentation stays relevant by focusing on decisions, not implementation details
- **Onboarding**: New developers (human or AI) can quickly understand project

## Consequences

- ✅ Better AI assistance in development
- ✅ Preserved decision context
- ✅ Easier onboarding
- ❌ Initial documentation overhead
- ❌ Need to maintain documentation discipline

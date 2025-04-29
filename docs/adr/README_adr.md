# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) that document significant architectural decisions made during the development of this project.

## What is an ADR?

An Architecture Decision Record is a document that captures an important architectural decision made along with its context and consequences.

## ADR Template

```markdown
# ADR-NNNN: Title

## Status

[Proposed | Accepted | Deprecated | Superseded by [ADR-NNNN](NNNN-filename.md)]

## Context

[Describe the context and problem statement that led to this decision. Include factors like requirements, constraints, and forces at play.]

## Decision

[Describe the decision that was made. State the position clearly and directly.]

## Consequences

[Describe the resulting context after applying the decision. Include both positive and negative consequences.]

## Alternatives Considered

[Describe alternative options that were considered and why they were not chosen.]

## References

[Include any references to related decisions, documentation, or resources.]
```

## How to Create a New ADR

1. Copy the template above into a new file named `NNNN-descriptive-title.md` where `NNNN` is the next sequential number.
2. Fill in the sections based on the architectural decision.
3. Submit the ADR as part of a pull request for review.
4. Update the status as the ADR moves through the decision process.

## Design Differences

- ADRs focus on architectural decisions, not implementation details
- Each ADR is a standalone document but may reference other ADRs
- ADRs are never deleted, only marked as deprecated or superseded 
# ADR 0001: Modular monolith for the first customer proof

- Status: accepted
- Date: 2026-09-08

## Context

The product must prove a bounded reimbursement workflow, policy correctness, explanations, and auditability before the team has evidence that independent services are needed.

## Decision

Use a Next.js web application, one FastAPI application, one Procrastinate worker, and PostgreSQL. Keep policy evaluation, workflow orchestration, audit, and persistence as explicit backend modules with typed seams.

## Consequences

Deployment and local reproduction stay small. The API and worker can scale independently from the same image. Modules may be extracted only when measured load, ownership, or failure isolation justifies it.


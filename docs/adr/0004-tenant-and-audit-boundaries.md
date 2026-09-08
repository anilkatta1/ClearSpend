# ADR 0004: Server-derived tenancy and hash-linked audit events

- Status: accepted
- Date: 2026-09-08

## Context

Client-provided organization identifiers create cross-tenant access risk. Finance actions also require a useful decision trace.

## Decision

Resolve organization and role from the authenticated principal, scope every query by that organization, and never accept an organization ID from an expense request. Store append-only audit events with per-organization sequence, prior hash, event hash, actor, correlation ID, and decision metadata.

## Consequences

The demo identity header is replaceable by OIDC without changing handlers. Hash verification detects mutation but is not external notarization. PostgreSQL row-level security is defense in depth planned before production onboarding.


# ADR 0003: PostgreSQL-backed jobs with Procrastinate

- Status: accepted
- Date: 2026-09-08

## Context

The MVP needs durable asynchronous assessment without operating Redis or Kafka. Expense state, audit evidence, and job state must remain recoverable together.

## Decision

Use PostgreSQL 17 for domain data and Procrastinate jobs. Write an outbox event in the expense transaction, attempt immediate enqueue after commit, and continuously relay unpublished events from the worker. Use a per-expense execution lock, queueing lock, and a unique assessment-attempt key for at-least-once safety.

## Consequences

There is one durable service to operate and inspect. PostgreSQL capacity is shared, so queue latency, connection utilization, and outbox age are operational signals. Kafka remains a later option if independently scalable event streaming becomes an evidenced need.


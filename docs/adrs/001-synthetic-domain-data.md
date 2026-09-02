# ADR 001: Purpose-built synthetic domain data

## Status

Accepted.

## Decision

Generate deterministic orders, escrow events, and finance transactions rather than use a generic public dataset.

## Rationale

The project demonstrates organizational disagreement about KPI meaning. Controlled data lets tests reproduce competing definitions without exposing employer or customer data. A fixed seed makes CI repeatable while a row-count parameter supports performance testing.

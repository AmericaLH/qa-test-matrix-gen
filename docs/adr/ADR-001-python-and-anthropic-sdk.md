# ADR-001: Use Python with the Anthropic SDK

## Status: Accepted

## Context

The project needs a language and AI SDK. Options considered: Python + Anthropic SDK, TypeScript + Codex SDK, Python + OpenAI Agents SDK.

## Decision

Use Python 3.11+ with the `anthropic` package directly.

## AI Tool Input

Claude Code helped evaluate the tradeoffs. Python aligns with existing QA automation tooling (pytest, selenium, playwright). The Anthropic SDK gives direct access to Claude's latest models with streaming and prompt caching support.

## Consequences

- pytest is the natural test runner — consistent with existing team automation
- Pydantic v2 for data validation (well-supported in Python ecosystem)
- TypeScript Codex SDK not used as primary; may be used for a comparison task in DEVLOG

# ADR-003: Ask Claude to Return Structured JSON Directly

## Status: Accepted

## Context

The matrix generator needs structured output (list of test cases) from Claude. Options: ask for JSON, ask for Markdown then parse it, use Claude's tool_use / function calling feature.

## Decision

Prompt Claude to return raw JSON only (no markdown fences), then `json.loads()` the response. Pydantic validates the shape.

## AI Tool Input

Compared structured output via tool_use vs plain JSON prompt. Tool use adds complexity for little gain here since the schema is simple and stable. Plain JSON with a strict system prompt is easier to debug and test.

## Consequences

- If Claude wraps output in markdown fences despite instructions, a strip step will be needed — monitor in production
- Pydantic validation will raise clearly if Claude returns unexpected fields
- Future improvement: use Claude's `tool_use` / structured output feature for guaranteed JSON conformance

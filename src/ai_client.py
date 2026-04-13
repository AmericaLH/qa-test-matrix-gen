import os
import sys
import anthropic
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_MODEL = "claude-sonnet-4-6"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def call_model(system: str, user_content: str, max_tokens: int = 4096) -> str:
    """Call Anthropic Claude. On rate limit, fall back to local Ollama automatically."""
    try:
        return _call_anthropic(system, user_content, max_tokens)
    except anthropic.RateLimitError as exc:
        _warn_rate_limit(exc)
        return _call_ollama(system, user_content)


def _call_anthropic(system: str, user_content: str, max_tokens: int) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text


def _call_ollama(system: str, user_content: str) -> str:
    try:
        from openai import OpenAI, APIConnectionError
    except ImportError:
        raise RuntimeError(
            "The 'openai' package is required for Ollama fallback.\n"
            "Run: pip install openai"
        )

    try:
        client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
        )
        return response.choices[0].message.content
    except APIConnectionError:
        raise RuntimeError(
            f"Ollama is not running at {OLLAMA_BASE_URL}.\n"
            f"Start it with:  ollama serve\n"
            f"Pull a model:   ollama pull {OLLAMA_MODEL}"
        )


def _warn_rate_limit(exc: anthropic.RateLimitError) -> None:
    headers = getattr(exc.response, "headers", {})
    retry_after = headers.get("retry-after")
    hint = ""
    if retry_after:
        try:
            secs = int(float(retry_after))
            if secs < 60:
                hint = f" (Anthropic retry in ~{secs}s)"
            elif secs < 3600:
                hint = f" (Anthropic retry in ~{secs // 60} min)"
            else:
                hint = f" (Anthropic retry in ~{secs // 3600}h)"
        except ValueError:
            pass

    print(
        f"\nAnthropic rate limit reached{hint}.\n"
        f"Falling back to Ollama ({OLLAMA_MODEL})...\n",
        file=sys.stderr,
    )

"""LLM clients. OpenAILLM is the production client; MockLLM is for tests."""
import os

class LLMError(Exception):
    """Any failure that should trigger the fallback chain (timeout, connection, rate limit, API error)."""

class OpenAILLM:
    def __init__(self, cfg, api_key=None, client=None):
        self.cfg = cfg
        if client is None:
            from openai import OpenAI                              # lazy import
            key = api_key or os.environ.get("OPENAI_API_KEY")
            if not key: raise LLMError("No API key configured")
            client = OpenAI(api_key=key, timeout=cfg.timeout, max_retries=cfg.retries)
        self.client = client

    def complete(self, system, user):
        from openai import APITimeoutError, APIConnectionError, RateLimitError, APIError
        try:
            r = self.client.chat.completions.create(model=self.cfg.model, max_tokens=self.cfg.max_tokens, temperature=0.1,
                                                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
            return (r.choices[0].message.content or "").strip()
        except (APITimeoutError, APIConnectionError, RateLimitError, APIError) as e:
            raise LLMError(type(e).__name__) from e

class MockLLM:
    """Scripted LLM for tests: reply is a string, an Exception to raise, or a callable(system, user)."""
    def __init__(self, reply="Answer from the passages [1]."):
        self.reply, self.calls = reply, []
    def complete(self, system, user):
        self.calls.append((system, user))
        r = self.reply(system, user) if callable(self.reply) else self.reply
        if isinstance(r, Exception): raise r
        return r

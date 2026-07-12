"""Runner backends: one abstraction, `generate(skill, prompt) -> text`.

claude  — `claude -p` headless subprocess (frontier; installed + authenticated)
openai  — any OpenAI-compatible chat endpoint via stdlib urllib; the local
          vLLM writer model on the 3090 is this with base_url localhost:8080
fake    — canned responses from a directory; the contact tests' zero-network
          backend

codex joins as a fourth when its CLI is installed — the abstraction is the
contract, not the vendor.
"""
from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from pathlib import Path

from . import DispatchError


class ClaudeRunner:
    name = "claude"

    def __init__(self, model: str | None = None, timeout: int = 1200):
        self.model = model
        self.timeout = timeout

    def generate(self, skill: str, prompt: str) -> str:
        cmd = ["claude", "-p", "--output-format", "text"]
        if self.model:
            cmd += ["--model", self.model]
        try:
            # cwd: neutral dir so no repo's CLAUDE.md leaks into the prompt.
            proc = subprocess.run(cmd, input=prompt, capture_output=True,
                                  text=True, timeout=self.timeout, cwd=Path.home())
        except FileNotFoundError as e:
            raise DispatchError("claude CLI not found on PATH") from e
        except subprocess.TimeoutExpired as e:
            raise DispatchError(f"claude timed out after {self.timeout}s on {skill}") from e
        if proc.returncode != 0:
            raise DispatchError(f"claude failed on {skill}: {proc.stderr.strip()[:500]}")
        return proc.stdout.strip()


class OpenAIRunner:
    name = "openai"

    def __init__(self, base_url: str, model: str, api_key: str | None = None,
                 temperature: float = 0.7, timeout: int = 1200):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.timeout = timeout

    def generate(self, skill: str, prompt: str) -> str:
        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=json.dumps({
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
            }).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {})},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            raise DispatchError(f"openai-compatible endpoint failed on {skill}: {e}") from e
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as e:
            raise DispatchError(f"unexpected completion shape: {json.dumps(data)[:300]}") from e


class FakeRunner:
    name = "fake"

    def __init__(self, responses_dir: str | Path):
        self.dir = Path(responses_dir)

    def generate(self, skill: str, prompt: str) -> str:
        p = self.dir / f"{skill}.md"
        if not p.is_file():
            raise DispatchError(f"fake runner has no canned response for {skill} ({p})")
        return p.read_text(encoding="utf-8").strip()


def make_runner(name: str, model: str | None = None, base_url: str | None = None,
                fake_dir: str | None = None):
    if name == "claude":
        return ClaudeRunner(model=model)
    if name == "openai":
        if not base_url:
            raise DispatchError("openai runner needs --base-url (e.g. http://127.0.0.1:8080)")
        return OpenAIRunner(base_url=base_url, model=model or "default",
                            api_key=os.environ.get("SCRIBE_DISPATCH_API_KEY"))
    if name == "fake":
        if not fake_dir:
            raise DispatchError("fake runner needs --fake-dir")
        return FakeRunner(fake_dir)
    raise DispatchError(f"unknown runner {name!r} (claude, openai, fake)")

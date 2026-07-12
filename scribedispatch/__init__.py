"""scribedispatch — the automatic agentic mode (docs/DISPATCH.md).

The coordinator: reads derived state through the scribectl CLI, runs skill
agents, lands artifacts with pack-sha receipts. It never authors, never
ratifies, never edits a human-touched file, never iterates on itself.
The engine package stays LLM-free; this one holds the runners.
"""


class DispatchError(Exception):
    pass

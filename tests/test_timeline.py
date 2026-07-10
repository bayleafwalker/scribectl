"""Timeline parsing and the prior-relevant oracle query."""
from pathlib import Path

from scribectl.core.timeline import _pos_key, load_events, prior_relevant
from scribectl.core.vault import Note


def _note(body: str) -> Note:
    return Note(path=Path("/x/Timeline.md"), meta={"type": "timeline"}, body=body)


def test_pos_key_forms():
    assert _pos_key("pre") == (-1, -1, -1)
    assert _pos_key("B1.C2.S3") == (1, 2, 3)
    assert _pos_key("b10.c1.s1") == (10, 1, 1)
    assert _pos_key("Chapter One") is None


def test_load_events_parses_actors_loc_fact():
    n = _note(
        "## pre\n"
        "- loc: Ashmarket | The founding lie.\n"
        "## B1.C1.S1\n"
        "- actors: Mara Vey, Kalen | loc: Gate Nine | They met | at dusk.\n"
        "## not a position\n"
        "- this bullet is ignored\n"
    )
    events = load_events(n)
    assert len(events) == 2
    pre, met = events
    assert pre.pos == (-1, -1, -1) and pre.actors == [] and pre.location == "Ashmarket"
    assert met.pos == (1, 1, 1)
    assert met.actors == ["Mara Vey", "Kalen"]
    assert met.location == "Gate Nine"
    assert met.fact == "They met | at dusk."


def test_prior_relevant_fixture(vault):
    events = prior_relevant(vault, (1, 1, 1), {"Mara Vey"}, "Lower Ashmarket")
    assert len(events) == 2  # the global pre event + Mara's ledger memory
    assert all(e.pos < (1, 1, 1) for e in events)


def test_prior_relevant_filters_by_actor_and_location(vault):
    # No actor/location overlap: only the actor-less (global) event survives.
    events = prior_relevant(vault, (1, 1, 1), {"Nobody"}, None)
    assert len(events) == 1
    assert events[0].actors == []


def test_prior_relevant_is_strictly_before(vault):
    assert prior_relevant(vault, (-1, -1, -1), {"Mara Vey"}, "Lower Ashmarket") == []

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


# -- scoped knowledge (the listening set) -------------------------------------

def _tl_vault(tmp_path, body: str):
    from scribectl.core.vault import Vault

    (tmp_path / "Timeline.md").write_text("---\ntype: timeline\n---\n" + body, encoding="utf-8")
    return Vault.load(tmp_path)


SCOPED_TL = (
    "## B1.C1.S1812\n"
    "- actors: Tavi | loc: Landing | heard: Café | The horn sounds.\n"
    "- loc: Landing | Slush packs against the pilings.\n"
    "- actors: Ferry operator, Leena | The crossing is cancelled.\n"
    "- The world turns.\n"
)


def test_heard_prefix_parses_and_stays_out_of_the_fact():
    horn = load_events(_note(SCOPED_TL))[0]
    assert horn.heard == ["Café"]
    assert horn.fact == "The horn sounds."
    assert load_events(_note("## pre\n- actors: A | x\n"))[0].heard == []


def test_scoped_knowledge_has_no_global_events(tmp_path):
    v = _tl_vault(tmp_path, SCOPED_TL)
    facts = lambda evs: [e.fact for e in evs]
    # Unscoped (every pre-existing set): actor-less events stay global.
    assert "The world turns." in facts(prior_relevant(v, (9, 9, 9), {"Nobody"}, None))
    # Scoped: a place hears what happens at it, and what is heard from it.
    assert facts(prior_relevant(v, (9, 9, 9), set(), "Landing", scoped=True)) == [
        "The horn sounds.", "Slush packs against the pilings."]
    assert facts(prior_relevant(v, (9, 9, 9), set(), "Café", scoped=True)) == ["The horn sounds."]
    # A person knows what they took part in — and nothing that names nobody.
    assert facts(prior_relevant(v, (9, 9, 9), {"Leena"}, "Leena", scoped=True)) == [
        "The crossing is cancelled."]
    assert prior_relevant(v, (9, 9, 9), {"Nobody"}, None, scoped=True) == []


def test_heard_reaches_people_too(tmp_path):
    v = _tl_vault(tmp_path, "## B1.C1.S1\n- actors: A | heard: B | Told in passing.\n")
    assert len(prior_relevant(v, (2, 0, 0), {"B"}, None, scoped=True)) == 1

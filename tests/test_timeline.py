"""Timeline parsing and the prior-relevant oracle query."""
from pathlib import Path

from scribectl.core.timeline import (_pos_key, dangling_supersedes, load_events, prior_relevant,
                                     render_standing)
from scribectl.core.vault import Note


def _note(body: str) -> Note:
    return Note(path=Path("/x/Timeline.md"), meta={"type": "timeline"}, body=body)


def test_pos_key_forms():
    assert _pos_key("pre") == (-1, -1, -1)
    assert _pos_key("B1.C2.S3") == (1, 2, 3)
    assert _pos_key("b10.c1.s1") == (10, 1, 1)
    assert _pos_key("Chapter One") is None
    assert _pos_key("B1.C1.S1812.40") == (1, 1, 1812, 40)


def test_sub_position_sorts_inside_its_unit():
    """S1812.40 is after S1812 and before S1813, and still before a card at 18:13."""
    keys = [_pos_key(k) for k in ("B1.C1.S1813", "B1.C1.S1812.40", "B1.C1.S1812")]
    assert sorted(keys) == [(1, 1, 1812), (1, 1, 1812, 40), (1, 1, 1813)]
    assert (1, 1, 1812, 40) < (1, 1, 1813) and not (1, 1, 1813, 0) < (1, 1, 1813)


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


def test_supersede_corrects_by_appending():
    tl = (
        "## B1.C3.S1950\n"
        "- actors: Customers | loc: Café | Plans around the bus; the closure comes up in passing.\n"
        "## B1.C3.S1812\n"
        "- loc: Landing | No engine, no horn.\n"
        "- loc: Landing | Slush at the ramp.\n"
        "## Corrections\n"
        "## B1.C3.S1950\n"
        "- supersedes: B1.C3.S1950 | actors: Customers | loc: Café | Plans around the bus.\n"
        "## B1.C3.S1812\n"
        "- supersedes: B1.C3.S1812\n"
        "- loc: Landing | Slush at the ramp, thicker.\n"
    )
    events = load_events(_note(tl))
    # The correction stands in place of the old entry; a bare supersedes
    # retracts; a bullet after it at the same position is a plain restatement.
    assert [(e.pos_label, e.fact) for e in events] == [
        ("B1.C3.S1950", "Plans around the bus."),
        ("B1.C3.S1812", "Slush at the ramp, thicker."),
    ]
    assert events[0].actors == ["Customers"] and events[0].location == "Café"
    assert dangling_supersedes(_note(tl)) == []


def test_supersede_moves_an_event_and_never_reaches_forward():
    tl = (
        "## B1.C2.S2004\n- loc: Café | Crates come in.\n"
        "## B1.C2.S2005\n- supersedes: B1.C2.S2004 | loc: Café | Crates come in.\n"
        "## B1.C2.S2010\n- supersedes: B1.C2.S2015 | loc: Café | Closing.\n"
        "## B1.C2.S2015\n- loc: Café | Lights off.\n"
    )
    events = load_events(_note(tl))
    assert [e.pos_label for e in events] == ["B1.C2.S2005", "B1.C2.S2010", "B1.C2.S2015"]
    # S2015 had no bullet before the correction, so it corrected nothing.
    assert dangling_supersedes(_note(tl)) == ["B1.C2.S2015"]
    assert dangling_supersedes(_note("## pre\n- supersedes: Chapter One | x\n")) == ["Chapter One"]


def test_supersede_one_bullet_by_ordinal():
    tl = (
        "## pre\n- The founding lie.\n- The old bridge.\n"
        "## B1.C1.S1\n- They met.\n"
        "## pre\n- supersedes: pre#2 | The old ferry.\n"
    )
    assert [e.fact for e in load_events(_note(tl))] == ["The founding lie.", "They met.", "The old ferry."]
    assert dangling_supersedes(_note(tl)) == []
    # Ordinals count bullets already written, so a later one cannot be named early.
    assert dangling_supersedes(_note("## pre\n- a\n- supersedes: pre#3 | b\n- c\n")) == ["pre#3"]


def test_render_standing_applies_corrections_and_drops_prose():
    n = _note(
        "Prose the reviewer must not hold over the voicer.\n\n"
        "## B1.C1.S1812\n"
        "- actors: Tavi | loc: Landing | heard: Café | Engine, then horn.\n"
        "- actors: Tavi, Leena | loc: Landing | The ramp goes down.\n"
        "## Corrections\n\nWhy the horn moved.\n\n"
        "## B1.C1.S1812\n"
        "- supersedes: B1.C1.S1812#1 | actors: Tavi | loc: Landing | Her engine.\n"
        "## B1.C1.S1812.40\n"
        "- actors: Tavi | loc: Landing | heard: Café | Her horn.\n")
    assert render_standing(n) == (
        "## B1.C1.S1812\n"
        "- actors: Tavi, Leena | loc: Landing | The ramp goes down.\n"
        "- actors: Tavi | loc: Landing | Her engine.\n"
        "\n## B1.C1.S1812.40\n"
        "- actors: Tavi | loc: Landing | heard: Café | Her horn.\n")

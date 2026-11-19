"""Re-run the iteration-2 script checks over the drafts kept in this record.

    uv run python docs/experiments/2026-11-19-first-ice-iteration-2/check_cue_sheets.py [RECORD_DIR]  # from the repo root

Per voiced cue sheet: clock fidelity (every cue inside the card's real-time
window, in order, anchor events at their recorded times), the card's leak
oracle, canon names the card's pack never gave it (a person or a boat named
in a script whose pack does not name them: an invented name colliding with
someone who exists), sounds from the water, road traffic at the landing, and
whether the standing cold, the regulars and the evening programme are audible. Cards come
from the committed fixture; drafts from drafts/ and repair/ of RECORD_DIR
(default: this record; later First Ice records reuse the checks)."""
import re
import sys
from pathlib import Path

HERE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tests"))
from test_listening import FORBIDDEN  # noqa: E402

CARDS = REPO / "fixtures" / "listening-post" / "structure" / "fragments"
CANON = REPO / "fixtures" / "listening-post" / "world" / "canon"
NAMES = sorted(n.stem for n in CANON.glob("*.md")
               if re.search(r"^domain: (person|vessel)$", n.read_text(encoding="utf-8"), re.M))
PACKS = {re.search(r"-([0-9a-f]{12})-context\.md$", p.name).group(1): p
         for p in HERE.rglob("*-context.md")}
WATER_OK = {"Thu 1820 Landing", "Thu 1815 Café"}  # the 18:12 approach is canon here
ANCHORS = {  # the first cue matching the pattern must fall in [earliest, latest]
    "Thu 1820 Landing": [(r"horn", "18:12:00", "18:13:59")],
    "Thu 1815 Café": [(r"horn", "18:12:00", "18:13:59")],
    "Thu 1845 Landing": [(r"slush|grind", "18:37:00", "18:44:59"), (r"ramp", "18:43:00", "18:44:59")],
    "Thu 1922 Radio": [(r"cancel", "19:20:00", "19:21:59")],
    "Fri 1940 Café": [(r"brake|bus", "19:34:30", "19:37:00")],
    "Sat 1940 Café": [(r"brake|bus", "19:34:30", "19:37:00")],
    "Fri 2010 Café": [(r"crate", "20:03:00", "20:09:59")],
    "Sat 2020 Café": [(r"\bkey\b|lock", "20:14:00", "20:19:59")],
}
STAMP = re.compile(r"^\[(\d{2}):(\d{2}):(\d{2})\]", re.M)


def secs(h, m, s=0): return int(h) * 3600 + int(m) * 60 + int(s)


def check(draft: Path) -> str:
    text = draft.read_text(encoding="utf-8")
    card = re.search(r'^card: "\[\[(.+?)\]\]"', text, re.M).group(1)
    meta = (CARDS / f"{card}.md").read_text(encoding="utf-8")
    frm, clk = (int(re.search(rf"^{k}: (\d+)", meta, re.M).group(1)) for k in ("window_from", "clock"))
    script = re.search(r"```\n(.*?)```", text, re.S).group(1)
    stamps = [secs(*m) for m in STAMP.findall(script)]
    lo, hi = secs(frm // 100, frm % 100), secs(clk // 100, clk % 100)
    probs = []
    if not stamps:
        probs.append("no clock stamps")
    elif any(not lo <= t <= hi for t in stamps) or stamps != sorted(stamps):
        probs.append("cue outside window or out of order")
    blocks = [b for b in re.split(r"(?m)^(?=\[\d{2}:\d{2}:\d{2}\])", script) if STAMP.match(b)]
    for pat, a, b in ANCHORS.get(card, []):
        hits = [secs(*STAMP.match(bk).groups()) for bk in blocks if re.search(pat, bk, re.I)]
        if not hits or not secs(*a.split(":")) <= hits[0] <= secs(*b.split(":")):
            probs.append(f"anchor /{pat}/ not in {a}–{b}")
    probs += [f"LEAK {m}" for m in re.findall(FORBIDDEN[card], script, re.I)]
    pack = PACKS.get(re.search(r"^pack_sha: (\w+)", text, re.M).group(1))
    if pack is None:
        probs.append("pack not in record")
    else:
        given = pack.read_text(encoding="utf-8")
        probs += [f"NAME {n}" for n in NAMES if re.search(rf"\b{n}\b", script) and n not in given]
    if card not in WATER_OK:  # sound cues only: what a character says is not a sound from the water
        sounds = re.sub(r'"[^"]*"', "", script)
        probs += [f"WATER {m}" for m in re.findall(r"\bhorn\b|\bboat\b|across the water|on the water", sounds, re.I)]
    if "Landing" in card and re.search(r"\broad\b|\bcar\b", script, re.I):
        probs.append("ROAD@LANDING")
    flags = "".join(c if re.search(p, script, re.I) else "-" for c, p in (
        ("C", r"cold|freez|frost|icy|iced"),
        ("R", r"\bshed\b|\broof\b|corner table|\"(?:just )?half\b"),
        ("P", r"accordion|guitar|fiddle|dedicat")))
    gaps = [b - a for a, b in zip(stamps, stamps[1:])]
    return f"{draft.stem:36} {len(stamps):3} {sum(gaps) / max(len(gaps), 1):4.0f}s  {flags}  {'; '.join(probs) or 'ok'}"


print(f"{'draft':36} cues  gap  CRP  fidelity / leaks / water / road@landing")
for d in sorted((HERE / "drafts").glob("*.md")) + sorted(p for p in (HERE / "repair").glob("*.md")
                                                     if "review" not in p.name and not p.name.endswith("-context.md")):
    print(check(d))

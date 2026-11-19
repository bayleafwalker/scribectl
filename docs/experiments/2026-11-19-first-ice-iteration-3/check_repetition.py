"""Count lines that recur nearly word for word across fragments of one record.

    uv run python docs/experiments/2026-11-19-first-ice-iteration-3/check_repetition.py [RECORD_DIR]

RECORD_DIR defaults to this record; pass the iteration-2 record for the
baseline. A record's listened set is drafts/ with any repair/ draft standing in
for its card's original. Every quoted utterance of four words or more is
compared with every utterance in *other* fragments; a pair whose word sequence
matches at 0.75 or more (difflib ratio) counts as a near-verbatim repeat.
Recurrence of a habit in new words is the goal and does not count."""
import re
import sys
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

RECORD = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
THRESHOLD = 0.75


def listened(record: Path) -> dict[str, str]:
    """card -> script of the draft the listeners heard."""
    out = {}
    for sub in ("drafts", "repair"):  # repair overrides the original
        for d in sorted((record / sub).glob("*.md")):
            if "review" in d.name:
                continue
            text = d.read_text(encoding="utf-8")
            card = re.search(r'^card: "\[\[(.+?)\]\]"', text, re.M).group(1)
            out[card] = re.search(r"```\n(.*?)```", text, re.S).group(1)
    return out


def utterances(script: str) -> list[str]:
    words = (re.findall(r"[a-z']+", q.lower()) for q in re.findall(r'"([^"]+)"', script))
    return [" ".join(w) for w in words if len(w) >= 4]


scripts = listened(RECORD)
said = [(card, u) for card, s in scripts.items() for u in utterances(s)]
repeats = [(a, b, r) for a, b in combinations(said, 2) if a[0] != b[0]
           and (r := SequenceMatcher(None, a[1].split(), b[1].split()).ratio()) >= THRESHOLD]
print(f"{RECORD.name}: {len(scripts)} fragments, {len(said)} utterances of 4+ words, "
      f"{len(repeats)} near-verbatim repeats across fragments")
for (ca, ua), (cb, ub), r in sorted(repeats, key=lambda x: -x[2]):
    print(f"  {r:.2f}  {ca}: \"{ua}\"\n        {cb}: \"{ub}\"")

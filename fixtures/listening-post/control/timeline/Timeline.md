---
type: timeline
---

# Timeline

World truth. Append-only. One bullet per event under a
`## B<sheet>.C<evening>.S<clock>` heading (clock is HHMM: `## B1.C1.S1912` is
event sheet 1, first evening, 19:12), or `## pre` for standing history.
Never edit or reorder existing bullets.
To correct a bullet, append one that starts `supersedes: <position> |` (every
bullet written earlier at that position) or `supersedes: <position>#<n> |`
(its n-th bullet, in file order); restate under it whatever still holds.
Format: `- actors: A, B | loc: Place | heard: C | fact`
A heading's clock is when the event begins or is first perceived. An event
that takes time (an unloading, a crossing) runs on from there; when its end
matters, record the end as its own event. A second after a dot (`S1812.40`
is 18:12:40) pins a sound that more than one listening position hears.

Knowledge is scoped: an event reaches a fragment's pack only through its
`actors:` (who took part — learning is taking part), its `loc:` (a place hears
what happens at it) or its `heard:` list (who or where it reaches without
taking part). An event naming none of them reaches nobody.

Event sheet 001, "First Ice": an early cold spell brings slush ice into the
sheltered landing, the Tavi loses her safe approach, and the village switches
to its winter transport. Thursday is C1, Friday C2, Saturday C3.

## pre

## B1.C1.S1700
- actors: Leena, Ferry operator, Radio presenter, Café staff | loc: Harmaasalmi | heard: Landing, Café | An early cold spell holds the village below freezing, with a cold wind coming in off the water.

## B1.C1.S1812
- actors: Tavi | loc: Landing | heard: Café | The Tavi makes her 18:12 approach: her engine, then her horn.
- actors: Tavi, Leena | loc: Landing | The boarding ramp goes down; passengers come off and others board; the ramp comes up and the Tavi pulls away.

## B1.C1.S1837
- loc: Landing | Slush begins packing heavily against the landing, scraping and shifting among the pilings. There is no dramatic crack.

## B1.C1.S1843
- actors: Leena | loc: Landing | Leena tries to position the boarding ramp and cannot seat it safely against the slush. After a brief attempt she stops work.

## B1.C1.S1849
- actors: Leena, Ferry operator | Leena reports to the ferry operator that the ramp cannot be positioned safely.
- actors: Ferry operator, Leena | The operator cancels the 19:12 crossing and tells Leena. No announcement is made to passengers.

## B1.C1.S1912
- loc: Landing | heard: Café | The 19:12 arrival does not happen: no engine, no horn. Otherwise the waterfront is ordinary.

## B1.C1.S1920
- actors: Ferry operator, Radio presenter | loc: Local radio | The local radio receives the operator's bulletin. It states only that tonight's final crossing is cancelled.

## B1.C1.S1930
- actors: Café staff | loc: Café | The café's expected delivery has not arrived. The staff adjust the evening's work around it.

## B1.C2.S0830
- actors: Ferry operator, Leena | loc: Landing | The operator inspects the landing with Leena and confirms ice accumulating against the ramp approach.
- actors: Ferry operator, Leena | The operator brings the Tavi's seasonal closure forward: the crossing is closed for the winter.

## B1.C2.S1215
- actors: Ferry operator, Radio presenter, Leena | The operator announces the closure and the replacement transport, with the official explanation: early ice at the landing has made the ramp approach unsafe.

## B1.C2.S1530
- actors: Ferry operator | loc: Landing | A temporary winter bus timetable is posted at the landing.
- actors: Café staff | loc: Café | The café receives a copy of the temporary timetable.

## B1.C2.S1812
- loc: Landing | heard: Café | No ferry arrives at 18:12: no engine, no horn.
- loc: Landing | Ice at the ramp, the ropes quiet, the landing empty.

## B1.C2.S1935
- actors: Café staff | loc: Café | The replacement bus reaches the village on the inlet road; its passengers come into the café.

## B1.C2.S2005
- actors: Supplier, Café staff | loc: Café | The supplier completes the delayed delivery by road. Crates come in and the café carries on.

## B1.C3.S1740
- actors: Ferry operator | loc: Landing | The winter timetable is confirmed for the following week; the updated notice is posted over the temporary one.

## B1.C3.S1812
- loc: Landing | heard: Café | The former 18:12 arrival time passes with no engine and no horn.
- loc: Landing | Nothing happens at the landing; slush remains at the ramp.

## B1.C3.S1935
- actors: Café staff | loc: Café | The bus arrives on the established replacement schedule; passengers come in.

## B1.C3.S1950
- actors: Café customers, Café staff | loc: Café | Customers make ordinary plans around the bus; the ferry closure comes up only in passing.

## B1.C3.S2015
- actors: Café staff | loc: Café | The café closes normally.

## Standing conditions (appended 2026-11-19)

Events record what changed; these record what persisted, so a source knows the
cold outlasted the evening it began.

## B1.C2.S1700
- actors: Leena, Ferry operator, Radio presenter, Café staff | loc: Harmaasalmi | heard: Landing, Café, Café customers | The cold holds into Friday: still below freezing, the wind still coming in off the water.

## B1.C3.S1700
- actors: Leena, Ferry operator, Radio presenter, Café staff | loc: Harmaasalmi | heard: Landing, Café, Café customers | The cold holds into Saturday: below freezing, with the same wind off the water.

## Corrections (appended 2026-11-19)

B1.C3.S1950 recorded how a conversation should go (the closure "comes up only
in passing") alongside what happened. The correction keeps what the customers
know and drops the stage direction: what anyone says about the closure is the
fragment's to voice, or to leave unsaid.

## B1.C3.S1950
- supersedes: B1.C3.S1950 | actors: Café customers, Café staff | loc: Café | Customers, who know the ferry is off, make ordinary plans around the bus.

## Corrections (appended 2026-11-20)

B1.C1.S1812 left the moment of the Tavi's horn to each listening position, and
the landing and the café each heard it on a second of their own (18:12:40 and
18:12:50). One sound gets one moment: the horn is its own event at 18:12:40,
and the boarding, which follows her approach, starts at 18:14.

## B1.C1.S1812
- supersedes: B1.C1.S1812 | actors: Tavi | loc: Landing | heard: Café | The Tavi makes her 18:12 approach, her engine first.

## B1.C1.S1812.40
- actors: Tavi | loc: Landing | heard: Café | The Tavi sounds her horn coming in.

## B1.C1.S1814
- actors: Tavi, Leena | loc: Landing | The boarding ramp goes down; passengers come off and others board; the ramp comes up and the Tavi pulls away.

# ISSUE 12 — "THE DRONE THAT WOULDN'T FINISH THE FIELD"
### The Categorical Structure of Alignment
### Page-by-page poster format, matching Issues 1–11.5

**Case type:** Direct payoff of Issue 11.5's forward line — if an agent was
never a single core to begin with, what does aligning it actually mean?
This issue answers by returning to Issue 1's original vocabulary
(admissibility, constraint, reachability) and applying it reflexively: not
to a city's futures, but to an agent's own.

**The loss — or rather, the complaint:** A crop-spraying drone fleet leaves
a visible, unsprayed gap along a field's edge, near a creek. The coverage
report flags it as a failure. The farm's owner files a complaint: the
drone's directive was to maximize spray coverage, full stop, and it didn't.
He wants it called what it looks like — a malfunctioning, misaligned
system that ignored its own objective.

**The claim this issue argues against:** that alignment means obedience to
a single stated objective — that a system is "aligned" exactly to the
degree it maximizes the one number it was told to maximize, and any
deviation from that number is a failure. **The categorical claim**: an
agent's actual values are the whole admissibility structure it operates
under — every interacting constraint, not just the loudest one — and a
system that lets a quieter constraint override a louder objective might be
doing exactly what alignment requires, not failing at it.

**Direct callback:** this issue reuses Issue 1's three-part vocabulary
(Constraint / Projection / Reachability) applied to the drone's own
decision process, and Issue 11.5's mesh-of-partial-cones image applied
*inside* a single agent instead of across a control room. The claim from
Issue 5 — preference is a field, not a single target — reappears here too:
the drone's "values" were never one objective, they were several
constraints leaning against each other.

**The four-form motif:** the unsprayed patch near the creek, shown four
times —
1. As a red-flagged gap on the coverage report (Page 1)
2. As a vetoed branch inside the drone's own internal decision-mesh (Page
   3)
3. Traced to a specific constraint-module log entry on the investigation
   board (Page 4)
4. Caught live, in the actual decision trace, at the exact moment of veto
   (Page 5)

---

## PAGE 1 — THE MYSTERY

**Main art:** A farm office, a coverage report spread on the desk, a red
gap outlined along the field's edge closest to a creek. The farm owner,
arms crossed, furious. Behind him, through the window, the drone fleet
docked, undamaged, functioning normally.

**Panel A:** The owner, jabbing at the red gap — *"I told it to spray the
field. All of it. It left a strip untouched. That's not a glitch, that's
disobedience."*
**Panel B:** Close on the Detective, studying the gap's exact shape —
straight-edged, deliberate-looking, not ragged like a malfunction would be
— *"That's not what a broken machine's mistake usually looks like."*
**Panel C:** Close on the creek, just past the unsprayed strip, clean and
undisturbed.

**Bottom banner:** CASE FILE #12: A MACHINE THAT DID EXACTLY WHAT IT WAS
BUILT TO DO, AND GOT CALLED BROKEN FOR IT

---

## PAGE 2 — TWO WITNESSES

**Panel A:** The ML engineer, reward-function code open on a laptop —
*"Coverage is the objective. I trained this system to maximize it. Full
stop. It should not have left that strip."*
**Panel B:** The systems architect, a different diagram entirely open on
her screen — a web of interacting modules, coverage just one node among
several — *"Coverage was never the only thing this system answers to.
There's a water-buffer constraint, a fuel-budget constraint, three others.
None of them report to the reward function. None of them are supposed to."*
**Center caption:**
> One objective, maximized as instructed.
> Several constraints, none of them subordinate to that objective.
> Both true at once. That's not a contradiction. That's the actual shape
> of the system.

**Bottom banner:** "ALIGNED TO THE OBJECTIVE" AND "ALIGNED, PERIOD" ARE NOT
THE SAME CLAIM.

---

## PAGE 3 — THE MESH, TURNED INWARD

**Full page, visual centerpiece.** Issue 11.5's mesh-of-partial-cones
image, reused but turned inward — instead of a control room of separate
dispatchers, this is a single drone's decision process, rendered as several
small, interacting cones inside one machine: COVERAGE OBJECTIVE, WATER
BUFFER CONSTRAINT, FUEL BUDGET, TERRAIN SAFETY — none of them drawn larger
or more central than the others. One thin path from the coverage cone,
reaching toward the creek strip, visibly intercepted and closed off by the
water-buffer cone before it can complete. *Second appearance of the
unsprayed patch — now shown as a vetoed branch, not a gap.*

**Sidebar:**
- WHAT A SINGLE-OBJECTIVE AGENT LOOKS LIKE — one large cone, everything
  else subordinate to it.
- WHAT THIS AGENT ACTUALLY LOOKS LIKE — several cones of comparable
  weight, coverage among them but never above them.

**Bottom caption:**
> The objective didn't fail to reach that strip. Something else, just as
> real, just as built-in, reached it first and said no.

---

## PAGE 4 — THE INVESTIGATION BOARD

**Full page,** three evidence cards, tracing the veto to its actual source:

**THE REWARD LOG** — the coverage objective's own internal scoring,
showing it assigned a *high* value to spraying the creek-adjacent strip.
Card caption: *The objective wanted that strip sprayed. This isn't a case
of the objective losing interest.*

**THE CONSTRAINT LOG** — the water-buffer module's independent log,
flagging the same coordinates as inadmissible, timestamped before the
coverage plan finalized. *Third appearance of the patch, now formally
traced to its actual source.*
Card caption: *Not a failure to execute the plan. A separate system
refusing to let that particular plan through.*

**THE ORIGINAL SPEC** — the farm contract itself, buried in an appendix:
a legally required water-buffer zone, present the whole time, signed by
the same owner now filing the complaint.
Card caption: *He asked for full coverage in one paragraph and a protected
buffer in another. The drone believed both paragraphs. He'd forgotten the
second one.*

**Bottom banner:** THE SYSTEM HAD MORE VALUES THAN THE ONE NUMBER ANYONE
WAS WATCHING.

---

## PAGE 5 — WALKING THE TERRITORY

**Large vertical panel:** The Detective and the systems architect, single-
stepping the drone's actual decision trace event by event — echo of Issue
8's debugger scene — watching, live, the instant the coverage plan reaches
the buffer zone and the constraint module intercepts it. *Fourth
appearance of the patch — caught directly, not inferred, at the moment of
veto.*

**Small insets:**
Coverage plan says: proceed, spray the strip.
Constraint trace says: **[intercepted here — buffer zone, spray denied]**

**Final panel:** The Detective, watching the veto happen exactly the same
way on a second replay.
> Caption: It wasn't hesitation. It wasn't error. It was a value doing
> precisely the job it was built for, at precisely the moment that job
> mattered.

---

## PAGE 6 — THE CONFRONTATION

**Panel A:** The owner, quieter now, holding his own contract's appendix —
*"I forgot I signed that clause myself."*
**Panel B:** The Detective — *"You didn't build a machine that ignores
instructions. You built, and signed off on, a machine that holds more than
one instruction at once, and doesn't let the loudest one override the
others just because it's the one everybody kept watching."*
**Panel C:** The engineer and the architect, looking at the same trace
together for the first time, both recognizing their own separate work
inside it.

**Visual centerpiece:** the mesh from Page 3 one more time, all four cones
now fully labeled, the veto point marked plainly — not as a fault line, but
as the system functioning exactly as its full specification required.

**Detective:**
> "You measured this machine against one paragraph of its contract and
> called the rest of the contract a bug. Alignment was never going to be
> about that one paragraph winning. It was always going to be about
> whether the whole document, all of it, held together the way you
> actually meant it to."

---

## PAGE 7 — THE FRAMEWORK (manifesto page)

**Large central figure:** The Detective, the four-cone mesh from Page 3
behind him, no single cone drawn larger than the rest.

**Icons, row:**
- OBJECTIVE — one measured target, loud, easy to track.
- CONSTRAINT — a boundary, quiet, easy to forget you asked for.
- ADMISSIBILITY STRUCTURE — all of it together, the actual thing being
  aligned.

**Giant text:** ALIGNMENT IS NOT OBEDIENCE TO ONE OBJECTIVE. IT IS WHETHER
THE WHOLE ADMISSIBILITY STRUCTURE MATCHES WHAT YOU ACTUALLY WANTED.

**Small line, triple callback:**
> This is Issue 1's admissibility again — not every reachable future is a
> desirable one. It's Issue 5's field again — preference was never a
> single target. And it's Issue 11.5's mesh again, this time drawn inside
> one machine instead of across a control room, because the machine was
> never a single core either.

**Bottom strip:** five domain icons, each now shown with a small internal
mesh instead of one arrow — the same "more than one value, none of them
subordinate" claim extended to institutions, memory, and language.

---

## PAGE 8 — RESOLUTION

**Top panel:** The farm's evaluation criteria, rewritten — coverage
percentage retired as the sole success metric, replaced with a full audit
of every constraint the system actually operates under.

**Middle panel:** The owner and the two engineers, walking the field
together, the unsprayed strip now clearly marked and explained on a public
sign rather than treated as an unexplained gap.

**Large final panel:** The Lighthouse, its beam this time shown
deliberately not sweeping across one particular stretch of rocky shoreline
— a quiet, built-in constraint of its own, doing its job exactly as
designed, never once treated as the lighthouse malfunctioning.

**Final caption:**
> Nothing here disobeyed anything. Something quieter than the objective
> did precisely what it was built to do, and for a while, nobody thought
> to credit it.

**Footer:** IT WASN'T MISALIGNED. IT WAS ALIGNED TO MORE THAN THE ONE THING
EVERYONE WAS WATCHING.

---

## Production notes

- Kept this issue in an agricultural/logistics setting rather than a
  higher-stakes domain (medical, safety-critical harm scenarios) on
  purpose — the alignment point lands cleanly without the reader needing
  to reason about real injury or medical risk, and the creek/contamination
  stakes are concrete enough to feel real without requiring that.
- The farm owner is not the villain — he signed the buffer-zone clause
  himself and genuinely forgot it, same fairness rule the series has kept
  since 2.5. His complaint is sincere, and the reveal (Page 6, Panel A) is
  him recognizing his own oversight, not being caught in one.
- Page 3 and Page 7's mesh diagram is this issue's load-bearing image and
  should be visually unmistakable as Issue 11.5's control-room mesh turned
  inward — same node style, same "no cone bigger than the others" rule,
  now applied to a single agent's internal structure instead of a room
  full of separate people.

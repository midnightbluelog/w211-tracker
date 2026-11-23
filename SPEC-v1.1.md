# Midnight Garage: spec v1.1 (DRAFT)

> **"Ask, don't guess."** When the app doesn't know something, it helps the owner find out, in words that fit how much they know.

Owner: midnightblue · Builder: Claude · Drafted: 2026-11-23
Status: **approved 2026-11-23.** Decisions below: I went with Claude's suggestions, and the why is written next to each.

## Decisions (approved)
1. "Looks fine" counts **half credit** for health. Why: someone looked, but nothing was serviced.
2. A "looks fine" check is trusted for **3 months**, then the app asks again. Why: fluids change slowly, but a check is only a snapshot.
3. "Looks bad" → **marked overdue + shown on the dashboard.** Why: a bad check is a real warning, so it gets treated like one.
4. If the AI thinks my level is wrong, it **only adjusts that answer** and never changes my setting. Why: I stay in control, and the AI can guess wrong.
5. Default level: **"the basics."** Why: it's the safe middle, neither too simple nor too technical.
6. Quick fixes: **all four.** Why: they're small and they came from my own testing.

---

## Why v1.1

Two ideas from the post #2 interview:
1. The fake 100% happened because the app ignored what it didn't know. Now it scores unknowns honestly (64%), but it still just sits there. **It should ask, and show the owner how to check.**
2. **The words people use show what they know.** "The thing under the hood" and "expansion tank" need different answers. The app should talk to beginners *and* pros.

Plus a few fixes from my own improve-it list (2026-11-17).

---

## Milestone A: Guided checks (1–2 sessions)

For every service with **NO DATA** (right now: brake fluid, coolant, glow plugs), the Service screen shows a **"check it"** button that opens a short guide:

- **How to check it**, in 2–4 simple steps (e.g. brake fluid: find the reservoir, look at the colour, check the level)
- **What you might see**: fine / getting old / bad, with what each one looks like
- **Quick answer buttons:**
  - "It was done at ___ km / on ___" → logs it like a normal service
  - "I checked: looks fine"
  - "I checked: looks bad"
  - "I can't check it" → suggest asking the mechanic at the next visit

The guide text lives in the knowledge file (like the intervals), so it's plain data you can edit, not code.

**✏️ Your decisions:**
1. Does "I checked: looks fine" count as data for the health score? If yes, how much? (Full credit like a real service, half credit, or "known but not serviced"?)
2. How long is a "looks fine" check trusted before the app asks again? (e.g. 3 months? 6 months? until the next oil change?)
3. "Looks bad": what should happen? (Mark it overdue? Add it to the watch list? Show a warning on the dashboard?)

**Done when:** I can turn all 3 unknowns on my own car into real data, and the health score updates honestly.

---

## Milestone B: Talks at your level (1 session)

**Simple version (reliable, in code):**
- On the Car screen, one question: "How much do you know about cars?"
  - "Not much, explain everything"
  - "The basics"
  - "Mechanic level, skip the basics"
- Saved with the car. Guided checks and the AI mechanic both use it.

**Smart version (on top, from the AI):**
- The AI mechanic is told the owner's level *and* to judge from the words they use.
- Two buttons under each answer: **"simpler please"** / **"skip the basics"**, so the owner can correct it.

**✏️ Your decisions:**
4. If the AI thinks you know more (or less) than your setting, should it **change the setting itself**, or only **adjust that one answer**?
5. What's the default before the owner picks? (I'd suggest "the basics", but it's your call.)

**Done when:** the same question ("my car shakes at idle") gets a clearly different answer at "not much" vs "mechanic level", and both are useful.

---

## Milestone C: Quick fixes from my own testing (1 session)

From the 2026-11-17 improve-it list:
- [x] **Year only accepts 4 digits** ("20040913" gets refused with a clear message)
- [x] **Duplicate warning:** "You already logged oil change at 409,000 km. Save anyway?"
- [x] **Oil spec field** on oil changes (e.g. 5W-40, MB 229.5) instead of only the brand
- [x] **The app refuses to start twice** if it's already running (no more ghost servers)

**✏️ Your decision:**
6. All four, or only some? (Each is small.)

---

## NOT in v1.1 (on purpose)

| Idea | Why not now |
|---|---|
| Claude API as the mechanic's brain | Needs a paid API key (and the payment card). Next, as roadmap Phase 2 |
| **Car journal (my idea, 2026-11-23):** photos of the car, how it was, what changed after each job, notes on how it drives. A personal journal per car, and the AI mechanic reads it as data | **v1.2, next after v1.1.** Works for one owner, no community needed. Pairs with multi-day projects (the restoration = one journal entry with before/after photos) |
| Multi-day projects (start + end date) | Real need, but bigger. v1.2, together with the journal |
| Community / fan space | v2+, needs other users first |
| Live OBD2 dashboard | v2 idea, needs the plug |
| Other cars | After the W211 version is solid |

---

## Your hands-on piece

Write **one guided check yourself** in the knowledge file: glow plugs, from what you know about your own car (cold starts, the coil light). Claude writes the other two; you review them.

**Estimated total:** 3–4 sessions.

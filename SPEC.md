# Midnight Garage: product spec (v1)

> An AI mechanic and service log for owners of classic Mercedes and BMWs.
> **v1 proves it on one car: my 2004 W211 E220 CDI.**

Owner: midnightblue · Builder: Claude · Last updated: 2026-11-16

---

## The problem

Owners of older Mercedes and BMWs love their cars but juggle scattered receipts, guess at service intervals, and spend hours on forums asking the same questions. Generic AI gives generic answers because it doesn't know *their* car's history or the known problems of *their* model.

## The idea

One place that:
1. makes logging a service **fast**
2. knows the **service intervals and common problems** of the exact model and engine
3. has an **AI mechanic** that answers using both: the car's real history plus model knowledge

---

## v1 scope: ONE car, done really well

**Car:** Mercedes W211 E220 CDI (OM646, 2002–2009). Mine first.
**Runs:** locally on my PC, free (Ollama). The AI brain stays swappable for Claude later.

### Milestone 1: Fast logging (1–2 sessions)
- [x] One-tap service chips instead of a dropdown
- [x] Odometer remembers the last mileage, so I only adjust it
- [x] **Log a whole job at once** (e.g. "restoration" = suspension + brakes + front end in one save)
- [x] Edit an entry (delete already done ✅)
- [x] **Car profile ("My Mercedes"):** created the moment you enter model, year and mileage, then remembered everywhere
- [x] **Optional VIN:** paste it and the app fills in what it can decode itself (maker, model series like 211, model year, body/engine code), so you type less
- [x] Mileage input styled like an odometer (the function now, the full styling in Milestone 4)
- **Done when:** logging a job takes under 15 seconds

### Milestone 2: W211 knowledge base (2 sessions)
- [x] A data file with the OM646 / W211 service intervals
- [x] Known issues by mileage (injector seals, turbo, EGR, engine mounts, timing chain...), each with symptoms and a source
- [x] "What's due" uses this data instead of my generic guesses
- **Done when:** at 410,000 km the app warns me about the things that actually matter at that mileage

### Milestone 3: Two mechanic modes (2 sessions)
- [x] **Quick question:** ask anything, get a short answer using my history + the knowledge base
- [x] **Diagnosis session:** the mechanic asks *me* 3–5 questions first (what sound, when, engine hot or cold...), then gives a ranked list of likely causes
- [x] Safety-critical topics (brakes, steering) always end with "see a mechanic"
- **Done when:** a diagnosis session for "grinding when braking" asks sensible questions and ends with a clear answer

### Milestone 4: The luxury redesign (1 session)
- [x] Calm, premium, fast. Inspired by classic car culture, never using Mercedes/BMW logos
- [x] Our own animated emblem (a vintage-style crest, not the Mercedes star). Click it and the car view opens
- [x] A "my car" view with an illustration of the W211, plus key stats
- [x] Instrument-cluster look: odometer and gauges for mileage and what's due
- **Rule:** design comes LAST, after it works

### Milestone 5: Ship (1 session)
- [x] README, screenshots, make the repo public (2026-11-23)
- [x] Post #2 on the blog: "I used to keep track of my car in my head" (2026-11-23)

**Estimated total:** about 2 weeks at 1–2 hours a day.

---

## NOT in v1 (on purpose)

| Idea | Why not now |
|---|---|
| Other models (BMW E39/E46, other Mercedes) | v2, after the W211 version works |
| User accounts, other people's cars | needs hosting and security; v3 |
| Paid sessions | needs a product people already love first |
| Mobile app | the web dashboard works on a phone screen already |
| Receipt photos / scanning | nice, not essential |
| "All the data in the world" | data is built one model at a time, accurately |

## Rules for building it

1. **One milestone at a time.** No jumping ahead.
2. **I write a short spec for each piece.** Claude builds. **I run it and verify it myself.**
3. **No design work before Milestone 4.**
4. Every milestone gets a few lines in the build log.
5. If an idea comes up mid-build, it goes on the "Later" list below, not into the code.

## Later (idea parking lot)

- BMW E39 / E46 support
- Paid deep-diagnosis sessions
- Share a car's service history when selling it (proof it was looked after)
- Reminders ("oil change in 500 km")
- Save past mechanic conversations, so it remembers what you already asked about

## Not possible (and why)

- **Logging in with an official Mercedes account to pull car details:** a 2004 W211 has no connected services, and car makers don't let outside apps into those accounts anyway. Our own "My Mercedes" car profile does the same job.
- **Full factory option list from the VIN:** Mercedes' detailed build data isn't openly published. The basic VIN structure is well known, so we decode that part ourselves; full option lists would need a paid third-party service (Later, maybe).
- **Using the real Mercedes or BMW logos:** they're trademarks. We design our own emblem instead.
- **An AI that "learns" by itself:** models don't learn from use. The mechanic gets smarter through better data (Milestone 2), your logs, and a better model later (Claude).

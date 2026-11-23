# Midnight Garage: spec v1.2, the car journal

Owner: midnightblue · Builder: Claude · Started: 2026-11-23
Status: **v1.2 BUILT 2026-11-23** (journal, photos, public/private, AI reads the notes). Tested on a copy. AI seeing photos = v1.3 (Claude API); sharing online = v2.

---

## The vision (my words)

> I want it to be open. Everyone can keep pictures of what they want related to their cars, for other people to check. It's also for car enthusiasts. Anything you want, the AI reads it and customizes its answers, and mentions things it saw in the pictures if they're related. Not just on your PC, in an open space. You can make it public or private.

## What that needs (honest)

| Part of the vision | What it takes | When |
|---|---|---|
| A journal with photos + notes for my car | Local feature, like the rest of the app | **v1.2 (now)** |
| Each entry marked public or private | Just a setting saved with the entry, ready for later | **v1.2 (now)** |
| The AI reads the journal *notes* | Same as the service history, works with the local AI | **v1.2 (now)** |
| The AI *looks at the photos* | A model that can see images. The small local model can't. Claude can (Phase 2, needs the payment card) | **v1.3, with the Claude API** |
| Public journals other people can browse | The app online: hosting, accounts and logins, photo storage, moderation | **v2, Phase 4 ("put it online")** |
| ⭐ Stars: people star photos, profiles and cars they like (my idea, 2026-11-23) | Accounts (so one person = one star), a star count per photo/car, a "most starred" view | **v2, with the online version** |

So v1.2 builds the journal so it's **ready** for the open version: the same entries, photos and public/private setting go online later without redoing anything.

## Decisions
1. ✅ **One entry = all of it:** photos (before/after possible), a title, a note (how it drives / what changed), optional link to a logged job, optional cost, mileage, and a mood. (2026-11-23, "yeah all that")
2. ✅ **Tied to anything:** an entry can stand alone (a road trip, a wash, a photo shoot) or link to a logged job like "restoration". (follows from 1)
3. ✅ **Public by default**, private with one tap. (2026-11-23) In v1.2 "public" only marks the entry for sharing; nothing leaves the PC until the app goes online (v2).
   - Guardrail (Claude's suggestion, built in when it goes online): photos get their hidden location data removed automatically, and the app reminds you to check for plates and faces before an entry is shared.
4. ✅ **Look: "modern, luxurious, vintage, fun, cool, and minimalistic."** Direction (draft): a vintage logbook that scrolls like a modern app. A timeline of entry cards: photo print, title in an elegant italic serif, date + mood, one-line note, mileage stamp, public/private badge. Tap to open. Filters: all / jobs / drives / private. Keep it minimal: lots of space, one accent colour, few details per card. (2026-11-23, mockup shown, to refine)

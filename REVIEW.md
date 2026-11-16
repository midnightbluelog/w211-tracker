# Your review guide: Milestones 1–4

Claude built these. Your job: **use it, read it, explain it.** Do it in two sittings (~1 hour each). Milestone 5 (going public + post #2) only happens after this review.

## Part A: Milestones 2–4 (do these after Part B below)

**Use it:**
- [ ] Check **What's due**: tap a service name to see *why* it matters. Is anything overdue for your real car?
- [ ] Read your **Watch list**: known W211/OM646 issues at 410,000 km. Tap each one. Do you recognise any symptoms?
- [ ] **Diagnosis session**: describe a real problem (or a made-up one), answer the 4 questions, read the result. Is it sensible?
- [ ] Tap the **emblem** (top left) to open the showroom view of your car
- [ ] Look at the **service health gauge**. Log a missing service and watch it change

**Read it:**

| File | Find this | What it does |
|---|---|---|
| `knowledge/w211_om646.json` | `intervals`, `issues` | The car's "brain data". Plain text you can edit. **Correct anything your mechanic disagrees with** |
| `knowledge.py` | `due_items()` | Your spec from day 4, now with time too: due when km **or** months run out, whichever comes first |
| `knowledge.py` | `watch_list()` | Issues relevant at your mileage, hiding ones you've already fixed |
| `mechanic.py` | `diagnose_start()` | Asks the model for 4 questions, and falls back to safe default questions if the model messes up the format |
| `mechanic.py` | `_with_safety()` | The **code** decides when to add the brakes/steering warning, not the model |

**Explain it:**
5. Why does `due_items()` check both km and months?
6. Why does `diagnose_start()` have `FALLBACK_QUESTIONS`?
7. Why is the safety warning added by code, not by the AI?

**Honest limits to know:**
- The knowledge base is built from common W211/OM646 owner and workshop knowledge, not an official Mercedes document. Show it to your mechanic and fix what they disagree with.
- The local 3B model is decent, not brilliant. It sometimes repeats itself or misses obvious causes. Claude would be much better once you have your card.

## Part B: Milestone 1

## 1. Use it (15 min)

```
cd "w211-tracker"
python dashboard.py
```

- [ ] Set up **My Mercedes**: paste your real VIN (it's on your carte grise / registration, or under the windscreen), press **Decode VIN**, add year and mileage, **Save car**
- [ ] Log the restoration as **one job**: tap oil change + brake pads + "+ other" (new suspension, front end, bodywork & paint), mileage, **Save job**
- [ ] Fix one entry with **✎**, delete a test one with **×**
- [ ] Update the odometer with **Update**
- [ ] Time yourself logging a job. The milestone goal is **under 15 seconds**. Did it pass?

Write down anything annoying. That's your list for "improve it."

## 2. Read it (30 min)

Open each file and find these parts. You don't need to understand every line, just **what each part does**.

| File | Find this | What it does |
|---|---|---|
| `vin.py` | `decode_vin()` | Splits the VIN: `vin[:3]` maker, `vin[3:6]` series, `vin[3:9]` variant |
| `vin.py` | `VARIANTS` | The list of exact models we know. **Your job: add more, one verified entry at a time** |
| `dashboard.py` | `/api/job` | Saves several services at once: one entry per service, same mileage |
| `dashboard.py` | `/api/edit` | Replaces one entry, but only after the safety check |
| `dashboard.py` | `bump_mileage()` | Logging a service at a higher mileage moves your odometer forward |
| `dashboard.html` | `selected` | The set of chips you've tapped |
| `dashboard.html` | `editing` | `null` normally; the entry you're fixing when you press ✎ |

## 3. Explain it (15 min)

Answer these in your own words (tell Claude, or write them in the build log):

1. What's the difference between `/api/job` and `/api/edit`?
2. Why does delete/edit check the service and mileage, not just the position?
3. Why can't the VIN tell us the model year on European cars?
4. Why is `car.json` in `.gitignore`?

## 4. Your hands-on piece

Add one model to `VARIANTS` in `vin.py` yourself. For example, a friend's car or another W211 variant you've verified. Then run `python vin.py` to test it.

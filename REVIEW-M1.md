# Your review guide: Milestone 1

Claude built this one. Your job tomorrow: **use it, read it, explain it.** About an hour.

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

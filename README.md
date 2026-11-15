# W211 maintenance tracker

A small Python tool that keeps track of every service on my 2004 Mercedes W211 E220 CDI and tells me what's due next.

It's my first project on the way to building AI agents. The plan is to give it an AI mechanic next.

## What it does

- **Log a service:** pick from common services (oil change, fuel filter, air filter...) or type your own, then add mileage, date and notes
- **Show history:** every service, newest first
- **What's due?** *(in progress)* enter your current mileage and see what's overdue, due soon, or fine

## Run it

Needs Python 3. No extra packages.

```bash
python tracker.py
```

Your log is saved to `service_log.json` next to the script. It stays on your machine and is not part of this repo.

## Roadmap

- [x] Step 1: log services and show history
- [ ] Step 2: "what's due" based on service intervals
- [ ] Step 3: ask an AI mechanic questions, answered using your own service history

## The story

I'm documenting the whole build, honestly, on my blog: [midnightbluelog.github.io](https://midnightbluelog.github.io)

*by midnightblue*

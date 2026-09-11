# Display Information Hierarchy

The display should answer one question first: **what should the player shoot now?** Persistent progress and flavor support that answer without competing with it.

## Gameplay Layout

| Band | Vertical range | Content |
|---|---:|---|
| Status | 0–160 | Player, ball, timers, and small temporary feature status |
| Objective | 160–315 | Mode title or the single current instruction |
| Score | 330–490 | Current player score, normally 112 px with a 10 px black outline |
| Progress | 570–725 | One actionable instruction plus no more than two counters |

- **Write instructions verb-first.** Use “SHOOT RIGHT RAMP,” not “RIGHT RAMP IS LIT.”
- **Show one immediate objective.** If a new state changes the best shot, replace the old instruction.
- **Keep persistent systems quiet.** Alamo and Manger Babies may appear on live gameplay screens, but never on rules, intro, finish, jackpot, or full-screen video slides.
- **Use the playfield for physical progress.** Grill lock count belongs on its inserts and physical balls; the display only announces when the grill is ready or changes state.
- **Reserve the center for score.** Jackpot names, progress, and rules must not cross the score band.

## Presentation Priority

| Priority | Use |
|---:|---|
| 500 | Live gameplay slide |
| 1000–1100 | Rules and mode-start cards |
| 1200 | Intro and completion clips |
| 1300 | Rare jackpot or major story clips |
| 9000+ | End-of-mode totals and system-level results |

Every presentation slide that temporarily covers gameplay must either expire into, or explicitly restore, the live gameplay slide. A transition must remove the outgoing slide in the same event that starts the incoming slide.

## Video and Audio

- **Keep looping episode audio underneath play.** Run it as a quieter bed (currently -5 dB) and duck the video bus whenever a voice callout plays.
- **Keep audio on one-shot story clips.** Intro, completion, and super-jackpot clips may carry their original audio.
- **Avoid distracting duplication.** Deliberate callouts take priority by ducking the episode audio; only remove dialogue from a loop when repetition becomes irritating in physical playtests.
- **Protect playability.** Routine shots receive effects or short callouts. Full-screen clips are reserved for mode starts, phase changes, completions, and major jackpots.
- **Restore the objective immediately.** The live instruction must return as soon as a clip ends.

## Copy Limits

- Live instruction: one line, preferably under 34 characters.
- Rules card: at most two actions and three lines.
- Progress label: one noun and one fraction, such as `BEERS 4 / 6`.
- Avoid repeating the mode title on the live screen when the art already identifies it.

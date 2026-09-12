# King of the Hill Pinball

**A full-size homebrew pinball machine created by Nick Taseris**

King of the Hill Pinball is my original, fan-built interpretation of the world
of *King of the Hill* as a physical pinball machine. I designed it to feel like
more than a themed collection of clips and callouts: the characters, stories,
and running jokes are built into the rules of the game.

The project combines game design, software development, electronics, physical
mechanisms, lighting, sound, animation, and fabrication. Every switch hit has
to move through that entire system, from a real mechanism on the playfield, to
a rule in the game code, to lights, scoring, audio, and animation that respond
at the right moment.

## My Role

I created and developed the machine as an end-to-end homebrew project. My work
includes:

- Designing the overall game, rules, scoring, progression, and shot objectives
- Programming modes, multiballs, mini-wizard modes, awards, and player systems
- Integrating switches, coils, servos, lights, and other playfield hardware
- Building the on-screen presentation, animation, sound, and event timing
- Writing automated gameplay tests and debugging interactions between systems
- Iterating on balance and presentation through real playtesting

This repository represents the software side of that work and the structure
that connects the physical machine to its audiovisual presentation.

## The Game

The rules are organized around characters and episodes from the show. Players
qualify and complete story modes, build toward character-focused mini-wizard
modes, start multiballs, collect jackpots, earn mystery awards, increase the
playfield multiplier, and progress toward the final wizard mode.

The codebase includes systems for skill shots, ball saves, bonus calculation,
tilt, multiplayer feedback, high scores, physical ball locks, custom
mechanisms, and coordinated light shows. Modes such as Beat the Surfer, Dog
Dale Afternoon, The Heat Waver, Pocket Sand, Whack-a-Mole, Strickland
Multiball, and Rainey Street Multiball demonstrate different approaches to
shots, timers, staged objectives, and presentation.

## How It Was Built

The game runs on [Mission Pinball Framework](https://missionpinball.org/)
(MPF), which manages the rules, scoring, player state, switches, coils, lights,
and physical devices. The display and audio presentation are built in
[Godot](https://godotengine.org/) with MPF-GMC. MPF and Godot communicate through
events, while FAST Pinball hardware connects the software to the physical
machine.

That event-driven architecture makes the machine modular: a shot can update a
player variable, advance a mode, change the lights, move a mechanism, and
trigger a synchronized display sequence without those systems becoming one
large block of code.

## Why This Repository Is Public

Homebrew pinball development depends heavily on builders sharing practical
examples. I am publishing this code so other creators can see how a complete,
evolving MPF project is organized and how its individual systems fit together.

Some useful starting points are:

- `Config/Config.yaml` — machine-wide MPF and FAST hardware configuration
- `modes/*/config/` — rules, scoring, event flow, and player state
- `modes/*/shows/` — insert and feature-light choreography
- `modes/*/slides/` and `modes/*/widgets/` — Godot presentation scenes
- `koth_code/` — custom MPF extensions
- `tests/` — automated examples of gameplay behavior

This is a reference and portfolio, not a ready-to-run distribution. Most
licensed video, music, voice, and image assets are intentionally excluded, so
a clone will not reproduce the complete machine.

## License

The original source code in this repository is available under the
[PolyForm Noncommercial License 1.0.0](LICENSE). You may study, copy, modify,
use, and share it for permitted noncommercial purposes under the license terms.
Commercial use requires separate written permission from Houseball Amusements
LLC at [nick@houseballamusements.com](mailto:nick@houseballamusements.com).

The license applies only to original material owned by Nick Taseris. It does
not grant rights to third-party characters, names, trademarks, artwork, music,
video, audio, fonts, software, or other intellectual property. *King of the
Hill* and its related intellectual property remain the property of their
respective rights holders.

## Project Status

King of the Hill Pinball is an active project. I continue to refine its rules,
balance, presentation, reliability, and hardware behavior as the machine is
played and developed.

## Acknowledgments

This project is made possible by the open-source pinball community and the
people behind MPF, MPF-GMC, Godot, and FAST Pinball hardware.

*King of the Hill* and its characters are the property of their respective
rights holders. This is an unofficial fan project and is not affiliated with
or endorsed by them.

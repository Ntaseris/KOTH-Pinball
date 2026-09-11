# KOTH Game Progression and Scoring

This is the working contract for balancing the game before the mini-wizards and final wizard are completed.

## Game Journey

1. The player qualifies and selects one of eight main modes.
2. Playing both modes associated with a character qualifies that character's mini-wizard.
3. The final wizard requires all eight main modes completed successfully, all four character mini-wizards played, and all three multiballs reached.
4. Progress persists for the entire game, not only the current ball.

The mode inserts represent the eight main-mode attempts used to build character progress. During Mission Select, the insert associated with the highlighted mode pulses white. A completed insert remains the persistent record after selection.

| Character | First mode | Insert | Second mode | Insert |
| --- | --- | --- | --- | --- |
| Hank | Beer Can Named Desire | `l_hank_1` | Duke the Dolphin | `l_hank_2` |
| Dale | Dog Dale Afternoon | `l_dale_1` | Gladstone | `l_dale_2` |
| Bill | Bill Bulk and the Body Buddies | `l_bill_1` | The Heat Waver | `l_bill_2` |
| Boomhauer | Beat the Surfer | `l_boom_1` | Patch Boomhauer | `l_boom_2` |

## Scoring Roles

The modes intentionally do not converge on one identical payout. Values below are expected one-times-playfield ranges before incidental switch scoring.

| Mode | Strategic role | Expected payout |
| --- | --- | --- |
| Beer Can Named Desire | Explicit safe-versus-risk choice | Dandy Don: 3M; Hank success: 10M |
| Beat the Surfer | Standard shot-variety mode | About 11M on completion |
| Duke the Dolphin | Random moving-shot execution | About 12.25M on completion |
| Bill Bulk and the Body Buddies | Escalating alternating-ramp execution | About 15M on completion |
| Dog Dale Afternoon | Spinner-built value with timed shot access | Highly variable; player controls value building |
| Gladstone | Long objective with staged cashouts | Up to about 18M |
| Patch Boomhauer | Rivalry path choice | Patch repeat-shot win: 9.75M; Boomhauer repeat-shot win: 12.75M; variety adds more |
| The Heat Waver | High-risk, high-ceiling speed mode | 6.25M fully sunburned; 10M warming; 20M fully fresh |

Heat Waver is the primary high-ceiling mode. Patch Boomhauer is the secondary strategic choice: Boomhauer pays a 5M victory bonus while Patch pays 2M. The shot scoring remains equal, so a player may still choose Patch when that side of the playfield is safer.

## Lighting Language

| Behavior | Meaning |
| --- | --- |
| Solid | Progress already earned or a persistent state |
| Slow pulse | Available choice or currently highlighted selection |
| Fast flash | Urgent shot that can be made now |
| Brief impact pulse | A successful hit just registered |
| Off | Inactive or unavailable |

Feature colors remain scoped and readable: green for Rainey, orange for Grill/BBQ, white for the Strickland inline path, blue for mode qualification, yellow for playfield multiplier, and red for failure/danger. Heat Waver intentionally overrides this with white fresh, orange warming, and dark red sunburned because the colors describe shot decay.

## Audio and Transition Priority

1. Rules and critical mechanical information.
2. Mode completion, jackpot, and major award callouts.
3. Shot callouts and progress sounds.
4. Ambient music and background effects.

Only one music bed should own the music bus at a time. Base music fades out before Mission Select, a main mode, or a multiball and fades back in when that feature stops. Episode video audio remains the focus in modes that use it; those modes should not add a competing music loop. Repeated switch sounds should stay short and quiet enough that voice and video remain intelligible.

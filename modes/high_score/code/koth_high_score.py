"""KOTH-specific end-of-game presentation before high-score processing."""

import asyncio

from mpf.modes.high_score.code.high_score import HighScore


class KothHighScore(HighScore):
    """Hold initials and awards until the Game Over bumper has finished."""

    async def _run(self) -> None:
        try:
            await asyncio.wait_for(
                self.machine.events.wait_for_event("slide_game_over_removed"),
                timeout=4.0,
            )
        except asyncio.TimeoutError:
            self.warning_log("Game Over slide completion was not received; continuing high-score processing.")

        await super()._run()

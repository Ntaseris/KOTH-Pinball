# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""Keep ball ending blocked until physical Grill locks reach the trough."""

from mpf.core.custom_code import CustomCode


class GrillLockCleanup(CustomCode):
    """Release partial Grill locks safely at the end of a ball."""

    __slots__ = ["_ball_ending_queue", "_balls_waiting_to_drain"]

    def on_load(self):
        """Register the machine-level ball-ending handler."""
        self._ball_ending_queue = None
        self._balls_waiting_to_drain = 0
        self.machine.events.add_handler(
            "ball_ending", self._on_ball_ending, priority=1000000
        )

    def _on_ball_ending(self, queue, **kwargs):
        """Open the Grill and hold ball ending for every ball it contains."""
        del kwargs
        grill = self.machine.ball_devices["bd_grill_lock"]
        balls_to_release = grill.available_balls
        if balls_to_release <= 0:
            return

        self._ball_ending_queue = queue
        self._balls_waiting_to_drain = balls_to_release
        queue.wait()
        self.machine.events.add_handler(
            "ball_drain", self._on_locked_ball_drain, priority=1000000
        )
        grill.eject(balls_to_release)

    def _on_locked_ball_drain(self, balls, **kwargs):
        """Consume released lock balls and continue once all reach the trough."""
        del kwargs
        balls_from_grill = min(self._balls_waiting_to_drain, balls)
        self._balls_waiting_to_drain -= balls_from_grill

        if self.machine.game:
            player = self.machine.game.player
            player.grill_balls_locked = max(
                0, player.grill_balls_locked - balls_from_grill
            )

        if self._balls_waiting_to_drain == 0:
            self._ball_ending_queue.clear()
            self._ball_ending_queue = None
            self.machine.events.remove_handler(self._on_locked_ball_drain)

        return {"balls": balls - balls_from_grill}

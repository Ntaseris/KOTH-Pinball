# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""Ball-device counter driven exclusively by entrance events."""

from mpf.devices.ball_device.entrance_switch_counter import EntranceSwitchCounter


class EventBallCounter(EntranceSwitchCounter):
    """Use MPF's entrance counter without requiring a physical switch."""

    __slots__ = []

    def __init__(self, ball_device, config):
        """Initialize the virtual counter as stable and empty."""
        super().__init__(ball_device, config)
        self._count_stable.set()

    @property
    def is_ready_to_receive(self):
        """An event-only device is always ready for another entrance event."""
        return True

    async def wait_for_ready_to_receive(self):
        """Return immediately because no entrance switch can remain active."""
        return True

    async def count_balls(self):
        """Return the virtual count without waiting on physical switch state."""
        self._count_stable.set()
        return await super().count_balls()

    def wait_for_count_stable(self):
        """Keep inventory checks from waiting on nonexistent switches."""
        self._count_stable.set()
        return super().wait_for_count_stable()

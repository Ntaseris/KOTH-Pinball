# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""Tests for tilt warnings and ball tilt behavior."""

from tests.koth_test_case import KothTestCase


class TestTilt(KothTestCase):
    """Verify the cabinet tilt bob uses MPF's three-strike flow."""

    def test_three_tilt_bob_hits_warn_twice_then_tilt(self):
        """The first two accepted hits warn and the third tilts the ball."""
        self.start_game_with_balls()
        self.mock_event('tilt_warning')
        self.mock_event('tilt')
        self.assertFalse(self.machine.modes['tilt'].config.get('slide_player'))

        self.hit_and_release_switch('s_tilt_bob')
        self.advance_time_and_run(1.01)
        self.assertEventCalledWith('tilt_warning', warnings=1, warnings_remaining=2)
        self.assertEventNotCalled('tilt')

        self.hit_and_release_switch('s_tilt_bob')
        self.advance_time_and_run(1.01)
        self.assertEventCalledWith('tilt_warning', warnings=2, warnings_remaining=1)
        self.assertEventNotCalled('tilt')

        self.hit_and_release_switch('s_tilt_bob')
        self.advance_time_and_run(0.02)

        self.assertEventCalled('tilt')
        self.assertTrue(self.machine.game.tilted)

    def test_first_warning_fires_amber_light_response(self):
        """The first warning visibly shakes alternating GI amber."""
        self.start_game_with_balls()

        self.hit_and_release_switch('s_tilt_bob')
        self.advance_time_and_run(0.02)

        self.assertLightColor('l_gi1', 'orange')
        self.assertLightColor('l_gi7', 'orange')
        self.assertLightColor('l_left_orbit', 'white')

    def test_one_bob_swing_does_not_disable_flippers(self):
        """Repeated closures from one bob swing count as one warning."""
        self.start_game_with_balls()
        self.mock_event('tilt_warning')
        self.mock_event('tilt')
        self.mock_event('cmd_flippers_disable')

        for _ in range(3):
            self.hit_and_release_switch('s_tilt_bob')
            self.advance_time_and_run(0.4)

        self.assertEventCalledWith('tilt_warning', warnings=1, warnings_remaining=2)
        self.assertEventNotCalled('tilt')
        self.assertEventNotCalled('cmd_flippers_disable')
        self.assertFalse(self.machine.game.tilted)

    def test_tilted_ball_holds_for_zero_bonus_display(self):
        """A tilted ball runs the zero-value bonus presentation after draining."""
        self.start_game_with_balls()

        for warning in range(3):
            self.hit_and_release_switch('s_tilt_bob')
            self.advance_time_and_run(1.01 if warning < 2 else 0.02)

        self.assertModeRunning('tilt_bonus')

        self.post_event(
            'balldevice_bd_trough_ball_enter',
            new_balls=1,
            unclaimed_balls=1,
            device=self.machine.ball_devices['bd_trough'],
        )
        self.advance_time_and_run(5)

        self.assertModeRunning('tilt_bonus')
        self.advance_time_and_run(3.1)
        self.assertModeNotRunning('tilt_bonus')

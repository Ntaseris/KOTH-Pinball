# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""Tests for Beat the Surfer shot progression and finish."""

from tests.koth_test_case import KothTestCase


class TestBeatTheSurfer(KothTestCase):

    BULLY_SWITCHES = (
        "s_left_orbit_enter",
        "s_left_ramp_exit",
        "s_left_inner_horseshoe",
        "s_center_spinner",
        "s_right_ramp_exit",
        "s_right_orbit_exit",
    )

    def _start_mode(self):
        self.start_game_with_balls()
        self.post_event("mission_select_beat_the_surfer_selected")
        self.advance_time_and_run(0.1)
        self.assertTrue(self.machine.modes["beat_the_surfer"].active)

    def test_only_first_hit_awards_bully_value(self):
        """A cleared shot cannot repeatedly award the mode's million points."""
        self._start_mode()

        score_before = self.machine.game.player.score
        self.hit_and_release_switch("s_left_orbit_enter")
        self.advance_time_and_run(0.1)
        first_delta = self.machine.game.player.score - score_before

        score_before = self.machine.game.player.score
        self.hit_and_release_switch("s_left_orbit_enter")
        self.advance_time_and_run(0.1)
        repeat_delta = self.machine.game.player.score - score_before

        self.assertEqual(1025000, first_delta)
        self.assertEqual(25000, repeat_delta)
        self.assertPlayerVarEqual(1, "surfer_bullies_cleared")

    def test_scoop_cannot_finish_mode_early(self):
        """The final scoop is disabled until all six red shots are cleared."""
        self._start_mode()
        self.mock_event("beat_the_surfer_done")

        self.hit_and_release_switch("s_scoop")
        self.advance_time_and_run(0.1)

        self.assertEventNotCalled("beat_the_surfer_done")
        self.assertPlayerVarEqual(0, "beat_the_surfer_completed")
        self.assertTrue(self.machine.modes["beat_the_surfer"].active)

    def test_six_bullies_light_final_scoop(self):
        """The six visible objectives qualify the scoop without hidden shots."""
        self._start_mode()
        self.mock_event("light_scoop_accrual_done")

        for switch in self.BULLY_SWITCHES:
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(0.05)

        self.assertPlayerVarEqual(6, "surfer_bullies_cleared")
        self.assertEventCalled("light_scoop_accrual_done")

    def test_qualified_scoop_awards_finish_and_ends_mode(self):
        """The qualified blue scoop awards five million and completes the mode."""
        self._start_mode()
        for switch in self.BULLY_SWITCHES:
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(0.05)

        score_before = self.machine.game.player.score
        self.hit_and_release_switch("s_scoop")
        self.advance_time_and_run(0.1)

        self.assertEqual(score_before + 5025000, self.machine.game.player.score)
        self.assertPlayerVarEqual(1, "beat_the_surfer_completed")
        # The finish video keeps the mode alive until its six-second slide ends.
        self.assertTrue(self.machine.modes["beat_the_surfer"].active)

        self.post_event("slide_beat_the_surfer_finish_removed")
        self.advance_time_and_run(0.1)
        self.assertFalse(self.machine.modes["beat_the_surfer"].active)

    def test_multiball_can_start_during_mode(self):
        """Base tracking remains active when multiball begins during the mission."""
        self._start_mode()

        self.post_event("multiball_grill_mb_started")
        self.advance_time_and_run(0.1)

        self.assertTrue(self.machine.modes["beat_the_surfer"].active)
        self.assertTrue(self.machine.modes["base"].active)
        self.assertPlayerVarEqual(1, "any_mb_active")

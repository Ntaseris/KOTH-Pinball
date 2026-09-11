# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""Tests for Bill, Bulk and the Body Buddies rep progression."""

from tests.koth_test_case import KothTestCase


class TestBillBulkAndTheBodyBuddies(KothTestCase):

    def _start_mode(self):
        self.start_game_with_balls()
        self.post_event("mission_select_bill_bulk_and_the_body_buddies_selected")
        self.advance_time_and_run(0.1)
        self.assertTrue(self.machine.modes["bill_bulk_and_the_body_buddies"].active)

    def _start_workout(self):
        self._start_mode()
        self.post_event("slide_bill_bulk_and_the_body_buddies_rules_removed")
        self.advance_time_and_run(0.1)

    def test_timer_waits_for_rules_slide(self):
        """The full workout clock begins only after the rules card leaves."""
        self._start_mode()

        timer = self.machine.timers["bill_bulk_and_the_body_buddies_mode_countdown"]
        self.assertFalse(timer.running)

        self.post_event("slide_bill_bulk_and_the_body_buddies_rules_removed")
        self.advance_time_and_run(0.1)
        self.assertTrue(timer.running)

    def test_wrong_ramp_only_awards_base_points(self):
        """An unlit ramp cannot advance reps or collect the workout value."""
        self._start_workout()

        score_before = self.machine.game.player.score
        self.hit_and_release_switch("s_right_ramp_exit")
        self.advance_time_and_run(0.1)

        self.assertEqual(25000, self.machine.game.player.score - score_before)
        self.assertPlayerVarEqual(0, "bill_bulk_reps")

    def test_correct_ramps_alternate_and_build_value(self):
        """Only the lit alternating ramp advances the escalating rep award."""
        self._start_workout()

        score_before = self.machine.game.player.score
        self.hit_and_release_switch("s_left_ramp_exit")
        self.advance_time_and_run(0.1)
        self.assertEqual(1025000, self.machine.game.player.score - score_before)
        self.assertPlayerVarEqual(1, "bill_bulk_reps")

        score_before = self.machine.game.player.score
        self.hit_and_release_switch("s_right_ramp_exit")
        self.advance_time_and_run(0.1)
        self.assertEqual(1275000, self.machine.game.player.score - score_before)
        self.assertPlayerVarEqual(2, "bill_bulk_reps")

    def test_nine_reps_complete_mode_after_finish_clip(self):
        """Nine correct reps trigger success and hold the mode for its finish clip."""
        self._start_workout()
        self.mock_event("bill_bulk_and_the_body_buddies_done")

        for rep in range(9):
            switch = "s_left_ramp_exit" if rep % 2 == 0 else "s_right_ramp_exit"
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(0.05)

        self.assertPlayerVarEqual(9, "bill_bulk_reps")
        self.assertEventCalled("bill_bulk_and_the_body_buddies_done")
        self.assertTrue(self.machine.modes["bill_bulk_and_the_body_buddies"].active)

        self.post_event("slide_bill_bulk_and_the_body_buddies_4_removed")
        self.advance_time_and_run(0.1)
        self.assertFalse(self.machine.modes["bill_bulk_and_the_body_buddies"].active)

    def test_multiball_can_start_during_mode(self):
        """The mission remains active when a multiball begins during the workout."""
        self._start_workout()

        self.post_event("multiball_grill_mb_started")
        self.advance_time_and_run(0.1)

        self.assertTrue(self.machine.modes["bill_bulk_and_the_body_buddies"].active)
        self.assertTrue(self.machine.modes["base"].active)
        self.assertPlayerVarEqual(1, "any_mb_active")

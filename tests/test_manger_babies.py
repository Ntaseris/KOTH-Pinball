# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""Tests for the per-ball Manger Babies risk/reward ladder."""

from tests.koth_test_case import KothTestCase


class TestMangerBabies(KothTestCase):

    def _start_base(self):
        self.start_game_with_balls()
        self.assertTrue(self.machine.modes["manger_babies"].active)

    def _complete_baby(self, switch):
        for _ in range(4):
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(0.05)

    def test_baby_hits_escalate_to_one_million(self):
        self._start_base()

        expected_totals = (250000, 750000, 1500000, 2500000)
        for expected in expected_totals:
            self.hit_and_release_switch("s_left_orbit_enter")
            self.advance_time_and_run(0.05)
            self.assertPlayerVarEqual(expected, "manger_babies_total")

        self.assertEqual(4, self.machine.counters["mb_reginald"].value)

    def test_completed_baby_does_not_restart_its_blink(self):
        """The fourth hit stops the pulse and leaves the earned insert solid."""
        self._start_base()
        self.mock_event("mb_start_reginald_pulse")
        self.mock_event("mb_stop_reginald_pulse")

        self._complete_baby("s_left_orbit_enter")

        self.assertEventCalled("mb_stop_reginald_pulse")
        self.assertEventNotCalled("mb_start_reginald_pulse")
        self.assertEqual(4, self.machine.counters["mb_reginald"].value)

    def test_early_cashout_ends_feature_for_remainder_of_ball(self):
        self._start_base()
        self._complete_baby("s_left_orbit_enter")

        self.hit_and_release_switch("s_luanne")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(3500000, "manger_babies_total")
        self.assertIn(self.machine.counters["mb_reginald"].value, (0, None))
        self.assertIn(self.machine.counters["mb_completed_tracker"].value, (0, None))
        self.assertPlayerVarEqual(1, "manger_babies_cashed_out_this_ball")
        self.assertFalse(self.machine.modes["manger_babies"].active)

        self.post_event("mode_beat_the_surfer_stopped")
        self.advance_time_and_run(0.1)
        self.assertFalse(self.machine.modes["manger_babies"].active)

    def test_waiting_for_two_babies_earns_larger_cashout(self):
        self._start_base()
        self._complete_baby("s_left_orbit_enter")
        self._complete_baby("s_left_ramp_exit")

        self.hit_and_release_switch("s_luanne")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(8000000, "manger_babies_total")

    def test_four_baby_cashout_keeps_ball_save_active_and_visible(self):
        """Cycle reset must not immediately cancel the four-baby ball save."""
        self._start_base()
        for switch in (
            "s_left_orbit_enter",
            "s_left_ramp_exit",
            "s_right_ramp_exit",
            "s_right_orbit_exit",
        ):
            self._complete_baby(switch)

        self.hit_and_release_switch("s_luanne")
        self.advance_time_and_run(0.1)

        self.assertTrue(self.machine.ball_saves["mb_luanne_ballsave"].enabled)
        self.assertEqual(420, self.machine.lights["l_ball_save"].stack[0].priority)

        self.advance_time_and_run(10.1)
        self.assertFalse(self.machine.ball_saves["mb_luanne_ballsave"].enabled)

    def test_progress_survives_main_mode_pause(self):
        self._start_base()
        self.hit_and_release_switch("s_left_orbit_enter")
        self.hit_and_release_switch("s_left_orbit_enter")
        self.advance_time_and_run(0.1)
        self.assertEqual(2, self.machine.counters["mb_reginald"].value)
        score_before_pause = self.machine.game.player.score

        self.post_event("mode_beat_the_surfer_started")
        self.advance_time_and_run(0.1)
        self.assertFalse(self.machine.modes["manger_babies"].active)

        self.post_event("mode_beat_the_surfer_stopped")
        self.advance_time_and_run(0.1)
        self.assertTrue(self.machine.modes["manger_babies"].active)
        self.assertEqual(2, self.machine.counters["mb_reginald"].value)
        self.assertEqual(score_before_pause, self.machine.game.player.score)

    def test_earned_baby_survives_pause_without_counting_twice(self):
        self._start_base()
        self._complete_baby("s_left_orbit_enter")
        self.assertEqual(1, self.machine.counters["mb_completed_tracker"].value)

        self.post_event("mode_beat_the_surfer_started")
        self.advance_time_and_run(0.1)
        self.post_event("mode_beat_the_surfer_stopped")
        self.advance_time_and_run(0.1)

        self.assertTrue(self.machine.modes["manger_babies"].active)
        self.assertEqual(4, self.machine.counters["mb_reginald"].value)
        self.assertEqual(1, self.machine.counters["mb_completed_tracker"].value)

    def test_uncashed_progress_resets_at_ball_end(self):
        self._start_base()
        self._complete_baby("s_left_orbit_enter")

        self.post_event("mb_cycle_reset")
        self.post_event("ball_ended")
        self.advance_time_and_run(0.1)
        self.post_event("mode_base_started")
        self.advance_time_and_run(0.1)

        self.assertEqual(0, self.machine.counters["mb_reginald"].value)
        self.assertEqual(0, self.machine.counters["mb_completed_tracker"].value)

    def test_multiball_stops_background_scoring(self):
        self._start_base()
        self.post_event("multiball_grill_mb_started")
        self.advance_time_and_run(0.1)
        self.assertFalse(self.machine.modes["manger_babies"].active)

        self.hit_and_release_switch("s_left_orbit_enter")
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(0, "manger_babies_total")

        self.post_event("multiball_grill_mb_ended")
        self.advance_time_and_run(0.1)
        self.assertTrue(self.machine.modes["manger_babies"].active)

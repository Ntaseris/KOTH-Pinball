# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""Tests for Gladstone's employee-firing and mass-layoff rounds."""

from tests.koth_test_case import KothTestCase


class TestGladstone(KothTestCase):

    EMPLOYEE_SWITCHES = (
        "s_p_target",
        "s_r_target",
        "s_o_target",
        "s_p2_target",
        "s_a_target",
        "s_n_target",
        "s_e_target",
    )

    def _start_mode(self):
        self.start_game_with_balls()
        self.post_event("mission_select_gladstone_selected")
        self.advance_time_and_run(0.1)
        self.assertTrue(self.machine.modes["gladstone"].active)

    def _fire_all_employees(self):
        for switch in self.EMPLOYEE_SWITCHES:
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(0.05)

    def test_unique_employee_scores_and_repeat_does_not_advance(self):
        """Only the first hit on an employee advances and earns mode value."""
        self._start_mode()

        score_before = self.machine.game.player.score
        self.hit_and_release_switch("s_p_target")
        self.advance_time_and_run(0.1)
        first_delta = self.machine.game.player.score - score_before

        score_before = self.machine.game.player.score
        self.hit_and_release_switch("s_p_target")
        self.advance_time_and_run(0.1)
        repeat_delta = self.machine.game.player.score - score_before

        self.assertGreaterEqual(first_delta, 500000)
        self.assertLess(repeat_delta, 500000)
        self.assertPlayerVarEqual(1, "employees_fired")

    def test_seven_employees_qualify_only_right_ramp(self):
        """Completing the red bank arms a clearly indicated right-ramp collect."""
        self._start_mode()
        self._fire_all_employees()

        self.assertPlayerVarEqual(7, "employees_fired")
        self.assertTrue(self.machine.shots["gladstone_layoff"].enabled)

        self.hit_and_release_switch("s_ladybird_target")
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(0, "gladstone_layoffs")

    def test_layoff_values_escalate_and_reset_employees(self):
        """Right-ramp layoffs score 5M, then build the next award by 2.5M."""
        self._start_mode()
        self._fire_all_employees()

        score_before = self.machine.game.player.score
        self.hit_and_release_switch("s_right_ramp_exit")
        self.advance_time_and_run(0.1)

        self.assertGreaterEqual(self.machine.game.player.score - score_before, 5000000)
        self.assertPlayerVarEqual(1, "gladstone_layoffs")
        self.assertPlayerVarEqual(0, "employees_fired")
        self.assertPlayerVarEqual(7500000, "gladstone_layoff_value")
        self.assertEqual("employed", self.machine.shots["gladstone_p"].state_name)
        self.assertEqual(0, self.machine.counters["gladstone_firings"].value)

    def test_three_layoffs_complete_after_finish_clip(self):
        """Three complete firing rounds end with the episode finish beat."""
        self._start_mode()
        self.mock_event("gladstone_mode_complete")

        for _ in range(3):
            self._fire_all_employees()
            self.hit_and_release_switch("s_right_ramp_exit")
            self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(3, "gladstone_layoffs")
        self.assertEventCalled("gladstone_mode_complete")
        self.assertTrue(self.machine.modes["gladstone"].active)

        self.post_event("slide_gladstone_finish_removed")
        self.advance_time_and_run(0.1)
        self.assertFalse(self.machine.modes["gladstone"].active)

    def test_timer_does_not_gain_time_from_repeat_hits(self):
        """Completed targets cannot farm extensions or desynchronize the video."""
        self._start_mode()
        timer = self.machine.timers["gladstone_mode_countdown"]
        start_ticks = timer.ticks

        for _ in range(10):
            self.hit_and_release_switch("s_p_target")
        self.advance_time_and_run(0.1)

        self.assertEqual(start_ticks, timer.ticks)

    def test_multiball_can_start_during_mode(self):
        """Gladstone remains active when multiball begins during the mission."""
        self._start_mode()

        self.post_event("multiball_grill_mb_started")
        self.advance_time_and_run(0.1)

        self.assertTrue(self.machine.modes["gladstone"].active)
        self.assertPlayerVarEqual(1, "any_mb_active")

    def test_target_bank_does_not_relight_rainey_after_it_was_used_this_ball(self):
        """Gladstone's target bank cannot advertise an unavailable Rainey lock."""
        self._start_mode()
        self.post_event("multiball_rainey_multiball_started")
        self.post_event("multiball_rainey_multiball_ended")
        self.advance_time_and_run(0.1)

        self._fire_all_employees()

        self.assertPlayerVarEqual(1, "rainey_mb_used_this_ball")
        self.assertNotEqual("started", self.machine.achievements["lock_lit"].state)
        self.assertLightColor("l_lock_lit", "black")

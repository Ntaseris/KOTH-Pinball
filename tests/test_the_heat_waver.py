"""Tests for The Heat Waver's left-to-right sunburn sequence."""

from tests.koth_test_case import KothTestCase


class TestTheHeatWaver(KothTestCase):

    def _start_mode(self):
        self.start_game_with_balls()
        self.post_event("mission_select_the_heat_waver_selected")
        self.advance_time_and_run(3.1)
        self.assertTrue(self.machine.modes["the_heat_waver"].active)

    def test_wrong_shot_does_not_advance_wave(self):
        self._start_mode()

        self.hit_and_release_switch("s_right_ramp_exit")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(0, "heat_waver_shots")
        self.assertEqual(
            "start",
            self.machine.state_machines["the_heat_waver"].state,
        )

    def test_fresh_warming_and_sunburned_values_have_no_gaps(self):
        self._start_mode()

        self.machine.game.player["shot_color"] = 35
        self.hit_and_release_switch("s_left_orbit_enter")
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(3000000, "the_heat_waver_total")

        self.machine.game.player["shot_color2"] = 34
        self.hit_and_release_switch("s_left_ramp_exit")
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(4000000, "the_heat_waver_total")

        self.machine.game.player["shot_color3"] = 19
        self.hit_and_release_switch("s_center_spinner")
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(4250000, "the_heat_waver_total")
        self.assertPlayerVarEqual(3, "heat_waver_shots")

    def test_completing_wave_awards_completion_bonus(self):
        self._start_mode()

        for switch in (
            "s_left_orbit_enter",
            "s_left_ramp_exit",
            "s_center_spinner",
            "s_right_ramp_exit",
            "s_right_orbit_exit",
        ):
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(5, "heat_waver_shots")
        self.assertPlayerVarEqual(20000000, "the_heat_waver_total")
        self.assertFalse(self.machine.modes["the_heat_waver"].active)

    def test_multiball_can_start_during_mode(self):
        self._start_mode()
        self.post_event("multiball_grill_mb_started")
        self.advance_time_and_run(0.1)

        self.assertTrue(self.machine.modes["the_heat_waver"].active)
        self.assertPlayerVarEqual(1, "any_mb_active")

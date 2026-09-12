"""Tests for the timed Super Spinners Mystery frenzy."""

from tests.koth_test_case import KothTestCase


class TestSuperSpinners(KothTestCase):

    def _start_mode(self):
        self.start_game_with_balls()
        self.post_event("slide_award_5_removed")
        self.advance_time_and_run(0.1)
        self.assertTrue(self.machine.modes["super_spinners"].active)

    def test_mode_starts_at_twenty_five_thousand_per_spin(self):
        self._start_mode()

        self.hit_and_release_switch("s_left_spinner")
        self.advance_time_and_run(0.05)

        self.assertPlayerVarEqual(1, "super_spinner_spins")
        self.assertPlayerVarEqual(25000, "super_spinner_value")
        self.assertPlayerVarEqual(25000, "super_spinners_total")

    def test_every_ten_spins_increases_spin_value(self):
        self._start_mode()

        for _ in range(10):
            self.hit_and_release_switch("s_left_spinner")
            self.advance_time_and_run(0.02)

        self.assertPlayerVarEqual(10, "super_spinner_spins")
        self.assertPlayerVarEqual(50000, "super_spinner_value")
        self.assertPlayerVarEqual(750000, "super_spinners_total")

        self.hit_and_release_switch("s_left_spinner")
        self.advance_time_and_run(0.05)
        self.assertPlayerVarEqual(800000, "super_spinners_total")

    def test_milestones_award_meaningful_bonus_points(self):
        self._start_mode()

        for _ in range(25):
            self.hit_and_release_switch("s_left_spinner")
            self.advance_time_and_run(0.02)

        # 10-spin bonus: 500K; 25-spin bonus: 1.5M.
        self.assertPlayerVarEqual(25, "super_spinner_spins")
        self.assertPlayerVarEqual(3125000, "super_spinners_total")

    def test_alternating_spinners_awards_cross_spin_bonus(self):
        self._start_mode()

        self.hit_and_release_switch("s_left_spinner")
        self.advance_time_and_run(0.05)
        self.hit_and_release_switch("s_center_spinner")
        self.advance_time_and_run(0.05)

        self.assertPlayerVarEqual(2, "super_spinner_spins")
        self.assertPlayerVarEqual(300000, "super_spinners_total")

    def test_playfield_multiplier_applies_to_all_scoring(self):
        self._start_mode()
        self.machine.game.player["pf_multiplier"] = 2

        self.hit_and_release_switch("s_left_spinner")
        self.advance_time_and_run(0.05)
        self.hit_and_release_switch("s_center_spinner")
        self.advance_time_and_run(0.05)

        self.assertPlayerVarEqual(600000, "super_spinners_total")

    def test_main_mode_and_multiball_do_not_stop_frenzy(self):
        self._start_mode()

        self.post_event("mode_beat_the_surfer_started")
        self.post_event("multiball_grill_mb_started")
        self.advance_time_and_run(0.1)

        self.assertTrue(self.machine.modes["super_spinners"].active)

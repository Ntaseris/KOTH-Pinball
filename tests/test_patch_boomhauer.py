# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""Tests for the Patch versus Boomhauer fight race."""

from tests.koth_test_case import KothTestCase


class TestPatchBoomhauer(KothTestCase):

    def _start_mode(self):
        self.start_game_with_balls()
        self.post_event("mission_select_patch_boomhauer_selected")
        self.advance_time_and_run(0.1)
        self.assertTrue(self.machine.modes["patch_boomhauer"].active)

    def test_both_fighters_start_even_at_zero(self):
        self._start_mode()
        self.assertPlayerVarEqual(0, "patch_hits")
        self.assertPlayerVarEqual(0, "boom_hits")

    def test_patch_and_boom_hits_have_equal_base_value(self):
        self._start_mode()

        self.hit_and_release_switch("s_p_target")
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(1, "patch_hits")
        self.assertPlayerVarEqual(1000000, "patch_boomhauer_total")

        self.hit_and_release_switch("s_p2_target")
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(1, "boom_hits")
        self.assertPlayerVarEqual(2000000, "patch_boomhauer_total")

    def test_repeating_a_shot_loses_only_variety_bonus(self):
        self._start_mode()

        self.hit_and_release_switch("s_p_target")
        self.advance_time_and_run(0.1)
        first_total = self.machine.game.player["patch_boomhauer_total"]

        self.hit_and_release_switch("s_p_target")
        self.advance_time_and_run(0.1)
        repeat_value = self.machine.game.player["patch_boomhauer_total"] - first_total

        self.assertEqual(750000, repeat_value)
        self.assertPlayerVarEqual(2, "patch_hits")

    def test_patch_wins_at_ten_and_waits_for_finish_clip(self):
        self._start_mode()
        self.mock_event("patch_wins")

        for _ in range(10):
            self.hit_and_release_switch("s_p_target")
            self.advance_time_and_run(0.05)

        self.assertEventCalled("patch_wins")
        self.assertPlayerVarEqual(10, "patch_hits")
        self.assertPlayerVarEqual("PATCH", "patch_boom_winner")
        self.assertPlayerVarEqual(9750000, "patch_boomhauer_total")
        self.assertTrue(self.machine.modes["patch_boomhauer"].active)

        self.post_event("slide_patch_wins_removed")
        self.advance_time_and_run(0.1)
        self.assertFalse(self.machine.modes["patch_boomhauer"].active)

    def test_boomhauer_wins_at_ten(self):
        self._start_mode()
        self.mock_event("boomhauer_wins")

        for _ in range(10):
            self.hit_and_release_switch("s_p2_target")
            self.advance_time_and_run(0.05)

        self.assertEventCalled("boomhauer_wins")
        self.assertPlayerVarEqual(10, "boom_hits")
        self.assertPlayerVarEqual("BOOMHAUER", "patch_boom_winner")
        self.assertPlayerVarEqual(12750000, "patch_boomhauer_total")

    def test_hits_after_winner_do_not_score(self):
        self._start_mode()
        for _ in range(10):
            self.hit_and_release_switch("s_p_target")
            self.advance_time_and_run(0.05)

        mode_total = self.machine.game.player["patch_boomhauer_total"]
        self.hit_and_release_switch("s_p2_target")
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(mode_total, "patch_boomhauer_total")

    def test_multiball_can_start_during_mode(self):
        self._start_mode()
        self.post_event("multiball_grill_mb_started")
        self.advance_time_and_run(0.1)

        self.assertTrue(self.machine.modes["patch_boomhauer"].active)
        self.assertPlayerVarEqual(1, "any_mb_active")

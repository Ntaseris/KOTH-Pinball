# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""Tests for Bloodline Multiball, Bill's mini-wizard mode."""

from tests.koth_test_case import KothTestCase


class TestBillMiniWizard(KothTestCase):
    """Verify the moving Violetta hazard, payouts, and recovery rules."""

    safe_shots = (
        "bill_safe_left_orbit",
        "bill_safe_left_ramp",
        "bill_safe_center_spinner",
        "bill_safe_right_ramp",
        "bill_safe_right_orbit",
    )
    hazard_shots = (
        "bill_hazard_left_orbit",
        "bill_hazard_left_ramp",
        "bill_hazard_center_spinner",
        "bill_hazard_right_ramp",
        "bill_hazard_right_orbit",
    )

    def _start_mode(self):
        self.start_game_with_balls()
        self.post_event("mission_select_bill_mini_wizard_selected")
        self.advance_time_and_run(0.1)
        # GMC reports this when the 4.5-second rules slide expires.
        self.post_event("slide_bill_mini_wizard_inactive")
        self.advance_time_and_run(0.1)

    def test_starts_two_ball_mode_with_four_safe_shots_and_one_hazard(self):
        self._start_mode()

        self.assertModeRunning("bill_mini_wizard")
        self.assertPlayerVarEqual(1, "any_mb_active")
        self.assertEqual(
            4,
            sum(self.machine.shots[name].enabled for name in self.safe_shots),
        )
        self.assertEqual(
            1,
            sum(self.machine.shots[name].enabled for name in self.hazard_shots),
        )
        self.assertEqual(
            2,
            self.machine.multiballs[
                "bill_mini_wizard_multiball"
            ].config["ball_count"].evaluate({}),
        )

    def test_six_jackpots_score_full_ladder_and_light_escape(self):
        self._start_mode()
        score_before = self.machine.game.player.score

        for _ in range(6):
            self.post_event("bill_mw_jackpot_collected")
            self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(6, "bill_mw_jackpots")
        self.assertPlayerVarEqual(31_500_000, "bill_mw_jackpot_total")
        self.assertEqual(
            score_before + 31_500_000,
            self.machine.game.player.score,
        )
        self.assertTrue(self.machine.shots["bill_escape_scoop"].enabled)

    def test_escape_super_and_completion_pay_full_award(self):
        self._start_mode()
        score_before = self.machine.game.player.score
        for _ in range(6):
            self.post_event("bill_mw_jackpot_collected")
            self.advance_time_and_run(0.1)

        self.post_event("bill_escape_scoop_hit")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(1, "bill_mini_wizard_completed")
        self.assertEqual(
            score_before + 88_000_000,
            self.machine.game.player.score,
        )
        self.assertTrue(all(
            self.machine.shots[name].enabled for name in self.safe_shots
        ))
        self.assertFalse(any(
            self.machine.shots[name].enabled for name in self.hazard_shots
        ))

    def test_violetta_disables_flippers_and_arms_last_ball_return(self):
        self._start_mode()
        self.mock_event("cmd_flippers_disable")

        self.post_event("bill_violetta_hit")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(1, "bill_mw_failed")
        self.assertEventCalled("cmd_flippers_disable")
        ball_save = self.machine.ball_saves["bill_violetta_return"]
        self.assertTrue(ball_save.enabled)
        self.assertTrue(ball_save.config["only_last_ball"])
        self.assertEqual(1, ball_save.saves_remaining)

    def test_violetta_returns_only_the_final_drained_ball(self):
        self._start_mode()
        self.mock_event("cmd_flippers_enable")
        self.post_event("bill_violetta_hit")
        self.advance_time_and_run(0.1)

        ball_save = self.machine.ball_saves["bill_violetta_return"]
        self.machine.game.balls_in_play = 2
        self.assertEqual(0, ball_save._get_number_of_balls_to_save(1))

        self.machine.game.balls_in_play = 1
        self.assertEqual(1, ball_save._get_number_of_balls_to_save(1))
        self.post_event("ball_save_bill_violetta_return_saving_ball")
        self.advance_time_and_run(0.1)

        self.assertEventCalled("cmd_flippers_enable")
        self.assertModeNotRunning("bill_mini_wizard")

    def test_pocket_sand_collects_safe_jackpot_not_violetta(self):
        self._start_mode()
        self.machine.game.player.pocket_sand = 1
        self.machine.game.player.pocket_sand_can_use = 1

        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(0.2)

        self.assertPlayerVarEqual(0, "pocket_sand")
        self.assertPlayerVarEqual(1, "bill_mw_jackpots")
        self.assertPlayerVarEqual(0, "bill_mw_failed")

    def test_signature_shows_and_media_are_loaded(self):
        for show in (
            "bill_mw_jackpot_collect",
            "bill_mw_escape_super",
            "bill_mw_violetta_fail",
        ):
            self.assertIn(show, self.machine.shows)

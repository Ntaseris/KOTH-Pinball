# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""Tests for the Whack-a-Mole video mode."""

from tests.koth_test_case import KothTestCase


class TestWhackAMole(KothTestCase):

    def _start_mode(self):
        self.start_game_with_balls()
        self.post_event("start_whack_a_mole")
        self.advance_time_and_run(0.1)
        self.assertModeRunning("whack_a_mole")

    def test_hank_and_peggy_score_lowest_and_bobby_scores_more(self):
        self._start_mode()

        self.post_event("whack_a_mole_target_hit", target="hank")
        self.post_event("whack_a_mole_target_hit", target="peggy")
        self.post_event("whack_a_mole_target_hit", target="bobby")
        self.advance_time_and_run(0.05)

        self.assertPlayerVarEqual(3, "whack_a_mole_hits")
        self.assertPlayerVarEqual(300000, "score")
        self.assertPlayerVarEqual(3, "whack_a_mole_streak")

    def test_tom_costs_a_life_and_resets_streak(self):
        self._start_mode()
        self.post_event("whack_a_mole_target_hit", target="hank")
        self.post_event("whack_a_mole_tom_hit")
        self.advance_time_and_run(0.05)

        self.assertPlayerVarEqual(2, "whack_a_mole_lives")
        self.assertPlayerVarEqual(0, "whack_a_mole_streak")

    def test_missed_target_resets_streak_without_costing_a_life(self):
        self._start_mode()
        self.post_event("whack_a_mole_target_hit", target="peggy")
        self.post_event("whack_a_mole_target_missed", target="peggy")
        self.advance_time_and_run(0.05)

        self.assertPlayerVarEqual(3, "whack_a_mole_lives")
        self.assertPlayerVarEqual(0, "whack_a_mole_streak")

    def test_streak_milestones_award_escalating_bonuses(self):
        self._start_mode()

        for streak in (5, 10, 15, 20):
            self.post_event("whack_a_mole_streak_bonus", streak=streak)
        self.advance_time_and_run(0.05)

        self.assertPlayerVarEqual(1850000, "score")

    def test_perfect_completion_awards_big_payout(self):
        self._start_mode()
        self.post_event("whack_a_mole_perfect")
        self.post_event("whack_a_mole_completed")
        self.advance_time_and_run(0.1)

        self.assertModeNotRunning("whack_a_mole")
        self.assertPlayerVarEqual(2500000, "score")

    def test_failure_stops_mode(self):
        self._start_mode()
        self.post_event("whack_a_mole_failed")
        self.advance_time_and_run(0.1)

        self.assertModeNotRunning("whack_a_mole")

    def test_mystery_intro_hands_off_to_video_mode(self):
        self.start_game_with_balls()
        self.post_event("test_whack_a_mole_mystery_flow")
        self.advance_time_and_run(0.2)
        self.assertModeRunning("mystery")
        self.assertModeNotRunning("whack_a_mole")

        self.post_event("slide_whack_a_mole_intro_removed")
        self.advance_time_and_run(0.1)
        self.assertModeRunning("whack_a_mole")
        self.assertModeRunning("mystery")

        self.post_event("whack_a_mole_completed")
        self.advance_time_and_run(0.1)
        self.assertModeNotRunning("whack_a_mole")
        self.assertModeNotRunning("mystery")

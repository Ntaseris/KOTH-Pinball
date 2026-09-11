# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""Tests for KOTH's custom high-score categories."""

from tests.koth_test_case import KothTestCase


class TestHighScore(KothTestCase):
    """Verify score and collectible champions are saved independently."""

    def test_alamo_champion_saves_count_and_initials(self):
        """A player above the saved can count becomes the Alamo champion."""
        self.start_game_with_balls()
        self.machine.game.player.alamo = 13
        self.machine.game.player.initials = "NCK"

        self.post_event("start_high_score")
        # The Game Over bumper runs before high-score awards are processed.
        self.advance_time_and_run(9)

        self.assertMachineVarEqual("NCK", "alamo1_name")
        self.assertMachineVarEqual(13, "alamo1_value")

    def test_initials_wait_for_game_over_bumper(self):
        """Initials entry does not appear underneath the Game Over video."""
        self.start_game_with_balls()
        self.machine.game.player.score = 5000000
        self.mock_event("high_score_enter_initials")

        self.post_event("start_high_score")
        self.advance_time_and_run(3)
        self.assertEventNotCalled("high_score_enter_initials")

        self.post_event("slide_game_over_removed")
        self.advance_time_and_run(0.1)
        self.assertEventCalled("high_score_enter_initials")
        self.assertEventCalledWith(
            "high_score_enter_initials",
            award="KING OF THE HILL",
            player_num=1,
            value=5000000,
            category_name="score",
        )

    def test_high_score_input_switch_posts_one_action(self):
        """KOTH input handlers replace MPF defaults instead of doubling them."""
        self.start_game_with_balls()
        self.machine.game.player.score = 5000000
        self.post_event("start_high_score")
        self.post_event("slide_game_over_removed")
        self.advance_time_and_run(0.1)
        self.mock_event("text_input")

        self.post_event("s_right_flipper_active")
        self.advance_time_and_run()

        self.assertEqual(1, self._events["text_input"])

    def test_qualifying_player_is_prompted_once(self):
        """One qualifying player receives one initials prompt before awards."""
        self.start_game_with_balls()
        self.machine.game.player.score = 5000000
        self.mock_event("high_score_enter_initials")

        self.post_event("start_high_score")
        self.post_event("slide_game_over_removed")
        self.advance_time_and_run(0.1)

        self.assertEqual(1, self._events["high_score_enter_initials"])

    def test_completed_initials_use_the_emitted_award_event(self):
        """The event emitted by MPF has a configured confirmation slide."""
        slide_config = self.machine.modes["high_score"].config["slide_player"]

        self.assertIn("high_score_award_display", slide_config)

"""Tests for Mystery qualification and awards."""

from tests.koth_test_case import KothTestCase


class TestMystery(KothTestCase):
    """Verify Mystery remains useful without interfering with multiball."""

    def _start_ball_and_mystery(self):
        """Finish the first-ball intro and start Mystery's active handlers."""
        self.start_game_with_balls()
        self.post_event("flipper_cancel")
        self.advance_time_and_run(1)
        self.post_event("ball_hold_mystery_scoop_held_ball")
        self.advance_time_and_run(0.1)
        self.assertTrue(self.machine.modes["mystery"].active)

    def test_mystery_can_qualify_during_a_normal_mode(self):
        """A running main mode does not suppress HANK Mystery qualification."""
        self.start_game_with_balls()
        self.mock_event("enable_mystery")
        self.machine.game.player.mode_running = 1

        self.post_event("logicblock_lb_hank_complete_count_updated", value=1)
        self.advance_time_and_run(0.1)

        self.assertEventCalled("enable_mystery")

    def test_mystery_cannot_qualify_during_multiball(self):
        """Any active multiball suppresses HANK Mystery qualification."""
        self.start_game_with_balls()
        self.mock_event("enable_mystery")
        self.machine.game.player.any_mb_active = 1

        self.post_event("logicblock_lb_hank_complete_count_updated", value=1)
        self.advance_time_and_run(0.1)

        self.assertEventNotCalled("enable_mystery")

    def test_starting_grill_multiball_clears_a_lit_mystery(self):
        """The third multiball follows the same Mystery exclusion as the others."""
        self.start_game_with_balls()
        self.mock_event("end_mystery")

        self.post_event("multiball_grill_mb_started")
        self.advance_time_and_run(0.1)

        self.assertEventCalled("end_mystery")

    def test_mystery_point_awards_use_playfield_multiplier(self):
        """Small, big, and weird Mystery points all honor playfield X."""
        self._start_ball_and_mystery()
        self.machine.game.player.pf_multiplier = 2
        score_before = self.machine.game.player.score

        self.post_event("mys_score_10000_points")
        self.post_event("mys_score_big_points")
        self.post_event("mys_weird_sound")
        self.advance_time_and_run(0.1)

        self.assertEqual(5_700_000, self.machine.game.player.score - score_before)

    def test_mystery_extra_ball_is_really_awarded(self):
        """The Mystery event feeds MPF's extra-ball device, not only its slide."""
        self.start_game_with_balls()
        self.post_event("flipper_cancel")
        self.advance_time_and_run(1)
        self.assertTrue(self.machine.modes["extra_ball"].active)
        self.assertPlayerVarEqual(0, "extra_balls")

        self.post_event("award_1")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(1, "extra_balls")

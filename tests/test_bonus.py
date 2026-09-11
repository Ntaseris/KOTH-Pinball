"""Tests for end-of-ball bonus scoring and persistent game totals."""

from tests.koth_test_case import KothTestCase


class TestBonus(KothTestCase):
    """Verify bonus uses per-ball Alamos without clearing game progress."""

    def test_bonus_preserves_game_totals_and_resets_ball_alamos(self):
        """Alamo Champ and completed-mode totals survive the bonus countdown."""
        self.start_game_with_balls()
        player = self.machine.game.player
        player.alamo = 9
        player.alamo_this_ball = 2
        player.modes = 3
        player.bonus_multiplier = 2
        starting_score = player.score

        self.machine.modes["bonus"].start()
        self.advance_time_and_run(14)

        self.assertPlayerVarEqual(9, "alamo")
        self.assertPlayerVarEqual(0, "alamo_this_ball")
        self.assertPlayerVarEqual(3, "modes")
        self.assertPlayerVarEqual(1, "bonus_multiplier")
        self.assertPlayerVarEqual(starting_score + 3_100_000, "score")

    def test_bonus_lighting_shows_are_loaded(self):
        """Every bonus-count phase has its dedicated light show available."""
        self.start_game_with_balls()

        for show in (
            "bonus_open",
            "bonus_alamo_count",
            "bonus_mode_count",
            "bonus_subtotal",
            "bonus_multiplier",
            "bonus_total",
        ):
            self.assertIn(show, self.machine.shows)

    def test_empty_bonus_waits_for_callouts_before_next_ball(self):
        """Even a zero-entry bonus remains active until its voice clips finish."""
        self.start_game_with_balls()

        self.machine.modes["bonus"].start()
        self.advance_time_and_run(5)
        self.assertTrue(self.machine.modes["bonus"].active)

        self.advance_time_and_run(1)
        self.assertFalse(self.machine.modes["bonus"].active)

    def test_beer_targets_feed_ball_and_game_counts(self):
        """Every normal beer target advances both Alamo counters together."""
        self.start_game_with_balls()

        self.hit_and_release_switch("s_right_ramp_standup")
        self.hit_and_release_switch("s_scoop_standup_left")
        self.hit_and_release_switch("s_scoop_standup_right")

        self.assertPlayerVarEqual(3, "alamo")
        self.assertPlayerVarEqual(3, "alamo_this_ball")

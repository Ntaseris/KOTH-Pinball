"""Tests for smaller playfield features and game-flow helpers."""

from tests.koth_test_case import KothTestCase


class TestSupportFeatures(KothTestCase):
    """Verify rollover, save, award, and selection behavior."""

    def _start_past_intro(self):
        """Start Player 1 and skip the once-per-game Arlen introduction."""
        self.start_game_with_balls()
        self.post_event("flipper_cancel")
        self.advance_time_and_run(1)

    def test_alamo_extra_ball_cannot_be_skipped_by_count_jump(self):
        """Crossing 24 in a multi-can award still awards the Alamo extra ball."""
        self._start_past_intro()
        self.machine.game.player.alamo = 23

        self.machine.modes["mystery"].start()
        self.advance_time_and_run(0.1)
        self.post_event("drink_beer")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(29, "alamo")
        self.assertPlayerVarEqual(1, "extra_balls")

    def test_normal_ball_save_flashes_orange(self):
        """Normal launch protection uses the orange flashing treatment."""
        self._start_past_intro()

        self.post_event("ball_save_default_timer_start")
        self.advance_time_and_run(0.02)

        self.assertLightColor("l_ball_save", "orange")

        self.post_event("ball_save_default_disabled")
        self.advance_time_and_run(0.02)
        self.assertLightColor("l_ball_save", "black")

    def test_extra_ball_lit_is_solid_yellow(self):
        """An earned extra ball remains visually distinct from ball save."""
        self._start_past_intro()
        self.post_event("ball_save_default_disabled")
        self.machine.game.player.extra_balls = 1
        self.advance_time_and_run(0.02)

        self.assertLightColor("l_ball_save", "yellow")

    def test_first_bbq_lane_completion_lights_two_x_bonus(self):
        """Completing all three BBQ lanes advances bonus and pays completion points."""
        self._start_past_intro()
        score_before = self.machine.game.player.score

        self.hit_and_release_switch("s_left_rollover_lane")
        self.hit_and_release_switch("s_middle_rollover_lane")
        self.hit_and_release_switch("s_right_rollover_lane")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(2, "bonus_multiplier")
        self.assertGreaterEqual(self.machine.game.player.score - score_before, 250_000)

    def test_ladybird_save_can_only_be_used_once_per_ball(self):
        """Three hits light one save, but it cannot be re-earned after use."""
        self._start_past_intro()

        for _ in range(3):
            self.hit_and_release_switch("s_ladybird_target")
        self.assertPlayerVarEqual(1, "ladybird_save_lit")

        self.hit_and_release_switch("s_left_outlane")
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(0, "ladybird_save_lit")
        self.assertPlayerVarEqual(1, "ladybird_save_used_this_ball")

        for _ in range(3):
            self.hit_and_release_switch("s_ladybird_target")
        self.assertPlayerVarEqual(0, "ladybird_save_lit")

    def test_mission_select_timeout_selects_current_mode(self):
        """An unattended carousel automatically chooses its highlighted mode."""
        self.start_game_with_balls()
        self.mock_event("mission_select_beat_the_surfer_selected")

        self.post_event("mode_scoop_hit")
        self.advance_time_and_run(16)

        self.assertEventCalled("mission_select_beat_the_surfer_selected")

    def test_mission_select_flipper_activity_restarts_timeout(self):
        """Cycling the carousel gives the player another full decision window."""
        self.start_game_with_balls()
        self.mock_event("player_selected_mission")

        self.post_event("mode_scoop_hit")
        self.advance_time_and_run(10)
        self.hit_and_release_switch("s_right_flipper")
        self.advance_time_and_run(10)

        self.assertEventNotCalled("player_selected_mission")

        self.advance_time_and_run(6)
        self.assertEventCalled("player_selected_mission")

    def test_start_cannot_add_player_after_first_plunge(self):
        """The first plunge permanently hands Start-button control to gameplay."""
        self._start_past_intro()
        self.hit_and_release_switch("s_plunger_lane_exit")
        self.advance_time_and_run(0.1)
        # Even an accidental helper restart must not reopen player adding.
        self.machine.modes["add_player"].start()
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(0.1)
        self.assertEqual(1, self.machine.game.num_players)

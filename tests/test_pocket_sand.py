"""Tests for the banked Pocket Sand strategic shot spotter."""

from tests.koth_test_case import KothTestCase


class TestPocketSand(KothTestCase):
    """Verify inventory, activation, and strategic scoring behavior."""

    def _start_after_first_plunge(self):
        self.start_game_with_balls()
        self.hit_and_release_switch("s_plunger_lane_exit")
        self.advance_time_and_run(0.1)

    def test_first_ball_awards_one_sand_after_launch(self):
        self._start_after_first_plunge()

        self.assertPlayerVarEqual(1, "pocket_sand")
        self.assertPlayerVarEqual(1, "pocket_sand_can_use")

    def test_signature_throw_show_is_loaded(self):
        self.assertIn("pocket_sand_throw", self.machine.shows)

    def test_start_does_not_spend_without_valid_mode_shot(self):
        self._start_after_first_plunge()
        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(1, "pocket_sand")
        self.assertEqual(1, self.machine.game.num_players)

    def test_unused_sand_banks_into_next_ball(self):
        self._start_after_first_plunge()
        self.machine.modes["pocket_sand"].stop()
        self.advance_time_and_run(0.1)
        self.machine.modes["pocket_sand"].start()
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(2, "pocket_sand")

    def test_multiple_saved_sands_can_be_used_on_one_ball(self):
        self._start_after_first_plunge()
        self.machine.game.player.pocket_sand = 2
        self.post_event("mission_select_beat_the_surfer_selected")
        self.post_event("slide_beat_the_surfer_rules_removed")
        self.advance_time_and_run(0.1)

        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(0, "pocket_sand")
        self.assertPlayerVarEqual(2_000_000, "beat_the_surfer_total")

    def test_sand_spots_next_surfer_shot_and_is_consumed(self):
        self._start_after_first_plunge()
        self.post_event("mission_select_beat_the_surfer_selected")
        self.post_event("slide_beat_the_surfer_rules_removed")
        self.advance_time_and_run(0.1)

        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(0, "pocket_sand")
        self.assertEqual("unlit", self.machine.shots[
            "shot_left_orbit_surfer"].state_name)
        self.assertPlayerVarEqual(1_000_000, "beat_the_surfer_total")

    def test_strickland_super_jackpot_takes_multiball_priority(self):
        self._start_after_first_plunge()
        self.machine.game.player.pocket_sand = 2
        self.post_event("strickland_multiball_sequence_done")
        self.advance_time_and_run(3.1)
        self.post_event("pop_bumper_counter_complete")
        self.advance_time_and_run(0.1)
        value = self.machine.game.player.strickland_super_jackpot_value
        score_before = self.machine.game.player.score

        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(1, "pocket_sand")
        self.assertEqual(score_before + value, self.machine.game.player.score)
        self.assertPlayerVarEqual(0, "strickland_jackpot_lit")

# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""Tests for the opening skill shot."""

from tests.koth_test_case import KothTestCase


class TestSkillshot(KothTestCase):
    """Verify the skill-shot award follows the game's scoring rules."""

    def test_skillshot_award_uses_playfield_multiplier(self):
        """A successful skill shot awards one million times playfield X."""
        self.start_game_with_balls()
        self.advance_time_and_run(0.1)
        self.machine.game.player.pf_multiplier = 2
        score_before = self.machine.game.player.score

        self.post_event("skillshot_lit_hit")
        self.advance_time_and_run(0.1)

        self.assertEqual(2_000_000, self.machine.game.player.score - score_before)

    def test_skillshot_success_fires_playfield_celebration(self):
        """A successful skill shot immediately flashes the target bank white."""
        self.start_game_with_balls()
        self.machine.modes["skillshot"].start()

        self.post_event("skillshot_lit_hit")
        self.advance_time_and_run(0.02)

        self.assertLightColor("l_p_target", "white")
        self.assertLightColor("l_e_target", "white")

    def test_skillshot_miss_does_not_award_points(self):
        """An unlit PROPANE target remains a zero-point skill-shot miss."""
        self.start_game_with_balls()
        self.advance_time_and_run(0.1)
        score_before = self.machine.game.player.score

        self.post_event("skillshot_off_hit")
        self.advance_time_and_run(0.1)

        self.assertEqual(score_before, self.machine.game.player.score)

    def test_skillshot_stop_does_not_fire_generic_voice_callouts(self):
        """A hit or miss result is not layered with launch encouragement."""
        self.start_game_with_balls()
        for event in (
            "play_hank_ready_kick_some_butt",
            "play_hank_keep_eye_on_ball",
            "play_hank_just_do_your_best",
        ):
            self.mock_event(event)

        self.post_event("stop_mode_skillshot")
        self.advance_time_and_run(0.1)

        for event in (
            "play_hank_ready_kick_some_butt",
            "play_hank_keep_eye_on_ball",
            "play_hank_just_do_your_best",
        ):
            self.assertEventNotCalled(event)

    def test_plunger_lane_exit_locks_one_skillshot(self):
        """Leaving the plunger lane stops rotation on one flashing target."""
        self.start_game_with_balls()
        self.advance_time_and_run(0.2)

        self.mock_event("skillshot_launch_committed")
        self.hit_switch_and_run("s_plunger_lane_exit", 0.01)
        self.release_switch_and_run("s_plunger_lane_exit", 0.01)
        self.advance_time_and_run(0.1)

        self.assertEventCalled("skillshot_launch_committed", times=1)
        self.assertFalse(self.machine.timers["skillshot_rotate"].running)

        shot_names = (
            "skillshot_p_target",
            "skillshot_r_target",
            "skillshot_o_target",
            "skillshot_p2_target",
            "skillshot_a_target",
            "skillshot_n_target",
            "skillshot_e_target",
        )
        lit_shots = [
            name for name in shot_names
            if self.machine.shots[name].state_name == "lit"
        ]
        self.assertEqual(1, len(lit_shots))

    def test_launch_switch_chatter_does_not_restart_skillshot_window(self):
        """Only the first launch signal commits the skill shot."""
        self.start_game_with_balls()
        self.advance_time_and_run(0.2)
        self.mock_event("skillshot_launch_committed")

        self.hit_switch_and_run("s_plunger_lane_exit", 0.01)
        self.release_switch_and_run("s_plunger_lane_exit", 0.01)
        self.advance_time_and_run(5)

        self.hit_switch_and_run("s_plunger_lane_exit", 0.01)
        self.release_switch_and_run("s_plunger_lane_exit", 0.01)
        self.advance_time_and_run(0.1)

        self.assertEventCalled("skillshot_launch_committed", times=1)
        self.advance_time_and_run(7)
        self.assertFalse(self.machine.modes["skillshot"].active)

    def test_roving_skillshot_does_not_expire_before_launch(self):
        """The roving selection remains active while the player waits."""
        self.start_game_with_balls()
        self.post_event("stop_mode_skillshot")
        self.advance_time_and_run(0.1)
        self.machine.modes["skillshot"].start()
        self.advance_time_and_run(30)

        self.assertTrue(self.machine.modes["skillshot"].active)
        self.assertTrue(self.machine.timers["skillshot_rotate"].running)

    def test_skillshot_window_runs_twelve_seconds_after_launch(self):
        """The shot window starts at launch and allows time to reach a flipper."""
        self.start_game_with_balls()
        self.post_event("stop_mode_skillshot")
        self.advance_time_and_run(0.1)
        self.machine.modes["skillshot"].start()
        self.post_event("skillshot_launch_committed")

        self.advance_time_and_run(11.9)
        self.assertTrue(self.machine.modes["skillshot"].active)

        self.advance_time_and_run(0.2)
        self.assertFalse(self.machine.modes["skillshot"].active)

"""Tests for Strickland Multiball qualification and jackpot cycles."""

from tests.koth_test_case import KothTestCase


class TestStricklandMultiball(KothTestCase):
    """Verify qualification remains fair and jackpot cycles repeat."""

    def _start_strickland(self):
        self.start_game_with_balls()
        self.post_event("strickland_multiball_sequence_done")
        self.advance_time_and_run(0.1)

        self.assertTrue(self.machine.modes["strickland_multiball"].active)
        self.assertFalse(self.machine.multiballs["strickland_multiball"].balls_added_live)

        self.advance_time_and_run(3.1)
        self.assertTrue(self.machine.multiballs["strickland_multiball"].balls_added_live)

    def test_rules_delay_precedes_ball_release(self):
        """The rules card gets three seconds before multiball launches."""
        self._start_strickland()

    def test_live_play_has_ambient_motion_beneath_objectives(self):
        """Strickland keeps moving after its launch burst releases the lights."""
        self._start_strickland()
        self.advance_time_and_run(0.6)

        self.assertNotLightColor("l_gi1", "black")
        self.assertNotLightColor("l_hank_1", "black")

    def test_jackpot_ready_escalates_left_orbit_and_gi(self):
        """Ten pops turn the left orbit into the dominant visual objective."""
        self._start_strickland()

        for _ in range(10):
            self.hit_and_release_switch("s_left_pop_bumper")
            self.advance_time_and_run(0.05)

        self.assertNotLightColor("l_left_orbit", "black")
        self.assertNotLightColor("l_gi1", "black")

    def test_jackpot_collect_fires_propane_burst(self):
        """Collecting the lit orbit produces the full-playfield jackpot beat."""
        self._start_strickland()

        for _ in range(10):
            self.hit_and_release_switch("s_left_pop_bumper")
            self.advance_time_and_run(0.05)

        self.hit_and_release_switch("s_left_orbit_enter")
        self.advance_time_and_run(0.02)

        self.assertLightColor("l_left_orbit", "white")
        self.assertLightColor("l_gi1", "white")

    def test_shoot_again_fires_playfield_rebound(self):
        """A saved Strickland drain flashes the ball-save insert and GI."""
        self._start_strickland()

        self.post_event("multiball_strickland_multiball_shoot_again", balls=1)
        self.advance_time_and_run(0.02)

        self.assertLightColor("l_ball_save", "white")
        self.assertLightColor("l_gi1", "white")

    def test_shoot_again_window_flashes_cyan(self):
        """Active multiball protection is distinct from normal ball save."""
        self._start_strickland()
        self.post_event("ball_save_strickland_multiball_timer_start")
        self.advance_time_and_run(0.02)

        self.assertLightColor("l_ball_save", "cyan")

    def test_rainey_lock_insert_is_hidden_during_strickland(self):
        """A qualified Rainey lock remains suspended without misleading the player."""
        self.start_game_with_balls()
        self.post_event("light_rainey_multiball_ball_lock_lit_complete")
        self.advance_time_and_run(0.1)
        self.assertLightColor("l_lock_lit", "green")

        self.post_event("strickland_multiball_sequence_done")
        self.advance_time_and_run(3.1)

        self.assertEqual("started", self.machine.achievements["lock_lit"].state)
        self.assertFalse(self.machine.counters["mb_counter"].enabled)
        self.assertLightColor("l_lock_lit", "black")

        self.post_event("multiball_strickland_multiball_ended")
        self.advance_time_and_run(1.1)

        self.assertTrue(self.machine.counters["mb_counter"].enabled)
        self.assertLightColor("l_lock_lit", "green")

    def test_pop_bumpers_build_and_repeat_propane_jackpot(self):
        """Ten pops light the orbit, which awards and resets the cycle."""
        self._start_strickland()

        for _ in range(10):
            self.hit_and_release_switch("s_left_pop_bumper")
            self.advance_time_and_run(0.05)

        self.assertPlayerVarEqual(1500000, "strickland_super_jackpot_value")
        self.assertTrue(self.machine.shots["super_jackpot_collect"].enabled)

        score_before_collect = self.machine.game.player.score
        self.hit_and_release_switch("s_left_orbit_enter")
        self.advance_time_and_run(0.1)

        self.assertEqual(1550000, self.machine.game.player.score - score_before_collect)
        self.assertFalse(self.machine.shots["super_jackpot_collect"].enabled)
        self.assertEqual(0, self.machine.counters["pop_bumper_counter"].value)

    def test_unlit_left_orbit_releases_post_into_pops(self):
        """An unlit spinner-to-orbit shot raises the post during multiball."""
        self._start_strickland()
        self.mock_event("left_orbit_post_release")

        self.hit_and_release_switch("s_left_spinner")
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s_left_orbit_enter")

        self.assertEventCalled("left_orbit_post_release")

    def test_lit_jackpot_left_orbit_stays_down(self):
        """A lit jackpot completes the orbit without raising the post."""
        self._start_strickland()

        for _ in range(10):
            self.hit_and_release_switch("s_left_pop_bumper")
            self.advance_time_and_run(0.05)

        self.mock_event("left_orbit_post_release")
        self.hit_and_release_switch("s_left_spinner")
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s_left_orbit_enter")

        self.assertEventNotCalled("left_orbit_post_release")

    def test_scoop_standups_do_not_erase_qualification_progress(self):
        """Common scoop grazing no longer resets a completed drop-bank step."""
        self.start_game_with_balls()
        self.mock_event("strickland_multiball_sequence_done")

        self.post_event("drop_target_bank_metallica_bank_down")
        self.hit_and_release_switch("s_scoop_standup_left")
        self.hit_and_release_switch("s_left_pop_bumper")
        self.advance_time_and_run(0.1)

        self.assertEventCalled("strickland_multiball_sequence_done")

    def test_right_ramp_standup_resets_qualification_progress(self):
        """The single designated standup still carries qualification risk."""
        self.start_game_with_balls()
        self.mock_event("strickland_multiball_sequence_done")

        self.post_event("drop_target_bank_metallica_bank_down")
        self.hit_and_release_switch("s_right_ramp_standup")
        self.hit_and_release_switch("s_left_pop_bumper")
        self.advance_time_and_run(0.1)

        self.assertEventNotCalled("strickland_multiball_sequence_done")

    def test_completed_bank_remains_qualified_for_the_ball(self):
        """Qualification does not expire while the bank remains completed."""
        self.start_game_with_balls()
        self.mock_event("strickland_multiball_sequence_done")

        self.post_event("drop_target_bank_metallica_bank_down")
        self.advance_time_and_run(10)
        self.hit_and_release_switch("s_left_pop_bumper")
        self.advance_time_and_run(0.1)

        self.assertEventCalled("strickland_multiball_sequence_done")

    def test_bbq_lane_temporarily_blocks_pop_start_without_erasing_qualification(self):
        """A lane-fed pop is ignored, then the qualified start becomes available again."""
        self.start_game_with_balls()
        self.mock_event("strickland_multiball_sequence_done")

        self.post_event("drop_target_bank_metallica_bank_down")
        self.hit_and_release_switch("s_middle_rollover_lane")
        self.hit_and_release_switch("s_left_pop_bumper")
        self.advance_time_and_run(0.1)

        self.assertEventNotCalled("strickland_multiball_sequence_done")

        self.advance_time_and_run(5.7)
        self.hit_and_release_switch("s_right_pop_bumper")
        self.advance_time_and_run(0.1)

        self.assertEventNotCalled("strickland_multiball_sequence_done")

        self.advance_time_and_run(0.1)
        self.hit_and_release_switch("s_right_pop_bumper")
        self.advance_time_and_run(0.1)

        self.assertEventCalled("strickland_multiball_sequence_done")

"""Tests for base mode: PRO qualification, playfield multiplier, scoring."""
from tests.koth_test_case import KothTestCase


class TestBaseMode(KothTestCase):
    def test_single_ball_drain_fires_red_collapse(self):
        """An ordinary drain begins with a brief red shot collapse."""
        self.start_game_with_balls()

        self.post_event('ball_drain', balls=1)
        self.advance_time_and_run(0.02)

        self.assertLightColor('l_left_orbit', 'red')
        self.assertLightColor('l_right_orbit', 'red')

    def test_gi_defaults_to_white_during_game(self):
        """All GI channels remain lit when the attract show releases them."""
        self.start_game_with_balls()
        self.advance_time_and_run(0.1)

        for light in (
            "l_gi1", "l_gi2", "l_gi3", "l_gi4",
            "l_gi5", "l_gi6", "l_gi7", "l_gi8",
        ):
            self.assertLightColor(light, "white")

    def _start_past_skillshot(self):
        """Start a game and advance past the skillshot window.

        PRO targets are disabled while the skillshot mode is running.
        Posting stop_mode_skillshot ends the skillshot window and enables
        the qualify_mission shot group.
        """
        self.start_game_with_balls()
        self.advance_time_and_run(2)
        self.post_event('stop_mode_skillshot')
        self.advance_time_and_run(1)

    # --- PRO target qualification ---

    def test_pro_targets_qualify_mission(self):
        """Hitting P-R-O lights the scoop for mission select."""
        self._start_past_skillshot()
        self.mock_event('qualify_mission_lit_complete')

        self.qualify_mission()

        self.assertEventCalled('qualify_mission_lit_complete')

    def test_incomplete_pro_does_not_qualify(self):
        """Hitting only two PRO targets does not fire qualify_mission_lit_complete."""
        self._start_past_skillshot()
        self.mock_event('qualify_mission_lit_complete')

        self.hit_and_release_switch('s_p_target')
        self.hit_and_release_switch('s_r_target')
        self.advance_time_and_run(0.5)

        self.assertEventNotCalled('qualify_mission_lit_complete')

    def test_friendly_neighbor_p_awards_r_when_r_unlit(self):
        """Hitting a lit P target when R is unlit awards R (friendly neighbor).

        After P is completed, hitting it again when R is unlit fires
        friendly_neighbor_award_r (gives R for free).
        """
        self._start_past_skillshot()
        self.mock_event('friendly_neighbor_award_r')

        self.hit_and_release_switch('s_p_target')   # P: unlit → lit → completed
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch('s_p_target')   # P completed again — neighbor award fires
        self.advance_time_and_run(0.5)

        self.assertEventCalled('friendly_neighbor_award_r')

    # --- Playfield multiplier ---

    def test_captive_ball_three_hits_gives_2x(self):
        """Three captive ball hits trigger the 2x playfield multiplier."""
        self.start_game_with_balls()
        self.advance_time_and_run(1)
        self.assertPlayerVarEqual(1, 'pf_multiplier')

        for _ in range(3):
            self.hit_and_release_switch('s_captive_ball_standup')
            self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(2, 'pf_multiplier')

    def test_pf_multiplier_resets_on_ball_end(self):
        """pf_multiplier resets to 1 when ball_will_end fires."""
        self.start_game_with_balls()
        self.advance_time_and_run(1)

        for _ in range(3):
            self.hit_and_release_switch('s_captive_ball_standup')
            self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(2, 'pf_multiplier')

        self.post_event('ball_will_end')
        self.advance_time_and_run(1)
        self.assertPlayerVarEqual(1, 'pf_multiplier')

    # --- Basic switch scoring ---

    def test_right_inlane_scores_points(self):
        """s_right_inlane scores 100 * pf_multiplier."""
        self.start_game_with_balls()
        self.advance_time_and_run(1)
        score_before = self.machine.game.player.score

        self.hit_and_release_switch('s_right_inlane')
        self.advance_time_and_run(0.1)

        self.assertGreater(self.machine.game.player.score, score_before)

    def test_first_alamo_can_posts_display_refresh_after_count_updates(self):
        """The first can creates the HUD after its player value becomes one."""
        self.start_game_with_balls()
        self.advance_time_and_run(1)
        self.mock_event('refresh_alamo_counter')

        self.hit_and_release_switch('s_right_ramp_standup')
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(1, 'alamo')
        self.assertEventCalled('refresh_alamo_counter')

    def test_either_spinner_restarts_steak_sizzle_tail(self):
        """Both physical spinner switches keep the sizzle tail alive."""
        self.start_game_with_balls()
        self.advance_time_and_run(1)

        for switch in ('s_left_spinner', 's_center_spinner'):
            with self.subTest(switch=switch):
                self.hit_and_release_switch(switch)
                self.advance_time_and_run(0.1)
                self.assertTrue(self.machine.timers['steak_spinner_stop'].running)

    def test_slings_score_points(self):
        """Left and right slings score points."""
        self.start_game_with_balls()
        self.advance_time_and_run(1)
        score_before = self.machine.game.player.score

        self.hit_and_release_switch('s_left_sling')
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch('s_right_sling')
        self.advance_time_and_run(0.1)

        self.assertGreater(self.machine.game.player.score, score_before)

    def test_every_playfield_switch_has_base_scoring(self):
        """Every legitimate scoring switch awards points outside special modes."""
        self.start_game_with_balls()
        scoring_switches = (
            's_right_inlane', 's_p_target', 's_r_target', 's_o_target',
            's_p2_target', 's_a_target', 's_n_target', 's_e_target',
            's_ladybird_target', 's_top_inline_drop', 's_middle_inline_drop',
            's_bottom_inline_drop', 's_left_ramp_exit', 's_right_ramp_exit',
            's_left_outlane', 's_left_inlane', 's_left_sling',
            's_right_sling', 's_right_outlane', 's_right_ramp_standup',
            's_left_orbit_enter', 's_left_spinner', 's_center_spinner',
            's_left_pop_bumper', 's_right_pop_bumper',
            's_left_rollover_lane', 's_middle_rollover_lane',
            's_right_rollover_lane', 's_right_orbit_exit',
            's_left_inner_horseshoe', 's_captive_ball_standup',
            's_scoop_standup_left', 's_scoop_standup_right', 's_scoop',
            's_luanne', 's_grill1', 's_grill2', 's_grill3',
        )

        for switch in scoring_switches:
            with self.subTest(switch=switch):
                score_before = self.machine.game.player.score
                self.post_event(f'{switch}_active')
                self.advance_time_and_run(0.01)
                self.assertGreater(self.machine.game.player.score, score_before)

    def test_multiball_adds_scoring_floor_to_every_switch(self):
        """Even an unqualified switch remains worthwhile during multiball."""
        self.start_game_with_balls()
        self.post_event('multiball_grill_mb_started')
        self.advance_time_and_run(0.1)
        score_before = self.machine.game.player.score

        self.post_event('s_left_sling_active')
        self.advance_time_and_run(0.1)

        self.assertEqual(score_before + 26000, self.machine.game.player.score)

    def test_captive_ball_scores_without_multiplier(self):
        """Captive ball scores 50000 at 1x."""
        self.start_game_with_balls()
        self.advance_time_and_run(1)
        score_before = self.machine.game.player.score

        self.hit_and_release_switch('s_captive_ball_standup')
        self.advance_time_and_run(0.1)

        # 50000 * 1 = 50000
        self.assertEqual(score_before + 50000, self.machine.game.player.score)

    def test_captive_ball_scores_double_with_2x(self):
        """Captive ball scores 100000 at 2x."""
        self.start_game_with_balls()
        self.advance_time_and_run(1)

        # Get to 2x
        for _ in range(3):
            self.hit_and_release_switch('s_captive_ball_standup')
            self.advance_time_and_run(0.1)

        # 2x is now active; record score after the multiplier kicks in
        self.assertPlayerVarEqual(2, 'pf_multiplier')
        score_before = self.machine.game.player.score

        self.hit_and_release_switch('s_captive_ball_standup')
        self.advance_time_and_run(0.1)

        self.assertEqual(score_before + 100000, self.machine.game.player.score)

    # --- mission_qualified state variable ---

    def test_mission_qualified_set_after_pro(self):
        """mission_qualified player var is 1 after completing PRO."""
        self._start_past_skillshot()

        self.qualify_mission()

        self.assertPlayerVarEqual(1, 'mission_qualified')

    def test_mission_qualified_cleared_on_mission_select_start(self):
        """mission_qualified is cleared when mission_select mode starts."""
        self._start_past_skillshot()
        self.qualify_mission()
        self.assertPlayerVarEqual(1, 'mission_qualified')

        self.post_event('mode_mission_select_started')
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(0, 'mission_qualified')

    def test_mission_select_owns_scoop_then_restores_lit_mystery(self):
        """A lit Mystery cannot eject the scoop during mode selection."""
        self.start_game_with_balls()
        self.post_event('enable_mystery')
        self.advance_time_and_run(0.1)
        self.assertTrue(self.machine.ball_holds['mystery_scoop'].enabled)

        self.post_event('qualify_mission_lit_complete')
        self.advance_time_and_run(0.1)
        self.assertFalse(self.machine.ball_holds['mystery_scoop'].enabled)
        self.assertTrue(self.machine.ball_holds['mission_select'].enabled)

        self.post_event('player_selected_mission')
        self.advance_time_and_run(0.1)
        self.assertTrue(self.machine.ball_holds['mystery_scoop'].enabled)

    def test_propane_display_latches_each_half_until_its_award_starts(self):
        """Each completed half remains latched until its qualified award starts."""
        self.start_game_with_balls()

        self.post_event('qualify_mission_lit_complete')
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(1, 'propane_ui_pro_complete')
        self.assertPlayerVarEqual(0, 'propane_ui_pane_complete')

        self.post_event('mode_mission_select_started')
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(0, 'propane_ui_pro_complete')

        self.post_event('light_rainey_multiball_ball_lock_lit_complete')
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(0, 'propane_ui_pro_complete')
        self.assertPlayerVarEqual(1, 'propane_ui_pane_complete')

        self.post_event('multiball_rainey_multiball_started')
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(0, 'propane_ui_pane_complete')

    def test_propane_display_does_not_clear_while_awards_are_waiting(self):
        """Completing PROPANE does not erase uncollected qualifications."""
        self.start_game_with_balls()

        self.post_event('qualify_mission_lit_complete')
        self.post_event('light_rainey_multiball_ball_lock_lit_complete')
        self.advance_time_and_run(3.2)
        self.assertPlayerVarEqual(1, 'propane_ui_pro_complete')
        self.assertPlayerVarEqual(1, 'propane_ui_pane_complete')

    # --- mode and multiball interaction rules ---

    def test_multiball_does_not_stop_active_mission(self):
        """Starting multiball while a mission runs leaves the mission active."""
        self.start_game_with_balls()
        self.post_event('mission_select_dog_dale_afternoon_selected')
        self.advance_time_and_run(0.5)
        self.assertTrue(self.machine.modes['dog_dale_afternoon'].active)

        self.post_event('multiball_strickland_multiball_started')
        self.advance_time_and_run(0.5)

        self.assertTrue(self.machine.modes['dog_dale_afternoon'].active)

    def test_mission_cannot_start_during_multiball(self):
        """Mission selection cannot launch a new mission during multiball."""
        self.start_game_with_balls()
        self.post_event('multiball_strickland_multiball_started')
        self.advance_time_and_run(0.1)

        self.post_event('mission_select_dog_dale_afternoon_selected')
        self.advance_time_and_run(0.5)

        self.assertFalse(self.machine.modes['dog_dale_afternoon'].active)

    def test_overlapping_multiball_state_clears_after_last_multiball(self):
        """Ending one stacked multiball does not falsely report that all are over."""
        self.start_game_with_balls()
        self.post_event('multiball_strickland_multiball_started')
        self.post_event('multiball_grill_mb_started')
        self.assertFalse(self.machine.counters['mb_counter'].enabled)
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(2, 'any_mb_active')

        self.post_event('multiball_strickland_multiball_ended')
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(1, 'any_mb_active')

        self.post_event('multiball_grill_mb_ended')
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(0, 'any_mb_active')

    def test_pane_targets_light_rainey_lock(self):
        """Completing P-A-N-E is the event that lights the Rainey lock."""
        self._start_past_skillshot()
        self.mock_event('light_rainey_multiball_ball_lock_lit_complete')

        for switch in ('s_p2_target', 's_a_target', 's_n_target', 's_e_target'):
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(0.1)

        self.assertEventCalled('light_rainey_multiball_ball_lock_lit_complete')
        self.advance_time_and_run(1.0)
        self.assertLightColor('l_lock_lit', 'green')

    def test_rainey_lock_counter_resumes_after_other_multiball(self):
        """An ended multiball re-enables a lit Rainey center-spinner lock."""
        self.start_game_with_balls()
        self.post_event('light_rainey_multiball_ball_lock_lit_complete')
        self.advance_time_and_run(0.1)
        self.assertEqual('started', self.machine.achievements['lock_lit'].state)
        self.hit_and_release_switch('s_center_spinner')
        self.advance_time_and_run(1.1)
        self.assertEqual(1, self.machine.counters['mb_counter'].value)
        self.assertLightColor('l_lock_1', 'green')

        self.post_event('multiball_grill_mb_started')
        self.hit_and_release_switch('s_center_spinner')
        self.advance_time_and_run(0.1)
        self.assertEqual(1, self.machine.counters['mb_counter'].value)

        self.post_event('multiball_grill_mb_ended')
        self.advance_time_and_run(1.1)
        self.assertTrue(self.machine.counters['mb_counter'].enabled)
        self.hit_and_release_switch('s_center_spinner')
        self.advance_time_and_run(1.1)
        self.assertEqual(2, self.machine.counters['mb_counter'].value)
        self.assertLightColor('l_lock_2', 'green')

    def test_other_multiball_indicators_are_hidden_during_multiball(self):
        """Only the active multiball may advertise shots on the playfield."""
        self.start_game_with_balls()
        self.post_event('light_rainey_multiball_ball_lock_lit_complete')
        self.post_event('drop_target_bank_metallica_bank_down')
        self.post_event('logicblock_grill_mb_counter_complete')
        self.advance_time_and_run(0.1)

        self.assertNotLightColor('l_lock_lit', 'black')
        self.assertNotLightColor('l_strickland_multiball', 'black')
        self.assertNotLightColor('l_right_ramp', 'black')

        self.post_event('multiball_grill_mb_started')
        self.advance_time_and_run(0.1)

        self.assertLightColor('l_lock_lit', 'black')
        self.assertLightColor('l_strickland_multiball', 'black')

    def test_rainey_stops_grill_ready_flash_and_hides_strickland(self):
        """Rainey owns its shot lights without showing other multiball readiness."""
        self.start_game_with_balls()
        self.post_event('drop_target_bank_metallica_bank_down')
        self.post_event('logicblock_grill_mb_counter_complete')
        self.advance_time_and_run(0.1)

        self.post_event('multiball_rainey_multiball_started')
        self.advance_time_and_run(1.1)

        self.assertLightColor('l_lock_lit', 'black')
        self.assertLightColor('l_strickland_multiball', 'black')
        self.assertLightColor('l_right_ramp', 'blue')

    def test_third_rainey_lock_starts_multiball_immediately(self):
        """The third center-spinner lock directly starts Rainey Multiball."""
        self.start_game_with_balls()
        self.post_event('light_rainey_multiball_ball_lock_lit_complete')
        self.mock_event('multiball_rainey_multiball_started')

        self.post_event('spinner_lock_spinner_active')
        self.post_event('spinner_lock_spinner_active')
        self.assertEventNotCalled('multiball_rainey_multiball_started')

        self.post_event('spinner_lock_spinner_active')
        self.advance_time_and_run(0.1)

        self.assertEventCalled('multiball_rainey_multiball_started')

    def test_rainey_display_progress_tracks_rule_phases(self):
        """Display variables follow character, beer, and Super Jackpot phases."""
        self.start_game_with_balls()
        self.post_event('multiball_rainey_multiball_started')
        self.advance_time_and_run(0.1)

        for _ in range(4):
            self.post_event('rainey_character_jackpot_collected')
            self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(4, 'rainey_characters_collected')
        self.assertPlayerVarEqual(2, 'rainey_phase')

        for _ in range(6):
            self.post_event('rainey_beer_collected')
            self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(6, 'rainey_beers_collected')
        self.assertPlayerVarEqual(3, 'rainey_phase')

    def test_rainey_super_jackpot_remembers_multiplied_award(self):
        """The Super Jackpot video displays the amount actually scored."""
        self.start_game_with_balls()
        self.machine.game.player.pf_multiplier = 2
        self.post_event('multiball_rainey_multiball_started')
        self.post_event('rainey_super_jackpot_collected')
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(10000000, 'rainey_last_super_award')

    def test_rainey_phase_lighting_keeps_objective_cues_readable(self):
        """Ambient motion changes by phase without replacing the blue jackpots."""
        self.start_game_with_balls()
        self.post_event('multiball_rainey_multiball_started')
        self.advance_time_and_run(0.7)

        self.assertLightColor('l_right_ramp', 'blue')
        self.assertNotLightColor('l_gi1', 'black')

        self.post_event('rainey_all_characters_collected')
        self.advance_time_and_run(0.7)
        self.assertNotLightColor('l_grill1', 'black')

        self.post_event('rainey_super_jackpot_lit')
        self.advance_time_and_run(0.1)
        self.assertNotLightColor('l_scoop', 'black')

    def test_rainey_shoot_again_fires_playfield_rebound(self):
        """A saved Rainey drain flashes the ball-save insert and GI."""
        self.start_game_with_balls()
        self.post_event('multiball_rainey_multiball_started')
        self.post_event('multiball_rainey_multiball_shoot_again', balls=1)
        self.advance_time_and_run(0.02)

        self.assertLightColor('l_ball_save', 'white')
        self.assertLightColor('l_gi1', 'white')

    def test_rainey_shoot_again_window_flashes_cyan(self):
        """Rainey protection stays visibly active before a drain occurs."""
        self.start_game_with_balls()
        self.post_event('multiball_rainey_multiball_started')
        self.post_event('ball_save_rainey_multiball_timer_start')
        self.advance_time_and_run(0.02)

        self.assertLightColor('l_ball_save', 'cyan')

    def test_rainey_intro_uses_explicit_gapless_display_timing(self):
        """Rules and live play replace one another without inactive-slide races."""
        self.start_game_with_balls()
        self.mock_event('rainey_show_rules')
        self.mock_event('rainey_show_playfield')

        self.post_event('multiball_rainey_multiball_started')
        self.advance_time_and_run(2.9)
        self.assertEventNotCalled('rainey_show_rules')
        self.assertEventNotCalled('rainey_show_playfield')

        self.advance_time_and_run(0.2)
        self.assertEventCalled('rainey_show_rules')
        self.assertEventNotCalled('rainey_show_playfield')

        self.advance_time_and_run(2.4)
        self.assertEventCalled('rainey_show_playfield')

    def test_grill_lock_requires_qualification_and_physical_lock(self):
        """Grill counts a ball only after qualification and lock arrival."""
        self.start_game_with_balls()
        self.mock_event('grill_lock_confirmed')

        self.hit_and_release_switch('s_right_ramp_exit')
        self.advance_time_and_run(1.5)
        self.assertEventNotCalled('grill_lock_confirmed')

        for _ in range(5):
            self.hit_and_release_switch('s_center_spinner')
            self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(1, 'grill_lock_ready')

        self.hit_and_release_switch('s_right_ramp_exit')
        self.advance_time_and_run(5)
        self.assertEventCalled('grill_lock_confirmed')

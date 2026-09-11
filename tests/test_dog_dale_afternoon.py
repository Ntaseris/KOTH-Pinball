"""Tests for Dog Dale Afternoon mission mode.

Mode starts on mission_select_dog_dale_afternoon_selected.
5 lit shots complete the mode (accrual → dog_dale_afternoon_done).
Spinner raises every remaining fire shot's value by 250K per spin.
Countdown timer at 46s stops the mode if not completed.
"""
from tests.koth_test_case import KothTestCase

_SHOTS = [
    's_right_orbit_exit',
    's_right_ramp_exit',
    's_left_inner_horseshoe',
    's_left_ramp_exit',
    's_left_orbit_enter',
]


class TestDogDaleAfternoon(KothTestCase):

    def _start_mode(self):
        """Helper: start a game, get ball in play, launch the mode."""
        self.start_game_with_balls()
        self.advance_time_and_run(2)
        self.post_event('mission_select_dog_dale_afternoon_selected')
        self.advance_time_and_run(1)

    # --- mode lifecycle ---

    def test_mode_starts_on_selection_event(self):
        self.start_game_with_balls()
        self.advance_time_and_run(1)
        self.mock_event('mode_dog_dale_afternoon_started')

        self.post_event('mission_select_dog_dale_afternoon_selected')
        self.advance_time_and_run(1)

        self.assertEventCalled('mode_dog_dale_afternoon_started')
        self.assertModeRunning('dog_dale_afternoon')

    def test_mode_sets_mode_running_var(self):
        self._start_mode()
        self.assertPlayerVarEqual(1, 'mode_running')

    def test_mode_stops_on_ball_ended(self):
        """Mode stops when the ball ends (ball_ended stop event fires)."""
        self._start_mode()
        self.mock_event('mode_dog_dale_afternoon_stopped')

        self.post_event('ball_ended')
        self.advance_time_and_run(1)

        self.assertEventCalled('mode_dog_dale_afternoon_stopped')
        self.assertModeNotRunning('dog_dale_afternoon')

    def test_mode_stops_on_timer_expiry(self):
        """Mode ends when the 46s countdown reaches zero.

        The countdown timer starts on slide_dog_dale_afternoon_rules_removed
        (a GMC event). We post it directly to start the timer, then advance
        past the 46s countdown.
        """
        self._start_mode()
        self.mock_event('mode_dog_dale_afternoon_stopped')
        # Start the countdown (normally fired by GMC when the rules slide expires)
        self.post_event('slide_dog_dale_afternoon_rules_removed')
        self.advance_time_and_run(47)

        self.assertEventCalled('mode_dog_dale_afternoon_stopped')

    # --- shots and scoring ---

    def test_lit_shot_scores(self):
        """Hitting a lit shot awards its guaranteed fire value."""
        self._start_mode()
        self.advance_time_and_run(1)
        score_before = self.machine.game.player.score

        self.hit_and_release_switch('s_right_orbit_exit')
        self.advance_time_and_run(0.5)

        self.assertEqual(525000, self.machine.game.player.score - score_before)

    def test_unlit_shot_scores_100k_when_shots_on_fire_low(self):
        """When shots_on_fire <= 6, an unlit hit scores 100000 * pf_multiplier.

        We force shots_on_fire to 3 directly via player variable, then check
        that hitting an unlit shot awards the correct base points.
        """
        self._start_mode()
        self.advance_time_and_run(1)

        # Force shots_on_fire below the threshold
        self.machine.game.player['shots_on_fire'] = 3

        # Hit a shot that is in unlit state.
        # All shots start lit, so we first complete one to make it available
        # for an unlit hit check — or just verify the condition fires correctly
        # by checking score changes. With shots_on_fire=3, an unlit hit scores 100k.
        score_before = self.machine.game.player.score
        self.post_event('right_orbit_dog_dale_unlit_hit')
        self.advance_time_and_run(0.1)

        # 100000 * pf_multiplier(1) = 100000
        self.assertEqual(score_before + 100000, self.machine.game.player.score)

    def test_spinner_increases_every_fire_value_per_spin(self):
        """Each center-spinner spin permanently adds 250K to every fire."""
        self._start_mode()
        self.advance_time_and_run(1)
        self.assertPlayerVarEqual(500000, 'dog_dale_fire_value')

        self.hit_and_release_switch('s_center_spinner')
        self.hit_and_release_switch('s_center_spinner')
        self.advance_time_and_run(0.1)

        self.assertEqual(1000000, self.machine.game.player['dog_dale_fire_value'])

    def test_collected_fire_does_not_reset_other_fire_values(self):
        """Collecting one fire leaves the spinner-built value on the others."""
        self._start_mode()
        self.advance_time_and_run(1)

        self.hit_and_release_switch('s_center_spinner')
        self.hit_and_release_switch('s_center_spinner')
        self.advance_time_and_run(0.1)
        self.assertEqual(1000000, self.machine.game.player['dog_dale_fire_value'])

        self.hit_and_release_switch('s_right_orbit_exit')
        self.advance_time_and_run(0.5)

        self.assertEqual(1000000, self.machine.game.player['dog_dale_fire_value'])

    # --- mode completion ---

    def test_all_five_shots_complete_mode(self):
        """Hitting all five fire shots completes and stops the mode."""
        self._start_mode()
        self.advance_time_and_run(1)
        self.mock_event('dog_dale_afternoon_done')

        for switch in _SHOTS:
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(0.3)

        self.assertEventCalled('dog_dale_afternoon_done')
        self.assertModeNotRunning('dog_dale_afternoon')

    def test_four_shots_do_not_complete_mode(self):
        """Four of the five fire shots do not complete the mode."""
        self._start_mode()
        self.advance_time_and_run(1)
        self.mock_event('dog_dale_afternoon_done')

        for switch in _SHOTS[:-1]:
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(0.3)

        self.assertEventNotCalled('dog_dale_afternoon_done')
        self.assertModeRunning('dog_dale_afternoon')

    def test_inline_and_captive_are_not_mode_objectives(self):
        """The two shots without clear fire cues cannot advance completion."""
        self._start_mode()
        self.mock_event('dog_dale_afternoon_done')

        self.hit_and_release_switch('s_bottom_inline_drop')
        self.hit_and_release_switch('s_captive_ball_standup')
        self.advance_time_and_run(0.2)

        self.assertEventNotCalled('dog_dale_afternoon_done')

    def test_mode_running_cleared_after_completion(self):
        """mode_running var goes back to 0 after mode completes."""
        self._start_mode()
        self.advance_time_and_run(1)

        for switch in _SHOTS:
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(0.3)

        self.assertPlayerVarEqual(0, 'mode_running')

    # --- dale mini wizard qualification ---

    def test_dog_dale_stopped_progresses_dale_mini_wizard_accrual(self):
        """Completing Dog Dale Afternoon contributes to dale_mini_wizard accrual."""
        self.start_game_with_balls()
        self.advance_time_and_run(1)
        self.mock_event('dale_mini_wizard_qualified')

        # Dog Dale stops (the accrual needs both dog_dale AND gladstone stopped)
        self.post_event('mode_dog_dale_afternoon_stopped')
        self.advance_time_and_run(0.1)

        # Not qualified yet — Gladstone still needed
        self.assertEventNotCalled('dale_mini_wizard_qualified')

        self.post_event('mode_gladstone_stopped')
        self.advance_time_and_run(0.1)

        self.assertEventCalled('dale_mini_wizard_qualified')

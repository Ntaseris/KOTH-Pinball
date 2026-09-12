"""Tests for Alamo Frenzy qualification, scoring, and mode interaction."""

from tests.koth_test_case import KothTestCase


class TestAlamoFrenzy(KothTestCase):
    """Verify the timed frenzy and its shared premium-shot feedback path."""

    def _start_alamo_frenzy(self):
        self.start_game_with_balls()
        self.post_event_with_params('player_alamo_target_hits', value=12)
        self.advance_time_and_run(0.2)
        self.assertTrue(self.machine.modes['alamo_frenzy'].active)

    def test_all_three_beer_targets_qualify_frenzy_at_twelve_hits(self):
        """The two scoop standups and right-ramp standup share qualification."""
        self.start_game_with_balls()
        beer_targets = ('s_scoop_standup_left', 's_scoop_standup_right',
                        's_right_ramp_standup')

        for hit in range(11):
            self.hit_and_release_switch(beer_targets[hit % 3])
            self.advance_time_and_run(0.6)

        self.assertPlayerVarEqual(11, 'alamo_target_hits')
        self.assertFalse(self.machine.modes['alamo_frenzy'].active)

        self.hit_and_release_switch('s_right_ramp_standup')
        self.advance_time_and_run(0.2)

        self.assertPlayerVarEqual(12, 'alamo_target_hits')
        self.assertTrue(self.machine.modes['alamo_frenzy'].active)

    def test_premium_shot_updates_frenzy_total(self):
        """A premium shot scores its frenzy value and updates the displayed total."""
        self._start_alamo_frenzy()

        self.hit_and_release_switch('s_p_target')
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(1, 'alamo_frenzy_hits')
        self.assertPlayerVarEqual(250000, 'alamo_frenzy_total')

    def test_every_fifth_hit_completes_six_pack_counter(self):
        """Five premium hits trigger the larger six-pack celebration event."""
        self._start_alamo_frenzy()
        self.mock_event('logicblock_alamo_frenzy_hit_counter_complete')

        for switch in ('s_p_target', 's_r_target', 's_o_target',
                       's_p2_target', 's_a_target'):
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(0.1)

        self.assertEventCalled('logicblock_alamo_frenzy_hit_counter_complete')
        self.assertPlayerVarEqual(5, 'alamo_frenzy_hits')

    def test_multiball_stops_frenzy(self):
        """A multiball start clears Alamo Frenzy presentation and scoring."""
        self._start_alamo_frenzy()

        self.post_event('multiball_grill_mb_started')
        self.advance_time_and_run(0.2)

        self.assertFalse(self.machine.modes['alamo_frenzy'].active)

    def test_frenzy_cannot_start_during_multiball(self):
        """Alamo Frenzy cannot begin while a multiball is active."""
        self.start_game_with_balls()
        self.post_event('multiball_grill_mb_started')
        self.post_event_with_params('player_alamo_target_hits', value=12)
        self.advance_time_and_run(0.2)

        self.assertFalse(self.machine.modes['alamo_frenzy'].active)

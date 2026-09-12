"""Tests for the Beer Can Named Desire character wager."""

from tests.koth_test_case import KothTestCase


class TestBeerCanNamedDesire(KothTestCase):

    def _start_character_choice(self):
        self.start_game_with_balls()
        self.post_event("slide_beer_can_named_desire_rules_removed")
        self.advance_time_and_run(0.1)
        self.assertTrue(self.machine.modes["beercan_carousel"].active)

    def _choose_hank(self):
        self._start_character_choice()
        self.post_event("beercan_carousel_hank_hill_selected")
        self.advance_time_and_run(0.1)
        self.assertTrue(self.machine.modes["beer_can_named_desire"].active)

    def test_dandy_don_awards_safe_bet_with_multiplier(self):
        """Dandy Don immediately awards the advertised multiplied safe bet."""
        self._start_character_choice()
        self.machine.game.player.pf_multiplier = 2
        score_before = self.machine.game.player.score

        self.post_event("beercan_carousel_dandy_don_selected")
        self.advance_time_and_run(0.1)

        self.assertEqual(score_before + 6000000, self.machine.game.player.score)
        self.assertFalse(self.machine.modes["beercan_carousel"].active)
        self.assertFalse(self.machine.modes["beer_can_named_desire"].active)

    def test_hank_ramp_is_disabled_during_ready_card(self):
        """The player cannot collect Hank's award before the countdown begins."""
        self._choose_hank()
        self.mock_event("shot_beercan_right_ramp_hit")

        self.hit_and_release_switch("s_right_ramp_exit")
        self.advance_time_and_run(0.1)

        self.assertEventNotCalled("shot_beercan_right_ramp_hit")
        self.assertTrue(self.machine.modes["beer_can_named_desire"].active)

    def test_hank_timer_waits_for_ready_card(self):
        """The ten-second timer does not run behind Hank's instructions."""
        self._choose_hank()
        self.mock_event("timer_beer_can_named_desire_mode_countdown_tick")

        self.advance_time_and_run(1.1)
        self.assertEventNotCalled("timer_beer_can_named_desire_mode_countdown_tick")

        self.post_event("slide_beer_can_hank_ready_inactive")
        self.advance_time_and_run(1.1)
        self.assertEventCalled("timer_beer_can_named_desire_mode_countdown_tick")

    def test_hank_right_ramp_awards_risk_value(self):
        """Once the wager starts, the right ramp awards ten million multiplied."""
        self._choose_hank()
        self.machine.game.player.pf_multiplier = 2
        self.post_event("slide_beer_can_hank_ready_inactive")
        self.advance_time_and_run(0.1)
        score_before = self.machine.game.player.score

        self.hit_and_release_switch("s_right_ramp_exit")
        self.advance_time_and_run(0.1)

        # 20M award plus the right ramp's 25K base value at 2X.
        self.assertEqual(score_before + 20050000, self.machine.game.player.score)
        self.assertFalse(self.machine.modes["beer_can_named_desire"].active)

    def test_hank_throw_value_declines_each_second(self):
        """Waiting makes Hank's riskier choice progressively less valuable."""
        self._choose_hank()
        self.post_event("slide_beer_can_hank_ready_inactive")
        self.advance_time_and_run(2.1)

        self.assertPlayerVarEqual(9000000, "beer_can_hank_value")
        score_before = self.machine.game.player.score
        self.hit_and_release_switch("s_right_ramp_exit")
        self.advance_time_and_run(0.1)

        self.assertEqual(score_before + 9025000, self.machine.game.player.score)

"""Tests for the branded attract carousel and its controls."""

from tests.koth_test_case import KothTestCase


class TestAttract(KothTestCase):

    def test_carousel_leads_with_company_credits(self):
        self.assertTrue(self.machine.modes["attract"].active)
        self.assertEqual(
            "companies",
            self.machine.modes["attract"]._get_highlighted_item(),
        )

    def test_timer_and_flippers_navigate_attract_cards(self):
        self.advance_time_and_run(5.1)
        self.assertEqual(
            "jupiter_seattle",
            self.machine.modes["attract"]._get_highlighted_item(),
        )

        self.hit_and_release_switch("s_right_flipper")
        self.advance_time_and_run(0.1)
        self.assertEqual(
            "lents_pinball",
            self.machine.modes["attract"]._get_highlighted_item(),
        )

        self.hit_and_release_switch("s_left_flipper")
        self.advance_time_and_run(0.1)
        self.assertEqual(
            "jupiter_seattle",
            self.machine.modes["attract"]._get_highlighted_item(),
        )

    def test_theme_starts_when_carousel_reaches_intro(self):
        self.mock_event("play_attract_theme")

        for _ in range(2):
            self.advance_time_and_run(5.1)
            self.assertEventNotCalled("play_attract_theme")

        self.advance_time_and_run(5.1)
        self.assertEqual(
            "koth_intro",
            self.machine.modes["attract"]._get_highlighted_item(),
        )
        self.assertEventCalled("play_attract_theme")

        self.advance_time_and_run(40)
        self.assertEventCalled("play_attract_theme", times=1)

    def test_theme_can_play_once_again_after_attract_restarts(self):
        self.mock_event("play_attract_theme")

        self.advance_time_and_run(15.1)
        self.assertEventCalled("play_attract_theme", times=1)

        self.machine.modes["attract"].stop()
        self.advance_time_and_run(0.1)
        self.machine.modes["attract"].start()
        self.advance_time_and_run(15.1)

        self.assertEventCalled("play_attract_theme", times=2)

    def test_flipper_cradle_pauses_auto_advance(self):
        self.post_event("flipper_cradle")
        self.advance_time_and_run(6)
        self.assertEqual(
            "companies",
            self.machine.modes["attract"]._get_highlighted_item(),
        )

        self.post_event("flipper_cradle_release")
        self.advance_time_and_run(5.1)
        self.assertEqual(
            "jupiter_seattle",
            self.machine.modes["attract"]._get_highlighted_item(),
        )

    def test_start_button_exits_attract_and_starts_game(self):
        self.start_game_with_balls()

        self.assertFalse(self.machine.modes["attract"].active)
        self.assertGameIsRunning()

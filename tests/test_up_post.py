"""Tests for the directional left-orbit up-post trigger."""

from tests.koth_test_case import KothTestCase


class TestUpPost(KothTestCase):
    """Verify only the spinner-to-orbit direction releases the up-post."""

    def test_base_play_left_orbit_does_not_release_post(self):
        """Base play leaves the post down so the orbit can complete."""
        self.start_game_with_balls()
        self.mock_event('left_orbit_post_release')

        self.hit_and_release_switch('s_left_spinner')
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch('s_left_orbit_enter')

        self.assertEventNotCalled('left_orbit_post_release')

    def test_orbit_then_left_spinner_does_not_release_post(self):
        """Travel through the switches in the reverse direction does not qualify."""
        self.start_game_with_balls()
        self.mock_event('left_orbit_post_release')

        self.hit_and_release_switch('s_left_orbit_enter')
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch('s_left_spinner')

        self.assertEventNotCalled('left_orbit_post_release')

    def test_released_post_returns_down_after_two_seconds(self):
        """The post raise timer completes two seconds after a qualified shot."""
        self.start_game_with_balls()
        self.mock_event('timer_up_post_raise_duration_complete')

        self.post_event('left_orbit_post_release')
        self.advance_time_and_run(1.9)
        self.assertEventNotCalled('timer_up_post_raise_duration_complete')

        self.advance_time_and_run(0.2)
        self.assertEventCalled('timer_up_post_raise_duration_complete')

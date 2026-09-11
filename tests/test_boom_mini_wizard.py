# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""Tests for the Dang Ol' Love Boomhauer mini-wizard mode."""

from pathlib import Path

from tests.koth_test_case import KothTestCase


class TestBoomMiniWizard(KothTestCase):
    """Verify every story phase, payout, and packaged presentation asset."""

    pursuit_switches = (
        "s_left_orbit_enter",
        "s_left_ramp_exit",
        "s_center_spinner",
        "s_right_ramp_exit",
        "s_right_orbit_exit",
    )

    def _start_mode(self):
        self.start_game_with_balls()
        self.post_event("mission_select_boom_mini_wizard_selected")
        self.advance_time_and_run(0.1)
        self.post_event("slide_boom_mini_wizard_inactive")
        self.advance_time_and_run(0.1)

    def _complete_pursuit(self):
        for switch in self.pursuit_switches:
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(0.1)

    def _reach_heartbreak(self):
        self._complete_pursuit()
        self.post_event("boom_mw_story_scoop_hit")
        self.advance_time_and_run(0.1)
        self.post_event("slide_boom_mw_proposal_inactive")
        self.advance_time_and_run(0.1)

    def _reach_rebound(self):
        self._reach_heartbreak()
        for _ in range(12):
            self.hit_and_release_switch("s_left_pop_bumper")
            self.advance_time_and_run(0.05)
        self.post_event("boom_mw_story_scoop_hit")
        self.advance_time_and_run(0.1)
        self.post_event("slide_boom_mw_pep_talk_inactive")
        self.advance_time_and_run(0.1)

    def test_starts_with_five_pink_pursuit_shots(self):
        self._start_mode()

        self.assertModeRunning("boom_mini_wizard")
        self.assertPlayerVarEqual(1, "boom_mw_phase")
        self.assertEqual(100, self.machine.timers["boom_mini_wizard_mode_countdown"].ticks_remaining)
        self.assertTrue(all(
            self.machine.shots[name].enabled
            for name in (
                "boom_mw_pursuit_left_orbit",
                "boom_mw_pursuit_left_ramp",
                "boom_mw_pursuit_center_spinner",
                "boom_mw_pursuit_right_ramp",
                "boom_mw_pursuit_right_orbit",
            )
        ))

    def test_two_boomhauer_modes_add_mini_wizard_to_mission_select(self):
        self.start_game_with_balls()
        self.advance_time_and_run(0.1)

        mission_select = self.machine.modes["mission_select"]
        mission_select.start()
        self.advance_time_and_run(0.1)
        self.assertNotIn("boom_mini_wizard", mission_select._items)
        mission_select.stop()
        self.advance_time_and_run(0.1)

        self.post_event("mode_patch_boomhauer_stopped")
        self.post_event("mode_beat_the_surfer_stopped")
        self.advance_time_and_run(0.1)

        self.assertTrue(self.machine.accruals["boom_mini_wizard"].completed)
        mission_select.start()
        self.advance_time_and_run(0.1)
        self.assertIn("boom_mini_wizard", mission_select._items)

    def test_pursuit_lights_proposal_scoop(self):
        self._start_mode()
        self._complete_pursuit()

        self.assertPlayerVarEqual(5, "boom_mw_pursuit_hits")
        self.assertPlayerVarEqual(2, "boom_mw_phase")
        self.assertTrue(self.machine.shots["boom_mw_story_scoop"].enabled)

    def test_proposal_advances_to_heartbreak(self):
        self._start_mode()
        self._reach_heartbreak()

        self.assertPlayerVarEqual(3, "boom_mw_phase")
        self.assertTrue(self.machine.shots["boom_mw_confidence_left_pop"].enabled)
        self.assertFalse(self.machine.shots["boom_mw_story_scoop"].enabled)

    def test_twelve_pop_or_spinner_hits_light_bill_pep_talk(self):
        self._start_mode()
        self._reach_heartbreak()

        for _ in range(12):
            self.hit_and_release_switch("s_center_spinner")
            self.advance_time_and_run(0.05)

        self.assertPlayerVarEqual(12, "boom_mw_confidence")
        self.assertPlayerVarEqual(4, "boom_mw_phase")
        self.assertTrue(self.machine.shots["boom_mw_story_scoop"].enabled)

    def test_bill_pep_talk_starts_five_blue_rebound_shots(self):
        self._start_mode()
        self._reach_rebound()

        self.assertPlayerVarEqual(5, "boom_mw_phase")
        self.assertTrue(all(
            self.machine.shots[name].enabled
            for name in (
                "boom_mw_rebound_left_orbit",
                "boom_mw_rebound_left_ramp",
                "boom_mw_rebound_center_spinner",
                "boom_mw_rebound_right_ramp",
                "boom_mw_rebound_right_orbit",
            )
        ))

    def test_complete_story_scores_thirty_eight_million(self):
        self._start_mode()
        self._reach_rebound()

        for switch in self.pursuit_switches:
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(6, "boom_mw_phase")
        self.post_event("boom_mw_story_scoop_hit")
        self.advance_time_and_run(0.1)
        self.post_event("slide_boom_mw_apology_inactive")
        self.post_event("slide_boom_mw_finale_tag_inactive")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(1, "boom_mini_wizard_completed")
        self.assertPlayerVarEqual(38_000_000, "boom_mini_wizard_total")
        self.assertModeNotRunning("boom_mini_wizard")

    def test_signature_shows_and_episode_media_are_packaged(self):
        project_root = Path(__file__).resolve().parents[1]
        for show in (
            "boom_mw_romance",
            "boom_mw_heartbreak",
            "boom_mw_rebound",
            "boom_mw_jackpot",
            "boom_mw_ring_ready",
            "boom_mw_pep_ready",
            "boom_mw_apology_ready",
        ):
            self.assertIn(show, self.machine.shows)

        for clip in (
            "intro.ogv",
            "proposal.ogv",
            "bill_pep_talk.ogv",
            "apology.ogv",
            "finale_tag.ogv",
        ):
            self.assertTrue(
                (project_root / "images" / "dang_ol_love_clips" / clip).is_file()
            )

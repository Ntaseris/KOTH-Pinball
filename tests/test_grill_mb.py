# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""Tests for Grill Multiball order, heat, and jackpot cycles."""

from tests.koth_test_case import KothTestCase


class TestGrillMultiball(KothTestCase):
    def _start_grill_multiball(self):
        self.start_game_with_balls()
        self.post_event("multiball_grill_mb_started")
        self.advance_time_and_run(0.1)

    def _qualify_grill_lock(self):
        self.start_game_with_balls()
        self.post_event("logicblock_grill_mb_counter_complete")
        self.advance_time_and_run(0.1)

    def _lock_ball(self):
        self.hit_and_release_switch("s_right_ramp_exit")
        self.advance_time_and_run(5)

    def _launch_replacement(self):
        self.release_switch_and_run("s_plunger", 0.1)
        self.hit_and_release_switch("s_plunger_lane_exit")
        self.advance_time_and_run(2)

    def test_grill_uses_native_lock_without_replacement_multiball(self):
        """The grill uses MPF's lock replacement flow, not a fake multiball."""
        self.assertNotIn("grill_replacement", self.machine.multiballs)
        grill_lock = self.machine.multiball_locks["grill_lock"]
        self.assertEqual(3, grill_lock.config["balls_to_lock"])
        self.assertEqual(2, grill_lock.config["balls_to_replace"])

    def test_right_ramp_is_lock_entrance_and_grill_optos_are_ignored(self):
        """Broken Grill optos cannot add locks; a qualified ramp shot can."""
        self._qualify_grill_lock()
        self.mock_event("grill_lock_confirmed")

        for switch in ("s_grill1", "s_grill2", "s_grill3"):
            self.hit_and_release_switch(switch)
        self.advance_time_and_run(1)
        self.assertEventNotCalled("grill_lock_confirmed")

        self._lock_ball()
        self.assertEventCalled("grill_lock_confirmed")
        self.assertEqual(1, self.machine.ball_devices["bd_grill_lock"].balls)

    def test_first_lock_is_held_and_replaced_from_trough(self):
        """One physical lock requests its replacement into the plunger lane."""
        self._qualify_grill_lock()
        self.mock_event("balldevice_bd_trough_ball_eject_attempt")
        self._lock_ball()

        self.assertEqual(1, self.machine.multiball_locks["grill_lock"].locked_balls)
        self.assertEqual(1, self.machine.ball_devices["bd_grill_lock"].balls)
        self.assertGreaterEqual(
            self._events["balldevice_bd_trough_ball_eject_attempt"], 1
        )
        self.assertEqual(1, self.machine.game.balls_in_play)
        self.assertPlayerVarEqual(1, "grill_balls_locked")

    def test_second_lock_is_held_and_replaced_from_trough(self):
        """Two physical locks still leave exactly one replacement ball live."""
        self._qualify_grill_lock()
        self.mock_event("balldevice_bd_trough_ball_eject_attempt")
        self._lock_ball()
        self._launch_replacement()
        self._lock_ball()

        self.assertEqual(2, self.machine.multiball_locks["grill_lock"].locked_balls)
        self.assertEqual(2, self.machine.ball_devices["bd_grill_lock"].balls)
        self.assertGreaterEqual(
            self._events["balldevice_bd_trough_ball_eject_attempt"], 2
        )
        self.assertEqual(1, self.machine.game.balls_in_play)
        self.assertPlayerVarEqual(2, "grill_balls_locked")

    def test_order_requires_three_distinct_shots(self):
        """Repeating a collected order shot cannot advance the grill twice."""
        self._start_grill_multiball()

        self.hit_and_release_switch("s_left_orbit_enter")
        self.hit_and_release_switch("s_left_orbit_enter")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(1, "grill_order_progress")

        self.hit_and_release_switch("s_left_ramp_exit")
        self.hit_and_release_switch("s_right_orbit_exit")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(3, "grill_order_progress")

    def test_each_order_turns_on_another_grill_section(self):
        """The grill rings remain a visible three-step order progress meter."""
        self._start_grill_multiball()

        self.hit_and_release_switch("s_left_orbit_enter")
        self.advance_time_and_run(0.05)
        self.assertNotLightColor("l_grill1", "black")
        self.assertLightColor("l_grill9", "black")
        self.assertLightColor("l_grill17", "black")

        self.hit_and_release_switch("s_left_ramp_exit")
        self.advance_time_and_run(0.05)
        self.assertNotLightColor("l_grill9", "black")
        self.assertLightColor("l_grill17", "black")

        self.hit_and_release_switch("s_right_orbit_exit")
        self.advance_time_and_run(0.05)
        self.assertNotLightColor("l_grill17", "black")

    def test_lock_progress_lights_first_two_sections_and_relights_ramp(self):
        """Each replacement lock adds a grill section and relights entry."""
        self.start_game_with_balls()
        self.post_event("logicblock_grill_mb_counter_complete")
        self.advance_time_and_run(0.1)

        self.post_event(
            "multiball_lock_grill_lock_locked_ball", total_balls_locked=1
        )
        self.advance_time_and_run(0.1)
        self.assertLightColor("l_grill1", "black")
        self.assertLightColor("l_grill9", "black")
        self.assertNotLightColor("l_grill17", "black")

        self.post_event("grill_replacement_ball_launched")
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(1, "grill_lock_ready")
        self.assertNotLightColor("l_right_ramp", "black")

        self.post_event(
            "multiball_lock_grill_lock_locked_ball", total_balls_locked=2
        )
        self.advance_time_and_run(0.1)
        self.assertLightColor("l_grill1", "black")
        self.assertNotLightColor("l_grill9", "black")
        self.assertNotLightColor("l_grill17", "black")

        self.post_event("grill_replacement_ball_launched")
        self.advance_time_and_run(0.1)
        self.assertPlayerVarEqual(1, "grill_lock_ready")

    def test_spinner_builds_heat_and_jackpot_value(self):
        """Each qualified spinner pulse increases heat and cashout value."""
        self._start_grill_multiball()

        for _ in range(5):
            self.hit_and_release_switch("s_left_spinner")
            self.hit_and_release_switch("s_center_spinner")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(10, "grill_heat")
        self.assertPlayerVarEqual(1250000, "grill_jackpot_value")

    def test_shoot_again_fires_playfield_rebound(self):
        """A saved multiball drain flashes the ball-save and surrounding GI."""
        self._start_grill_multiball()

        self.post_event("multiball_grill_mb_shoot_again", balls=1)
        self.advance_time_and_run(0.02)

        self.assertLightColor("l_ball_save", "white")
        self.assertLightColor("l_gi1", "white")

    def test_shoot_again_window_flashes_cyan(self):
        """Grill Multiball protection uses the common cyan treatment."""
        self._start_grill_multiball()
        self.post_event("ball_save_grill_mb_timer_start")
        self.advance_time_and_run(0.02)

        self.assertLightColor("l_ball_save", "cyan")

    def test_right_ramp_cashout_resets_and_escalates_cycle(self):
        """Cashout clears heat/orders and raises the next jackpot base."""
        self._start_grill_multiball()

        self.hit_and_release_switch("s_left_orbit_enter")
        self.hit_and_release_switch("s_left_ramp_exit")
        self.hit_and_release_switch("s_right_orbit_exit")
        for _ in range(4):
            self.hit_and_release_switch("s_left_spinner")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(1100000, "grill_jackpot_value")
        score_before = self.machine.game.player.score
        self.hit_and_release_switch("s_right_ramp_exit")
        self.advance_time_and_run(0.1)

        # 1.1M jackpot plus the right ramp's 25K base and 25K MB floor.
        self.assertEqual(score_before + 1150000, self.machine.game.player.score)
        self.assertPlayerVarEqual(1100000, "grill_last_jackpot_award")
        self.assertPlayerVarEqual(0, "grill_order_progress")
        self.assertPlayerVarEqual(0, "grill_heat")
        self.assertPlayerVarEqual(2, "grill_jackpot_cycle")
        self.assertPlayerVarEqual(1500000, "grill_jackpot_base")
        self.assertPlayerVarEqual(1500000, "grill_jackpot_value")

    def test_right_ramp_does_not_cash_out_before_order_complete(self):
        """The right ramp is ordinary switch scoring until all orders are made."""
        self._start_grill_multiball()
        self.mock_event("grill_jackpot_collected")

        self.hit_and_release_switch("s_left_orbit_enter")
        self.hit_and_release_switch("s_right_ramp_exit")
        self.advance_time_and_run(0.1)

        self.assertEventNotCalled("grill_jackpot_collected")
        self.assertPlayerVarEqual(1, "grill_order_progress")

    def test_grill_multiball_stops_manger_babies_overlap(self):
        """Background Manger Babies scoring cannot leak into Grill Multiball."""
        self.start_game_with_balls()
        self.assertTrue(self.machine.modes["manger_babies"].active)

        self.post_event("multiball_grill_mb_started")
        self.advance_time_and_run(0.1)

        self.assertFalse(self.machine.modes["manger_babies"].active)

    def test_third_lock_releases_grill_and_starts_three_ball_multiball(self):
        """The full physical lock starts Grill MB with exactly three live balls."""
        self._qualify_grill_lock()
        self.mock_event("multiball_grill_mb_started")
        self.mock_event("servo_grill_shelf_down")
        self.mock_event("balldevice_bd_trough_ball_eject_attempt")
        self._lock_ball()
        self._launch_replacement()
        self._lock_ball()
        self._launch_replacement()
        replacement_ejects = self._events[
            "balldevice_bd_trough_ball_eject_attempt"
        ]
        self._lock_ball()

        self.assertEventCalled("multiball_grill_mb_started")
        self.assertEqual(3, self.machine.game.balls_in_play)
        self.assertEventCalled("servo_grill_shelf_down")
        self.assertEqual(
            replacement_ejects,
            self._events["balldevice_bd_trough_ball_eject_attempt"],
        )

    def test_unrelated_multiball_end_does_not_disable_flippers(self):
        """Ending an unrelated multiball cannot kill resumed single-ball play."""
        self.start_game_with_balls()
        self.mock_event("cmd_flippers_disable")

        self.post_event("multiball_strickland_multiball_started")
        self.post_event("multiball_strickland_multiball_ended")
        self.advance_time_and_run(0.1)

        self.assertEventNotCalled("cmd_flippers_disable")

    def test_unrelated_multiball_keeps_grill_balls_locked(self):
        """Another multiball uses the trough and does not dump the grill lock."""
        self._qualify_grill_lock()
        self._lock_ball()
        self.machine.game.player.any_mb_active = 1

        self.post_event("multiball_rainey_multiball_started")
        self.advance_time_and_run(0.1)

        self.assertEqual(1, self.machine.ball_devices["bd_grill_lock"].available_balls)

    def test_partial_lock_drain_does_not_force_flippers_or_end_ball(self):
        """A replacement drain is handled only by MPF's normal ball lifecycle."""
        self._qualify_grill_lock()
        self._lock_ball()
        self.mock_event("cmd_flippers_disable")
        self.mock_event("end_ball")

        self.post_event("ball_drain", balls=1)
        self.advance_time_and_run(0.1)

        self.assertEventNotCalled("cmd_flippers_disable")
        self.assertEventNotCalled("end_ball")

    def test_ball_ending_waits_for_grill_balls_to_reach_trough(self):
        """The next ball is blocked until the released physical locks drain."""
        self._qualify_grill_lock()
        self._lock_ball()
        self.assertEqual(1, self.machine.ball_devices["bd_grill_lock"].available_balls)
        self.mock_event("servo_grill_shelf_down")
        self.mock_event("ball_ended")

        self.machine.ball_saves["default"].disable()
        self.post_relay_event_with_params("ball_drain", balls=1)
        self.advance_time_and_run(1)

        self.assertEventCalled("servo_grill_shelf_down")
        self.assertEventNotCalled("ball_ended")
        self.assertBallNumber(1)
        cleanup = next(
            item
            for item in self.machine.custom_code
            if item.__class__.__name__ == "GrillLockCleanup"
        )
        self.assertEqual(1, cleanup._balls_waiting_to_drain)

        self.machine.default_platform.add_ball_to_device(
            self.machine.ball_devices["bd_trough"]
        )
        self.advance_time_and_run(10)

        self.assertEqual(0, cleanup._balls_waiting_to_drain)
        self.assertEventCalled("ball_ended")
        self.assertBallNumber(2)

    def test_ball_ending_waits_for_both_grill_balls(self):
        """Two partial locks must both return before the next ball starts."""
        self._qualify_grill_lock()
        self._lock_ball()
        self._launch_replacement()
        self._lock_ball()
        self.assertEqual(2, self.machine.ball_devices["bd_grill_lock"].available_balls)
        self.mock_event("ball_ended")

        self.machine.ball_saves["default"].disable()
        self.post_relay_event_with_params("ball_drain", balls=1)
        self.advance_time_and_run(1)

        cleanup = next(
            item
            for item in self.machine.custom_code
            if item.__class__.__name__ == "GrillLockCleanup"
        )
        self.assertEqual(2, cleanup._balls_waiting_to_drain)
        self.machine.default_platform.add_ball_to_device(
            self.machine.ball_devices["bd_trough"]
        )
        self.advance_time_and_run(1)
        self.assertEqual(1, cleanup._balls_waiting_to_drain)
        self.assertEventNotCalled("ball_ended")

        self.machine.default_platform.add_ball_to_device(
            self.machine.ball_devices["bd_trough"]
        )
        self.advance_time_and_run(10)
        self.assertEqual(0, cleanup._balls_waiting_to_drain)
        self.assertEventCalled("ball_ended")
        self.assertBallNumber(2)

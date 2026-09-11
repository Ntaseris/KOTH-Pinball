"""Base test case for all KOTH tests.

Uses MpfTestCase with smart_virtual platform. smart_virtual simulates ball
routing through ball devices. simulate_manual_plunger is enabled so the
plunger (mechanical_eject=true) auto-launches after a short delay.
"""
import os
from mpf.tests.MpfTestCase import MpfTestCase


class KothTestCase(MpfTestCase):
    """Shared base for KOTH tests."""

    def __init__(self, methodName):
        super().__init__(methodName)
        # Enable auto-simulation of the mechanical plunger launch in tests.
        self.machine_config_patches['smart_virtual'] = {
            'simulate_manual_plunger': True,
            'simulate_manual_plunger_timeout': 1000,  # 1s in ms
        }

    def get_config_file(self):
        return 'Config.yaml'

    def get_absolute_machine_path(self):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    def get_platform(self):
        return 'smart_virtual'

    # --- game lifecycle helpers ---

    def start_game_with_balls(self):
        """Fill trough and start a game.

        Advances enough time for:
        - trough → plunger eject (smart_virtual auto-routes)
        - plunger → playfield launch (simulate_manual_plunger, 1s delay)
        - s_plunger_lane_exit confirm and ball save timer to start
        """
        for switch in ['s_trough1', 's_trough2', 's_trough3',
                       's_trough4', 's_trough5', 's_trough6']:
            self.hit_switch_and_run(switch, 0)
        self.advance_time_and_run(2)

        self.assertFalse(self.machine.game)
        self.hit_and_release_switch('s_start')
        # Let ball route: trough eject + plunger launch + confirm
        self.advance_time_and_run(5)

        self.assertIsNotNone(self.machine.game, "Game did not start")

    def drain_ball(self):
        """Drain the current ball past the ball save window.

        Sets balls_in_play=1 so the game tracks the ball, starts the ball save
        timer via s_plunger_lane_exit, waits for the save window to expire,
        then posts ball_drain.
        """
        # Ensure the game tracks a ball so drain processing runs
        self.machine.game.balls_in_play = 1
        self.machine.playfield.balls = 1
        # Start the ball save timer then exhaust the window
        self.hit_and_release_switch('s_plunger_lane_exit')
        self.advance_time_and_run(7)   # 2s active + 2s hurry_up + 2s grace + 1s buffer
        self.post_relay_event_with_params('ball_drain', balls=1)
        self.advance_time_and_run(5)

    def assertGameIsRunning(self):
        self.assertIsNotNone(self.machine.game, "Expected a game to be running")

    def assertGameIsNotRunning(self):
        self.assertIsNone(self.machine.game, "Expected no game to be running")

    def assertPlayerNumber(self, number):
        self.assertGameIsRunning()
        self.assertEqual(number, self.machine.game.player.number)

    def assertBallNumber(self, number):
        self.assertGameIsRunning()
        self.assertEqual(number, self.machine.game.player.ball)

    def qualify_mission(self):
        """Hit P-R-O targets to qualify the mission scoop."""
        self.hit_and_release_switch('s_p_target')
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch('s_r_target')
        self.advance_time_and_run(0.1)
        self.hit_and_release_switch('s_o_target')
        self.advance_time_and_run(0.5)

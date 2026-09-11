"""Smoke tests — machine loads, game starts, basic lifecycle works."""
from tests.koth_test_case import KothTestCase


class TestStartup(KothTestCase):

    def test_machine_loads(self):
        """Config loads without errors and core modes are present."""
        self.assertModeRunning('attract')
        self.assertIn('base', self.machine.modes)
        self.assertIn('dog_dale_afternoon', self.machine.modes)
        self.assertIn('beat_the_surfer', self.machine.modes)
        self.assertIn('mission_select', self.machine.modes)

    def test_game_starts(self):
        """Starting a game activates base mode and sets initial player vars."""
        self.start_game_with_balls()
        self.assertGameIsRunning()
        self.assertModeRunning('base')
        self.assertPlayerNumber(1)
        self.assertBallNumber(1)

    def test_right_flipper_is_not_a_plunger_eject_control(self):
        """Shooter-lane balls require the physical plunger."""
        plunger = self.machine.ball_devices['bd_plunger']

        self.assertIsNone(plunger.config['player_controlled_eject_event'])

    def test_pf_multiplier_initialises_to_one(self):
        """pf_multiplier is 1 at game start."""
        self.start_game_with_balls()
        self.advance_time_and_run(1)
        self.assertPlayerVarEqual(1, 'pf_multiplier')

    def test_base_mode_stops_on_ball_will_end(self):
        """base mode stops when ball_will_end fires."""
        self.start_game_with_balls()
        self.assertModeRunning('base')
        self.post_event('ball_will_end')
        self.advance_time_and_run(1)
        self.assertModeNotRunning('base')

    def test_ball_one_extra_ball_does_not_replay_show_intro(self):
        """An extra ball numbered Ball 1 skips the one-time show intro."""
        self.start_game_with_balls()
        self.machine.modes['intro'].stop()
        self.advance_time_and_run(0.1)

        self.post_event(
            'ball_will_start',
            ball=1,
            player=1,
            is_extra_ball=True,
        )
        self.advance_time_and_run(0.1)

        self.assertModeNotRunning('intro')

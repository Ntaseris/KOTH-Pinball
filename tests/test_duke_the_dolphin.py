"""Tests for Duke the Dolphin's random moving-shot progression."""

from tests.koth_test_case import KothTestCase


class TestDukeTheDolphin(KothTestCase):

    SHOT_SWITCHES = {
        "shot_1_duke": "s_left_orbit_enter",
        "shot_2_duke": "s_left_ramp_exit",
        "shot_3_duke": "s_center_spinner",
        "shot_4_duke": "s_right_ramp_exit",
        "shot_5_duke": "s_right_orbit_exit",
    }

    def _start_mode(self):
        self.start_game_with_balls()
        self.post_event("mission_select_duke_the_dolphin_selected")
        self.advance_time_and_run(0.1)
        self.assertTrue(self.machine.modes["duke_the_dolphin"].active)

    def _start_play(self):
        self._start_mode()
        self.post_event("slide_duke_the_dolphin_rules_removed")
        self.advance_time_and_run(0.1)

    def _enabled_shot(self):
        enabled = [name for name in self.SHOT_SWITCHES
                   if self.machine.shots[name].enabled]
        self.assertEqual(1, len(enabled))
        return enabled[0]

    def _hit_enabled_shot(self):
        shot = self._enabled_shot()
        self.hit_and_release_switch(self.SHOT_SWITCHES[shot])
        self.advance_time_and_run(0.1)
        return shot

    def test_full_timer_and_first_shot_start_after_rules(self):
        """The player receives a blue objective and full clock after the rules."""
        self._start_mode()
        timer = self.machine.timers["duke_the_dolphin_mode_countdown"]
        self.assertFalse(timer.running)

        self.post_event("slide_duke_the_dolphin_rules_removed")
        self.advance_time_and_run(0.1)

        self.assertTrue(timer.running)
        self._enabled_shot()

    def test_random_movement_never_repeats_current_shot(self):
        """A timed random move cannot choose the same location twice in a row."""
        self._start_play()

        previous = self._enabled_shot()
        for _ in range(12):
            self.post_event("duke_choose_next_shot")
            self.advance_time_and_run(0.05)
            current = self._enabled_shot()
            self.assertNotEqual(previous, current)
            previous = current

    def test_correct_hit_scores_once_and_immediately_moves(self):
        """A rescue scores its escalating value and moves Duke immediately."""
        self._start_play()
        first = self._enabled_shot()
        score_before = self.machine.game.player.score

        self._hit_enabled_shot()

        self.assertGreaterEqual(self.machine.game.player.score - score_before, 1000000)
        self.assertPlayerVarEqual(1000000, "duke_the_dolphin_total")
        self.assertPlayerVarEqual(1, "duke_rescues")
        self.assertNotEqual(first, self._enabled_shot())

    def test_three_rescues_start_faster_magenta_chase_phase(self):
        """The second cycle changes pace, color state, and scoring tier."""
        self._start_play()

        for _ in range(3):
            self._hit_enabled_shot()

        self.assertPlayerVarEqual(2, "duke_phase")
        self.assertFalse(self.machine.timers["random_event_timer"].running)
        self.assertTrue(self.machine.timers["duke_chase_timer"].running)
        total_before = self.machine.game.player.duke_the_dolphin_total
        self._hit_enabled_shot()
        self.assertPlayerVarEqual(total_before + 2000000,
                                  "duke_the_dolphin_total")

    def test_active_spinner_rip_only_counts_once(self):
        """Moving Duke after the first spin prevents a spinner rip from farming."""
        self._start_play()

        for _ in range(10):
            if self._enabled_shot() == "shot_3_duke":
                break
            self.post_event("duke_choose_next_shot")
            self.advance_time_and_run(0.05)
        self.assertEqual("shot_3_duke", self._enabled_shot())

        for _ in range(8):
            self.hit_and_release_switch("s_center_spinner")
        self.advance_time_and_run(0.2)

        self.assertPlayerVarEqual(1, "duke_rescues")

    def test_six_rescues_light_final_scoop_then_finish(self):
        """Six moving rescues lead to a deliberate final scoop rescue."""
        self._start_play()
        self.mock_event("logicblock_duke_counter_complete")

        for _ in range(6):
            self._hit_enabled_shot()

        self.assertPlayerVarEqual(6, "duke_rescues")
        self.assertTrue(self.machine.shots["shot_duke_final_rescue"].enabled)
        self.assertTrue(self.machine.ball_holds["duke_finish"].enabled)
        self.hit_and_release_switch("s_scoop")
        self.advance_time_and_run(0.1)

        self.assertPlayerVarEqual(7, "duke_rescues")
        self.assertPlayerVarEqual(16250000, "duke_the_dolphin_total")
        self.assertEventCalled("logicblock_duke_counter_complete")
        self.assertTrue(self.machine.modes["duke_the_dolphin"].active)

        self.post_event("slide_duke_the_dolphin_finish_removed")
        self.advance_time_and_run(0.1)
        self.assertFalse(self.machine.ball_holds["duke_finish"].enabled)
        self.assertFalse(self.machine.modes["duke_the_dolphin"].active)

    def test_multiball_can_start_during_mode(self):
        """Duke remains active when multiball starts during the mission."""
        self._start_play()

        self.post_event("multiball_grill_mb_started")
        self.advance_time_and_run(0.1)

        self.assertTrue(self.machine.modes["duke_the_dolphin"].active)
        self.assertPlayerVarEqual(1, "any_mb_active")

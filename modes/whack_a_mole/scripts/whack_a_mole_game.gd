# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

extends Control

const ROUND_SECONDS := 30.0
const STARTING_LIVES := 3
const HANK := 0
const BOBBY := 1
const PEGGY := 2
const TOM := 3
const TARGET_NAMES: Array[String] = ["HANK", "BOBBY", "PEGGY", "TOM"]
const TARGET_VALUES: Array[int] = [50_000, 200_000, 50_000, 0]
const LANE_X: Array[float] = [92.0, 452.0, 808.0]
const HIDDEN_Y := 540.0
const RAISED_Y := 270.0
const BOBBY_LIFETIME := 0.58
const NORMAL_LIFETIME := 1.05
const SPAWN_DELAY := 0.28
const COMBO_WINDOW := 0.1
const END_SCREEN_SECONDS := 5.4
const STREAK_BONUSES := {5: 100_000, 10: 250_000, 15: 500_000, 20: 1_000_000}
const PERFECT_BONUS := 2_500_000

@export var target_textures: Array[Texture2D]
@export var start_callout: AudioStream
@export var bobby_callout: AudioStream
@export var tom_callout: AudioStream
@export var final_callout: AudioStream
@export var whack_sound: AudioStream

@onready var timer_label: Label = $TimerLabel
@onready var score_label: Label = $ScoreLabel
@onready var streak_label: Label = $StreakLabel
@onready var lives_label: Label = $LivesLabel
@onready var message_label: Label = $MessageLabel
@onready var callout_player: AudioStreamPlayer = $CalloutPlayer
@onready var effects_player: AudioStreamPlayer = $EffectsPlayer
@onready var targets: Array[TextureRect] = [
	$Targets/LeftTarget,
	$Targets/MiddleTarget,
	$Targets/RightTarget,
]
@onready var bonk_labels: Array[Label] = [
	$Bonks/LeftBonk,
	$Bonks/MiddleBonk,
	$Bonks/RightBonk,
]
@onready var hammers: Array[Node2D] = [
	$Hammers/LeftHammer,
	$Hammers/MiddleHammer,
	$Hammers/RightHammer,
]
@onready var final_panel: Panel = $FinalPanel
@onready var final_title: Label = $FinalPanel/FinalTitle
@onready var final_score: Label = $FinalPanel/FinalScore

var time_remaining := ROUND_SECONDS
var lives := STARTING_LIVES
var streak := 0
var round_score := 0
var active_lane := -1
var active_target := -1
var target_elapsed := 0.0
var target_lifetime := NORMAL_LIFETIME
var spawn_elapsed := 0.0
var left_flipper_down := false
var right_flipper_down := false
var pending_lane := -1
var pending_elapsed := 0.0
var accepting_input := false
var finishing := false
var finish_elapsed := 0.0
var finish_event := ""
var perfect_run := true
var active_tween: Tween


func _ready() -> void:
	MPF.server.add_event_handler("s_left_flipper_active", _on_left_flipper_active)
	MPF.server.add_event_handler("s_left_flipper_inactive", _on_left_flipper_inactive)
	MPF.server.add_event_handler("s_right_flipper_active", _on_right_flipper_active)
	MPF.server.add_event_handler("s_right_flipper_inactive", _on_right_flipper_inactive)
	_reset_targets()
	_refresh_hud()
	_play_callout(start_callout)
	accepting_input = true
	_spawn_target()


func _exit_tree() -> void:
	MPF.server.remove_event_handler("s_left_flipper_active", _on_left_flipper_active)
	MPF.server.remove_event_handler("s_left_flipper_inactive", _on_left_flipper_inactive)
	MPF.server.remove_event_handler("s_right_flipper_active", _on_right_flipper_active)
	MPF.server.remove_event_handler("s_right_flipper_inactive", _on_right_flipper_inactive)


func _process(delta: float) -> void:
	if finishing:
		finish_elapsed += delta
		if finish_elapsed >= END_SCREEN_SECONDS:
			MPF.server.send_event(finish_event)
			set_process(false)
		return
	if pending_lane >= 0:
		pending_elapsed += delta
		if pending_elapsed >= COMBO_WINDOW:
			var lane := pending_lane
			pending_lane = -1
			_whack(lane)
	time_remaining = maxf(0.0, time_remaining - delta)
	timer_label.text = "%02d" % ceili(time_remaining)
	if time_remaining <= 0.0:
		_complete_round()
		return
	if active_lane >= 0:
		target_elapsed += delta
		if target_elapsed >= target_lifetime:
			_expire_target()
	else:
		spawn_elapsed += delta
		if spawn_elapsed >= SPAWN_DELAY:
			_spawn_target()


func _on_left_flipper_active(_payload: Dictionary) -> void:
	left_flipper_down = true
	if right_flipper_down:
		pending_lane = -1
		_whack(1)
	else:
		pending_lane = 0
		pending_elapsed = 0.0


func _on_left_flipper_inactive(_payload: Dictionary) -> void:
	left_flipper_down = false


func _on_right_flipper_active(_payload: Dictionary) -> void:
	right_flipper_down = true
	if left_flipper_down:
		pending_lane = -1
		_whack(1)
	else:
		pending_lane = 2
		pending_elapsed = 0.0


func _on_right_flipper_inactive(_payload: Dictionary) -> void:
	right_flipper_down = false


func _whack(lane: int) -> void:
	if not accepting_input or active_lane != lane:
		return
	_play_whack_effect(lane)
	if active_target == TOM:
		_hit_tom()
	else:
		_hit_scoring_target()
	_lower_active_target(true)


func _hit_scoring_target() -> void:
	var target_name: String = TARGET_NAMES[active_target]
	var target_value: int = TARGET_VALUES[active_target]
	streak += 1
	round_score += target_value
	message_label.text = "+%s  %s" % [_format_score(target_value), target_name]
	MPF.server.send_event_with_args("whack_a_mole_target_hit", {"target": target_name.to_lower()})
	if active_target == BOBBY:
		_play_callout(bobby_callout)
	if STREAK_BONUSES.has(streak):
		var bonus: int = STREAK_BONUSES[streak]
		round_score += bonus
		message_label.text = "%d STREAK!  +%s" % [streak, _format_score(bonus)]
		MPF.server.send_event_with_args("whack_a_mole_streak_bonus", {"streak": streak})
	_refresh_hud()


func _hit_tom() -> void:
	lives -= 1
	streak = 0
	perfect_run = false
	message_label.text = "TOM! LIFE LOST"
	MPF.server.send_event("whack_a_mole_tom_hit")
	_play_callout(tom_callout)
	_refresh_hud()
	if lives <= 0:
		_fail_round()


func _spawn_target() -> void:
	active_lane = randi_range(0, 2)
	active_target = _choose_target()
	target_elapsed = 0.0
	spawn_elapsed = 0.0
	target_lifetime = BOBBY_LIFETIME if active_target == BOBBY else NORMAL_LIFETIME
	var target := targets[active_lane]
	target.texture = target_textures[active_target]
	target.position = Vector2(LANE_X[active_lane], HIDDEN_Y)
	target.visible = true
	active_tween = create_tween()
	active_tween.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	active_tween.tween_property(target, "position:y", RAISED_Y, 0.16)


func _expire_target() -> void:
	if active_target != TOM:
		streak = 0
		perfect_run = false
		message_label.text = "%s ESCAPED — STREAK LOST" % TARGET_NAMES[active_target]
		MPF.server.send_event_with_args("whack_a_mole_target_missed", {"target": TARGET_NAMES[active_target].to_lower()})
		_refresh_hud()
	_lower_active_target()


func _lower_active_target(was_hit := false) -> void:
	if active_lane < 0:
		return
	if active_tween and active_tween.is_valid():
		active_tween.kill()
	var lane := active_lane
	var target := targets[lane]
	if was_hit:
		target.rotation = deg_to_rad(-6.0 if lane == 0 else 6.0)
	active_tween = create_tween()
	active_tween.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	active_tween.tween_property(target, "position:y", HIDDEN_Y, 0.12)
	active_tween.parallel().tween_property(target, "modulate", Color(1.0, 0.4, 0.25, 1.0) if was_hit else Color.WHITE, 0.06)
	active_tween.tween_callback(_finish_lowering.bind(target))
	active_lane = -1
	active_target = -1
	target_elapsed = 0.0
	spawn_elapsed = 0.0


func _finish_lowering(target: TextureRect) -> void:
	target.visible = false
	target.rotation = 0.0
	target.modulate = Color.WHITE


func _reset_targets() -> void:
	for lane in targets.size():
		targets[lane].position = Vector2(LANE_X[lane], HIDDEN_Y)
		targets[lane].visible = false
	for bonk in bonk_labels:
		bonk.visible = false
	for hammer in hammers:
		hammer.visible = false
	final_panel.visible = false


func _choose_target() -> int:
	var roll := randi_range(0, 99)
	if roll < 12:
		return TOM
	if roll < 27:
		return BOBBY
	return HANK if randi_range(0, 1) == 0 else PEGGY


func _play_whack_effect(lane: int) -> void:
	effects_player.stream = whack_sound
	effects_player.play()
	var hammer := hammers[lane]
	hammer.visible = true
	hammer.rotation = deg_to_rad(-48.0 if lane < 2 else 48.0)
	hammer.scale = Vector2(0.9, 0.9)
	var hammer_tween := create_tween()
	hammer_tween.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	hammer_tween.tween_property(hammer, "rotation", 0.0, 0.09)
	hammer_tween.parallel().tween_property(hammer, "scale", Vector2(1.08, 0.92), 0.09)
	hammer_tween.tween_interval(0.07)
	hammer_tween.tween_property(hammer, "rotation", deg_to_rad(-32.0 if lane < 2 else 32.0), 0.1)
	hammer_tween.parallel().tween_property(hammer, "modulate:a", 0.0, 0.1)
	hammer_tween.tween_callback(func() -> void:
		hammer.visible = false
		hammer.modulate = Color.WHITE
	)
	var bonk := bonk_labels[lane]
	bonk.visible = true
	bonk.scale = Vector2(0.55, 0.55)
	bonk.modulate = Color.WHITE
	var tween := create_tween()
	tween.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.tween_property(bonk, "scale", Vector2.ONE, 0.08)
	tween.tween_interval(0.08)
	tween.tween_property(bonk, "modulate:a", 0.0, 0.1)
	tween.tween_callback(func() -> void: bonk.visible = false)


func _complete_round() -> void:
	if perfect_run:
		round_score += PERFECT_BONUS
		final_title.text = "PERFECT ROUND!"
		MPF.server.send_event("whack_a_mole_perfect")
	else:
		final_title.text = "TIME!"
	_begin_finish("whack_a_mole_completed")


func _fail_round() -> void:
	final_title.text = "OUT OF LIVES!"
	_begin_finish("whack_a_mole_failed")


func _begin_finish(event_name: String) -> void:
	if finishing:
		return
	finishing = true
	accepting_input = false
	pending_lane = -1
	finish_event = event_name
	finish_elapsed = 0.0
	_lower_active_target()
	final_score.text = "FINAL SCORE\n%s" % _format_score(round_score)
	final_panel.visible = true
	_play_callout(final_callout)


func _refresh_hud() -> void:
	score_label.text = _format_score(round_score)
	streak_label.text = "STREAK %d" % streak
	lives_label.text = "LIVES " + "●".repeat(lives) + "○".repeat(STARTING_LIVES - lives)


func _format_score(value: int) -> String:
	return "%d" % value


func _play_callout(stream: AudioStream) -> void:
	if stream == null:
		return
	callout_player.stream = stream
	callout_player.play()

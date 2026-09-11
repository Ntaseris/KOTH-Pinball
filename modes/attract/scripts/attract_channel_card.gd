# Copyright (C) 2026 One More Game - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

extends Control

@onready var animation_player: AnimationPlayer = $AnimationPlayer
@onready var static_sound: AudioStreamPlayer = $StaticSound


func _ready() -> void:
	visibility_changed.connect(_on_visibility_changed)
	_on_visibility_changed()


func _on_visibility_changed() -> void:
	if visible:
		animation_player.play("channel_change")
		static_sound.play()
	else:
		animation_player.stop()
		static_sound.stop()


# GlowButton.gd
extends Button
@export var colorway : int = 0 # 0 = teal, 1 = amber
@export var glow_strength : float = 0.30

var mat : ShaderMaterial

func _ready():
    if material == null:
        material = ShaderMaterial.new()
        material.shader = load("res://GlowButton.shader")
    mat = material
    _apply_colors()
    connect("mouse_entered", _hover_on)
    connect("mouse_exited", _hover_off)
    connect("pressed", _press)
    connect("button_up", _release)

func _apply_colors():
    var teal = Color8(30,195,179,255)
    var amber = Color8(246,168,0,255)
    var c = teal if colorway == 0 else amber
    mat.set_shader_parameter("edge_glow_color", c)
    mat.set_shader_parameter("glow", glow_strength)

func _hover_on():
    mat.set_shader_parameter("glow", glow_strength + 0.1)

func _hover_off():
    mat.set_shader_parameter("glow", glow_strength)

func _press():
    self.position.y += 1

func _release():
    self.position.y -= 1

extends Node
class_name EscToClose
## Universal escape-contract helper (fix/ui-no-dead-ends).
##
## Attaches ui_cancel (Esc) handling to any panel/dialog -- INCLUDING scriptless
## Panels built procedurally (e.g. the Liability Ledger) -- so the panel honors the
## "every panel is escapable" contract on its OWN, without depending on a host input
## router (MainUI._input) being wired. That intrinsic exit is what stops a panel
## becoming a dead-end if the host wiring is ever absent or regresses. See
## docs/game-design/UI_ESCAPE_CONTRACT.md.
##
## Uses _unhandled_input on purpose: an in-game host that consumes Esc FIRST
## (MainUI._input calls set_input_as_handled) still wins, so this never double-fires
## in the running game; it is the fallback that guarantees the panel is never trapped.

var on_close: Callable

static func attach(target: Node, close_cb: Callable) -> EscToClose:
	var helper := EscToClose.new()
	helper.name = "EscToClose"
	helper.on_close = close_cb
	target.add_child(helper)
	return helper

func _unhandled_input(event: InputEvent) -> void:
	if not on_close.is_valid():
		return
	if event.is_action_pressed("ui_cancel"):
		on_close.call()
		var vp := get_viewport()
		if vp:
			vp.set_input_as_handled()

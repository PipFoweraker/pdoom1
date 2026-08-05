class_name LabNameGenerator
extends RefCounted
## Random lab-name generator (the [random] button on pre-game setup, plus the
## one-time default-identity prompt's reroll at game over).
##
## REGISTER (docs/game-design/DESIGN_PHILOSOPHY.md): dry gallows humour. "You
## can't win. You can only buy time." A rolled name should be keepable -- earnest,
## corporate, faintly ominous, or (rarely) openly absurd. The old generator was
## one shape (prefix + topic + suffix) over beige word lists, so every result
## sounded like the same institute; the benchmark for "good" is that Pip's own
## hand-typed "Notkilleveryone Inc" beat every generated name.
##
## FIVE SHAPES, WEIGHTED (why these): real AI-org names cluster into a few
## recognisable species -- the university institute, the startup, the law-firm-
## like consultancy, the backronymed NGO -- and shape variety reads as a
## different ORG each roll, where longer word lists inside one shape still read
## as the same org with the serial number filed off. The openly-absurd shape is
## weighted rare (10%) so it stays a punchline instead of the house style.
## Freeform portmanteau-mashing was considered and rejected: at these pool sizes
## curation beats combinatorics (syllable-mash produces embarrassments; every
## curated entry below was chosen on purpose).
##
## RNG / DETERMINISM (ADR-0006, replay is sacred): draws come ONLY from the
## RandomNumberGenerator the caller hands in. Callers are UI-side (pregame
## setup's randomize()d local RNG; the game-over identity prompt) -- the seeded
## run RNG (GameState.rng) never routes through here, so draw counts here can
## never shift a seeded run. Tests pass a seeded RNG to pin THIS generator's
## own determinism.
##
## ASCII ONLY (issue #744): every pool entry below must stay plain ASCII.

# ---- shape weights (out of 100) --------------------------------------------
const _W_INSTITUTE := 30  # "Bureau of Recursive Alignment Triage"
const _W_CORPORATE := 25  # "Paperclip Holdings"
const _W_FIRM := 20       # "Voss & Okafor Containment"
const _W_ACRONYM := 15    # "SAFE (Society Against Foom Events)"
const _W_GALLOWS := 10    # "Five More Minutes Foundation"

# ---- institute shape --------------------------------------------------------
const _PREFIXES := [
	"Center for", "Institute for", "Bureau of", "Department of",
	"Coalition for", "Office of", "Commission on", "Society for",
	"Initiative for", "Foundation for",
]
const _TOPICS := [
	"AI Safety", "Aligned Intelligence", "Machine Cognition",
	"Frontier Oversight", "Existential Risk", "Recursive Alignment",
	"Model Interpretability", "Beneficial Computation", "Artificial Prudence",
	"Catastrophe Deferral", "Applied Foresight", "Machine Ethics",
]
const _SUFFIXES := [
	"Research", "Studies", "Assurance", "Preparedness",
	"Stewardship", "Triage", "Mitigation", "Containment",
]

# ---- corporate shape --------------------------------------------------------
const _CORP_WORDS := [
	"Failsafe", "Sentinel", "Guardrail", "Foresight", "Redline",
	"Tripwire", "Bastion", "Lighthouse", "Deadline", "Provenance",
	"Halcyon", "Meridian", "Paperclip", "Anodyne",
]
const _ORG_SUFFIXES := [
	"Labs", "Systems", "Dynamics", "Analytics", "Holdings",
	"Collective", "Group", "Trust", "Inc", "Ventures",
]

# ---- surname-firm shape -----------------------------------------------------
const _SURNAMES := [
	"Voss", "Okafor", "Marlowe", "Chen", "Ishikawa", "Reyes",
	"Lindqvist", "Adeyemi", "Novak", "Whitmore", "Kaur", "Petrov",
]
const _FIRM_DOMAINS := [
	"Alignment", "Oversight", "Containment", "Associates", "Consulting",
]

# ---- acronym shape (curated pairs: the letters must actually expand) --------
const _ACRONYMS := [
	"HALT (Halting Autonomous Lethal Takeoff)",
	"CALM (Center for Aligned Language Models)",
	"SAFE (Society Against Foom Events)",
	"GRIM (Global Risk Intervention Mechanism)",
	"LATE (League Against Terminal Events)",
	"WELP (Worldwide Emergency Longtermist Partnership)",
	"OMEN (Oversight of Machine-Emergent Networks)",
	"DOOM (Department of Ominous Machines)",
]

# ---- gallows shape (curated, rare on purpose) -------------------------------
const _GALLOWS := [
	"Probably Fine Labs",
	"Time Buyers Collective",
	"The Off Switch Company",
	"Mostly Aligned Ventures",
	"Deadline Extension Bureau",
	"Five More Minutes Foundation",
	"Second Thoughts Institute",
	"It Gets Worse Analytics",
	"Room for Error Holdings",
	"Fine Print Futures",
]

## Roll one lab name. Same seeded rng in -> same name out (unit-pinned).
static func generate(rng: RandomNumberGenerator) -> String:
	# Belt-and-braces: the pools are curated so adjacent-duplicate words cannot
	# occur today, but a future pool edit could introduce one ("AI Safety" +
	# "Safety Research"); redraw rather than ship "Safety Safety".
	for _attempt in range(5):
		var name := _compose(rng)
		if not _has_adjacent_duplicate(name):
			return name
	return _GALLOWS[0]  # unreachable with the current pools; total fallback

static func _compose(rng: RandomNumberGenerator) -> String:
	var roll := rng.randi_range(0, 99)
	if roll < _W_INSTITUTE:
		return _institute(rng)
	roll -= _W_INSTITUTE
	if roll < _W_CORPORATE:
		return "%s %s" % [_pick(rng, _CORP_WORDS), _pick(rng, _ORG_SUFFIXES)]
	roll -= _W_CORPORATE
	if roll < _W_FIRM:
		return _firm(rng)
	roll -= _W_FIRM
	if roll < _W_ACRONYM:
		return _pick(rng, _ACRONYMS)
	return _pick(rng, _GALLOWS)

static func _institute(rng: RandomNumberGenerator) -> String:
	var topic: String = _pick(rng, _TOPICS)
	var form := rng.randi_range(0, 3)
	if form <= 1:  # 50%: the full three-parter
		return "%s %s %s" % [_pick(rng, _PREFIXES), topic, _pick(rng, _SUFFIXES)]
	if form == 2:  # 25%: "Bureau of Existential Risk"
		return "%s %s" % [_pick(rng, _PREFIXES), topic]
	return "%s %s" % [topic, _pick(rng, _SUFFIXES)]  # 25%: "Machine Ethics Triage"

static func _firm(rng: RandomNumberGenerator) -> String:
	# Distinct surnames: walk from a random start so no redraw loop is needed
	# (keeps the draw count per shape fixed and the output well-formed).
	var n := _SURNAMES.size()
	var first := rng.randi_range(0, n - 1)
	var second: int = (first + rng.randi_range(1, n - 1)) % n
	var form := rng.randi_range(0, 3)
	if form <= 1:  # 50%: "Voss & Chen Containment"
		return "%s & %s %s" % [_SURNAMES[first], _SURNAMES[second], _pick(rng, _FIRM_DOMAINS)]
	if form == 2:  # 25%: the bare two-name partnership
		return "%s & %s" % [_SURNAMES[first], _SURNAMES[second]]
	# 25%: the three-name letterhead
	var third: int = (second + rng.randi_range(1, n - 1)) % n
	if third == first:
		third = (third + 1) % n
		if third == second:  # squeezed between the other two: step once more
			third = (third + 1) % n
	return "%s, %s & %s" % [_SURNAMES[first], _SURNAMES[second], _SURNAMES[third]]

static func _pick(rng: RandomNumberGenerator, pool: Array) -> String:
	return pool[rng.randi_range(0, pool.size() - 1)]

## True if two consecutive words match case-insensitively ("Safety Safety").
## Punctuation-bearing tokens ("&", "(Society") never match a plain word, which
## is fine: the failure this guards against is doubled plain words.
static func _has_adjacent_duplicate(name: String) -> bool:
	var words := name.split(" ", false)
	for i in range(1, words.size()):
		if words[i].nocasecmp_to(words[i - 1]) == 0:
			return true
	return false

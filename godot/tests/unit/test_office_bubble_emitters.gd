extends GutTest
## Pass-3 organic water-cooler bubbles (Pip 2026-07-26: "make them way more
## intermittent and seemingly-random -- if you have 2 firing on slightly
## off-kilter timers, it seems organic."). Two independent emitters with
## INCOMMENSURATE base periods (7.3 s / 11.9 s: no short common multiple) each
## fire one short 3-frame rise per period; a deterministic per-prop phase
## (hash of the prop position -- ADR-0006, no RNG draws) offsets each emitter.
## These tests pin: purity/determinism of the emitter math, sparseness (events,
## not a constant loop), and NO-SHORT-PERIOD REPETITION -- the combined burst
## signal must not repeat with any period <= the longest single period.

const FEET := Vector2(317, 37)   # a representative water-cooler feet point


func _phases() -> Array:
	var out: Array = []
	for i in range(OfficeFloor.BUBBLE_EMITTER_PERIODS.size()):
		out.append(OfficeFloor.bubble_phase_for(FEET, OfficeFloor.BUBBLE_EMITTER_PERIODS[i], i))
	return out


# Combined signal: is ANY emitter mid-burst at time t?
func _active(t: float, phases: Array) -> bool:
	for i in range(OfficeFloor.BUBBLE_EMITTER_PERIODS.size()):
		if OfficeFloor.bubble_frame_at(t, OfficeFloor.BUBBLE_EMITTER_PERIODS[i], phases[i]) >= 0:
			return true
	return false


func test_two_emitters_with_incommensurate_periods():
	var p: Array = OfficeFloor.BUBBLE_EMITTER_PERIODS
	assert_eq(p.size(), 2, "the desync trick needs exactly two off-kilter timers")
	assert_ne(p[0], p[1])
	# Tripwire for future edits: neither period may (near-)divide the other --
	# a clean ratio would give the combined pattern a short visible loop.
	var remainder := fposmod(maxf(p[0], p[1]), minf(p[0], p[1]))
	assert_gt(remainder, 0.5, "long period is not a near-multiple of the short one")
	assert_lt(remainder, minf(p[0], p[1]) - 0.5,
		"nor one step short of the next multiple (which would also near-align)")


func test_phase_is_deterministic_and_in_range():
	for i in range(2):
		var period: float = OfficeFloor.BUBBLE_EMITTER_PERIODS[i]
		var a := OfficeFloor.bubble_phase_for(FEET, period, i)
		var b := OfficeFloor.bubble_phase_for(FEET, period, i)
		assert_eq(a, b, "same prop position + emitter -> same phase (pure hash, no RNG)")
		assert_between(a, 0.0, period, "phase lies inside one period")
	assert_ne(
		OfficeFloor.bubble_phase_for(FEET, 7.3, 0),
		OfficeFloor.bubble_phase_for(FEET + Vector2(50, 10), 7.3, 0),
		"a cooler in a different spot fires on a different schedule")


func test_frame_at_is_pure_and_walks_the_short_rise():
	var period := 7.3
	var phase := 0.0
	assert_eq(OfficeFloor.bubble_frame_at(1.0, period, phase),
		OfficeFloor.bubble_frame_at(1.0, period, phase), "pure function of time")
	# From the burst start the frames rise 0 -> 1 -> 2, then the emitter is quiet
	# for the rest of the period (an EVENT, not a loop).
	var ft := OfficeFloor.BUBBLE_FRAME_TIME
	assert_eq(OfficeFloor.bubble_frame_at(0.5 * ft, period, phase), 0)
	assert_eq(OfficeFloor.bubble_frame_at(1.5 * ft, period, phase), 1)
	assert_eq(OfficeFloor.bubble_frame_at(2.5 * ft, period, phase), 2)
	assert_eq(OfficeFloor.bubble_frame_at(3.5 * ft, period, phase), -1, "burst over -> quiet")
	assert_eq(OfficeFloor.bubble_frame_at(period * 0.6, period, phase), -1, "mid-period silence")
	assert_eq(OfficeFloor.bubble_frame_at(period + 0.5 * ft, period, phase), 0,
		"next period fires the next burst")


func test_bursts_are_sparse_events():
	# Over 60 s the combined signal is mostly OFF (sparse events), yet both
	# emitters actually fire: expect ~8 bursts from the 7.3 s emitter and ~5
	# from the 11.9 s one, each ~1 s long -> active fraction well under 0.4.
	var phases := _phases()
	var dt := 0.05
	var steps := int(60.0 / dt)
	var active_n := 0
	var rising_edges := 0
	var prev := false
	for n in range(steps):
		var a := _active(n * dt, phases)
		if a:
			active_n += 1
		if a and not prev:
			rising_edges += 1
		prev = a
	var frac := float(active_n) / float(steps)
	assert_between(frac, 0.05, 0.4, "sparse: quiet most of the time, but alive")
	assert_between(rising_edges, 7, 15, "roughly 60/7.3 + 60/11.9 ~= 13 bursts (+/- overlap merges)")


func test_combined_sequence_has_no_short_period():
	# THE organic guarantee: sample the combined burst signal on a 0.1 s grid
	# over 60 s and assert NO shift <= max(single periods) reproduces it. The
	# 7.3 s emitter alone repeats at 7.3 s and the 11.9 s emitter at 11.9 s, but
	# their SUM only realigns at 7.3 * 11.9 ~= 86.9 s -- so every candidate
	# period up to 11.9 s must mismatch somewhere in the window.
	var phases := _phases()
	var dt := 0.1
	var steps := int(60.0 / dt)
	var sig: Array = []
	for n in range(steps):
		sig.append(_active(n * dt, phases))
	var max_period: float = maxf(
		OfficeFloor.BUBBLE_EMITTER_PERIODS[0], OfficeFloor.BUBBLE_EMITTER_PERIODS[1])
	var max_shift := int(max_period / dt)
	for shift in range(1, max_shift + 1):
		var mismatch := false
		for n in range(steps - shift):
			if sig[n] != sig[n + shift]:
				mismatch = true
				break
		assert_true(mismatch,
			"combined burst signal must not repeat with period %.1f s" % (shift * dt))

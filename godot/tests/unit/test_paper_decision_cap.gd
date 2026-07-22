extends GutTest
## #630 stopgap -- paper-decision flood throttle.
##
## Papers whose decision_turn has arrived resolve on a path NOT governed by
## GameEvents.MAX_NEW_EVENTS_PER_TURN, so clustered decision_turns otherwise dump a
## click-through wall (playtest 2026-07-13 saw 28+ at once). process_paper_decisions
## now caps how many decisions surface per turn (Balance "papers.max_decisions_per_turn");
## the surplus stays UNDER_REVIEW and resolves on later turns -- no outcome dropped.

const CURRENT_TURN := 10
const DECISION_TURN := 5  # already due: DECISION_TURN < CURRENT_TURN


func _make_due_paper(idx: int) -> PaperSubmissions.PaperSubmission:
	var paper := PaperSubmissions.PaperSubmission.new()
	paper.id = "paper_test_%d" % idx
	paper.title = "Test Paper %d" % idx
	paper.status = PaperSubmissions.Status.UNDER_REVIEW
	paper.decision_turn = DECISION_TURN
	# Invalid conference id -> deterministic auto-reject (no rng, no Conferences
	# dependency). The per-turn cap/break happens BEFORE the decision branch, so an
	# auto-reject paper exercises the throttle identically to a real accept/reject.
	paper.target_conference_id = "no_such_conf_for_test"
	return paper


func _count_status(papers: Array, status: int) -> int:
	var n := 0
	for p in papers:
		if p.status == status:
			n += 1
	return n


func test_cap_throttles_decisions_per_turn():
	var cap := Balance.inum("papers.max_decisions_per_turn", 3)
	assert_true(cap > 0, "test assumes a positive per-turn cap in defaults.json")
	var total := cap + 4
	var papers := []
	for i in range(total):
		papers.append(_make_due_paper(i))
	var rng := RandomNumberGenerator.new()
	rng.seed = 12345
	var results := PaperSubmissions.process_paper_decisions(papers, CURRENT_TURN, 50.0, rng)
	assert_eq(results.size(), cap, "only 'cap' decisions surface on a single turn")
	assert_eq(
		_count_status(papers, PaperSubmissions.Status.UNDER_REVIEW), total - cap,
		"the surplus stays UNDER_REVIEW (deferred, not dropped)")


func test_deferred_papers_resolve_on_later_turns_none_dropped():
	var cap := Balance.inum("papers.max_decisions_per_turn", 3)
	assert_true(cap > 0)
	var total := cap * 2 + 1  # needs 3 passes to drain the backlog
	var papers := []
	for i in range(total):
		papers.append(_make_due_paper(i))
	var rng := RandomNumberGenerator.new()
	rng.seed = 999
	var resolved := 0
	var guard := 0
	# Re-run the SAME turn's decision step; deferred papers re-qualify each pass
	# (decision_turn already <= CURRENT_TURN), draining 'cap' at a time.
	while _count_status(papers, PaperSubmissions.Status.UNDER_REVIEW) > 0 and guard < 20:
		guard += 1
		var results := PaperSubmissions.process_paper_decisions(papers, CURRENT_TURN, 50.0, rng)
		assert_true(results.size() <= cap, "never exceeds the cap on any single pass")
		resolved += results.size()
	assert_eq(resolved, total, "every paper eventually resolves -- no outcome dropped")
	assert_eq(
		_count_status(papers, PaperSubmissions.Status.UNDER_REVIEW), 0,
		"backlog fully drained")


func test_papers_not_yet_due_are_untouched():
	# A paper whose decision_turn is in the future must not resolve, and must not
	# consume the per-turn budget meant for due papers.
	var papers := []
	var due := _make_due_paper(0)
	papers.append(due)
	var future := _make_due_paper(1)
	future.decision_turn = CURRENT_TURN + 3
	papers.append(future)
	var rng := RandomNumberGenerator.new()
	var results := PaperSubmissions.process_paper_decisions(papers, CURRENT_TURN, 50.0, rng)
	assert_eq(results.size(), 1, "only the due paper resolves")
	assert_eq(
		future.status, PaperSubmissions.Status.UNDER_REVIEW,
		"the not-yet-due paper stays UNDER_REVIEW")

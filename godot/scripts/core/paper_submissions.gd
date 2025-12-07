extends Node
class_name PaperSubmissions
## Paper submission tracking for academic travel system
## Issue #468: Travel and Paper Publication System

# Paper status enumeration
enum Status {
	DRAFTING,       # Being written (not yet submitted)
	UNDER_REVIEW,   # Submitted, awaiting decision
	ACCEPTED,       # Paper accepted, can present at conference
	REJECTED,       # Paper rejected
	PRESENTED       # Presented at conference (final state)
}

# Paper topic areas
enum Topic {
	SAFETY,           # AI safety research
	ALIGNMENT,        # Alignment theory
	INTERPRETABILITY, # Model interpretability
	CAPABILITIES,     # Capabilities research (increases doom if published)
	GOVERNANCE        # AI governance/policy
}

# Paper submission data structure
class PaperSubmission:
	var id: String
	var title: String
	var target_conference_id: String
	var submit_turn: int = -1
	var decision_turn: int = -1
	var presentation_deadline_turn: int = -1  # Must present by this turn
	var status: int = Status.DRAFTING
	var quality: float = 0.5  # 0.0 - 1.0
	var topic: int = Topic.SAFETY
	var research_invested: float = 0.0
	var lead_researcher_name: String = ""  # Track by name since Researcher refs may change
	var co_author_names: Array[String] = []

	func _init():
		id = "paper_%d" % Time.get_ticks_msec()

	func get_status_text() -> String:
		match status:
			Status.DRAFTING: return "Drafting"
			Status.UNDER_REVIEW: return "Under Review"
			Status.ACCEPTED: return "Accepted"
			Status.REJECTED: return "Rejected"
			Status.PRESENTED: return "Presented"
		return "Unknown"

	func get_topic_text() -> String:
		match topic:
			Topic.SAFETY: return "Safety"
			Topic.ALIGNMENT: return "Alignment"
			Topic.INTERPRETABILITY: return "Interpretability"
			Topic.CAPABILITIES: return "Capabilities"
			Topic.GOVERNANCE: return "Governance"
		return "General"

	func is_safety_paper() -> bool:
		return topic in [Topic.SAFETY, Topic.ALIGNMENT, Topic.INTERPRETABILITY, Topic.GOVERNANCE]

	func to_dict() -> Dictionary:
		return {
			"id": id,
			"title": title,
			"target_conference_id": target_conference_id,
			"submit_turn": submit_turn,
			"decision_turn": decision_turn,
			"presentation_deadline_turn": presentation_deadline_turn,
			"status": status,
			"status_text": get_status_text(),
			"quality": quality,
			"topic": topic,
			"topic_text": get_topic_text(),
			"research_invested": research_invested,
			"lead_researcher_name": lead_researcher_name,
			"co_author_names": co_author_names
		}

	static func from_dict(data: Dictionary) -> PaperSubmission:
		var paper = PaperSubmission.new()
		paper.id = data.get("id", paper.id)
		paper.title = data.get("title", "")
		paper.target_conference_id = data.get("target_conference_id", "")
		paper.submit_turn = data.get("submit_turn", -1)
		paper.decision_turn = data.get("decision_turn", -1)
		paper.presentation_deadline_turn = data.get("presentation_deadline_turn", -1)
		paper.status = data.get("status", Status.DRAFTING)
		paper.quality = data.get("quality", 0.5)
		paper.topic = data.get("topic", Topic.SAFETY)
		paper.research_invested = data.get("research_invested", 0.0)
		paper.lead_researcher_name = data.get("lead_researcher_name", "")
		paper.co_author_names = data.get("co_author_names", [])
		return paper

# ============================================
# Static Helper Methods
# ============================================

static func calculate_paper_quality(research_invested: float, lead_skill: int, co_author_count: int, has_media_savvy: bool) -> float:
	"""Calculate paper quality based on inputs"""
	# Base quality from research invested (0-100 research -> 0.0-1.0 quality)
	var base = clamp(research_invested / 100.0, 0.0, 1.0)

	# Lead researcher contribution (skill 1-10 -> 0.3-1.0 multiplier)
	var lead_mult = 0.3 + (lead_skill * 0.07)

	# Co-author bonus (each adds 5% up to 20%)
	var coauthor_bonus = min(co_author_count * 0.05, 0.20)

	# Trait bonuses
	var trait_bonus = 0.0
	if has_media_savvy:
		trait_bonus += 0.10  # Better at writing/presentation

	return clamp(base * lead_mult + coauthor_bonus + trait_bonus, 0.0, 1.0)

static func generate_paper_title(topic: int, rng: RandomNumberGenerator) -> String:
	"""Generate a procedural paper title based on topic"""
	var prefixes = {
		Topic.SAFETY: ["Toward Safe", "Ensuring Safety in", "Risk Mitigation for", "Defensive Measures in", "Safety-Critical"],
		Topic.ALIGNMENT: ["Aligning", "Value Learning in", "Corrigibility of", "Goal Stability in", "Preference Learning for"],
		Topic.INTERPRETABILITY: ["Interpreting", "Explaining", "Transparency in", "Understanding", "Mechanistic Analysis of"],
		Topic.CAPABILITIES: ["Scaling", "Advancing", "Novel Architectures for", "Efficient", "State-of-the-Art"],
		Topic.GOVERNANCE: ["Governing", "Regulating", "Policy Frameworks for", "International Coordination in", "Standards for"]
	}

	var subjects = {
		Topic.SAFETY: ["Large Language Models", "Neural Networks", "AI Systems", "Autonomous Agents", "Foundation Models"],
		Topic.ALIGNMENT: ["Language Models", "Reward Learning", "Human Preferences", "AI Assistants", "Agent Objectives"],
		Topic.INTERPRETABILITY: ["Transformer Attention", "Neural Representations", "Model Decisions", "Hidden States", "Activation Patterns"],
		Topic.CAPABILITIES: ["Language Understanding", "Reasoning Tasks", "Multi-Modal Learning", "In-Context Learning", "Chain-of-Thought"],
		Topic.GOVERNANCE: ["AI Development", "Frontier Models", "Dual-Use Research", "AI Deployment", "Research Norms"]
	}

	var suffixes = [
		"via Empirical Analysis",
		"through Formal Methods",
		": A Case Study",
		"in Practice",
		": Challenges and Solutions",
		"under Uncertainty",
		": New Perspectives"
	]

	var prefix_array = prefixes.get(topic, prefixes[Topic.SAFETY])
	var subject_array = subjects.get(topic, subjects[Topic.SAFETY])

	var prefix = prefix_array[rng.randi() % prefix_array.size()]
	var subject = subject_array[rng.randi() % subject_array.size()]
	var suffix = suffixes[rng.randi() % suffixes.size()] if rng.randf() > 0.4 else ""

	return "%s %s%s" % [prefix, subject, suffix]

static func process_paper_decisions(papers: Array, current_turn: int, player_reputation: float, rng: RandomNumberGenerator) -> Array[Dictionary]:
	"""Process paper decisions for all papers at decision turn"""
	var results: Array[Dictionary] = []

	for paper in papers:
		if paper.status != Status.UNDER_REVIEW:
			continue

		if current_turn < paper.decision_turn:
			continue

		# Time for decision!
		var conf = Conferences.get_conference_by_id(paper.target_conference_id)
		if conf == null:
			# Conference not found, auto-reject
			paper.status = Status.REJECTED
			results.append({
				"accepted": false,
				"paper": paper,
				"message": "Paper '%s' rejected - conference not found" % paper.title
			})
			continue

		var accept_prob = Conferences.calculate_acceptance_probability(
			paper.quality,
			conf.prestige,
			player_reputation
		)

		var roll = rng.randf()

		if roll < accept_prob:
			paper.status = Status.ACCEPTED
			# Set presentation deadline (conference month, roughly)
			paper.presentation_deadline_turn = paper.decision_turn + (conf.submission_deadline_weeks_before * 5)
			results.append({
				"accepted": true,
				"paper": paper,
				"conference": conf,
				"probability": accept_prob,
				"message": "Paper '%s' ACCEPTED to %s! (%.0f%% chance)" % [
					paper.title, conf.name, accept_prob * 100
				]
			})
		else:
			paper.status = Status.REJECTED
			results.append({
				"accepted": false,
				"paper": paper,
				"conference": conf,
				"probability": accept_prob,
				"message": "Paper '%s' rejected from %s (%.0f%% chance)" % [
					paper.title, conf.name, accept_prob * 100
				]
			})

	return results

static func get_papers_by_status(papers: Array, status: int) -> Array:
	"""Filter papers by status"""
	var result = []
	for paper in papers:
		if paper.status == status:
			result.append(paper)
	return result

static func get_accepted_paper_for_conference(papers: Array, conf_id: String) -> PaperSubmission:
	"""Get an accepted paper for a specific conference (for presentation)"""
	for paper in papers:
		if paper.status == Status.ACCEPTED and paper.target_conference_id == conf_id:
			return paper
	return null

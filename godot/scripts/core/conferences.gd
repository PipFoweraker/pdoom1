extends Node
class_name Conferences
## Conference definitions for academic travel system
## Issue #468: Travel and Paper Publication System

# Conference tier enumeration
enum Tier { MAJOR, MINOR, UNUSUAL }

# Location tier for travel costs
enum LocationTier { LOCAL = 1, DOMESTIC = 2, INTERNATIONAL = 3 }

# Travel cost constants
const FLIGHT_COSTS = {
	1: 0,       # Local - no flight needed
	2: 500,     # Domestic
	3: 2500     # International
}

const ACCOMMODATION_DAILY = {
	1: 0,       # Local - no hotel
	2: 150,     # Domestic hotel
	3: 300      # International hotel
}

# Conference data structure
class Conference:
	var id: String
	var name: String
	var tier: int  # Tier enum
	var month: int  # 1-12, when conference occurs
	var location_tier: int  # LocationTier enum
	var registration_cost: int
	var duration_turns: int  # Conference duration in turns/days
	var review_period_weeks: int  # How long paper review takes
	var submission_deadline_weeks_before: int  # When submissions close before conference
	var reputation_gain: float
	var doom_reduction: float
	var prestige: float  # 0.0-1.0, affects paper acceptance rate
	var description: String
	var safety_focus: bool  # Has dedicated AI safety track
	var is_funded: bool  # Program covers costs (MATS, ILIAD)
	var rolling_admission: bool  # No fixed deadline (unusual events)

	func _init(conf_id: String, conf_name: String):
		id = conf_id
		name = conf_name
		tier = Tier.MINOR
		month = 1
		location_tier = LocationTier.DOMESTIC
		registration_cost = 500
		duration_turns = 3
		review_period_weeks = 8
		submission_deadline_weeks_before = 12
		reputation_gain = 5.0
		doom_reduction = 2.0
		prestige = 0.5
		description = ""
		safety_focus = false
		is_funded = false
		rolling_admission = false

	func get_travel_cost() -> Dictionary:
		"""Calculate total travel cost for attending this conference"""
		if is_funded:
			return {"flights": 0, "accommodation": 0, "registration": 0, "total": 0}

		var flights = FLIGHT_COSTS.get(location_tier, 500)
		var accommodation = ACCOMMODATION_DAILY.get(location_tier, 150) * duration_turns
		return {
			"flights": flights,
			"accommodation": accommodation,
			"registration": registration_cost,
			"total": flights + accommodation + registration_cost
		}

	func to_dict() -> Dictionary:
		return {
			"id": id,
			"name": name,
			"tier": tier,
			"month": month,
			"location_tier": location_tier,
			"registration_cost": registration_cost,
			"duration_turns": duration_turns,
			"review_period_weeks": review_period_weeks,
			"prestige": prestige,
			"description": description,
			"safety_focus": safety_focus,
			"is_funded": is_funded,
			"travel_cost": get_travel_cost()
		}

# ============================================
# Static Factory Methods
# ============================================

static func get_all_conferences() -> Array[Conference]:
	"""Return all conferences (major, minor, and unusual)"""
	var all: Array[Conference] = []
	all.append_array(get_major_conferences())
	all.append_array(get_minor_conferences())
	all.append_array(get_unusual_events())
	return all

static func get_major_conferences() -> Array[Conference]:
	"""Major ML/AI conferences - high prestige, competitive"""
	var conferences: Array[Conference] = []

	# NeurIPS - December, largest ML conference
	var neurips = Conference.new("neurips", "NeurIPS")
	neurips.tier = Tier.MAJOR
	neurips.month = 12
	neurips.location_tier = LocationTier.INTERNATIONAL
	neurips.registration_cost = 800
	neurips.duration_turns = 5
	neurips.review_period_weeks = 12
	neurips.submission_deadline_weeks_before = 20
	neurips.reputation_gain = 15.0
	neurips.doom_reduction = 5.0
	neurips.prestige = 1.0
	neurips.description = "Neural Information Processing Systems - the premier ML conference"
	neurips.safety_focus = true
	conferences.append(neurips)

	# ICML - July
	var icml = Conference.new("icml", "ICML")
	icml.tier = Tier.MAJOR
	icml.month = 7
	icml.location_tier = LocationTier.INTERNATIONAL
	icml.registration_cost = 700
	icml.duration_turns = 5
	icml.review_period_weeks = 10
	icml.submission_deadline_weeks_before = 16
	icml.reputation_gain = 12.0
	icml.doom_reduction = 4.0
	icml.prestige = 0.95
	icml.description = "International Conference on Machine Learning"
	icml.safety_focus = true
	conferences.append(icml)

	# ICLR - May
	var iclr = Conference.new("iclr", "ICLR")
	iclr.tier = Tier.MAJOR
	iclr.month = 5
	iclr.location_tier = LocationTier.INTERNATIONAL
	iclr.registration_cost = 600
	iclr.duration_turns = 4
	iclr.review_period_weeks = 10
	iclr.submission_deadline_weeks_before = 16
	iclr.reputation_gain = 10.0
	iclr.doom_reduction = 3.5
	iclr.prestige = 0.90
	iclr.description = "International Conference on Learning Representations"
	iclr.safety_focus = true
	conferences.append(iclr)

	# AAAI - February
	var aaai = Conference.new("aaai", "AAAI")
	aaai.tier = Tier.MAJOR
	aaai.month = 2
	aaai.location_tier = LocationTier.DOMESTIC
	aaai.registration_cost = 500
	aaai.duration_turns = 4
	aaai.review_period_weeks = 8
	aaai.submission_deadline_weeks_before = 14
	aaai.reputation_gain = 8.0
	aaai.doom_reduction = 2.5
	aaai.prestige = 0.85
	aaai.description = "Association for the Advancement of AI - broad AI conference"
	aaai.safety_focus = false
	conferences.append(aaai)

	return conferences

static func get_minor_conferences() -> Array[Conference]:
	"""Minor/specialized conferences - easier acceptance, lower impact"""
	var conferences: Array[Conference] = []

	# FAccT (formerly FAT*) - March
	var facct = Conference.new("facct", "FAccT")
	facct.tier = Tier.MINOR
	facct.month = 3
	facct.location_tier = LocationTier.DOMESTIC
	facct.registration_cost = 400
	facct.duration_turns = 3
	facct.review_period_weeks = 6
	facct.submission_deadline_weeks_before = 12
	facct.reputation_gain = 6.0
	facct.doom_reduction = 3.0
	facct.prestige = 0.70
	facct.description = "Fairness, Accountability, and Transparency in ML"
	facct.safety_focus = true
	conferences.append(facct)

	# AIES - February
	var aies = Conference.new("aies", "AIES")
	aies.tier = Tier.MINOR
	aies.month = 2
	aies.location_tier = LocationTier.DOMESTIC
	aies.registration_cost = 350
	aies.duration_turns = 3
	aies.review_period_weeks = 6
	aies.submission_deadline_weeks_before = 10
	aies.reputation_gain = 5.0
	aies.doom_reduction = 2.5
	aies.prestige = 0.65
	aies.description = "AI, Ethics, and Society"
	aies.safety_focus = true
	conferences.append(aies)

	return conferences

static func get_unusual_events() -> Array[Conference]:
	"""Unusual events - programs, retreats, non-traditional"""
	var events: Array[Conference] = []

	# MATS - Rolling admission mentorship program
	var mats = Conference.new("mats", "MATS Program")
	mats.tier = Tier.UNUSUAL
	mats.month = 0  # Rolling (0 = any month)
	mats.location_tier = LocationTier.DOMESTIC
	mats.registration_cost = 0
	mats.duration_turns = 10  # Multi-week program
	mats.review_period_weeks = 4
	mats.submission_deadline_weeks_before = 0
	mats.reputation_gain = 8.0
	mats.doom_reduction = 4.0
	mats.prestige = 0.80
	mats.description = "ML Alignment Theory Scholars - intensive mentorship program"
	mats.safety_focus = true
	mats.is_funded = true
	mats.rolling_admission = true
	events.append(mats)

	# ILIAD - Summer research program
	var iliad = Conference.new("iliad", "ILIAD Program")
	iliad.tier = Tier.UNUSUAL
	iliad.month = 6  # June start
	iliad.location_tier = LocationTier.DOMESTIC
	iliad.registration_cost = 0
	iliad.duration_turns = 20  # ~4 weeks
	iliad.review_period_weeks = 6
	iliad.submission_deadline_weeks_before = 16
	iliad.reputation_gain = 7.0
	iliad.doom_reduction = 3.5
	iliad.prestige = 0.75
	iliad.description = "Intro to ML Alignment - summer research program"
	iliad.safety_focus = true
	iliad.is_funded = true
	events.append(iliad)

	# Safety Research Retreat - November
	var retreat = Conference.new("safety_retreat", "Safety Research Retreat")
	retreat.tier = Tier.UNUSUAL
	retreat.month = 11
	retreat.location_tier = LocationTier.LOCAL
	retreat.registration_cost = 500
	retreat.duration_turns = 3
	retreat.review_period_weeks = 2
	retreat.submission_deadline_weeks_before = 4
	retreat.reputation_gain = 4.0
	retreat.doom_reduction = 2.0
	retreat.prestige = 0.60
	retreat.description = "Informal gathering of safety researchers for discussion"
	retreat.safety_focus = true
	events.append(retreat)

	return events

static func get_conference_by_id(conf_id: String) -> Conference:
	"""Look up a conference by its ID"""
	for conf in get_all_conferences():
		if conf.id == conf_id:
			return conf
	return null

static func get_conferences_by_month(month: int) -> Array[Conference]:
	"""Get conferences occurring in a specific month"""
	var result: Array[Conference] = []
	for conf in get_all_conferences():
		if conf.month == month or conf.month == 0:  # 0 = rolling
			result.append(conf)
	return result

static func get_conferences_accepting_submissions(current_month: int, _current_week: int) -> Array[Conference]:
	"""Get conferences currently accepting paper submissions"""
	var result: Array[Conference] = []
	for conf in get_all_conferences():
		if conf.rolling_admission:
			result.append(conf)
			continue

		# Calculate submission deadline
		var deadline_month = conf.month
		var weeks_before = conf.submission_deadline_weeks_before
		var months_before = int(weeks_before / 4)
		deadline_month = deadline_month - months_before
		if deadline_month <= 0:
			deadline_month += 12

		# Check if we're before the deadline (simplified)
		# This is a rough check - submissions open 4 weeks before deadline
		var submission_window_start = deadline_month - 1
		if submission_window_start <= 0:
			submission_window_start += 12

		if current_month >= submission_window_start and current_month <= deadline_month:
			result.append(conf)

	return result

static func calculate_acceptance_probability(paper_quality: float, conf_prestige: float, player_reputation: float) -> float:
	"""Calculate probability of paper acceptance"""
	# Higher prestige = harder to get in
	var difficulty = conf_prestige * 0.8  # 0.48 - 0.80 for prestige 0.6-1.0

	# Reputation helps (0-100 -> 0.0 - 0.15 bonus)
	var rep_bonus = player_reputation / 100.0 * 0.15

	# Base probability
	var prob = paper_quality - difficulty + rep_bonus

	# Clamp to reasonable range
	return clamp(prob, 0.05, 0.95)  # Always 5-95% chance

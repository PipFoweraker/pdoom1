extends RefCounted
class_name MediaStory
## Represents a media story affecting public opinion
##
## Media stories are generated from player actions, competitor actions,
## and random events. They affect public opinion metrics and have a duration.

enum StoryType {
	BREAKTHROUGH,      # Positive research/achievement story
	SCANDAL,          # Negative story about misconduct
	HUMAN_INTEREST,   # Personal angle on AI research
	POLICY,           # Government/regulatory discussion
	SAFETY_CONCERN,   # Public worry about AI risks
	INDUSTRY_NEWS,    # General AI sector news
	COMPETITOR       # Story about rival lab
}

## Headline text for the story
var headline: String = ""

## Type of story (affects display and mechanics)
var story_type: StoryType = StoryType.INDUSTRY_NEWS

## How many turns the story remains active
var duration: int = 3

## Turns remaining before story expires
var remaining_turns: int = 3

## Opinion effects when story is active
var sentiment_impact: float = 0.0
var trust_impact: float = 0.0
var safety_awareness_impact: float = 0.0
var media_attention_impact: float = 5.0  # Most stories increase attention

## Whether this story is about the player (vs competitors/general)
var about_player: bool = true

## Optional metadata for tracking story source
var metadata: Dictionary = {}


func _init(
	p_headline: String,
	p_type: StoryType,
	p_duration: int = 3,
	p_sentiment: float = 0.0,
	p_trust: float = 0.0,
	p_safety: float = 0.0,
	p_attention: float = 5.0,
	p_about_player: bool = true
):
	"""Create a new media story"""
	headline = p_headline
	story_type = p_type
	duration = p_duration
	remaining_turns = p_duration
	sentiment_impact = p_sentiment
	trust_impact = p_trust
	safety_awareness_impact = p_safety
	media_attention_impact = p_attention
	about_player = p_about_player


func apply_effects(public_opinion: PublicOpinion):
	"""Apply this story's effects to public opinion"""
	if sentiment_impact != 0.0:
		public_opinion.update_opinion("public_sentiment", sentiment_impact, headline)
	if trust_impact != 0.0:
		public_opinion.update_opinion("lab_trust", trust_impact, headline)
	if safety_awareness_impact != 0.0:
		public_opinion.update_opinion("safety_awareness", safety_awareness_impact, headline)
	if media_attention_impact != 0.0:
		public_opinion.update_opinion("media_attention", media_attention_impact, headline)


func process_turn():
	"""Process end-of-turn for this story (countdown duration)"""
	remaining_turns -= 1


func is_expired() -> bool:
	"""Check if story has expired"""
	return remaining_turns <= 0


func get_type_name() -> String:
	"""Get human-readable story type"""
	match story_type:
		StoryType.BREAKTHROUGH:
			return "Breakthrough"
		StoryType.SCANDAL:
			return "Scandal"
		StoryType.HUMAN_INTEREST:
			return "Human Interest"
		StoryType.POLICY:
			return "Policy"
		StoryType.SAFETY_CONCERN:
			return "Safety Concern"
		StoryType.INDUSTRY_NEWS:
			return "Industry News"
		StoryType.COMPETITOR:
			return "Competitor News"
		_:
			return "Unknown"


func get_type_icon() -> String:
	"""Get emoji icon for story type"""
	match story_type:
		StoryType.BREAKTHROUGH:
			return "🔬"
		StoryType.SCANDAL:
			return "⚠️"
		StoryType.HUMAN_INTEREST:
			return "👥"
		StoryType.POLICY:
			return "🏛️"
		StoryType.SAFETY_CONCERN:
			return "🚨"
		StoryType.INDUSTRY_NEWS:
			return "📰"
		StoryType.COMPETITOR:
			return "🏢"
		_:
			return "📄"


func get_summary() -> String:
	"""Get compact summary for UI display"""
	var target = "You" if about_player else "AI Sector"
	return "%s %s (%d turns) - %s" % [
		get_type_icon(),
		get_type_name(),
		remaining_turns,
		headline
	]


func get_impact_summary() -> String:
	"""Get summary of opinion impacts"""
	var impacts: Array[String] = []

	if sentiment_impact > 0:
		impacts.append("Sentiment +%.1f" % sentiment_impact)
	elif sentiment_impact < 0:
		impacts.append("Sentiment %.1f" % sentiment_impact)

	if trust_impact > 0:
		impacts.append("Trust +%.1f" % trust_impact)
	elif trust_impact < 0:
		impacts.append("Trust %.1f" % trust_impact)

	if safety_awareness_impact > 0:
		impacts.append("Safety Awareness +%.1f" % safety_awareness_impact)
	elif safety_awareness_impact < 0:
		impacts.append("Safety Awareness %.1f" % safety_awareness_impact)

	if media_attention_impact > 0:
		impacts.append("Media +%.1f" % media_attention_impact)

	if impacts.is_empty():
		return "No direct impact"

	return " | ".join(impacts)


func to_dict() -> Dictionary:
	"""Serialize to dictionary for saving"""
	return {
		"headline": headline,
		"story_type": story_type,
		"duration": duration,
		"remaining_turns": remaining_turns,
		"sentiment_impact": sentiment_impact,
		"trust_impact": trust_impact,
		"safety_awareness_impact": safety_awareness_impact,
		"media_attention_impact": media_attention_impact,
		"about_player": about_player,
		"metadata": metadata
	}


static func from_dict(data: Dictionary) -> MediaStory:
	"""Deserialize from dictionary for loading"""
	var story = MediaStory.new(
		data.get("headline", ""),
		data.get("story_type", StoryType.INDUSTRY_NEWS),
		data.get("duration", 3),
		data.get("sentiment_impact", 0.0),
		data.get("trust_impact", 0.0),
		data.get("safety_awareness_impact", 0.0),
		data.get("media_attention_impact", 5.0),
		data.get("about_player", true)
	)
	story.remaining_turns = data.get("remaining_turns", story.duration)
	story.metadata = data.get("metadata", {})
	return story


## Preset story templates for common scenarios

static func create_breakthrough_story(lab_name: String, reputation_gain: float) -> MediaStory:
	"""Create a positive breakthrough story"""
	var headlines = [
		"%s Achieves Major AI Safety Milestone" % lab_name,
		"Breakthrough: %s Advances Alignment Research" % lab_name,
		"%s Publishes Groundbreaking Safety Paper" % lab_name,
		"Industry Applauds %s Research Achievement" % lab_name
	]

	var intensity = clamp(reputation_gain / 3.0, 0.5, 2.0)  # Scale with reputation

	return MediaStory.new(
		headlines[randi() % headlines.size()],
		StoryType.BREAKTHROUGH,
		3,  # duration
		intensity * 3.0,  # sentiment
		intensity * 5.0,  # trust
		intensity * 2.0,  # safety awareness
		10.0,  # media attention
		true  # about player
	)


static func create_scandal_story(lab_name: String, severity: float = 1.0) -> MediaStory:
	"""Create a negative scandal story"""
	var headlines = [
		"Safety Concerns Raised About %s Practices" % lab_name,
		"%s Under Scrutiny for Research Ethics" % lab_name,
		"Whistleblower: %s Prioritizing Speed Over Safety" % lab_name,
		"Leaked Documents Raise Questions About %s" % lab_name
	]

	return MediaStory.new(
		headlines[randi() % headlines.size()],
		StoryType.SCANDAL,
		4,  # longer duration
		-severity * 5.0,  # sentiment
		-severity * 8.0,  # trust (major impact)
		severity * 3.0,  # safety awareness increases
		15.0,  # high media attention
		true  # about player
	)


static func create_safety_concern_story() -> MediaStory:
	"""Create a general AI safety concern story"""
	var headlines = [
		"Experts Warn of AI Alignment Challenges",
		"Public Growing Concerned About AI Development",
		"New Study Highlights AI Risk Scenarios",
		"Calls for Stronger AI Safety Regulations"
	]

	return MediaStory.new(
		headlines[randi() % headlines.size()],
		StoryType.SAFETY_CONCERN,
		3,
		-2.0,  # slight negative sentiment
		0.0,  # no trust impact (general concern)
		8.0,  # increases safety awareness significantly
		5.0,  # moderate attention
		false  # not about player specifically
	)


static func create_competitor_story(competitor_name: String, positive: bool) -> MediaStory:
	"""Create a story about a competitor"""
	var headlines_positive = [
		"%s Secures Major Funding Round" % competitor_name,
		"%s Announces Research Breakthrough" % competitor_name,
		"%s Expands Operations Amid AI Boom" % competitor_name
	]

	var headlines_negative = [
		"%s Faces Setback in Safety Research" % competitor_name,
		"Concerns Raised About %s Practices" % competitor_name,
		"%s Under Investigation by Regulators" % competitor_name
	]

	var headlines = headlines_positive if positive else headlines_negative

	return MediaStory.new(
		headlines[randi() % headlines.size()],
		StoryType.COMPETITOR,
		2,  # shorter duration
		-1.0 if positive else 1.0,  # negative if competitor succeeds
		1.0 if not positive else 0.0,  # trust boost if competitor struggles
		0.0,  # no safety awareness impact
		3.0,  # low attention
		false  # not about player
	)

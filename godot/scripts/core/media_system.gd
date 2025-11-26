extends Node
class_name MediaSystem
## Manages media stories and media-related actions
##
## The media system generates stories from player/competitor actions,
## processes random media events, and provides media actions the player
## can use to manage their public image.

## Active media stories
var active_stories: Array[MediaStory] = []

## Maximum number of active stories at once
const MAX_ACTIVE_STORIES: int = 5

## Reference to public opinion system
var public_opinion: PublicOpinion

## Random number generator for deterministic story generation
var rng: RandomNumberGenerator


func _init(p_public_opinion: PublicOpinion, p_rng: RandomNumberGenerator):
	"""Initialize media system with opinion tracking and RNG"""
	public_opinion = p_public_opinion
	rng = p_rng


func add_story(story: MediaStory):
	"""Add a new media story (applying immediate effects)"""
	# Apply story effects immediately
	story.apply_effects(public_opinion)

	# Add to active stories
	active_stories.append(story)

	# Remove oldest stories if we exceed the limit
	if active_stories.size() > MAX_ACTIVE_STORIES:
		active_stories.pop_front()

	print("[MediaSystem] New story: %s" % story.headline)


func process_turn():
	"""Process end-of-turn for all active stories"""
	# Age all stories
	for story in active_stories:
		story.process_turn()

	# Remove expired stories
	var expired_count = 0
	active_stories = active_stories.filter(func(story):
		if story.is_expired():
			expired_count += 1
			return false
		return true
	)

	if expired_count > 0:
		print("[MediaSystem] %d stories expired" % expired_count)


func generate_random_story() -> bool:
	"""
	Generate a random media story (called each turn)
	Returns true if a story was generated
	"""
	# Base probability increases with media attention
	var base_prob = 0.15  # 15% base chance
	var attention_bonus = public_opinion.media_attention / 1000.0  # Up to +10% at max attention
	var total_prob = base_prob + attention_bonus

	if rng.randf() > total_prob:
		return false  # No story this turn

	# Determine story type
	var story_type_roll = rng.randf()

	if story_type_roll < 0.3:
		# Safety concern story (30% chance)
		add_story(MediaStory.create_safety_concern_story())
		return true
	elif story_type_roll < 0.5:
		# Competitor story (20% chance)
		var positive = rng.randf() < 0.5
		add_story(MediaStory.create_competitor_story("Rival Lab", positive))
		return true
	elif story_type_roll < 0.7:
		# Policy/industry news (20% chance)
		add_story(_create_policy_story())
		return true
	else:
		# Human interest (30% chance)
		add_story(_create_human_interest_story())
		return true


func _create_policy_story() -> MediaStory:
	"""Create a policy/regulatory story"""
	var headlines = [
		"Congress Considers AI Safety Regulation",
		"International AI Safety Summit Announced",
		"White House Issues AI Development Guidelines",
		"Regulators Seek Input on AI Governance"
	]

	return MediaStory.new(
		headlines[rng.randi() % headlines.size()],
		MediaStory.StoryType.POLICY,
		3,
		0.0,  # neutral sentiment
		0.0,  # no trust impact
		5.0,  # increases safety awareness
		8.0,  # moderate-high attention
		false  # not about player
	)


func _create_human_interest_story() -> MediaStory:
	"""Create a human interest story about AI"""
	var headlines = [
		"AI Researchers: 'We're Working to Ensure Safe AI'",
		"Inside the World of AI Safety Research",
		"What Motivates AI Alignment Researchers?",
		"The Human Side of Artificial Intelligence"
	]

	var sentiment_impact = rng.randf_range(-2.0, 3.0)  # Slightly biased positive

	return MediaStory.new(
		headlines[rng.randi() % headlines.size()],
		MediaStory.StoryType.HUMAN_INTEREST,
		2,
		sentiment_impact,
		1.0,  # slight trust boost
		2.0,  # modest awareness increase
		5.0,  # moderate attention
		false  # general story
	)


func check_for_action_story(action_type: String, reputation_gain: float, lab_name: String) -> bool:
	"""
	Check if a player action should generate a media story
	Returns true if a story was generated
	"""
	# Only significant reputation gains generate stories
	if reputation_gain < 2.0:
		return false

	# Higher media attention = more likely to generate story
	var story_prob = 0.3 + (public_opinion.media_attention / 200.0)  # 30-80% chance

	if rng.randf() < story_prob:
		add_story(MediaStory.create_breakthrough_story(lab_name, reputation_gain))
		return true

	return false


func has_active_scandal() -> bool:
	"""Check if there are any active scandal stories about the player"""
	return active_stories.any(func(s):
		return s.story_type == MediaStory.StoryType.SCANDAL and s.about_player
	)


func get_active_story_count() -> int:
	"""Get number of currently active stories"""
	return active_stories.size()


func get_stories_summary() -> String:
	"""Get summary of active stories for display"""
	if active_stories.is_empty():
		return "No active media stories"

	var summary = "Active Media Stories:\n"
	for story in active_stories:
		summary += "- %s\n" % story.get_summary()
	return summary


func to_dict() -> Dictionary:
	"""Serialize to dictionary for saving"""
	var stories_data: Array = []
	for story in active_stories:
		stories_data.append(story.to_dict())

	return {
		"active_stories": stories_data
	}


func from_dict(data: Dictionary):
	"""Deserialize from dictionary for loading"""
	active_stories.clear()

	var stories_data = data.get("active_stories", [])
	for story_data in stories_data:
		active_stories.append(MediaStory.from_dict(story_data))


## Media Action Definitions
##
## These are called from the main actions system

func execute_press_release(game_state) -> Dictionary:
	"""
	Execute Press Release action ($50k)
	Moderate boost to trust and sentiment
	"""
	var cost = 50000

	if game_state.money < cost:
		return {"success": false, "message": "Insufficient funds"}

	# Deduct cost
	game_state.money -= cost

	# Apply effects
	public_opinion.update_opinion("lab_trust", 3.0, "Press Release")
	public_opinion.update_opinion("public_sentiment", 2.0, "Press Release")
	public_opinion.add_modifier("lab_trust", 1.0, 2, "Press Release (ongoing)")

	return {
		"success": true,
		"message": "Press release increases public trust (+3) and sentiment (+2)",
		"log": "Issued press release to shape public narrative"
	}


func execute_exclusive_interview(game_state) -> Dictionary:
	"""
	Execute Exclusive Interview action (5 reputation, 1 AP)
	High-impact story with small risk of backfire
	"""
	if game_state.reputation < 10.0:
		return {"success": false, "message": "Requires 10+ reputation"}

	if game_state.action_points < 1:
		return {"success": false, "message": "Insufficient AP"}

	# Costs reputation and AP
	game_state.reputation -= 5.0
	game_state.action_points -= 1

	# Risk of backfire (10% chance)
	var backfire = rng.randf() < 0.1

	if backfire:
		# Backfire: negative story
		public_opinion.update_opinion("lab_trust", -5.0, "Interview Backfire")
		add_story(MediaStory.new(
			"Controversial Interview Raises Questions About Lab Practices",
			MediaStory.StoryType.SCANDAL,
			3,
			-4.0,  # public_sentiment
			-6.0,  # lab_trust
			2.0,  # safety awareness
			12.0,  # high attention
			true
		))

		return {
			"success": true,
			"message": "Interview backfired! Trust -5, negative media story",
			"log": "Exclusive interview did not go as planned"
		}
	else:
		# Success: major boost
		public_opinion.update_opinion("lab_trust", 8.0, "Exclusive Interview")
		public_opinion.update_opinion("public_sentiment", 5.0, "Exclusive Interview")
		add_story(MediaStory.new(
			"In-Depth Interview Reveals Commitment to AI Safety",
			MediaStory.StoryType.HUMAN_INTEREST,
			3,
			5.0,  # public_sentiment
			8.0,  # lab_trust
			4.0,  # safety awareness
			10.0,  # attention
			true
		))

		return {
			"success": true,
			"message": "Excellent interview! Trust +8, positive media story",
			"log": "Exclusive interview strengthens public trust"
		}


func execute_damage_control(game_state) -> Dictionary:
	"""
	Execute Damage Control action ($200k)
	Reduces negative story impact, only available during scandals
	"""
	if not has_active_scandal():
		return {"success": false, "message": "No active scandals to address"}

	var cost = 200000
	if game_state.money < cost:
		return {"success": false, "message": "Insufficient funds"}

	# Deduct cost
	game_state.money -= cost

	# Reduce impact of scandal stories
	for story in active_stories:
		if story.story_type == MediaStory.StoryType.SCANDAL and story.about_player:
			# Reduce negative impacts by 50%
			story.trust_impact *= 0.5
			story.sentiment_impact *= 0.5
			# Shorten duration
			story.remaining_turns = max(1, story.remaining_turns - 2)

	# Add positive modifier
	public_opinion.add_modifier("lab_trust", 2.0, 3, "Damage Control Efforts")

	return {
		"success": true,
		"message": "Damage control reduces scandal impact by 50%",
		"log": "PR team executes damage control strategy"
	}


func execute_social_media_campaign(game_state) -> Dictionary:
	"""
	Execute Social Media Campaign action ($75k)
	Good for sentiment, moderate for trust
	Risk of backlash if overused
	"""
	var cost = 75000
	if game_state.money < cost:
		return {"success": false, "message": "Insufficient funds"}

	# Check if already used this turn (risky)
	# TODO: Track this in metadata
	var overuse_risk = rng.randf() < 0.15  # 15% base risk

	game_state.money -= cost

	if overuse_risk:
		# Backlash
		public_opinion.update_opinion("lab_trust", -3.0, "Campaign Backlash")
		public_opinion.update_opinion("public_sentiment", -2.0, "Campaign Backlash")
		return {
			"success": true,
			"message": "Social media campaign seen as manipulative. Lab Trust -3, Public Sentiment -2",
			"log": "Social media campaign backfired"
		}
	else:
		# Success
		public_opinion.update_opinion("public_sentiment", 4.0, "Social Media Campaign")
		public_opinion.update_opinion("lab_trust", 2.0, "Social Media Campaign")
		return {
			"success": true,
			"message": "Social media campaign improves sentiment (+4) and trust (+2)",
			"log": "Successful social media outreach campaign"
		}


func execute_public_statement(game_state) -> Dictionary:
	"""
	Execute Public Statement action ($10k)
	Quick response, enhanced during high media attention
	"""
	var cost = 10000
	if game_state.money < cost:
		return {"success": false, "message": "Insufficient funds"}

	game_state.money -= cost

	# Base effects
	var trust_change = 1.5
	var sentiment_change = 1.0

	# Amplify if high media attention
	if public_opinion.is_high_media_attention():
		trust_change *= 2.0
		sentiment_change *= 2.0

	public_opinion.update_opinion("lab_trust", trust_change, "Public Statement")
	public_opinion.update_opinion("public_sentiment", sentiment_change, "Public Statement")

	var message = "Public statement improves lab trust (+%.1f) and public sentiment (+%.1f)" % [trust_change, sentiment_change]
	if public_opinion.is_high_media_attention():
		message += " (amplified by media attention!)"

	return {
		"success": true,
		"message": message,
		"log": "Issued public statement on current events"
	}


func execute_investigative_tip(game_state, target_lab_name: String) -> Dictionary:
	"""
	Execute Investigative Tip action ($100k)
	Plant negative story about competitor
	Risk of discovery
	"""
	if game_state.reputation < 20.0:
		return {"success": false, "message": "Requires 20+ reputation"}

	var cost = 100000
	if game_state.money < cost:
		return {"success": false, "message": "Insufficient funds"}

	game_state.money -= cost

	# Risk of discovery increases with low trust
	var discovery_chance = 0.3 - (public_opinion.lab_trust / 500.0)  # 10-30% based on trust
	var discovered = rng.randf() < discovery_chance

	if discovered:
		# Discovery: major reputation hit
		game_state.reputation -= 15.0
		public_opinion.update_opinion("lab_trust", -15.0, "Exposed: Media Manipulation")
		add_story(MediaStory.new(
			"Scandal: Lab Caught Planting Negative Stories About Competitors",
			MediaStory.StoryType.SCANDAL,
			5,  # long duration
			-8.0,  # public_sentiment
			-15.0,  # lab_trust (devastating)
			0.0,  # safety awareness
			20.0,  # huge attention
			true
		))

		return {
			"success": true,
			"message": "EXPOSED! Reputation -15, Lab Trust -15, major scandal",
			"log": "Media manipulation exposed by investigative journalists"
		}
	else:
		# Success: competitor gets negative story
		add_story(MediaStory.create_scandal_story(target_lab_name, 0.8))
		# Small trust boost from competitor problems
		public_opinion.update_opinion("lab_trust", 2.0, "Competitor Scrutiny")

		return {
			"success": true,
			"message": "Negative story published about %s. Your lab trust +2" % target_lab_name,
			"log": "Leaked damaging information about competitor to press"
		}

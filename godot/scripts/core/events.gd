extends Node
class_name GameEvents
## Random and triggered events system

# Track which events have already triggered
static var triggered_events: Array[String] = []

static func get_all_events() -> Array[Dictionary]:
	"""Return all event definitions"""
	return [
		{
			"id": "funding_crisis",
			"name": "Funding Crisis",
			"description": "Your lab is running dangerously low on funds!",
			"type": "popup",
			"trigger_type": "turn_and_resource",
			"trigger_turn": 10,
			"trigger_condition": "money < 50000",
			"repeatable": false,
			"options": [
				{
					"id": "emergency_fundraise",
					"text": "Emergency Fundraising (costs 1 AP)",
					"costs": {"action_points": 1},
					"effects": {"money": 75000},
					"message": "Secured emergency funding: +$75,000"
				},
				{
					"id": "sell_assets",
					"text": "Sell Lab Equipment (costs 2 AP)",
					"costs": {"action_points": 2},
					"effects": {"money": 120000, "research": -10},
					"message": "Sold equipment for emergency funds: +$120,000, -10 research"
				},
				{
					"id": "accept",
					"text": "Continue Anyway (no AP cost)",
					"costs": {},
					"effects": {},
					"message": "Continuing with limited funds..."
				}
			]
		},
		{
			"id": "talent_recruitment",
			"name": "Talent Opportunity",
			"description": "A brilliant researcher wants to join your lab at reduced cost!",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.15,
			"min_turn": 5,
			"repeatable": true,
			"options": [
				{
					"id": "hire_immediately",
					"text": "Fast-Track Hiring (costs 1 AP, %s)" % GameConfig.format_money(25000),
					"costs": {"money": 25000, "action_points": 1},
					"effects": {"safety_researchers": 1, "doom": -3},
					"message": "Fast-tracked hiring process! (+1 safety researcher, -3 doom)"
				},
				{
					"id": "hire_discounted",
					"text": "Standard Hiring (%s, no AP)" % GameConfig.format_money(25000),
					"costs": {"money": 25000},
					"effects": {"safety_researchers": 1, "doom": -2},
					"message": "Hired talented researcher at discount! (+1 safety researcher, -2 doom)"
				},
				{
					"id": "decline",
					"text": "Decline Offer (no cost)",
					"costs": {},
					"effects": {},
					"message": "Declined recruitment opportunity"
				}
			]
		},
		{
			"id": "ai_breakthrough",
			"name": "AI Breakthrough!",
			"description": "Your team has made an unexpected AI capability advancement!",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.10,
			"min_turn": 8,
			"repeatable": true,
			"options": [
				{
					"id": "publish_open",
					"text": "Publish Openly",
					"effects": {"doom": 5, "reputation": 10, "research": 20},
					"message": "Published breakthrough! (+5 doom, +10 reputation, +20 research)"
				},
				{
					"id": "keep_proprietary",
					"text": "Keep Proprietary",
					"effects": {"doom": 2, "research": 30},
					"message": "Kept research proprietary (+2 doom, +30 research)"
				},
				{
					"id": "safety_review",
					"text": "Conduct Safety Review First",
					"costs": {"action_points": 1, "money": 20000},
					"effects": {"doom": 1, "research": 15, "reputation": 5},
					"message": "Safety review complete (+1 doom, +15 research, +5 reputation)"
				}
			]
		},
		{
			"id": "funding_windfall",
			"name": "Unexpected Funding",
			"description": "A philanthropist wants to donate to your safety research!",
			"type": "popup",
			"trigger_type": "threshold",
			"trigger_condition": "papers >= 3 and reputation >= 40",
			"repeatable": false,
			"options": [
				{
					"id": "accept_donation",
					"text": "Accept Donation",
					"effects": {"money": 150000, "reputation": 5},
					"message": "Accepted $150,000 donation! (+5 reputation)"
				},
				{
					"id": "decline_donation",
					"text": "Decline (Stay Independent)",
					"effects": {"reputation": 3},
					"message": "Declined donation to maintain independence (+3 reputation)"
				}
			]
		},
		{
			"id": "compute_deal",
			"name": "Compute Partnership",
			"description": "A tech company offers discounted compute access!",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.12,
			"min_turn": 6,
			"repeatable": true,
			"options": [
				{
					"id": "accept_deal",
					"text": "Accept Deal",
					"effects": {"compute": 100, "reputation": -2},
					"message": "Accepted compute deal (+100 compute, -2 reputation for corporate ties)"
				},
				{
					"id": "negotiate",
					"text": "Negotiate Better Terms",
					"costs": {"reputation": 5},
					"effects": {"compute": 150},
					"message": "Negotiated better terms! (+150 compute, -5 reputation)"
				},
				{
					"id": "decline_deal",
					"text": "Decline",
					"effects": {},
					"message": "Declined compute partnership"
				}
			]
		},
		{
			"id": "employee_burnout",
			"name": "Employee Burnout Crisis",
			"description": "Your team is overworked! Several researchers are considering leaving.",
			"type": "popup",
			"trigger_type": "threshold",
			"trigger_condition": "safety_researchers >= 5",
			"repeatable": true,
			"options": [
				{
					"id": "emergency_intervention",
					"text": "Emergency Intervention (costs 2 AP, %s)" % GameConfig.format_money(30000),
					"costs": {"money": 30000, "action_points": 2},
					"effects": {"reputation": 8, "doom": -5},
					"message": "Personal intervention prevented resignations! (+8 reputation, -5 doom)"
				},
				{
					"id": "team_retreat",
					"text": "Organize Team Retreat (%s, no AP)" % GameConfig.format_money(30000),
					"costs": {"money": 30000},
					"effects": {"reputation": 5, "doom": -2},
					"message": "Team retreat restored morale (+5 reputation, -2 doom)"
				},
				{
					"id": "salary_raise",
					"text": "Give Raises ($50k, no AP)",
					"costs": {"money": 50000},
					"effects": {"reputation": 8},
					"message": "Salary raises improved retention (+8 reputation)"
				},
				{
					"id": "ignore_burnout",
					"text": "Push Through (no cost)",
					"costs": {},
					"effects": {"doom": 3},
					"message": "Team morale suffered (+3 doom)"
				}
			]
		},
		{
			"id": "rival_poaching",
			"name": "Rival Lab Poaching",
			"description": "A well-funded competitor is trying to recruit your best researchers!",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.08,
			"min_turn": 10,
			"repeatable": true,
			"options": [
				{
					"id": "counter_offer",
					"text": "Counter-Offer ($80k)",
					"costs": {"money": 80000},
					"effects": {},
					"message": "Successfully retained researchers with counter-offer"
				},
				{
					"id": "let_go",
					"text": "Let Them Go",
					"effects": {"safety_researchers": -1, "money": 20000},
					"message": "Lost researcher but saved money (-1 safety researcher, +$20k saved)"
				}
			]
		},
		{
			"id": "media_scandal",
			"name": "Media Scandal",
			"description": "Negative press coverage is damaging your lab's reputation!",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.06,
			"min_turn": 7,
			"repeatable": true,
			"options": [
				{
					"id": "pr_campaign",
					"text": "Launch PR Campaign ($40k)",
					"costs": {"money": 40000},
					"effects": {"reputation": 10},
					"message": "PR campaign restored public image (+10 reputation)"
				},
				{
					"id": "ignore_media",
					"text": "Ignore and Focus on Work",
					"effects": {"reputation": -8},
					"message": "Reputation suffered from negative coverage (-8 reputation)"
				}
			]
		},
		{
			"id": "government_regulation",
			"name": "New AI Regulation Proposed",
			"description": "Government is considering new AI safety regulations. Should you lobby?",
			"type": "popup",
			"trigger_type": "threshold",
			"trigger_condition": "doom >= 60",
			"repeatable": false,
			"options": [
				{
					"id": "support_regulation",
					"text": "Publicly Support ($50k lobbying)",
					"costs": {"money": 50000, "action_points": 1},
					"effects": {"doom": -10, "reputation": 15},
					"message": "Regulation passed! Global safety improved (-10 doom, +15 reputation)"
				},
				{
					"id": "oppose_regulation",
					"text": "Oppose (Stay Competitive)",
					"effects": {"doom": 5, "reputation": -5},
					"message": "Regulation weakened (+5 doom, -5 reputation)"
				},
				{
					"id": "stay_neutral",
					"text": "Remain Neutral",
					"effects": {"doom": 2},
					"message": "Stayed neutral as doom increased (+2 doom)"
				}
			]
		},
		{
			"id": "technical_failure",
			"name": "Critical System Failure",
			"description": "Your compute infrastructure suffered a major failure!",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.05,
			"min_turn": 12,
			"repeatable": true,
			"options": [
				{
					"id": "emergency_repair",
					"text": "Emergency Repair ($60k)",
					"costs": {"money": 60000},
					"effects": {"compute": 30},
					"message": "System repaired and upgraded (+30 compute)"
				},
				{
					"id": "basic_fix",
					"text": "Basic Fix ($20k)",
					"costs": {"money": 20000},
					"effects": {"compute": -20},
					"message": "System limping along (-20 compute)"
				}
			]
		},
		{
			"id": "stray_cat",
			"name": "A Stray Cat Appears!",
			"description": "A friendly stray cat has wandered into your lab. It seems to enjoy watching the researchers work and occasionally walks across keyboards. Adopt it?",
			"type": "popup",
			"trigger_type": "turn_exact",
			"trigger_turn": 7,
			"repeatable": false,
			"options": [
				{
					"id": "adopt_cat",
					"text": "Adopt the Cat",
					"costs": {"money": 500},
					"effects": {"has_cat": 1, "doom": -1},
					"message": "Cat adopted! Your researchers' morale improves slightly. The cat has claimed its spot in the lab. (-1 doom)"
				},
				{
					"id": "feed_and_release",
					"text": "Feed It and Let It Go",
					"costs": {"money": 100},
					"effects": {},
					"message": "You give the cat some food and it wanders off, purring contentedly."
				},
				{
					"id": "shoo_away",
					"text": "Shoo It Away",
					"effects": {"doom": 1},
					"message": "The cat leaves, disappointed. Your researchers seem a bit sad. (+1 doom for being heartless)"
				}
			]
		},
		# HR PROBLEMS (issue #179)
		{
			"id": "workplace_conflict",
			"name": "Interpersonal Conflict",
			"description": "Two researchers are in a heated disagreement that's disrupting the entire team. Productivity is suffering.",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.10,
			"min_turn": 8,
			"repeatable": true,
			"options": [
				{
					"id": "mediate_personally",
					"text": "Mediate Personally (costs 1 AP)",
					"costs": {"action_points": 1},
					"effects": {"reputation": 3, "doom": -1},
					"message": "Successful mediation! Team cohesion improved (+3 reputation, -1 doom)"
				},
				{
					"id": "hire_mediator",
					"text": "Hire Professional Mediator ($15k)",
					"costs": {"money": 15000},
					"effects": {"reputation": 5},
					"message": "Professional mediator resolved the conflict (+5 reputation)"
				},
				{
					"id": "ignore_conflict",
					"text": "Let Them Work It Out",
					"effects": {"reputation": -3, "doom": 2},
					"message": "Conflict festered and spread (-3 reputation, +2 doom)"
				}
			]
		},
		{
			"id": "harassment_complaint",
			"name": "Workplace Complaint Filed",
			"description": "A formal complaint has been filed. This requires immediate and careful attention.",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.06,
			"min_turn": 10,
			"repeatable": true,
			"options": [
				{
					"id": "thorough_investigation",
					"text": "Full Investigation (costs 2 AP, $25k)",
					"costs": {"action_points": 2, "money": 25000},
					"effects": {"reputation": 8},
					"message": "Thorough investigation completed. Appropriate action taken (+8 reputation)"
				},
				{
					"id": "quick_resolution",
					"text": "Quick Resolution ($40k)",
					"costs": {"money": 40000},
					"effects": {"reputation": 3},
					"message": "Resolved quickly with settlement (+3 reputation)"
				},
				{
					"id": "minimize_issue",
					"text": "Minimize the Issue",
					"effects": {"reputation": -10, "doom": 3},
					"message": "Poor handling damaged lab culture (-10 reputation, +3 doom)"
				}
			]
		},
		{
			"id": "salary_dispute",
			"name": "Pay Equity Concerns",
			"description": "Several employees have raised concerns about pay disparities. They're comparing notes.",
			"type": "popup",
			"trigger_type": "threshold",
			"trigger_condition": "safety_researchers >= 3",
			"repeatable": true,
			"options": [
				{
					"id": "salary_audit",
					"text": "Conduct Salary Audit & Adjust ($60k)",
					"costs": {"money": 60000},
					"effects": {"reputation": 10, "doom": -2},
					"message": "Salary audit complete, adjustments made (+10 reputation, -2 doom)"
				},
				{
					"id": "explain_structure",
					"text": "Explain Compensation Structure (costs 1 AP)",
					"costs": {"action_points": 1},
					"effects": {"reputation": 2},
					"message": "Transparent discussion helped (+2 reputation)"
				},
				{
					"id": "ignore_concerns",
					"text": "Dismiss Concerns",
					"effects": {"reputation": -5, "doom": 1},
					"message": "Ignored concerns bred resentment (-5 reputation, +1 doom)"
				}
			]
		},
		{
			"id": "mental_health_crisis",
			"name": "Employee Mental Health Crisis",
			"description": "A valued researcher is struggling with severe stress and anxiety. They've requested time off.",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.08,
			"min_turn": 12,
			"repeatable": true,
			"options": [
				{
					"id": "full_support",
					"text": "Full Support + Paid Leave ($30k)",
					"costs": {"money": 30000},
					"effects": {"reputation": 8, "doom": -3},
					"message": "Provided full support. Team sees you care (+8 reputation, -3 doom)"
				},
				{
					"id": "partial_leave",
					"text": "Unpaid Leave Approved",
					"costs": {},
					"effects": {"reputation": 3},
					"message": "Leave approved, but no pay (+3 reputation)"
				},
				{
					"id": "deny_leave",
					"text": "Deny Request (Too Busy)",
					"effects": {"reputation": -8, "doom": 5},
					"message": "Denial caused serious damage to culture (-8 reputation, +5 doom)"
				}
			]
		},
		{
			"id": "office_theft",
			"name": "Equipment Gone Missing",
			"description": "Expensive equipment has disappeared from the lab. Someone may be stealing.",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.05,
			"min_turn": 15,
			"repeatable": true,
			"options": [
				{
					"id": "security_upgrade",
					"text": "Install Security System ($35k)",
					"costs": {"money": 35000},
					"effects": {"reputation": 5, "compute": 10},
					"message": "Security installed, recovered some equipment (+5 reputation, +10 compute)"
				},
				{
					"id": "team_meeting",
					"text": "Address at Team Meeting (costs 1 AP)",
					"costs": {"action_points": 1},
					"effects": {"reputation": 2},
					"message": "Open discussion restored some trust (+2 reputation)"
				},
				{
					"id": "ignore_theft",
					"text": "Write It Off",
					"effects": {"compute": -15, "reputation": -3},
					"message": "Theft continued (-15 compute, -3 reputation)"
				}
			]
		},
		{
			"id": "policy_violation",
			"name": "Policy Violation Discovered",
			"description": "A senior researcher has been caught violating company policy. Others are watching how you respond.",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.07,
			"min_turn": 10,
			"repeatable": true,
			"options": [
				{
					"id": "formal_discipline",
					"text": "Formal Disciplinary Action (costs 1 AP)",
					"costs": {"action_points": 1},
					"effects": {"reputation": 5},
					"message": "Fair process maintained trust (+5 reputation)"
				},
				{
					"id": "verbal_warning",
					"text": "Verbal Warning Only",
					"effects": {"reputation": -2},
					"message": "Light response noted by others (-2 reputation)"
				},
				{
					"id": "sweep_under_rug",
					"text": "Ignore It (They're Valuable)",
					"effects": {"reputation": -6, "doom": 2},
					"message": "Favoritism damaged morale (-6 reputation, +2 doom)"
				}
			]
		},
		# WHISTLEBLOWING & LEAKS (issue #191)
		{
			"id": "research_leak",
			"name": "Research Leaked!",
			"description": "Someone leaked your unpublished safety research to a competitor lab. They're using it to accelerate their capabilities work.",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.08,
			"min_turn": 12,
			"repeatable": true,
			"options": [
				{
					"id": "investigate_leak",
					"text": "Full Investigation (costs 2 AP, $30k)",
					"costs": {"action_points": 2, "money": 30000},
					"effects": {"doom": 3, "reputation": 5},
					"message": "Found and addressed the leak, but damage done (+3 doom, +5 reputation)"
				},
				{
					"id": "publish_immediately",
					"text": "Publish Research Publicly",
					"costs": {"action_points": 1},
					"effects": {"papers": 1, "reputation": 8, "doom": 5},
					"message": "Published to get credit, but all labs benefit (+1 paper, +8 rep, +5 doom)"
				},
				{
					"id": "accept_leak",
					"text": "Accept the Loss",
					"effects": {"doom": 8, "reputation": -3},
					"message": "Competitor gained significant advantage (+8 doom, -3 reputation)"
				}
			]
		},
		{
			"id": "competitor_intel",
			"name": "Competitor Intelligence",
			"description": "A contact offers information about a rival lab's dangerous capabilities research. How did they get it?",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.07,
			"min_turn": 15,
			"repeatable": true,
			"options": [
				{
					"id": "use_intel",
					"text": "Use the Information ($20k)",
					"costs": {"money": 20000},
					"effects": {"doom": -5, "reputation": -8},
					"message": "Used intel to counter their work (-5 doom, -8 reputation for ethics)"
				},
				{
					"id": "report_intel",
					"text": "Report to Authorities",
					"costs": {"action_points": 1},
					"effects": {"reputation": 10, "doom": -3},
					"message": "Reported concerns, triggering investigation (+10 reputation, -3 doom)"
				},
				{
					"id": "refuse_intel",
					"text": "Refuse and Walk Away",
					"effects": {"reputation": 3},
					"message": "Maintained ethical standards (+3 reputation)"
				}
			]
		},
		{
			"id": "whistleblower_approach",
			"name": "Whistleblower Approaches",
			"description": "A researcher from a competitor lab wants to expose their unsafe practices. They're asking for your help.",
			"type": "popup",
			"trigger_type": "threshold",
			"trigger_condition": "reputation >= 60",
			"repeatable": true,
			"options": [
				{
					"id": "full_support",
					"text": "Fully Support & Publicize (costs 2 AP, $50k)",
					"costs": {"action_points": 2, "money": 50000},
					"effects": {"doom": -15, "reputation": 20},
					"message": "Major exposé! Industry-wide safety improvements (-15 doom, +20 reputation)"
				},
				{
					"id": "anonymous_support",
					"text": "Anonymous Support ($25k)",
					"costs": {"money": 25000},
					"effects": {"doom": -8, "reputation": 5},
					"message": "Quietly helped expose dangers (-8 doom, +5 reputation)"
				},
				{
					"id": "hire_whistleblower",
					"text": "Hire Them Instead ($60k, 1 AP)",
					"costs": {"money": 60000, "action_points": 1},
					"effects": {"safety_researchers": 1, "doom": -3},
					"message": "Hired the concerned researcher (+1 safety researcher, -3 doom)"
				},
				{
					"id": "decline_involvement",
					"text": "Stay Out of It",
					"effects": {"reputation": -5},
					"message": "Refused to help, whistleblower went elsewhere (-5 reputation)"
				}
			]
		},
		{
			"id": "employee_whistleblower",
			"name": "Internal Concerns Raised",
			"description": "One of your researchers wants to go public about concerns with your lab's direction. Handle carefully.",
			"type": "popup",
			"trigger_type": "threshold",
			"trigger_condition": "capability_researchers >= 2",
			"repeatable": true,
			"options": [
				{
					"id": "address_concerns",
					"text": "Open Forum Discussion (costs 1 AP)",
					"costs": {"action_points": 1},
					"effects": {"reputation": 8, "doom": -2},
					"message": "Transparent discussion improved practices (+8 reputation, -2 doom)"
				},
				{
					"id": "private_resolution",
					"text": "Private Resolution ($30k)",
					"costs": {"money": 30000},
					"effects": {"reputation": 3},
					"message": "Quietly addressed concerns (+3 reputation)"
				},
				{
					"id": "suppress_concerns",
					"text": "Suppress the Issue",
					"effects": {"reputation": -15, "doom": 5},
					"message": "Suppression backfired badly (-15 reputation, +5 doom)"
				}
			]
		},
		{
			"id": "plant_source_opportunity",
			"name": "Intelligence Opportunity",
			"description": "You could place someone inside a competitor lab to monitor their safety practices. Ethically questionable but potentially valuable.",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.05,
			"min_turn": 20,
			"repeatable": false,
			"options": [
				{
					"id": "plant_source",
					"text": "Plant a Source ($80k, 1 AP)",
					"costs": {"money": 80000, "action_points": 1},
					"effects": {"doom": -10, "reputation": -15},
					"message": "Source planted, early warnings enabled (-10 doom, -15 reputation if discovered)"
				},
				{
					"id": "legitimate_partnership",
					"text": "Propose Legitimate Partnership",
					"costs": {"action_points": 1, "money": 40000},
					"effects": {"doom": -5, "reputation": 8},
					"message": "Established safety information sharing (-5 doom, +8 reputation)"
				},
				{
					"id": "decline_espionage",
					"text": "Decline (Too Risky)",
					"effects": {"reputation": 2},
					"message": "Maintained ethical boundaries (+2 reputation)"
				}
			]
		},
		# REAL-WORLD INSPIRED EVENTS
		{
			"id": "competitor_password_breach",
			"name": "Competitor Security Breach",
			"description": "A rival lab's AI system was secured with '1234' as the password. Millions of training data records are now exposed. The industry is watching how labs respond.",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.06,
			"min_turn": 10,
			"repeatable": false,
			"options": [
				{
					"id": "public_security_audit",
					"text": "Announce Public Security Audit ($40k, 1 AP)",
					"costs": {"money": 40000, "action_points": 1},
					"effects": {"reputation": 15, "doom": -3},
					"message": "Proactive security audit boosted confidence (+15 reputation, -3 doom)"
				},
				{
					"id": "offer_help",
					"text": "Offer to Help Affected Users ($25k)",
					"costs": {"money": 25000},
					"effects": {"reputation": 10},
					"message": "Goodwill gesture appreciated (+10 reputation)"
				},
				{
					"id": "stay_silent",
					"text": "Stay Silent",
					"effects": {"reputation": -5, "doom": 2},
					"message": "Silence perceived as indifference (-5 reputation, +2 doom)"
				},
				{
					"id": "exploit_weakness",
					"text": "Exploit Their Weakness (Poach Clients)",
					"costs": {"action_points": 1},
					"effects": {"money": 50000, "reputation": -10, "doom": 3},
					"message": "Gained clients but damaged reputation (+$50k, -10 rep, +3 doom)"
				}
			]
		},
		{
			"id": "your_security_audit",
			"name": "Security Vulnerability Found",
			"description": "An internal audit discovered your systems have weak password policies. If exploited, research data could be compromised.",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.07,
			"min_turn": 8,
			"repeatable": true,
			"options": [
				{
					"id": "full_security_overhaul",
					"text": "Full Security Overhaul ($60k, 2 AP)",
					"costs": {"money": 60000, "action_points": 2},
					"effects": {"reputation": 8, "doom": -5},
					"message": "Comprehensive security upgrade complete (+8 reputation, -5 doom)"
				},
				{
					"id": "patch_critical",
					"text": "Patch Critical Issues ($20k)",
					"costs": {"money": 20000},
					"effects": {"reputation": 3, "doom": -2},
					"message": "Critical vulnerabilities patched (+3 reputation, -2 doom)"
				},
				{
					"id": "defer_security",
					"text": "Defer (We're Too Busy)",
					"effects": {"doom": 5},
					"message": "Security risks remain (+5 doom)"
				}
			]
		},
		# COMPETITOR POACHING (issue #197)
		{
			"id": "researcher_poached",
			"name": "Competitor Poaching Attempt",
			"description": "A competitor is trying to recruit one of your top researchers with a lucrative offer.",
			"type": "popup",
			"trigger_type": "threshold",
			"trigger_condition": "researchers >= 2",
			"probability": 0.04,  # ~4% per turn when conditions met, <1/year
			"min_turn": 20,
			"repeatable": true,
			"options": [
				{
					"id": "match_offer",
					"text": "Match Their Offer ($50k)",
					"costs": {"money": 50000},
					"effects": {"reputation": 2},
					"message": "Matched offer, researcher stays (+2 reputation for loyalty)"
				},
				{
					"id": "counter_promotion",
					"text": "Counter with Promotion (1 AP, $30k)",
					"costs": {"action_points": 1, "money": 30000},
					"effects": {"reputation": 3},
					"message": "Promoted researcher to senior role (+3 reputation)"
				},
				{
					"id": "let_them_go",
					"text": "Let Them Leave",
					"effects": {"lose_researcher": 1, "doom": 3},
					"message": "Researcher departed for competitor (+3 doom, lost valuable team member)"
				}
			]
		}
	]

static func check_triggered_events(state: GameState, rng: RandomNumberGenerator) -> Array[Dictionary]:
	"""Check all events and return those that should trigger this turn"""
	var to_trigger: Array[Dictionary] = []

	for event in get_all_events():
		if should_trigger(event, state, rng):
			to_trigger.append(event)
			if not event.get("repeatable", false):
				triggered_events.append(event["id"])

	return to_trigger

static func should_trigger(event: Dictionary, state: GameState, rng: RandomNumberGenerator) -> bool:
	"""Check if event should trigger"""
	var event_id = event.get("id", "")

	# Don't trigger if already triggered (unless repeatable)
	if event_id in triggered_events and not event.get("repeatable", false):
		return false

	var trigger_type = event.get("trigger_type", "")

	match trigger_type:
		"turn_exact":
			# Exact turn trigger (e.g., cat on turn 7)
			return state.turn == event.get("trigger_turn", -1)

		"turn_and_resource":
			# Specific turn + condition
			if state.turn != event.get("trigger_turn", -1):
				return false
			return evaluate_condition(event.get("trigger_condition", "false"), state)

		"threshold":
			# Resource threshold condition
			return evaluate_condition(event.get("trigger_condition", "false"), state)

		"random":
			# Random chance after min turn
			if state.turn < event.get("min_turn", 0):
				return false
			var event_roll = rng.randf()

			# Record RNG outcome for verification
			VerificationTracker.record_rng_outcome("event_%s" % event_id, event_roll, state.turn)

			return event_roll < event.get("probability", 0.1)

	return false

static func evaluate_condition(condition: String, state: GameState) -> bool:
	"""Evaluate condition string safely"""
	# Simple parser for conditions like "money < 50000"
	# Format: "resource operator value"

	if condition == "false":
		return false
	if condition == "true":
		return true

	var parts = condition.split(" ")
	if parts.size() < 3:
		return false

	var resource_name = parts[0]
	var operator = parts[1]
	var value_str = parts[2]

	# Get resource value from state
	var resource_value = 0.0
	match resource_name:
		"money":
			resource_value = state.money
		"compute":
			resource_value = state.compute
		"research":
			resource_value = state.research
		"papers":
			resource_value = state.papers
		"reputation":
			resource_value = state.reputation
		"doom":
			resource_value = state.doom
		"action_points":
			resource_value = state.action_points
		"safety_researchers":
			resource_value = state.safety_researchers
		"capability_researchers":
			resource_value = state.capability_researchers
		"compute_engineers":
			resource_value = state.compute_engineers
		"managers":
			resource_value = state.managers
		"researchers":
			# Individual researcher count (new system)
			resource_value = state.researchers.size()
		"total_staff":
			# Total staff including managers
			resource_value = state.get_total_staff()
		_:
			return false

	var threshold = float(value_str)

	# Evaluate operator
	match operator:
		"<":
			return resource_value < threshold
		">":
			return resource_value > threshold
		"<=":
			return resource_value <= threshold
		">=":
			return resource_value >= threshold
		"==":
			return abs(resource_value - threshold) < 0.01
		"!=":
			return abs(resource_value - threshold) >= 0.01

	return false

static func execute_event_choice(event: Dictionary, choice_id: String, state: GameState) -> Dictionary:
	"""Execute player's event choice and return result"""
	var options = event.get("options", [])

	# Find chosen option
	var chosen_option: Dictionary = {}
	for opt in options:
		if opt.get("id", "") == choice_id:
			chosen_option = opt
			break

	if chosen_option.is_empty():
		return {"success": false, "message": "Unknown choice"}

	# Check costs
	var costs = chosen_option.get("costs", {})
	if not state.can_afford(costs):
		return {"success": false, "message": "Cannot afford this choice"}

	# Pay costs
	state.spend_resources(costs)

	# Apply effects
	var effects = chosen_option.get("effects", {})
	for key in effects.keys():
		var value = effects[key]

		# Map effect keys to state properties
		match key:
			"money":
				state.money += value
			"compute":
				state.compute += value
			"research":
				state.research += value
			"papers":
				state.papers += value
			"reputation":
				state.reputation += value
			"doom":
				state.doom += value
			"safety_researchers":
				state.safety_researchers += value
			"capability_researchers":
				state.capability_researchers += value
			"compute_engineers":
				state.compute_engineers += value
			"has_cat":
				state.has_cat = (value > 0)
			"lose_researcher":
				# Remove a random researcher (poaching)
				if state.researchers.size() > 0:
					var idx = state.rng.randi() % state.researchers.size()

					# Record RNG outcome for verification
					VerificationTracker.record_rng_outcome("poach_researcher_select", float(idx), state.turn)

					var researcher = state.researchers[idx]
					state.remove_researcher(researcher)

	var message = chosen_option.get("message", "Event resolved")
	return {"success": true, "message": message}

static func reset_triggered_events():
	"""Clear triggered events (for new game)"""
	triggered_events.clear()

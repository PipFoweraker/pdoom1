from typing import List, Optional, TypedDict


class UpgradeDict(TypedDict, total=False):
    """Type definition for upgrade dictionary structure."""
    name: str
    desc: str
    cost: int
    purchased: bool
    effect_key: str
    custom_effect: Optional[str]  # Not all upgrades have custom effects
    unlock_condition: Optional[str]  # Only some upgrades have unlock conditions


UPGRADES: List[UpgradeDict] = [
    {
        "name": "Upgrade Computer System",
        "desc": "Boosts research effectiveness (+1 research per action)",
        "cost": 200,
        "purchased": False,
        "effect_key": "better_computers"
    },
    {
        "name": "Buy Comfy Office Chairs",
        "desc": "Staff morale up (less likely to lose staff on low funds)",
        "cost": 120,
        "purchased": False,
        "effect_key": "comfy_chairs"
    },
    {
        "name": "Secure Cloud Provider",
        "desc": "Reduces doom spikes from lab breakthroughs",
        "cost": 160,
        "purchased": False,
        "effect_key": "secure_cloud"
    },
    {
        "name": "Accounting Software",
        "desc": "Enables cash flow tracking, prevents board oversight ($500)",
        "cost": 500,
        "purchased": False,
        "effect_key": "accounting_software",
        "custom_effect": "buy_accounting_software"  # Special handling for this upgrade
    },
    {
        "name": "Compact Activity Display",
        "desc": "Minimize activity log to save screen space ($150)",
        "cost": 150,
        "purchased": False,
        "effect_key": "compact_activity_display",
        "custom_effect": "buy_compact_activity_display"  # Special handling for this upgrade
    },
    {
        "name": "High-Performance Computing Cluster",
        "desc": "Advanced compute infrastructure (+20 compute, research effectiveness +25%)",
        "cost": 800,
        "purchased": False,
        "effect_key": "hpc_cluster"
    },
    {
        "name": "Research Automation Suite",
        "desc": "AI-assisted research tools (research actions more effective with compute)",
        "cost": 600,
        "purchased": False,
        "effect_key": "research_automation"
    },
    {
        "name": "Magical Orb of Seeing",
        "desc": "Advanced surveillance apparatus revealing laptop and mobile contents of all humans connected to the Internet",
        "cost": 371640000000,  # 371.64 billion USD placeholder
        "purchased": False,
        "effect_key": "magical_orb_seeing",
        "unlock_condition": "palandir_discovered",  # Only shows when Palandir is discovered
        "custom_effect": "buy_magical_orb_seeing"  # Special handling for this upgrade
    }
]
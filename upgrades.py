UPGRADES = [
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
    }
]
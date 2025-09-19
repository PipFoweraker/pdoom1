"""
Dialog system utilities extracted from game_state.py

This module contains utilities for managing game dialog systems including
hiring, fundraising, research, and intelligence dialogs. These are pure
dialog state management functions that handle user interaction flows.
"""

from typing import Dict, Any, List, Tuple, Optional


class DialogManager:
    """Manages dialog state and options for various game interactions."""
    
    @staticmethod
    def create_hiring_dialog_state(available_subtypes: List[Dict[str, Any]], 
                                 complexity_level: Dict[str, Any]) -> Dict[str, Any]:
        """Create hiring dialog state with available employee subtypes."""
        return {
            "available_subtypes": available_subtypes,
            "complexity_level": complexity_level,
            "title": f"Hire Employee - {complexity_level['description']}",
            "description": complexity_level['complexity_note']
        }
    
    @staticmethod
    def create_fundraising_dialog_state(available_options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create fundraising dialog state with available funding options."""
        return {
            "available_options": available_options,
            "title": "Fundraising Strategy Selection",
            "description": "Choose your approach to raising capital. Each option has different risk/reward profiles."
        }
    
    @staticmethod
    def create_research_dialog_state(available_options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create research dialog state with available research options."""
        return {
            "title": "Research Strategy Selection",
            "description": "Choose your research approach. Each type has different costs, benefits, and risks.",
            "available_options": available_options
        }
    
    @staticmethod
    def create_intelligence_dialog_state(intelligence_options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create intelligence dialog state with available intelligence options."""
        return {
            "title": "Intelligence Gathering",
            "description": "Choose your intelligence approach. Different methods reveal different information.",
            "available_options": intelligence_options
        }


class FundraisingDialogBuilder:
    """Builds fundraising dialog options based on game state."""
    
    @staticmethod
    def get_small_fundraising_option(economic_config) -> Dict[str, Any]:
        """Get small fundraising option (always available)."""
        small_range = economic_config.get_fundraising_amount_range("small")
        return {
            "id": "fundraise_small",
            "name": "Fundraise Small",
            "description": f"Conservative funding approach - ${small_range[0]//1000}-{small_range[1]//1000}k range, minimal reputation risk",
            "min_amount": small_range[0] // 1000,
            "max_amount": small_range[1] // 1000,
            "reputation_risk": 0.1,  # 10% chance of -1 reputation
            "requirements": "Always available",
            "cost": 0,
            "ap_cost": 1,
            "affordable": True,  # Always affordable since no cost
            "available": True
        }
    
    @staticmethod
    def get_big_fundraising_option(economic_config, reputation: int) -> Dict[str, Any]:
        """Get big fundraising option (requires reputation)."""
        big_available = reputation >= 10
        big_range = economic_config.get_fundraising_amount_range("big")
        return {
            "id": "fundraise_big", 
            "name": "Fundraise Big",
            "description": f"Aggressive funding round - ${big_range[0]//1000}-{big_range[1]//1000}k range, higher stakes and reputation requirements",
            "min_amount": big_range[0] // 1000,
            "max_amount": big_range[1] // 1000,
            "reputation_risk": 0.3,  # 30% chance of -2 reputation
            "requirements": "Requires 10+ reputation",
            "cost": 0,
            "ap_cost": 1,
            "affordable": True,
            "available": big_available
        }
    
    @staticmethod
    def get_borrow_money_option(reputation: int) -> Dict[str, Any]:
        """Get borrow money option (requires creditworthiness)."""
        borrow_available = reputation >= 5
        return {
            "id": "borrow_money",
            "name": "Borrow Money", 
            "description": "Immediate $50-80k via debt - creates future payment obligations",
            "min_amount": 50,
            "max_amount": 80,
            "reputation_risk": 0.0,  # No reputation risk, but creates debt
            "requirements": "Requires 5+ reputation for creditworthiness",
            "cost": 0,
            "ap_cost": 1,
            "affordable": True,
            "available": borrow_available,
            "creates_debt": True
        }
    
    @staticmethod
    def get_alternative_funding_option(advanced_funding_unlocked: bool) -> Dict[str, Any]:
        """Get alternative funding option (unlocked after milestones)."""
        return {
            "id": "alternative_funding",
            "name": "Alternative Funding",
            "description": "Grants, partnerships, revenue - $40-100k from non-traditional sources",
            "min_amount": 40,
            "max_amount": 100,
            "reputation_risk": 0.15,  # 15% chance of -1 reputation
            "requirements": "Requires advanced funding milestone",
            "cost": 0,
            "ap_cost": 1,
            "affordable": True,
            "available": advanced_funding_unlocked,
            "special_effects": True
        }
    
    @staticmethod
    def build_fundraising_options(economic_config, reputation: int, 
                                advanced_funding_unlocked: bool = False) -> List[Dict[str, Any]]:
        """Build complete list of fundraising options based on game state."""
        options = []
        
        # Always available options
        options.append(FundraisingDialogBuilder.get_small_fundraising_option(economic_config))
        options.append(FundraisingDialogBuilder.get_big_fundraising_option(economic_config, reputation))
        options.append(FundraisingDialogBuilder.get_borrow_money_option(reputation))
        options.append(FundraisingDialogBuilder.get_alternative_funding_option(advanced_funding_unlocked))
        
        return options


class ResearchDialogBuilder:
    """Builds research dialog options based on game state."""
    
    @staticmethod
    def get_safety_research_option(money: int) -> Dict[str, Any]:
        """Get safety research option."""
        safety_cost = 40
        safety_affordable = money >= safety_cost
        return {
            "id": "safety_research", 
            "name": "Safety Research",
            "description": "Traditional AI safety research - interpretability, alignment, robustness",
            "min_doom_reduction": 2,
            "max_doom_reduction": 6,
            "reputation_gain": 2,
            "cost": safety_cost,
            "ap_cost": 1,
            "available": True,
            "affordable": safety_affordable,
            "requirements": f"Cost: ${safety_cost}k" if safety_affordable else f"Need ${safety_cost}k (have ${money}k)",
            "technical_debt_risk": "Low"
        }
    
    @staticmethod
    def get_governance_research_option(money: int) -> Dict[str, Any]:
        """Get governance research option."""
        governance_cost = 45
        governance_affordable = money >= governance_cost
        return {
            "id": "governance_research",
            "name": "Governance Research", 
            "description": "Policy research, international coordination, regulatory frameworks",
            "min_doom_reduction": 2,
            "max_doom_reduction": 5,
            "reputation_gain": 3,
            "cost": governance_cost,
            "ap_cost": 1,
            "available": True,
            "affordable": governance_affordable,
            "requirements": f"Cost: ${governance_cost}k" if governance_affordable else f"Need ${governance_cost}k (have ${money}k)",
            "technical_debt_risk": "Low"
        }
    
    @staticmethod
    def get_capabilities_research_option(money: int, reputation: int) -> Dict[str, Any]:
        """Get capabilities research option (requires reputation)."""
        capabilities_cost = 60
        capabilities_available = reputation >= 15
        capabilities_affordable = money >= capabilities_cost
        return {
            "id": "capabilities_research",
            "name": "Capabilities Research",
            "description": "Advanced AI capabilities research - scaling, efficiency, new architectures",
            "min_doom_reduction": -2,  # May increase doom
            "max_doom_reduction": 1,
            "reputation_gain": 4,
            "cost": capabilities_cost,
            "ap_cost": 1,
            "available": capabilities_available,
            "affordable": capabilities_affordable and capabilities_available,
            "requirements": f"Cost: ${capabilities_cost}k, 15+ reputation" if capabilities_available else "Requires 15+ reputation",
            "technical_debt_risk": "Medium",
            "warning": "May increase existential risk"
        }
    
    @staticmethod
    def build_research_options(money: int, reputation: int) -> List[Dict[str, Any]]:
        """Build complete list of research options based on game state."""
        options = []
        
        # Core research options
        options.append(ResearchDialogBuilder.get_safety_research_option(money))
        options.append(ResearchDialogBuilder.get_governance_research_option(money))
        options.append(ResearchDialogBuilder.get_capabilities_research_option(money, reputation))
        
        return options


class DialogValidator:
    """Validates dialog interactions and selections."""
    
    @staticmethod
    def validate_hiring_selection(dialog_state: Optional[Dict[str, Any]], 
                                subtype_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Validate employee hiring selection."""
        if not dialog_state:
            return False, "No hiring dialog active.", None
        
        # Find the selected subtype
        selected_subtype = None
        for subtype_info in dialog_state["available_subtypes"]:
            if subtype_info["id"] == subtype_id:
                selected_subtype = subtype_info
                break
        
        if not selected_subtype:
            return False, f"Invalid employee subtype: {subtype_id}", None
        
        if not selected_subtype["affordable"]:
            subtype_data = selected_subtype["data"]
            return False, f"Cannot afford {subtype_data['name']} - need ${subtype_data['cost']} and {subtype_data['ap_cost']} AP", None
        
        return True, "Selection valid", selected_subtype
    
    @staticmethod
    def validate_fundraising_selection(dialog_state: Optional[Dict[str, Any]], 
                                     option_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Validate fundraising option selection."""
        if not dialog_state:
            return False, "No fundraising dialog active.", None
        
        # Find the selected option
        selected_option = None
        for option in dialog_state["available_options"]:
            if option["id"] == option_id:
                selected_option = option
                break
        
        if not selected_option:
            return False, f"Invalid fundraising option: {option_id}", None
        
        if not selected_option.get("affordable", True):
            return False, f"Cannot afford {selected_option['name']}", None
        
        if not selected_option.get("available", False):
            return False, f"{selected_option['name']} is not available: {selected_option.get('requirements', 'Unknown requirements')}", None
        
        return True, "Selection valid", selected_option
    
    @staticmethod
    def validate_research_selection(dialog_state: Optional[Dict[str, Any]], 
                                  option_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Validate research option selection."""
        if not dialog_state:
            return False, "No research dialog active.", None
        
        # Find the selected option
        selected_option = None
        for option in dialog_state["available_options"]:
            if option["id"] == option_id:
                selected_option = option
                break
        
        if not selected_option:
            return False, f"Invalid research option: {option_id}", None
        
        if not selected_option.get("affordable", True):
            return False, f"Cannot afford {selected_option['name']} - {selected_option.get('requirements', 'insufficient resources')}", None
        
        if not selected_option.get("available", False):
            return False, f"{selected_option['name']} is not available: {selected_option.get('requirements', 'Unknown requirements')}", None
        
        return True, "Selection valid", selected_option


def create_dialog_help_context(dialog_type: str, complexity_level: Optional[str] = None) -> Dict[str, str]:
    """Create help context for dialog systems."""
    help_contexts = {
        "hiring": {
            "title": "Employee Hiring Help",
            "basic_description": "Hire employees to expand your team capabilities.",
            "intermediate_description": "Choose employee specializations to match your research needs.",
            "advanced_description": "Balance specialist skills, management overhead, and team synergy."
        },
        "fundraising": {
            "title": "Fundraising Help", 
            "description": "Raise capital through different funding approaches with varying risk/reward profiles."
        },
        "research": {
            "title": "Research Strategy Help",
            "description": "Choose research approaches that balance progress, risk, and reputation."
        },
        "intelligence": {
            "title": "Intelligence Gathering Help",
            "description": "Gather information about competitors and market conditions."
        }
    }
    
    base_context = help_contexts.get(dialog_type, {
        "title": "Dialog Help",
        "description": "Select from available options."
    })
    
    # Add complexity-specific context for hiring
    if dialog_type == "hiring" and complexity_level:
        if complexity_level in ["basic", "intermediate", "advanced"]:
            base_context["description"] = base_context[f"{complexity_level}_description"]
    
    return base_context

#!/usr/bin/env python3
"""
Technical Failure Cascades Demonstration Script

This script demonstrates the key features of the Technical Failure Cascades system
implemented for Issue #193. It shows how failures can cascade, how prevention
systems work, and the difference between transparency and cover-up approaches.
"""

from src.services.deterministic_rng import get_rng
from src.core.game_state import GameState
from src.features.technical_failures import FailureType

def demonstrate_cascade_system():
    """Demonstrate the technical failure cascades system."""
    print("=== P(Doom) Technical Failure Cascades Demonstration ===")
    print()
    
    # Initialize game state
    get_rng().seed(42)  # Deterministic for demo
    gs = GameState('cascade-demo')
    
    # Set up a mid-game scenario
    gs.money = 500
    gs.staff = 12
    gs.reputation = 15
    gs.doom = 45
    gs.turn = 25
    gs.technical_debt.accumulated_debt = 12  # Moderate technical debt
    
    print(f"Initial State:")
    print(f"  Turn: {gs.turn}")
    print(f"  Money: ${gs.money}k")
    print(f"  Staff: {gs.staff}")
    print(f"  Reputation: {gs.reputation}")
    print(f"  Technical Debt: {gs.technical_debt.accumulated_debt}")
    print(f"  Doom: {gs.doom}")
    print()
    
    cascade_system = gs.technical_failures
    
    print("=== 1. Prevention System Investment ===")
    print("Investing in cascade prevention capabilities...")
    
    # Upgrade incident response
    success = cascade_system.upgrade_incident_response(30)
    print(f"Incident Response Training: {'Success' if success else 'Failed'} (Level {cascade_system.incident_response_level})")
    
    # Upgrade monitoring
    success = cascade_system.upgrade_monitoring_systems(40)
    print(f"Monitoring Systems: {'Success' if success else 'Failed'} (Level {cascade_system.monitoring_systems})")
    
    # Upgrade communication
    success = cascade_system.upgrade_communication_protocols(25)
    print(f"Communication Protocols: {'Success' if success else 'Failed'} (Level {cascade_system.communication_protocols})")
    
    print(f"Remaining money: ${gs.money}k")
    print()
    
    print("=== 2. Near-Miss Detection ===")
    # Simulate a near-miss
    failure = cascade_system._create_failure_event(FailureType.SYSTEM_CRASH, 4)
    cascade_system._trigger_near_miss(failure)
    
    print("Recent messages:")
    for msg in gs.messages[-3:]:
        print(f"  {msg}")
    print()
    
    print(f"Near-miss count: {cascade_system.near_miss_count}")
    print(f"Lessons learned: {dict(cascade_system.lessons_learned)}")
    print()
    
    print("=== 3. Actual Failure Cascade ===")
    # Clear messages for cleaner demo
    gs.messages = []
    
    # Create a more severe failure that will cascade
    failure = cascade_system._create_failure_event(FailureType.SECURITY_BREACH, 7)
    failure.cascade_chance = 1.0  # Force cascade for demo
    
    print(f"Triggering {failure.failure_type.value} (severity {failure.severity})...")
    print(f"Description: {failure.description}")
    
    # Apply the failure
    for resource, amount in failure.immediate_impact.items():
        if hasattr(gs, resource):
            old_value = getattr(gs, resource)
            gs._add(resource, amount)
            new_value = getattr(gs, resource)
            print(f"  {resource}: {old_value} -> {new_value} ({amount:+})")
    
    # Start cascade
    cascade = cascade_system._start_cascade(failure)
    
    print("\nRecent messages:")
    for msg in gs.messages[-5:]:
        print(f"  {msg}")
    print()
    
    print("=== 4. Cascade Progression ===")
    # Simulate cascade progression over multiple turns
    for turn in range(3):
        print(f"\nCascade Turn {turn + 1}:")
        if cascade_system.active_cascades:
            cascade = cascade_system.active_cascades[0]
            print(f"  Contained: {cascade.is_contained}")
            print(f"  Subsequent failures: {len(cascade.subsequent_failures)}")
            
            # Update cascade
            gs.messages = []  # Clear for clean output
            cascade_system._update_cascade(cascade)
            
            if gs.messages:
                print("  Messages:")
                for msg in gs.messages:
                    print(f"    {msg}")
            
            if cascade not in cascade_system.active_cascades:
                print("  Cascade resolved!")
                break
        else:
            print("  No active cascades")
            break
    
    print()
    
    print("=== 5. Transparency vs Cover-up Demonstration ===")
    # Reset for transparency demo
    cascade_system.transparency_reputation = 0.0
    cascade_system.cover_up_debt = 0
    
    print("\nTransparency Approach:")
    print("  Immediate reputation cost, long-term trust building")
    print("  Maximum learning from failures")
    
    # Simulate transparency response
    initial_rep = gs.reputation
    gs._add('reputation', -3)  # Immediate cost
    cascade_system.transparency_reputation += 0.5  # Long-term benefit
    
    print(f"  Reputation: {initial_rep} -> {gs.reputation} (-3)")
    print(f"  Transparency reputation: +0.5 (builds over time)")
    
    print("\nCover-up Approach:")
    print("  No immediate reputation loss, accumulates future risk")
    print("  Reduced learning, increased future failure chances")
    
    # Simulate cover-up response
    gs._add('money', -30)  # Cover-up costs
    cascade_system.cover_up_debt += 5  # Future risk
    
    print(f"  Money: -$30k (cover-up costs)")
    print(f"  Cover-up debt: +5 (increases future failure risk)")
    print(f"  Future failure risk modifier: {cascade_system.get_cover_up_risk_modifier():.1f}x")
    print()
    
    print("=== 6. System Summary ===")
    summary = cascade_system.get_failure_cascade_summary()
    print(f"Total failures experienced: {summary['total_failures']}")
    print(f"Near-misses detected: {summary['near_misses']}")
    print(f"Active cascades: {summary['active_cascades']}")
    print(f"Incident response level: {summary['incident_response_level']}/5")
    print(f"Monitoring systems level: {summary['monitoring_systems']}/5")
    print(f"Communication protocols level: {summary['communication_protocols']}/5")
    print(f"Cover-up debt: {summary['cover_up_debt']}")
    print(f"Transparency reputation: {summary['transparency_reputation']:.1f}")
    print()
    
    print("=== Prevention Investment Analysis ===")
    total_investment = (summary['incident_response_level'] * 30 + 
                       summary['monitoring_systems'] * 40 + 
                       summary['communication_protocols'] * 25)
    
    print(f"Total prevention investment: ${total_investment}k")
    print(f"Estimated cascade damage prevented: ${total_investment * 2}k+ (conservative)")
    print(f"ROI from prevention: 200%+ (not including reputation benefits)")
    print()
    
    print("=== Key Lessons ===")
    print("1. Prevention systems reduce failure frequency and severity")
    print("2. Near-misses provide learning without consequences")
    print("3. Transparency has short-term costs but long-term benefits")
    print("4. Cover-ups avoid immediate damage but accumulate future risks")
    print("5. Cascades can be contained with proper incident response")
    print("6. Investment in prevention pays dividends over time")


if __name__ == "__main__":
    demonstrate_cascade_system()

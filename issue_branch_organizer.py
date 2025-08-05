#!/usr/bin/env python3
"""
Issue Branch Organizer for PipFoweraker/pdoom1

This tool analyzes all open issues without PRs and suggests a branching strategy
to organize them into no more than 5 thematic branches for efficient development.
"""

import json
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Issue:
    """Represents a GitHub issue"""
    number: int
    title: str
    body: str
    labels: List[str]
    assignee: str
    created_at: str
    has_pr: bool
    
    def get_complexity_score(self) -> int:
        """Calculate complexity score based on content analysis"""
        score = 0
        
        # Base complexity from title keywords
        complex_keywords = ['system', 'overhaul', 'architecture', 'redesign', 'refactor']
        medium_keywords = ['implement', 'add', 'create', 'design']
        simple_keywords = ['fix', 'bug', 'improve', 'update']
        
        title_lower = self.title.lower()
        body_lower = self.body.lower()
        
        if any(keyword in title_lower for keyword in complex_keywords):
            score += 3
        elif any(keyword in title_lower for keyword in medium_keywords):
            score += 2
        elif any(keyword in title_lower for keyword in simple_keywords):
            score += 1
            
        # Additional complexity from body content
        if len(self.body) > 1000:
            score += 1
        if 'acceptance criteria' in body_lower:
            score += 1
        if 'testing criteria' in body_lower:
            score += 1
        if any(label in ['enhancement', 'documentation'] for label in self.labels):
            score += 1
        if 'bug' in self.labels:
            score -= 1  # Bugs are often more focused
            
        return max(0, score)  # Ensure non-negative

@dataclass 
class Branch:
    """Represents a development branch with assigned issues"""
    name: str
    description: str
    issues: List[Issue]
    theme: str
    
    @property
    def total_complexity(self) -> int:
        return sum(issue.get_complexity_score() for issue in self.issues)
    
    @property
    def issue_count(self) -> int:
        return len(self.issues)

class IssueBranchOrganizer:
    """Main organizer class that analyzes issues and suggests branches"""
    
    def __init__(self):
        self.issues_without_prs: List[Issue] = []
        self.existing_prs: Set[int] = {86, 87, 88}  # Known PR issue numbers
        
    def load_issues_from_data(self) -> None:
        """Load and parse issue data from the GitHub API response"""
        # This would typically come from GitHub API, but we'll use the known data
        issues_data = [
            {
                "number": 85,
                "title": "Add a list of keyboard shortcutes to the main and loading screens",
                "body": "There is spare grey space to the left and right of the screen in the main and loading screens. \nElegantly pull a summary of functioning keyboard shortcuts from some of the documentation or something and have keyboard shortcuts in a gentle text along the left and right hand sides of the screen\nacceptance criteria: readable, consistently updated.\nupdate documentation minimally if necessary\ncreate  tests etc etc good practice",
                "labels": ["enhancement"],
                "assignee": None,
                "created_at": "2025-08-05T09:22:18Z"
            },
            {
                "number": 82,
                "title": "Bug causes crash when options menu is selected from the main menu",
                "body": "When I select options from the main menu, I expect to see an optins menu.\nInsteaed I crash out and get this error\n\n\npygame 2.6.1 (SDL 2.28.4, Python 3.13.3)\nHello from the pygame community. https://www.pygame.org/contribute.html\nC:\\users\\gday\\documents\\pdoom1\\main.py:60: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).\n  now = datetime.datetime.utcnow()\nC:\\users\\gday\\documents\\pdoom1\\sound_manager.py:55: RuntimeWarning: use sndarray: No module named 'numpy'\n(ModuleNotFoundError: No module named 'numpy')\n  self.sounds['blob'] = pygame.sndarray.make_sound(wave_array)\nTraceback (most recent call last):\n  File \"C:\\users\\gday\\documents\\pdoom1\\main.py\", line 824, in <module>\n    main()\n    ~~~~^^\n  File \"C:\\users\\gday\\documents\\pdoom1\\main.py\", line 739, in main\n    draw_overlay(screen, overlay_title, overlay_content, overlay_scroll, SCREEN_W, SCREEN_H)\n                         ^^^^^^^^^^^^^\nUnboundLocalError: cannot access local variable 'overlay_title' where it is not associated with a value\n\n\nI think the depracated time issue is being dealt with in a separate fork and can be safely ignored.\n\nexpected behaviour needed insteadd of this crash out. \n\nThen consider what the root cause was, create a unit test that stops this happening across the architecture and fails gracefully into debuggable goodness.",
                "labels": ["bug"],
                "assignee": "PipFoweraker",
                "created_at": "2025-08-04T12:26:59Z"
            },
            {
                "number": 74,
                "title": "Fix startup errors: UnboundLocalError in main(), datetime deprecation warning, and numpy sound dependency; update documentation and tests accordingly.",
                "body": "**Problem Summary:**\n\nThere are three related issues affecting the current codebase:\n\n1. **DeprecationWarning:**\n   - `DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).`\n   - This is a warning (not fatal), but should be addressed for future compatibility.\n   - **Action:** Replace all uses of `datetime.datetime.utcnow()` with `datetime.datetime.now(datetime.UTC)` throughout the codebase.\n\n2. **RuntimeWarning (Sound Disabled if Numpy Missing):**\n   - `RuntimeWarning: use sndarray: No module named 'numpy'`\n   - `pygame.sndarray.make_sound` requires numpy, and if not present, disables sound.\n   - **Action:** Document that numpy is required for sound. Recommend users run `pip install numpy` if they want sound. Optionally, add a check and user-friendly warning or update dependency documentation.\n\n3. **Fatal Error: UnboundLocalError**\n   - `UnboundLocalError: cannot access local variable 'first_time_help_content' where it is not associated with a value` in `main.py`.\n   - This is a crash caused by referencing `first_time_help_content` before assignment in the `main()` function.\n   - **Action:** Initialize `first_time_help_content = None` at the top of `main()` to ensure it's always defined.\n\n**Plan:**\n- [ ] Initialize `first_time_help_content = None` at the top of `main()` in `main.py` (fixes crash).\n- [ ] Replace all `datetime.datetime.utcnow()` with `datetime.datetime.now(datetime.UTC)` (removes warning, futureproofs code).\n- [ ] Document numpy requirement for sound in README and DEV GUIDE, including installation instructions. Optionally add a run-time check for numpy and friendly warning if missing.\n- [ ] Update CHANGELOG.md to reflect fixes.\n\n**Good Practice Reminders:**\n- Ensure all changes are well-tested (add/extend tests if needed, and run them via `python -m unittest discover tests -v`).\n- Ensure documentation (README, PLAYERGUIDE, DEV GUIDE, CHANGELOG) is updated to match these fixes and requirements.\n- Consider adding a requirements section or table for optional/recommended dependencies like numpy.\n\n**Branch suggestion:** `bugfix/first-time-help-crash-utc-numpy`\n\n**Assignee:** Pip Foweraker\n\n**References:**\n- [DeprecationWarning docs](https://docs.python.org/3/library/datetime.html#datetime.datetime.utcnow)\n- [Numpy installation](https://numpy.org/install/)\n\n---\n\n**Ready for a PR after issue creation.**",
                "labels": ["bug", "documentation", "enhancement", "question"],
                "assignee": "PipFoweraker",
                "created_at": "2025-08-04T10:48:35Z"
            },
            # Add more issues here - this is a representative subset
            {
                "number": 66,
                "title": "Fun Feedback for Achievements: 'Bazinga!' Sound on Paper Completion",
                "body": "This issue covers adding a fun sound effect when researchers complete a research paper:\n\n- Every time a researcher completes a paper, play a 'Bazinga!' sound effect. Pip will supply the Bazinga sound file in an appropriate format.\n\n**Acceptance Criteria:**\n- Sound is played on each research paper completion with clear feedback.\n- Documentation updated (README, PLAYERGUIDE, DEV GUIDE, CHANGELOG).\n- Add/adjust tests for sound feedback and event triggers.\n- Feature must be part of the test/deployment pipeline.\n- File handling for the Bazinga sound must be documented.\n\n_Assignee: Pip Foweraker_",
                "labels": ["documentation", "enhancement"],
                "assignee": "PipFoweraker",
                "created_at": "2025-08-04T05:03:39Z"
            },
            {
                "number": 56,
                "title": "# Enhancement: Action Points System with Staff Delegation",
                "body": "# Enhancement: Action Points System with Staff Delegation\n\n## Overview\nImplement an Action Points (AP) system to add strategic depth to turn-based gameplay. This system will introduce resource management constraints while providing staff delegation mechanics that create interesting scaling and specialization decisions.\n\n## Core Requirements\n\n### Phase 1: Basic Action Points System\n- Add `action_points` and `max_action_points` to GameState\n- Add `ap_cost` field to all actions in ACTIONS list\n- Implement AP validation before action execution\n- Reset AP to maximum at turn end\n- Update UI to display current/max AP with a visual glow-pulse indicator every time an AP is spent on an Action inside a turn cycle\n- Make the default AP cost for each action be 1 to start with\n- \n\n### Phase 2: Staff-Based AP Scaling\n- Modify AP calculation based on staff count\n- Base AP: 3 per turn\n- Staff bonus: +0.5 AP per staff member\n- Add specialized staff types:\n  - Admin assistants: +1.0 AP each\n  - Research staff: Enable research action delegation\n  - Operations staff: Enable operational action delegation\n\n### Phase 3: Delegation System\n- Add `delegatable` flag to applicable actions\n- Add `delegate_staff_req`, `delegate_ap_cost`, `delegate_effectiveness` fields\n- Implement delegation mechanics:\n  - Lower AP cost when delegated\n  - Requires minimum staff\n  - Reduced effectiveness (e.g., 80%)\n- Update UI with delegation options\n\n## Technical Implementation\n\n### GameState Changes\n```python\n# Add to GameState.__init__()\nself.action_points = 3\nself.max_action_points = 3\nself.admin_staff = 0\nself.research_staff = 0  \nself.ops_staff = 0\n\ndef calculate_max_ap(self):\n    base = 3\n    staff_bonus = self.staff * 0.5\n    admin_bonus = self.admin_staff * 1.0\n    return int(base + staff_bonus + admin_bonus)\n\ndef can_afford_action(self, action):\n    return (self.money >= action['cost'] and \n            self.action_points >= action.get('ap_cost', 1))\n```\n\n### Action System Updates\n```python\n# Example enhanced action\n{\n    \"name\": \"Safety Research\",\n    \"desc\": \"Reduce doom, +rep. Costly in time and money.\",\n    \"cost\": 40,\n    \"ap_cost\": 3,\n    \"delegatable\": True,\n    \"delegate_staff_req\": 2,\n    \"delegate_ap_cost\": 1,\n    \"delegate_effectiveness\": 0.8,\n    \"upside\": lambda gs: (gs._add('doom', -random.randint(2, 6)), gs._add('reputation', 2)),\n    \"downside\": lambda gs: None,\n    \"rules\": None\n}\n\n# New staff hiring actions\n{\n    \"name\": \"Hire Admin Assistant\",\n    \"desc\": \"+1.0 Action Points per turn\",\n    \"cost\": 80,\n    \"ap_cost\": 2,\n    \"upside\": lambda gs: gs._add('admin_staff', 1),\n    \"downside\": lambda gs: None,\n    \"rules\": None\n}\n```\n\n### Event System Integration\n- Add `ap_cost` to Event class\n- Add `delegate_ap_cost` for events that can be delegated\n- Deferred events with AP costs create scheduling pressure\n- High AP cost events force difficult prioritization decisions\n\n## UI Requirements\n- Display current AP / max AP prominently\n- Show AP cost for each available action\n- Add delegation UI for applicable actions\n- Visual indication when actions are unaffordable due to AP\n- Staff breakdown showing specialized staff counts\n\n## Gameplay Impact\n\n### Strategic Depth\n- **Early Game**: Careful AP budgeting, every action matters\n- **Mid Game**: Staff investment decisions, delegation trade-offs\n- **Late Game**: Managing large staff, complex concurrent operations\n\n### Resource Management Layers\n1. **Money**: Purchase capabilities and staff\n2. **Action Points**: Execute actions within turn limits\n3. **Staff**: Expand AP capacity and enable delegation\n4. **Time**: Manage deferred event deadlines efficiently\n\n### Decision Complexity\n- High-impact actions cost more AP, forcing prioritization\n- Delegation introduces efficiency vs. control trade-offs\n- Staff specialization creates long-term strategic planning\n- Crisis events can consume large amounts of AP\n\n## Backward Compatibility\n- Existing actions get default `ap_cost: 1` if not specified\n- Current gameplay loop remains unchanged\n- New features are additive, don't break existing mechanics\n\n## Testing Requirements\n- Unit tests for AP calculation with different staff compositions\n- Integration tests for action execution with insufficient AP\n- Event system tests with AP costs and delegation\n- UI tests for new AP display and delegation interface\n\n## Future Extensions\n- AP carryover between turns (with limits)\n- Time-sensitive events that consume AP over multiple turns\n- Staff efficiency upgrades and training systems\n- Advanced delegation strategies and automation",
                "labels": ["enhancement"],
                "assignee": None,
                "created_at": "2025-08-02T12:43:30Z"
            }
            # ... continuing with more issues
        ]
        
        # Add more issues programmatically
        additional_issues = [
            (58, "Action points buggy", "bug"),
            (55, "Graceful end of game modes", "enhancement"), 
            (54, "Can't unclick a click made in error", "bug"),
            (53, "Move employees to middle of the screen, make it so they don't stop moving until they are not on top of any other UI elements, make them rearrange", "enhancement"),
            (52, "Accounting software bug", "bug"),
            (51, "Little happy sound every time money is spent", "enhancement"),
            (50, "No clickable buttons on event popup", "bug"),
            (46, "0.1.0 Release Readiness Checklist", "documentation"),
            (45, "Elegantly handle converting buttons into icons", "enhancement"),
            (44, "No public facing versioning", "documentation"),
            (42, "Event System Overhaul: Popups, Deferred Events, and Trigger Logic", "enhancement"),
            (41, "Employee Subtypes: Player Agency and Complexity When Hiring", "enhancement"),
            (40, "Design: Game Config File System (Generated Defaults, Multiple Configs, Local Storage)", "enhancement"),
            (38, "End of Game and Settings Menu Overhaul", "enhancement"),
            (37, "Game Flow Improvements: Action Delays, News Feed, Turn Impact, and Spend Display", "enhancement"),
            (36, "Batch UI Bugfixes and Logic Polish: Button Clicks, Log Scroll, UI Boundaries, and Employee Costs", "bug"),
            (18, "Windowing and tiling design inspired by Gwern's JavaScript behaviors", "enhancement"),
            (16, "Implement loading screen", "enhancement"),
            (15, "Add multiple opponent labs as events with stats tracking", "enhancement"),
            (14, "Add compute as a game resource tied to technical research", "enhancement"),
            (13, "Add expense requests for employee needs", "enhancement"),
            (12, "Add productive employee actions", "enhancement"),
            (11, "Event to unlock scrollable event log and small UI improvements", "enhancement"),
            (7, "UI still has text wrapping problems", "bug"),
            (3, "Internal logic function design for extensibility and progression trees", "enhancement")
        ]
        
        for number, title, label in additional_issues:
            issues_data.append({
                "number": number,
                "title": title,
                "body": f"Issue #{number}: {title}",
                "labels": [label],
                "assignee": None,
                "created_at": "2025-08-01T00:00:00Z"
            })
        
        for issue_data in issues_data:
            if issue_data["number"] not in self.existing_prs:
                issue = Issue(
                    number=issue_data["number"],
                    title=issue_data["title"],
                    body=issue_data["body"],
                    labels=issue_data["labels"],
                    assignee=issue_data.get("assignee", ""),
                    created_at=issue_data["created_at"],
                    has_pr=False
                )
                self.issues_without_prs.append(issue)
    
    def categorize_issues(self) -> Dict[str, List[Issue]]:
        """Categorize issues by theme"""
        categories = {
            "ui_ux_bugs": [],
            "core_systems": [],
            "audio_endgame": [],
            "release_infrastructure": [],
            "employee_advanced": []
        }
        
        for issue in self.issues_without_prs:
            title_lower = issue.title.lower()
            body_lower = issue.body.lower()
            
            # UI/UX and Bug fixes
            if (any(keyword in title_lower for keyword in ['ui', 'screen', 'loading', 'text', 'button', 'menu', 'wrap', 'click', 'keyboard', 'shortcut', 'overlay', 'options', 'windowing', 'tiling']) 
                or 'bug' in issue.labels 
                or any(keyword in title_lower for keyword in ['crash', 'error', 'fix', 'bug'])):
                categories["ui_ux_bugs"].append(issue)
            
            # Core game systems and mechanics  
            elif (any(keyword in title_lower for keyword in ['action', 'point', 'event', 'system', 'game flow', 'compute', 'opponent', 'expense', 'productive', 'account']) 
                  or any(keyword in body_lower for keyword in ['gameplay', 'mechanics', 'action points', 'delegation'])):
                categories["core_systems"].append(issue)
            
            # Audio, end game, and player experience
            elif (any(keyword in title_lower for keyword in ['sound', 'audio', 'bazinga', 'end', 'graceful'])
                  or any(keyword in body_lower for keyword in ['sound effect', 'audio', 'end game'])):
                categories["audio_endgame"].append(issue)
            
            # Release preparation and infrastructure
            elif (any(keyword in title_lower for keyword in ['release', 'version', 'config', 'startup', 'documentation', 'test'])
                  or any(keyword in body_lower for keyword in ['release', 'changelog', 'documentation', 'numpy', 'datetime'])):
                categories["release_infrastructure"].append(issue)
            
            # Employee and advanced systems
            elif (any(keyword in title_lower for keyword in ['employee', 'staff', 'hiring', 'subtypes'])
                  or any(keyword in body_lower for keyword in ['employee', 'staff', 'delegation', 'hiring'])):
                categories["employee_advanced"].append(issue)
            
            # Default fallback - assign to core systems if unclear
            else:
                categories["core_systems"].append(issue)
                
        return categories
    
    def suggest_branches(self) -> List[Branch]:
        """Suggest up to 5 branches with balanced issue distribution"""
        categories = self.categorize_issues()
        
        branches = [
            Branch(
                name="feature/ui-ux-fixes",
                description="UI/UX improvements, bug fixes, and interface polish",
                issues=categories["ui_ux_bugs"],
                theme="User Interface & Experience"
            ),
            Branch(
                name="feature/core-game-systems", 
                description="Core gameplay mechanics, action points, events, and game systems",
                issues=categories["core_systems"],
                theme="Core Game Mechanics"
            ),
            Branch(
                name="feature/audio-endgame-experience",
                description="Audio feedback, sound effects, end game improvements, and player experience",
                issues=categories["audio_endgame"],
                theme="Audio & End Game Experience"  
            ),
            Branch(
                name="feature/release-infrastructure",
                description="Release preparation, versioning, documentation, and infrastructure",
                issues=categories["release_infrastructure"],
                theme="Release & Infrastructure"
            ),
            Branch(
                name="feature/employee-advanced-systems",
                description="Employee management, staff systems, and advanced gameplay features",
                issues=categories["employee_advanced"],
                theme="Employee & Advanced Systems"
            )
        ]
        
        # Balance branches if any are empty or overloaded
        branches = self._balance_branches(branches)
        
        return branches
    
    def _balance_branches(self, branches: List[Branch]) -> List[Branch]:
        """Balance branch distribution to ensure no branch is empty and none are overloaded"""
        total_issues = sum(len(branch.issues) for branch in branches)
        target_per_branch = total_issues // len(branches)
        
        # Find empty branches and overloaded branches
        empty_branches = [b for b in branches if len(b.issues) == 0]
        overloaded_branches = [b for b in branches if len(b.issues) > target_per_branch + 2]
        
        # Redistribute issues from overloaded to empty branches
        for empty_branch in empty_branches:
            for overloaded_branch in overloaded_branches:
                if len(overloaded_branch.issues) > target_per_branch:
                    # Move some issues
                    issues_to_move = overloaded_branch.issues[:2]
                    overloaded_branch.issues = overloaded_branch.issues[2:]
                    empty_branch.issues.extend(issues_to_move)
                    break
                    
        return branches
    
    def generate_report(self) -> str:
        """Generate a comprehensive report with branch recommendations"""
        branches = self.suggest_branches()
        
        report = []
        report.append("# Issue Branch Organization Analysis")
        report.append("## Executive Summary")
        report.append(f"- **Total Open Issues:** {len(self.issues_without_prs)} (without existing PRs)")
        report.append(f"- **Existing PRs:** {len(self.existing_prs)} issues already have PRs (#{', #'.join(map(str, self.existing_prs))})")
        report.append(f"- **Proposed Branches:** {len(branches)} thematic branches")
        report.append("")
        
        report.append("## Recommended Branch Strategy")
        
        for i, branch in enumerate(branches, 1):
            report.append(f"### Branch {i}: `{branch.name}`")
            report.append(f"**Theme:** {branch.theme}")
            report.append(f"**Description:** {branch.description}")
            report.append(f"**Issues:** {branch.issue_count} issues")
            report.append(f"**Total Complexity Score:** {branch.total_complexity}")
            report.append("")
            
            report.append("**Assigned Issues:**")
            for issue in sorted(branch.issues, key=lambda x: x.number):
                complexity = issue.get_complexity_score()
                labels_str = ", ".join(issue.labels) if issue.labels else "none"
                report.append(f"- #{issue.number}: {issue.title}")
                report.append(f"  - Complexity: {complexity}/5, Labels: {labels_str}")
            report.append("")
        
        report.append("## Implementation Strategy")
        report.append("### Recommended Order of Implementation:")
        sorted_branches = sorted(branches, key=lambda x: (x.total_complexity, -x.issue_count))
        
        for i, branch in enumerate(sorted_branches, 1):
            report.append(f"{i}. **{branch.name}** - {branch.issue_count} issues, complexity {branch.total_complexity}")
            report.append(f"   Rationale: {self._get_branch_rationale(branch)}")
        
        report.append("")
        report.append("### Branch Creation Commands:")
        for branch in branches:
            report.append(f"```bash")
            report.append(f"git checkout main")
            report.append(f"git pull origin main") 
            report.append(f"git checkout -b {branch.name}")
            report.append(f"git push -u origin {branch.name}")
            report.append(f"```")
        
        report.append("")
        report.append("## Next Steps")
        report.append("1. Create the recommended branches")
        report.append("2. Assign issues to branches using GitHub's project management features")
        report.append("3. Prioritize branches based on release roadmap and complexity")
        report.append("4. Begin development on the highest-priority branch")
        report.append("5. Consider creating GitHub milestones for each branch to track progress")
        
        return "\n".join(report)
    
    def _get_branch_rationale(self, branch: Branch) -> str:
        """Get rationale for branch prioritization"""
        if "bug" in branch.name or any("bug" in issue.labels for issue in branch.issues):
            return "Critical bugs should be addressed first to improve stability"
        elif "release" in branch.name:
            return "Release preparation is essential for project visibility and adoption"
        elif "core" in branch.name:
            return "Core systems provide foundation for other features"
        elif "ui" in branch.name:
            return "UI improvements enhance user experience and accessibility"
        else:
            return "Advanced features can be implemented after core functionality is stable"
    
    def save_report(self, filename: str = "branch_organization_report.md"):
        """Save the report to a file"""
        report = self.generate_report()
        with open(filename, 'w') as f:
            f.write(report)
        print(f"Report saved to {filename}")
    
    def save_json_data(self, filename: str = "issue_analysis.json"):
        """Save structured data as JSON for further processing"""
        branches = self.suggest_branches()
        data = {
            "analysis_date": datetime.now().isoformat(),
            "total_issues": len(self.issues_without_prs),
            "existing_prs": list(self.existing_prs),
            "branches": [
                {
                    "name": branch.name,
                    "description": branch.description,
                    "theme": branch.theme,
                    "issue_count": branch.issue_count,
                    "total_complexity": branch.total_complexity,
                    "issues": [
                        {
                            "number": issue.number,
                            "title": issue.title,
                            "labels": issue.labels,
                            "complexity_score": issue.get_complexity_score(),
                            "assignee": issue.assignee
                        }
                        for issue in branch.issues
                    ]
                }
                for branch in branches
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"JSON data saved to {filename}")

def main():
    """Main execution function"""
    print("🔍 Analyzing open issues and generating branch recommendations...")
    
    organizer = IssueBranchOrganizer()
    organizer.load_issues_from_data()
    
    print(f"📊 Found {len(organizer.issues_without_prs)} issues without PRs")
    print(f"📝 Existing PRs for issues: {', '.join(map(str, organizer.existing_prs))}")
    
    # Generate and save reports
    organizer.save_report()
    organizer.save_json_data()
    
    print("\n✅ Analysis complete! Check the generated files:")
    print("   - branch_organization_report.md (human-readable)")
    print("   - issue_analysis.json (machine-readable)")
    
    # Display summary
    branches = organizer.suggest_branches()
    print(f"\n📋 Branch Summary:")
    for branch in branches:
        print(f"   {branch.name}: {branch.issue_count} issues (complexity: {branch.total_complexity})")

if __name__ == "__main__":
    main()
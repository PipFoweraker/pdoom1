"""
Version management for P(Doom): Bureaucracy Strategy Game

This module provides centralized version information for the game,
following Semantic Versioning (SemVer) specification.
"""

# Semantic version following MAJOR.MINOR.PATCH format
# MAJOR: Incompatible API changes (gameplay mechanics overhauls)
# MINOR: Backwards-compatible functionality additions (new features, events, opponents)
# PATCH: Backwards-compatible bug fixes
__version__ = "0.6.0"

# Version components for programmatic access
VERSION_MAJOR = 0
VERSION_MINOR = 6
VERSION_PATCH = 0

# Pre-release identifier (e.g., "alpha", "beta", "rc1", or "" for stable)
VERSION_PRERELEASE = ""

# Build metadata (optional, e.g., commit hash for development builds)
VERSION_BUILD = ""

def get_version():
    """
    Get the full version string including pre-release and build metadata.
    
    Returns:
        str: Full version string in SemVer format
    """
    version = __version__
    
    if VERSION_PRERELEASE:
        version += f"-{VERSION_PRERELEASE}"
    
    if VERSION_BUILD:
        version += f"+{VERSION_BUILD}"
    
    return version

def get_display_version():
    """
    Get a display-friendly version string for UI purposes.
    
    Returns:
        str: Version string formatted for display (e.g., "v0.1.0")
    """
    return f"v{get_version()}"

def get_version_info():
    """
    Get detailed version information as a dictionary.
    
    Returns:
        dict: Version components and metadata
    """
    return {
        "version": __version__,
        "full_version": get_version(),
        "display_version": get_display_version(),
        "major": VERSION_MAJOR,
        "minor": VERSION_MINOR,
        "patch": VERSION_PATCH,
        "prerelease": VERSION_PRERELEASE,
        "build": VERSION_BUILD
    }

# === STABILITY TRACKING METADATA ===
# For managing rapid iteration during UI/game stability push

# Version milestone tracking
MILESTONE_STATUS = "UI_STABILITY_PUSH"  # Current development focus
EXPECTED_HOTFIXES = ["0.2.2", "0.2.3", "0.2.4", "0.2.5"]  # Anticipated patch releases

# Stability tracking
STABILITY_FOCUS = [
    "3-column UI layout",
    "Keystroke action system", 
    "Button sizing and visibility",
    "Color differentiation system",
    "Turn processing flow",
    "Installation compatibility"
]

# Development notes for hotfix management
HOTFIX_GUIDELINES = """
HOTFIX VERSION STRATEGY (v0.2.x series):

Quick Reference for Version Bumps:
- 0.2.1 ? 0.2.2: Button layout fixes, text overflow patches
- 0.2.2 ? 0.2.3: Color system refinements, visibility improvements  
- 0.2.3 ? 0.2.4: Keystroke binding fixes, input handling
- 0.2.4 ? 0.2.5: UI interaction fixes, Factorio-style hint system
- 0.2.5 ? 0.3.0: Major milestone - stable UI release

Increment Trigger Events:
- Any UI crash or freeze ? immediate patch
- Button accessibility issues ? same-day patch
- Keystroke conflicts ? priority patch
- Installation/dependency issues ? emergency patch
- Performance degradation ? planned patch

Version Update Process:
1. Update VERSION_PATCH number
2. Update VERSION_PRERELEASE if needed ("", "hotfix-candidate", "stable")
3. Add entry to CHANGELOG.md with specific fixes
4. Test critical user flows before release

Target: Achieve stable UI by v0.3.0 for wider distribution
"""

def get_next_hotfix_version():
    """Get the suggested next hotfix version."""
    return f"0.2.{VERSION_PATCH + 1}"

def is_hotfix_candidate():
    """Check if current version is marked for hotfix development."""
    return VERSION_PRERELEASE == "hotfix-candidate"
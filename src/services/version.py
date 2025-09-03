"""
Version management for P(Doom): Bureaucracy Strategy Game

This module provides centralized version information for the game,
following Semantic Versioning (SemVer) specification.
"""

# Semantic version following MAJOR.MINOR.PATCH format
# MAJOR: Incompatible API changes (gameplay mechanics overhauls)
# MINOR: Backwards-compatible functionality additions (new features, events, opponents)
# PATCH: Backwards-compatible bug fixes
__version__ = "0.2.0"

# Version components for programmatic access
VERSION_MAJOR = 0
VERSION_MINOR = 2
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
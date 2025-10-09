# !/usr/bin/env python3
"""
Convenience launcher for P(Doom) development tools.
Simply forwards all arguments to the main dev tool.

Usage:
    python dev.py --test dual      # Same as python tools/dev_tool.py --test dual
    python dev.py --list           # Same as python tools/dev_tool.py --list
    python dev.py                  # Interactive menu
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Forward all arguments to the dev tool."""
    dev_tool_path = Path(__file__).parent / "tools" / "dev_tool.py"
    
    # Forward all command line arguments
    cmd = [sys.executable, str(dev_tool_path)] + sys.argv[1:]
    
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error running dev tool: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

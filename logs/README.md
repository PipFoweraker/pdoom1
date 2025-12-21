# Build & Automation Logs

This directory contains structured logs from P(Doom) development tools and CI/CD processes.

## Directory Structure

```
logs/
  quality/    - Code quality enforcement (ASCII compliance, standards checks)
  release/    - Build and release processes (version bumps, exports)
  testing/    - Test execution and validation results
  docs/       - Documentation generation and processing
  dev/        - General development activity logs
```

## Log Categories

| Category | Subdirectory | Description |
|----------|--------------|-------------|
| QUALITY | `quality/` | Quality checks, linting, code standards |
| ASCII | `quality/` | ASCII compliance tools and fixes |
| STANDARDS | `quality/` | Development standards enforcement |
| VERSION | `release/` | Version management operations |
| BUILD | `release/` | Build exports and packaging |
| TESTS | `testing/` | Test execution results |
| DOCS | `docs/` | Documentation generation |
| GENERAL | `dev/` | General-purpose logging |

## Log Format

Logs use structured JSON format for machine parsing:

```json
{
  "timestamp": "2025-12-19T14:30:00.000000",
  "level": "INFO",
  "tool": "pdoom.build_all_platforms",
  "category": "BUILD",
  "session_id": "20251219_143000",
  "message": "Building Windows...",
  "module": "build_all_platforms",
  "function": "export_platform",
  "line": 115
}
```

## File Naming

- Session logs: `{tool_name}_{YYYYMMDD_HHMMSS}.log`
- Daily aggregates: `daily_{YYYYMMDD}.log`

## Usage in Scripts

```python
from scripts.logging_system import get_logger, LogCategory

# Get a configured logger
logger = get_logger('my_script', LogCategory.BUILD)

# Basic logging
logger.info('Starting build process')
logger.error('Build failed', extra_data={'error_code': 1})

# Step tracking
logger.step_start('Export Windows')
logger.step_success('Export Windows')

# Performance metrics
logger.performance('Export', duration_ms=1234.5)
```

## Retention

- Session logs: Rotated at 10MB, 5 backups retained
- Daily logs: Rotated at 50MB, 30 days retained
- Logs are gitignored (not committed to repository)

## CI/CD Integration

In GitHub Actions, logs automatically use structured JSON output for better parsing.
GitHub-specific annotations are also emitted:

```python
logger.github_action_error('Build failed', file_path='godot/project.godot', line=15)
```

## Related Files

- [`scripts/logging_system.py`](../scripts/logging_system.py) - Logging implementation
- [`scripts/build_all_platforms.py`](../scripts/build_all_platforms.py) - Multi-platform build script

---

*This directory structure is auto-created by scripts that use the logging system.*

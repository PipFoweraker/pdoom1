# CI/CD Data Validation Automation

## Overview

Automated validation and feed publishing pipeline for historical AI safety data in PDoom1, ensuring data quality and inter-repository consistency.

## Workflow: data-validation.yml

### Trigger Conditions

The validation workflow runs on:
- **Pull Requests** modifying data or schemas
- **Pushes to main/develop** affecting data files
- **Manual trigger** via workflow_dispatch

### Jobs

#### 1. validate-data
Validates all historical data against JSON Schemas.

**Steps**:
1. Checkout repository
2. Setup Python 3.11 with pip caching
3. Install `jsonschema>=4.0.0`
4. Run `scripts/validate_historical_data.py --verbose`
5. Generate validation report
6. Upload report as artifact (30-day retention)
7. Comment on PR if validation fails (PR only)

**Outputs**:
- Validation report artifact
- GitHub Step Summary with results
- PR comment with error details (on failure)

**Exit behavior**:
- Fails if any validation errors found
- Blocks PR merge if validation fails
- Provides actionable error messages

#### 2. schema-validation-status
Checks the health of JSON Schema files themselves.

**Steps**:
1. Verify all required schema files exist:
   - `shared/schemas/event.schema.json`
   - `shared/schemas/organization.schema.json`
   - `shared/schemas/researcher.schema.json`

2. Validate JSON Schema syntax using AJV CLI
   - Checks Draft-07 compliance
   - Validates with strict mode

**Exit behavior**:
- Fails if any schema file missing
- Fails if schema syntax invalid

#### 3. publish-feeds
Generates and publishes data feeds (main branch only).

**Trigger**: Only runs after successful validation on `main` branch push

**Steps**:
1. Generate RSS and JSON feeds (placeholder - Issue #437)
2. Upload feed artifacts
3. Generate provenance log with:
   - Build timestamp
   - Commit SHA and ref
   - Run ID and number
   - Schema version
   - Validation status

4. Create release manifest documenting:
   - Build metadata
   - Validation status
   - Artifacts produced
   - Provenance reference

**Outputs**:
- Data feeds artifact
- Provenance JSON
- Release manifest in step summary

## Integration with Other Issues

### Issue #440 - Shared Schemas
- Uses schemas from `shared/schemas/`
- Validates data against event, organization, and researcher schemas
- Reports schema-specific errors with field paths

### Issue #437 - Blog Publishing
- Feed generation placeholder ready
- Will auto-publish RSS/JSON feeds from validated events
- Provenance log tracks published data lineage

### Issue #442 - API Events
- Ensures API event data meets schema requirements
- Validates game transformations before integration
- Blocks invalid API data from deployment

## Local Development

### Running Validation Locally

```bash
# Basic validation
python scripts/validate_historical_data.py

# Verbose output
python scripts/validate_historical_data.py --verbose

# Check specific data types
python scripts/validate_historical_data.py -v 2>&1 | grep "researcher"
```

### Testing Schema Changes

1. Modify schema in `shared/schemas/`
2. Run validation locally to test
3. Create PR - automatic validation runs
4. Review validation report in PR comments
5. Merge when validation passes

### Debugging Validation Failures

**Check validation report**:
```bash
# Download from GitHub Actions artifacts
# Or run locally:
python scripts/validate_historical_data.py --verbose > report.txt
```

**Common errors**:
- Missing required fields
- Invalid enum values
- Date format mismatches
- URL format violations
- Type mismatches

**Fix process**:
1. Identify failing file from error message
2. Check error path (e.g., `events.0.title`)
3. Refer to schema documentation in `shared/schemas/README.md`
4. Fix data or schema as appropriate
5. Re-run validation

## Workflow Configuration

### Path Filters
Workflow only triggers when these paths change:
- `godot/data/**` - Godot data files
- `shared/data/**` - Shared data files
- `shared/schemas/**` - JSON Schemas
- `scripts/validate_historical_data.py` - Validation script
- `.github/workflows/data-validation.yml` - Workflow itself

### Artifact Retention
- Validation reports: 30 days
- Data feeds: 30 days
- Can be downloaded from Actions tab

### Performance Optimization
- Python pip caching enabled
- Runs only when data/schema files change
- Parallel job execution where possible

## Future Enhancements

### Planned Features
1. **Feed Generation** (Issue #437)
   - Auto-generate RSS feeds from events
   - Publish JSON feeds for API consumption
   - Update static site with new content

2. **Cross-Repository Sync**
   - Validate data consistency between pdoom1 and pdoom-data
   - Auto-create sync PRs when schemas update
   - Track schema version compatibility

3. **Data Quality Metrics**
   - Track validation pass rates over time
   - Monitor schema coverage
   - Alert on data quality degradation

4. **Automated Fixes**
   - Auto-format dates to ISO 8601
   - Suggest enum corrections
   - Fix common URL issues

## Monitoring

### Success Indicators
- ✅ Green checks on PRs
- ✅ "Validation passed" in step summary
- ✅ No error artifacts

### Failure Indicators
- ❌ Red X on PR checks
- ❌ PR comment with error details
- ❌ Validation report artifact present

### Key Metrics
- Validation execution time
- Number of files validated
- Error frequency by schema type
- Feed generation success rate

## Security Considerations

- Validation runs in isolated GitHub Actions environment
- No secrets required for data validation
- Read-only access to repository data
- Feed publishing uses artifact upload (no direct deployment)
- Provenance log ensures build traceability

## Related Documentation

- [PDOOM_DATA_INTEGRATION_PLAN.md](PDOOM_DATA_INTEGRATION_PLAN.md) - Overall integration strategy
- [shared/schemas/README.md](../../shared/schemas/README.md) - Schema documentation
- [validate_historical_data.py](../../scripts/validate_historical_data.py) - Validation script

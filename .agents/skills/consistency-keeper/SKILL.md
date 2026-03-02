# Consistency Keeper Skill

> Maintains consistency between code, documentation, and configuration files.

## When to Use

- After making changes to code structure
- Before committing to ensure docs are up-to-date
- When CI fails on documentation checks
- To verify project health

## Commands

```bash
# Check documentation consistency
python .agents/doc_agent.py --check

# Run full consistency check (code + docs + config)
make check

# Auto-fix issues where possible
python .agents/doc_agent.py --update
```

## Key Files to Monitor

| File | Purpose | Check Command |
|------|---------|---------------|
| `AGENTS.md` | Project guide for AI agents | Version match |
| `CHANGELOG.md` | Release history | Entry format |
| `docs/*.md` | User documentation | Link validity |
| `pyproject.toml` | Tool configurations | Sync with CI |
| `.github/workflows/*.yml` | CI/CD configs | Match local tools |

## CI/CD Integration

The documentation workflow runs on:
- Changes to `docs/**`, `modules/**`, `pages/**`
- Changes to `AGENTS.md`, `CHANGELOG.md`

## Common Issues & Fixes

### Issue: CI lint fails but local passes
**Cause**: Version mismatch between CI and local tools
**Fix**: Update CI to install from requirements-dev.txt

### Issue: doc_agent.py path errors in CI
**Cause**: Hardcoded local paths
**Fix**: Use `Path(__file__).parent.parent` for project root

### Issue: Line too long errors (E501)
**Solutions**:
1. Break strings using parentheses
2. Use Black to auto-format
3. Configure Ruff line-length in pyproject.toml

## Quick Health Check

```bash
python .agents/doc_agent.py --check
```

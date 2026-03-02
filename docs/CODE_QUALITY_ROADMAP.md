# Code Quality Roadmap

> Plan to gradually improve code quality and reduce technical debt.

## Current State (2026-03-02)

✅ **CI/CD Pipeline**: PASSING
- Black 26.1.0 formatting
- Ruff linting (line-length: 150)
- Essential tests passing
- Security scans (Bandit/Safety) - reports generated

⚠️ **Technical Debt**:
- Ruff line-length: 150 (target: 100)
- Several style rules disabled (N818, N806, E402, E741, etc.)
- Bandit security warnings (not blocking)
- Test coverage incomplete

## Phase 1: Stabilization (COMPLETED) ✅

- [x] Fix Black formatting
- [x] Sync CI versions with requirements-dev.txt
- [x] Fix critical import errors
- [x] Configure Ruff with reasonable defaults
- [x] Make CI tolerant to non-blocking issues
- [x] Fix doc_agent.py for CI compatibility

## Phase 2: Code Quality (NEXT)

### 2.1 Reduce Line Length
**Goal**: Reduce Ruff line-length from 150 → 100

```bash
# Step 1: 150 → 130
# Files to fix: ~15
python -m ruff check modules/ --select E501 --line-length 130

# Step 2: 130 → 110  
# Files to fix: ~25
python -m ruff check modules/ --select E501 --line-length 110

# Step 3: 110 → 100
# Files to fix: ~40
python -m ruff check modules/ --select E501 --line-length 100
```

### 2.2 Re-enable Style Rules
Priority order:
1. `E741` - Ambiguous variable names (easy fix)
2. `E402` - Import ordering (medium)
3. `N806` - Variable naming (requires refactoring)
4. `N818` - Exception naming (requires refactoring)

### 2.3 Security Hardening
- Fix B608 (SQL injection risks)
- Fix B324 (MD5 hash usage)
- Review B301 (pickle usage)

## Phase 3: Testing

- [ ] Add integration tests
- [ ] Improve test coverage to 80%+
- [ ] Add E2E tests with Playwright
- [ ] Mock external services (AI APIs)

## Phase 4: Documentation

- [ ] Add README.md to each module
- [ ] Document public APIs
- [ ] Add architecture decision records (ADRs)

## Tools & Commands

### Daily Development
```bash
make check        # Quick check before commit
make test         # Run essential tests
make format       # Auto-format code
```

### Before PR
```bash
make ci           # Full CI simulation
python scripts/ci_health_check.py
```

### Gradual Cleanup
```bash
# Fix E501 in one module
python -m ruff check modules/db/ --select E501 --fix

# Check specific rule
python -m ruff check modules/ --select E741
```

## Metrics Tracking

| Metric | Current | Target |
|--------|---------|--------|
| Line length | 150 | 100 |
| Ruff ignores | 7 | 0 |
| Test coverage | ~40% | 80% |
| Bandit warnings | ~30 | 0 |
| Missing docstrings | ~200 | 0 |

## Resources

- [Ruff Rules](https://docs.astral.sh/ruff/rules/)
- [Black Style Guide](https://black.readthedocs.io/en/stable/the_black_code_style.html)
- [Bandit Tests](https://bandit.readthedocs.io/en/latest/plugins/index.html)

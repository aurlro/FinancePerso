# Copilot Instructions for FinancePerso

## Project Overview

FinancePerso (MyFinance Companion) is a personal finance management application built with Streamlit. It provides:
- Automatic bank transaction import (CSV)
- AI-powered transaction categorization (cloud or local ML)
- Budget tracking and visual analytics
- Multi-member household support

## Architecture

### Tech Stack
- **Framework**: Streamlit 1.47.0
- **Language**: Python 3.12+
- **Database**: SQLite
- **Data Science**: pandas 2.3.1, plotly 6.2.0
- **AI**: Google GenAI (cloud) or scikit-learn (local)
- **Security**: cryptography 44.0.0

### Project Structure
```
FinancePerso/
├── app.py                 # Main entry point
├── pages/                 # Streamlit pages (auto-routed)
│   ├── 1_Opérations.py   # Import + Validation
│   ├── 3_Synthèse.py     # Dashboard
│   ├── 4_Intelligence.py # Rules, budgets
│   └── ...
├── modules/              # Business logic
│   ├── ai/              # AI suite (anomaly detection, predictions)
│   ├── core/            # Events and messaging
│   ├── db/              # Data layer (SQLite)
│   └── ui/              # UI components
└── tests/               # pytest suite
```

## Coding Standards

### Style Guide
- **Formatter**: Black (line-length: 100)
- **Linter**: Ruff
- **Docstrings**: Google style
- **Type hints**: Recommended for public functions

### Example Function
```python
def categorize_transaction(
    transaction: Transaction,
    rules: list[Rule] | None = None,
) -> Category:
    """Categorize a transaction according to existing rules.
    
    Args:
        transaction: The transaction to categorize
        rules: Optional list of rules to apply
        
    Returns:
        The assigned category
        
    Raises:
        ValueError: If the transaction is invalid
    """
    ...
```

### Import Order
1. Standard library (os, sys, json)
2. Third-party (pandas, streamlit)
3. Local modules (from modules.xxx import yyy)

## Key Patterns

### Database Access
Always use the context manager:
```python
from modules.db.connection import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE status = ?", ("pending",))
    results = cursor.fetchall()
```

### Session State
Initialize keys at the start of pages:
```python
if "ma_cle" not in st.session_state:
    st.session_state["ma_cle"] = default_value
```

### Caching
- `@st.cache_data` for expensive DB calls
- `@st.cache_resource` for connections

### Logging
Use the project logger, not print:
```python
from modules.logger import logger
logger.info("Message")
logger.error("Error: %s", error)
```

## Security Guidelines

1. **Never commit credentials** - Use `.env` file
2. **Use parameterized queries** - Prevent SQL injection
3. **Encrypt sensitive data** - Use `modules/encryption.py`
4. **Validate inputs** - Use `modules.validators`

## Testing

### Running Tests
```bash
make test      # Essential tests (~5s)
make test-all  # All tests + coverage (~30s)
make check     # Lint + tests (~10s)
```

### Test Structure
```python
def test_ma_fonction():
    # Arrange
    input_data = "test"
    
    # Act
    result = ma_fonction(input_data)
    
    # Assert
    assert result == "expected"
```

## Common Tasks

### Adding a New Page
1. Create file in `pages/` with numeric prefix (e.g., `6_NewPage.py`)
2. Initialize session state at the top
3. Use existing UI components from `modules/ui/`

### Adding a Database Migration
1. Add migration logic to `modules/db/migrations.py`
2. Update `CURRENT_SCHEMA_VERSION`
3. Test migration on a backup database

### Adding an AI Feature
1. Add logic to appropriate file in `modules/ai/`
2. Integrate with `modules/ai_manager_v2.py`
3. Add configuration option in settings

## Performance Tips

1. Use `@st.cache_data(ttl=300)` for DB queries
2. Batch database operations
3. Use `st.spinner()` for long operations
4. Lazy load heavy modules

## Streamlit-Specific Guidelines

1. **Rerun on every interaction** - Keep callbacks lightweight
2. **Use forms** for multiple inputs that should submit together
3. **Prefer `st.session_state`** over global variables
4. **Use `st.empty()`** for dynamic content updates

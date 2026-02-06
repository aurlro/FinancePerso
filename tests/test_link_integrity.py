import os
import re
import pytest
from pathlib import Path

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent
PAGES_DIR = BASE_DIR / "pages"
MODULES_DIR = BASE_DIR / "modules"

# Regex for finding Streamlit page navigation
PAGE_NAV_REGEX = re.compile(r'st\.(?:switch_page|page_link)\(\s*(?:f?["\'](pages\/[^"\']+)["\']|["\'](pages\/[^"\']+)["\']\.format)')

def is_dynamic(path: str) -> bool:
    """Return True if path contains placeholders."""
    return "{" in path or "%" in path

def get_python_files():
    """Recursively find all Python files in the project."""
    files = []
    # Project root (app.py)
    files.append(BASE_DIR / "app.py")
    
    # modules/
    for path in MODULES_DIR.rglob("*.py"):
        files.append(path)
        
    # pages/
    for path in PAGES_DIR.rglob("*.py"):
        files.append(path)
        
    return [f for f in files if f.exists()]

def test_link_integrity():
    """
    Scans all Python files for st.switch_page and st.page_link calls
    and verifies that the target files exist in the pages/ directory.
    """
    python_files = get_python_files()
    broken_links = []
    
    # Get set of all existing pages (basenames like 'pages/1_Opérations.py')
    existing_pages = set()
    if PAGES_DIR.exists():
        for p in PAGES_DIR.glob("*.py"):
            existing_pages.add(f"pages/{p.name}")

    for file_path in python_files:
        try:
            content = file_path.read_text(encoding='utf-8')
            matches = [m[0] or m[1] for m in PAGE_NAV_REGEX.findall(content)]
            
            for target in matches:
                # Skip dynamic targets like 'pages/{}.py'
                if is_dynamic(target):
                    continue
                    
                # Basic check: does the file exist?
                if target not in existing_pages:
                    broken_links.append({
                        "file": str(file_path.relative_to(BASE_DIR)),
                        "target": target,
                        "status": "MISSING"
                    })
        except Exception as e:
            # Skip files that can't be read (binary etc, though we only look for .py)
            continue

    if broken_links:
        report = "\n".join([f"❌ In {b['file']}: target '{b['target']}' is missing!" for b in broken_links])
        pytest.fail(f"Broken links detected:\n{report}")

def test_markdown_absolute_links():
    """
    Checks for broken file:// links in documentation.
    """
    docs_dir = BASE_DIR / "docs"
    brain_dir = Path("/Users/aurelien/.gemini/antigravity/brain")
    
    md_files = list(BASE_DIR.glob("*.md"))
    if docs_dir.exists():
        md_files.extend(list(docs_dir.rglob("*.md")))
    if brain_dir.exists():
        md_files.extend(list(brain_dir.rglob("*.md")))

    broken_md_links = []
    # Regex for [text](file:///absolute/path)
    MD_FILE_LINK_REGEX = re.compile(r'\[[^\]]*\]\(file:\/\/(\/[^)]+)\)')

    for md_path in md_files:
        try:
            content = md_path.read_text(encoding='utf-8')
            matches = MD_FILE_LINK_REGEX.findall(content)
            
            for path_str in matches:
                # Some links might have #L123 fragments
                clean_path = path_str.split('#')[0]
                if not os.path.exists(clean_path):
                    broken_md_links.append({
                        "file": str(md_path),
                        "target": clean_path
                    })
        except Exception:
            continue

    # We don't fail the whole build for doc links, but we report them
    if broken_md_links:
        print(f"\n⚠️  {len(broken_md_links)} broken documentation links found.")

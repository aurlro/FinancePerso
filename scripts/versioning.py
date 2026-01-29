import re
import subprocess
import os
from datetime import datetime

CONSTANTS_PATH = "modules/constants.py"
CHANGELOG_PATH = "CHANGELOG.md"

def get_current_version():
    with open(CONSTANTS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'APP_VERSION = "([^"]+)"', content)
    return match.group(1) if match else "0.0.0"

def get_commits_since_last_version(current_version):
    # This assumes we might have git tags for versions, or we just look for the last commit that touched constants.py with that version.
    # Simpler: just get commits since the last time CHANGELOG.md was updated (which should be per version).
    
    # Let's try to find the last tag or just recent commits if no tag exists.
    try:
        # Get the hash of the last commit that modified CHANGELOG.md
        last_log_commit = subprocess.check_output(["git", "log", "-n", "1", "--format=%H", "--", CHANGELOG_PATH]).decode().strip()
        # Get commits since that hash
        commits = subprocess.check_output(["git", "log", f"{last_log_commit}..HEAD", "--oneline"]).decode().strip().split("\n")
        return [c for c in commits if c]
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
        # Fallback to last 10 commits if something fails (e.g., no git history, no CHANGELOG.md)
        try:
            return subprocess.check_output(["git", "log", "-n", "10", "--oneline"]).decode().strip().split("\n")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            # No git available or not a git repo
            return []

def determine_new_version(current_version, commits):
    """
    Determines the next version based on Semantic Versioning (SemVer) principles:
    - MAJOR: Breaking changes (e.g., 'feat!:' or 'BREAKING CHANGE' in commit message).
    - MINOR: New features ('feat:').
    - PATCH: Bug fixes ('fix:'), performance ('perf:'), or refactoring ('refactor:').
    - SKIP: Documentation ('docs:'), maintenance ('chore:'), tests ('test:'), or style ('style:').
    """
    major, minor, patch = map(int, current_version.split("."))
    
    # Categorize commits based on Conventional Commits
    has_breaking = False
    has_feat = False
    has_fix = False
    has_functional_change = False
    
    meaningful_commits = []
    
    for commit in commits:
        parts = commit.split(" ", 1)
        if len(parts) < 2: continue
        msg = parts[1].lower()
        
        # Check for breaking change
        if "breaking change" in msg or "!" in msg.split(":")[0]:
            has_breaking = True
        
        # Check types
        if msg.startswith("feat:"):
            has_feat = True
            has_functional_change = True
            meaningful_commits.append(commit)
        elif msg.startswith("fix:") or msg.startswith("perf:") or msg.startswith("refactor:"):
            has_fix = True
            has_functional_change = True
            meaningful_commits.append(commit)
        elif not msg.startswith(("docs:", "chore:", "test:", "style:")):
            # Any other unknown type that isn't explicitly "non-functional"
            has_functional_change = True
            meaningful_commits.append(commit)

    # Decision logic
    if not meaningful_commits:
        return None, [] # No functional update

    if has_breaking:
        major += 1
        minor = 0
        patch = 0
    elif has_feat:
        minor += 1
        patch = 0
    else:
        patch += 1
        
    return f"{major}.{minor}.{patch}", meaningful_commits

def update_constants(new_version):
    with open(CONSTANTS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = re.sub(r'APP_VERSION = "[^"]+"', f'APP_VERSION = "{new_version}"', content)
    with open(CONSTANTS_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

def update_changelog(new_version, commits):
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Group commits
    added = []
    fixed = []
    other = []
    
    for commit in commits:
        parts = commit.split(" ", 1)
        if len(parts) < 2: continue
        msg = parts[1]
        
        if msg.lower().startswith("feat:"):
            added.append(msg[5:].strip())
        elif msg.lower().startswith("fix:"):
            fixed.append(msg[4:].strip())
        else:
            other.append(msg)

    new_entry = f"\n## [{new_version}] - {date_str}\n"
    if added:
        new_entry += "\n### Ajouté\n"
        for item in added:
            new_entry += f"- {item}\n"
    if fixed:
        new_entry += "\n### Corrigé\n"
        for item in fixed:
            new_entry += f"- {item}\n"
    if other and not added and not fixed:
        new_entry += "\n### Autres\n"
        for item in other:
            new_entry += f"- {item}\n"
            
    new_entry += "\n---\n"

    with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    # Find the line after "---" separator for the header intro
    insert_idx = 7 # Default based on current file structure (after line 7)
    for i, line in enumerate(lines):
        if line.strip() == "---":
            insert_idx = i + 1
            break
            
    lines.insert(insert_idx, new_entry)
    
    with open(CHANGELOG_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

def main():
    if not os.path.exists(".git"):
        print("Erreur: Pas un dépôt git.")
        return

    current = get_current_version()
    raw_commits = get_commits_since_last_version(current)
    
    if not raw_commits:
        print("Aucun nouveau commit détecté.")
        return

    new_v, meaningful = determine_new_version(current, raw_commits)
    
    if new_v is None:
        print("Aucune remise à jour réelle détectée (seulement des changements mineurs types docs/chore).")
        return

    print(f"Passage de version: {current} -> {new_v}")
    print(f"Basé sur {len(meaningful)} modifications fonctionnelles :")
    for c in meaningful:
        print(f"  - {c}")
    
    update_constants(new_v)
    update_changelog(new_v, meaningful)
    print("\n✅ Mise à jour effectuée avec succès.")

if __name__ == "__main__":
    main()

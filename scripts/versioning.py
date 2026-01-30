import re
import subprocess
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional

CONSTANTS_PATH = "modules/constants.py"
CHANGELOG_PATH = "CHANGELOG.md"

# Emoji mapping for change types
EMOJI_MAP = {
    "feat": "✨",
    "fix": "🐛",
    "security": "🔒",
    "perf": "⚡",
    "refactor": "🔄",
    "docs": "📚",
    "test": "✅",
    "chore": "🔧",
    "ui": "🎨",
    "api": "🔌",
    "db": "💾",
    "config": "⚙️"
}

def get_current_version():
    """Get current version from constants.py"""
    with open(CONSTANTS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'APP_VERSION = "([^"]+)"', content)
    return match.group(1) if match else "0.0.0"


def get_detailed_commits_since_last_version():
    """
    Get detailed commit information including full body and files changed.
    Returns list of commit dictionaries.
    """
    try:
        # Get the hash of the last commit that modified CHANGELOG.md
        last_log_commit = subprocess.check_output(
            ["git", "log", "-n", "1", "--format=%H", "--", CHANGELOG_PATH]
        ).decode().strip()

        # Get detailed commits since that hash
        commits_raw = subprocess.check_output([
            "git", "log",
            f"{last_log_commit}..HEAD",
            "--format=COMMIT_SEP%n%H%n%s%n%b",
            "--name-only"
        ]).decode().strip()

    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        # Fallback to last 10 commits
        try:
            commits_raw = subprocess.check_output([
                "git", "log",
                "-n", "10",
                "--format=COMMIT_SEP%n%H%n%s%n%b",
                "--name-only"
            ]).decode().strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

    # Parse commits
    commits = []
    commit_blocks = commits_raw.split("COMMIT_SEP\n")

    for block in commit_blocks:
        if not block.strip():
            continue

        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue

        commit_hash = lines[0]
        subject = lines[1]

        # Extract body and files
        body_lines = []
        files = []
        in_body = True

        for line in lines[2:]:
            if line.strip() == "":
                continue
            # Files don't have spaces at start and look like paths
            if "/" in line or line.endswith(".py") or line.endswith(".md"):
                in_body = False
                files.append(line.strip())
            elif in_body:
                body_lines.append(line.strip())

        commits.append({
            "hash": commit_hash,
            "subject": subject,
            "body": body_lines,
            "files": files
        })

    return commits


def categorize_commit(commit: Dict) -> Tuple[str, bool, bool]:
    """
    Categorize commit and determine version impact.
    Returns (type, is_breaking, is_meaningful)
    """
    subject = commit["subject"].lower()
    body_text = " ".join(commit["body"]).lower()

    # Check for breaking change
    is_breaking = "breaking change" in body_text or "!" in subject.split(":")[0]

    # Determine type
    commit_type = "other"
    for ctype in ["feat", "fix", "security", "perf", "refactor", "docs", "test", "chore"]:
        if subject.startswith(f"{ctype}:") or subject.startswith(f"{ctype}!:"):
            commit_type = ctype
            break

    # Determine if meaningful (functional change)
    is_meaningful = commit_type not in ["docs", "test", "chore", "style"]

    return commit_type, is_breaking, is_meaningful


def determine_new_version(current_version: str, commits: List[Dict]) -> Tuple[Optional[str], List[Dict]]:
    """
    Determine next version based on commits.
    Returns (new_version, meaningful_commits)
    """
    major, minor, patch = map(int, current_version.split("."))

    has_breaking = False
    has_feat = False
    has_fix = False
    meaningful_commits = []

    for commit in commits:
        commit_type, is_breaking, is_meaningful = categorize_commit(commit)

        if not is_meaningful:
            continue

        meaningful_commits.append(commit)

        if is_breaking:
            has_breaking = True
        if commit_type == "feat":
            has_feat = True
        if commit_type in ["fix", "security", "perf"]:
            has_fix = True

    if not meaningful_commits:
        return None, []

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


def generate_rich_changelog_entry(version: str, commits: List[Dict]) -> str:
    """
    Generate a rich, detailed changelog entry with sections and emojis.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Group commits by type and analyze details
    grouped = {
        "security": [],
        "feat": [],
        "fix": [],
        "refactor": [],
        "perf": [],
        "other": []
    }

    breaking_changes = []

    for commit in commits:
        commit_type, is_breaking, _ = categorize_commit(commit)

        if is_breaking:
            breaking_changes.append(commit)

        # Extract details from commit
        details = {
            "subject": commit["subject"],
            "body": commit["body"],
            "files": commit["files"],
            "type": commit_type
        }

        if commit_type in grouped:
            grouped[commit_type].append(details)
        else:
            grouped["other"].append(details)

    # Build changelog entry
    entry = f"\n## [{version}] - {date_str}\n\n"

    # Security section
    if grouped["security"]:
        entry += "### 🔒 Sécurité et Validation\n\n"
        for commit in grouped["security"]:
            entry += format_commit_details(commit)
        entry += "\n"

    # Features section
    if grouped["feat"]:
        entry += "### ✨ Nouvelles Fonctionnalités\n\n"
        for commit in grouped["feat"]:
            entry += format_commit_details(commit)
        entry += "\n"

    # Fixes section
    if grouped["fix"]:
        entry += "### 🐛 Corrections\n\n"
        for commit in grouped["fix"]:
            entry += format_commit_details(commit)
        entry += "\n"

    # Refactoring section
    if grouped["refactor"]:
        entry += "### 🔄 Améliorations Techniques\n\n"
        for commit in grouped["refactor"]:
            entry += format_commit_details(commit)
        entry += "\n"

    # Performance section
    if grouped["perf"]:
        entry += "### ⚡ Performances\n\n"
        for commit in grouped["perf"]:
            entry += format_commit_details(commit)
        entry += "\n"

    # Breaking changes section
    if breaking_changes:
        entry += "### ⚠️ Breaking Changes\n\n"
        for commit in breaking_changes:
            # Extract breaking change description from body
            breaking_desc = ""
            for line in commit["body"]:
                if "breaking change" in line.lower():
                    breaking_desc = line
                    break
            entry += f"**{extract_title(commit['subject'])}**\n\n"
            if breaking_desc:
                entry += f"- {breaking_desc}\n"
            for line in commit["body"]:
                if line and line != breaking_desc and not line.startswith("Co-Authored"):
                    entry += f"- {line}\n"
            entry += "\n"

    entry += "---\n"
    return entry


def extract_title(subject: str) -> str:
    """Extract clean title from commit subject"""
    # Remove type prefix (feat:, fix:, etc.)
    title = re.sub(r'^[a-z]+(!)?:\s*', '', subject, flags=re.IGNORECASE)
    return title.strip()


def format_commit_details(commit_details: Dict) -> str:
    """Format a single commit with its details"""
    output = ""

    # Main title
    title = extract_title(commit_details["subject"])
    output += f"**{title}**\n"

    # Body details as bullet points
    if commit_details["body"]:
        for line in commit_details["body"]:
            # Skip empty lines and co-authored lines
            if line and not line.startswith("Co-Authored"):
                # Check if line is already a bullet point
                if line.startswith("-"):
                    output += f"{line}\n"
                else:
                    output += f"- {line}\n"

    # Files modified (only if significant)
    if commit_details["files"]:
        key_files = [f for f in commit_details["files"] if not f.startswith("tests/")]
        if key_files and len(key_files) <= 5:  # Only show if reasonable number
            output += f"\n*Fichiers modifiés* : {', '.join([f'`{f}`' for f in key_files[:3]])}"
            if len(key_files) > 3:
                output += f" (+{len(key_files) - 3} autres)"
            output += "\n"

    output += "\n"
    return output


def update_constants(new_version: str):
    """Update APP_VERSION in constants.py"""
    with open(CONSTANTS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = re.sub(
        r'APP_VERSION = "[^"]+"',
        f'APP_VERSION = "{new_version}"',
        content
    )
    with open(CONSTANTS_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)


def update_changelog(new_version: str, commits: List[Dict]):
    """Update CHANGELOG.md with new entry"""
    new_entry = generate_rich_changelog_entry(new_version, commits)

    with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find insertion point (after first ---)
    insert_idx = 7
    for i, line in enumerate(lines):
        if line.strip() == "---":
            insert_idx = i + 1
            break

    lines.insert(insert_idx, new_entry)

    with open(CHANGELOG_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)


def main():
    """Main versioning workflow"""
    if not os.path.exists(".git"):
        print("❌ Erreur: Pas un dépôt git.")
        return

    print("🔍 Analyse des commits...")
    current = get_current_version()
    all_commits = get_detailed_commits_since_last_version()

    if not all_commits:
        print("ℹ️  Aucun nouveau commit détecté.")
        return

    print(f"📦 {len(all_commits)} commit(s) trouvé(s)")

    new_v, meaningful = determine_new_version(current, all_commits)

    if new_v is None:
        print("ℹ️  Aucune mise à jour fonctionnelle (docs/chore/test uniquement).")
        return

    print(f"\n🎯 Version: {current} → {new_v}")
    print(f"📝 {len(meaningful)} commit(s) fonctionnel(s):\n")

    for commit in meaningful:
        commit_type, is_breaking, _ = categorize_commit(commit)
        emoji = EMOJI_MAP.get(commit_type, "📌")
        breaking_mark = " ⚠️ BREAKING" if is_breaking else ""
        print(f"  {emoji} {extract_title(commit['subject'])}{breaking_mark}")

    print(f"\n📝 Génération du CHANGELOG détaillé...")
    update_constants(new_v)
    update_changelog(new_v, meaningful)

    print(f"\n✅ Mise à jour terminée !")
    print(f"   Version: {new_v}")
    print(f"   Fichiers modifiés: {CONSTANTS_PATH}, {CHANGELOG_PATH}")
    print(f"\n💡 N'oubliez pas de commit et push ces changements.")


if __name__ == "__main__":
    main()

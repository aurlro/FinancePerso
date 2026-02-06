"""
Update Manager for FinancePerso.
Handles changelog updates, version management, and agent file synchronization.
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from modules.logger import logger


@dataclass
class VersionEntry:
    """Represents a version entry."""
    version: str
    date: str
    title: str
    categories: Dict[str, List[str]]  # category -> list of changes
    files_modified: List[str]
    breaking_changes: List[str]


class UpdateManager:
    """Manages application updates and documentation synchronization."""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize update manager.
        
        Args:
            project_root: Root directory of the project. If None, uses current directory.
        """
        self.project_root = project_root or os.getcwd()
        self.changelog_path = os.path.join(self.project_root, "CHANGELOG.md")
        self.agents_path = os.path.join(self.project_root, "AGENTS.md")
        self.readme_path = os.path.join(self.project_root, "README.md")
        self.constants_path = os.path.join(self.project_root, "modules", "constants.py")
    
    def get_current_version(self) -> str:
        """
        Extract current version from constants.py or changelog.
        
        Returns:
            Current version string (e.g., "3.5.0")
        """
        # Try constants.py first
        if os.path.exists(self.constants_path):
            try:
                with open(self.constants_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = re.search(r'APP_VERSION\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)
            except Exception as e:
                logger.warning(f"Could not read constants.py: {e}")
        
        # Fallback to changelog
        try:
            with open(self.changelog_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'## \[?([0-9]+\.[0-9]+\.[0-9]+)\]?', content)
                if match:
                    return match.group(1)
        except Exception as e:
            logger.warning(f"Could not read CHANGELOG.md: {e}")
        
        return "0.0.0"
    
    def bump_version(self, version: str, bump_type: str = "patch") -> str:
        """
        Bump version number.
        
        Args:
            version: Current version (e.g., "3.5.0")
            bump_type: Type of bump: "patch", "minor", or "major"
            
        Returns:
            New version string
        """
        parts = version.split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        return f"{major}.{minor}.{patch}"
    
    def add_changelog_entry(self, entry: VersionEntry) -> bool:
        """
        Add a new entry to CHANGELOG.md.
        
        Args:
            entry: Version entry to add
            
        Returns:
            True if successful
        """
        try:
            # Read existing content
            if os.path.exists(self.changelog_path):
                with open(self.changelog_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = "# Changelog\n\nToutes les modifications notables...\n"
            
            # Build new entry
            new_entry = self._format_changelog_entry(entry)
            
            # Insert after header (find first ## and insert before it)
            lines = content.split('\n')
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('##'):
                    insert_idx = i
                    break
            
            lines.insert(insert_idx, new_entry)
            
            # Write back
            with open(self.changelog_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            logger.info(f"Added changelog entry for v{entry.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add changelog entry: {e}")
            return False
    
    def _format_changelog_entry(self, entry: VersionEntry) -> str:
        """Format version entry for changelog."""
        lines = [
            f"## [{entry.version}] - {entry.date}",
            "",
            f"### {entry.title}",
            ""
        ]
        
        # Add categories
        emoji_map = {
            "added": "✨ Ajouté",
            "changed": "🔄 Modifié", 
            "deprecated": "⚠️ Déprécié",
            "removed": "🗑️ Supprimé",
            "fixed": "🐛 Corrigé",
            "security": "🔒 Sécurité",
            "performance": "⚡ Performance"
        }
        
        for category, items in entry.categories.items():
            if items:
                header = emoji_map.get(category, f"### {category.title()}")
                lines.append(f"**{header}**")
                for item in items:
                    lines.append(f"- {item}")
                lines.append("")
        
        # Add breaking changes
        if entry.breaking_changes:
            lines.append("**⚠️ Breaking Changes**")
            for change in entry.breaking_changes:
                lines.append(f"- {change}")
            lines.append("")
        
        # Add files modified
        if entry.files_modified:
            lines.append(f"*Fichiers modifiés* : {', '.join(entry.files_modified)}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        return '\n'.join(lines)
    
    def update_agents_md(self, entry: VersionEntry) -> bool:
        """
        Update AGENTS.md with new version info.
        
        Args:
            entry: Version entry
            
        Returns:
            True if successful
        """
        try:
            if not os.path.exists(self.agents_path):
                logger.warning("AGENTS.md not found")
                return False
            
            with open(self.agents_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update version in header if present
            version_pattern = r'\*\*Version du projet\*\*:?\s*\*?`?v?([0-9]+\.[0-9]+\.[0-9]+)`?\*?'
            if re.search(version_pattern, content):
                content = re.sub(
                    version_pattern,
                    f'**Version du projet**: `v{entry.version}`',
                    content
                )
            else:
                # Add version near top if not present
                lines = content.split('\n')
                for i, line in enumerate(lines[:10]):
                    if line.startswith('# ') and 'AGENTS' in line.upper():
                        lines.insert(i+1, f"> **Version du projet**: `v{entry.version}`")
                        lines.insert(i+2, ">")
                        break
                content = '\n'.join(lines)
            
            # Update last modified date
            date_pattern = r'\*\*Dernière mise à jour\*\*\s*:?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})?'
            if re.search(date_pattern, content):
                content = re.sub(
                    date_pattern,
                    f'**Dernière mise à jour** : {entry.date}',
                    content
                )
            
            # Add new features to feature list if present
            if 'added' in entry.categories and entry.categories['added']:
                # Find feature list section
                feature_section = re.search(
                    r'### Fonctionnalités principales.*?(?=###|\Z)',
                    content,
                    re.DOTALL
                )
                if feature_section:
                    # Add new features
                    new_features = entry.categories['added'][:3]  # Top 3
                    for feature in new_features:
                        # Check if already present
                        if feature.split(':')[0] not in content:
                            # Add to list
                            section_end = feature_section.end()
                            insertion = f"\n- {feature}"
                            content = content[:section_end] + insertion + content[section_end:]
            
            with open(self.agents_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Updated AGENTS.md for v{entry.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update AGENTS.md: {e}")
            return False
    
    def update_constants(self, version: str) -> bool:
        """
        Update version in constants.py.
        
        Args:
            version: New version
            
        Returns:
            True if successful
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.constants_path), exist_ok=True)
            
            if not os.path.exists(self.constants_path):
                # Create constants.py if not exists
                with open(self.constants_path, 'w', encoding='utf-8') as f:
                    f.write(f'"""Application constants."""\n\n')
                    f.write(f'APP_VERSION = "{version}"\n')
                    f.write(f'APP_NAME = "MyFinance Companion"\n')
                logger.info(f"Created constants.py with v{version}")
                return True
            
            with open(self.constants_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update version
            if 'APP_VERSION' in content:
                content = re.sub(
                    r'APP_VERSION\s*=\s*["\'][^"\']+["\']',
                    f'APP_VERSION = "{version}"',
                    content
                )
            else:
                content += f'\nAPP_VERSION = "{version}"\n'
            
            with open(self.constants_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Updated constants.py to v{version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update constants.py: {e}")
            return False
    
    def create_update(self, 
                     title: str,
                     changes: Dict[str, List[str]],
                     bump_type: str = "patch",
                     files_modified: Optional[List[str]] = None,
                     breaking_changes: Optional[List[str]] = None,
                     force: bool = False) -> Tuple[bool, str]:
        """
        Create a complete update across all files.
        
        Args:
            title: Title for this update
            changes: Dict of category -> list of changes
            bump_type: "patch", "minor", or "major"
            files_modified: List of modified files
            breaking_changes: List of breaking changes
            force: If True, bypass duplicate detection
            
        Returns:
            Tuple of (success, new_version_or_error_message)
        """
        # Check for duplicate with last entry (unless forced)
        if not force:
            recent = self.get_recent_changes(count=1)
            if recent:
                last_entry = recent[0]
                # Compare changes content (normalize and compare)
                last_content = last_entry.get('content', '').lower().strip()
                
                # Build a signature from current changes
                current_items = []
                for category, items in changes.items():
                    for item in items:
                        # Clean the item (remove leading "- " if present)
                        clean_item = item.lstrip('- ').lower().strip()
                        current_items.append(clean_item)
                
                # Check if all current items exist in the last entry
                if current_items:
                    matches = sum(1 for item in current_items if item in last_content)
                    match_ratio = matches / len(current_items)
                    
                    if match_ratio > 0.8:  # 80% similarity threshold
                        logger.warning(f"Duplicate update detected: {match_ratio:.0%} similar to v{last_entry.get('version')}")
                        return False, f"Cette mise à jour est identique à la version précédente (v{last_entry.get('version')}). Cochez 'Forcer la création' pour ignorer cette alerte."
        
        current_version = self.get_current_version()
        new_version = self.bump_version(current_version, bump_type)
        
        entry = VersionEntry(
            version=new_version,
            date=datetime.now().strftime("%Y-%m-%d"),
            title=title,
            categories=changes,
            files_modified=files_modified or [],
            breaking_changes=breaking_changes or []
        )
        
        # Update all files
        success = True
        
        if not self.add_changelog_entry(entry):
            success = False
        
        if not self.update_agents_md(entry):
            success = False
        
        if not self.update_constants(new_version):
            success = False
        
        return success, new_version
    
    def get_recent_changes(self, count: int = 5) -> List[Dict]:
        """
        Get recent changes from changelog.
        
        Args:
            count: Number of recent versions to return
            
        Returns:
            List of version dictionaries
        """
        try:
            from modules.ui.changelog_parser import parse_changelog
            versions = parse_changelog(self.changelog_path)
            return versions[:count]
        except Exception as e:
            logger.error(f"Failed to parse changelog: {e}")
            return []
    
    def analyze_git_changes(self) -> Dict:
        """
        Analyze git changes since last version tag.
        
        Includes both committed changes (since last tag) and uncommitted changes
        (staged and unstaged) to reflect the most recent "live" work.
        
        Returns:
            Dict with detected changes:
            {
                'files_modified': List[str],           # All relevant files changed
                'committed_files': List[str],          # Files changed in commits
                'uncommitted_files': List[str],        # Local unstaged/staged files
                'uncommitted_status': Dict[str, str],  # File -> status mapping
                'added': List[str],                    # Features added (from commits)
                'fixed': List[str],                    # Bugs fixed (from commits)
                'performance': List[str],              # Performance improvements
                'other': List[str],                    # Other commits
                'suggested_title': str,
                'suggested_bump': str,
                'has_committed_changes': bool,         # True if commits since tag
                'has_uncommitted_changes': bool,       # True if local modifications exist
            }
        """
        import subprocess
        
        result = {
            'files_modified': [],
            'committed_files': [],
            'uncommitted_files': [],
            'uncommitted_status': {},
            'added': [],
            'fixed': [],
            'performance': [],
            'other': [],
            'suggested_title': '',
            'suggested_bump': 'patch',
            'has_committed_changes': False,
            'has_uncommitted_changes': False,
        }
        
        try:
            # Check if we're in a git repo first
            git_check = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True, text=True, cwd=self.project_root
            )
            if git_check.returncode != 0:
                logger.warning("Not a git repository")
                return result
            
            # ==========================================
            # 1. Get uncommitted changes (staged + unstaged)
            # ==========================================
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, cwd=self.project_root
            )
            
            uncommitted_files = []
            uncommitted_status = {}
            
            if status_result.returncode == 0 and status_result.stdout.strip():
                for line in status_result.stdout.strip().split('\n'):
                    if len(line) < 3:
                        continue
                    
                    # Porcelain format: "XY path" or "XY orig_path -> new_path" for renames
                    status_code = line[:2]
                    file_path = line[3:].strip()
                    
                    # Handle renamed files (format: "R  old -> new")
                    if status_code[0] == 'R' or status_code[1] == 'R':
                        # Extract the new path after " -> "
                        if ' -> ' in file_path:
                            file_path = file_path.split(' -> ')[-1].strip()
                    
                    uncommitted_files.append(file_path)
                    uncommitted_status[file_path] = self._parse_git_status_code(status_code)
                
                result['uncommitted_files'] = self._filter_relevant_files(uncommitted_files)
                result['uncommitted_status'] = {k: v for k, v in uncommitted_status.items() 
                                                 if k in result['uncommitted_files']}
                result['has_uncommitted_changes'] = len(result['uncommitted_files']) > 0
            
            # ==========================================
            # 2. Get committed changes since last tag
            # ==========================================
            commit_range = self._get_commit_range_since_last_tag()
            
            committed_files = []
            if commit_range:
                files_result = subprocess.run(
                    ['git', 'diff', '--name-only', commit_range],
                    capture_output=True, text=True, cwd=self.project_root
                )
                if files_result.returncode == 0:
                    committed_files = [f.strip() for f in files_result.stdout.split('\n') if f.strip()]
                    result['committed_files'] = self._filter_relevant_files(committed_files)
                    result['has_committed_changes'] = len(result['committed_files']) > 0
                
                # Get commit messages for categorization
                commits_result = subprocess.run(
                    ['git', 'log', '--pretty=format:%s', commit_range],
                    capture_output=True, text=True, cwd=self.project_root
                )
                
                if commits_result.returncode == 0:
                    commits = commits_result.stdout.strip().split('\n') if commits_result.stdout.strip() else []
                    self._categorize_commits(commits, result)
            
            # ==========================================
            # 3. Merge all files and generate suggestions
            # ==========================================
            all_files = list(set(committed_files + uncommitted_files))
            result['files_modified'] = self._filter_relevant_files(all_files)
            
            # Generate title based on all changes (committed + uncommitted context)
            result['suggested_title'] = self._generate_suggested_title(result)
            
            # Adjust bump type if uncommitted changes suggest major work
            if result['has_uncommitted_changes']:
                # Check uncommitted file names for major change indicators
                major_indicators = ['refactor', 'rewrite', 'breaking', 'api', 'arch']
                for f in result['uncommitted_files']:
                    if any(ind in f.lower() for ind in major_indicators):
                        if result['suggested_bump'] != 'major':
                            result['suggested_bump'] = 'minor'
                        break
                    
        except Exception as e:
            logger.error(f"Failed to analyze git changes: {e}")
        
        return result
    
    def _get_commit_range_since_last_tag(self) -> str:
        """
        Determine the commit range since the last version tag.
        
        Returns:
            Commit range string (e.g., "v3.5.0..HEAD") or empty string if no range.
        """
        import subprocess
        
        try:
            # Try to get the last version tag
            tag_result = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0', '--match', 'v*'],
                capture_output=True, text=True, cwd=self.project_root
            )
            
            if tag_result.returncode == 0 and tag_result.stdout.strip():
                last_tag = tag_result.stdout.strip()
                return f"{last_tag}..HEAD"
            
            # No version tags found, try any tag
            tag_result = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0'],
                capture_output=True, text=True, cwd=self.project_root
            )
            
            if tag_result.returncode == 0 and tag_result.stdout.strip():
                last_tag = tag_result.stdout.strip()
                return f"{last_tag}..HEAD"
            
            # No tags at all - get last N commits safely
            count_result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                capture_output=True, text=True, cwd=self.project_root
            )
            
            if count_result.returncode == 0:
                total_commits = int(count_result.stdout.strip())
                if total_commits == 0:
                    return ""  # Empty repo
                elif total_commits == 1:
                    return "HEAD"  # Single commit
                else:
                    window = min(total_commits - 1, 20)  # Up to 20 commits
                    if window > 0:
                        return f"HEAD~{window}..HEAD"
            
            return ""
            
        except Exception as e:
            logger.warning(f"Could not determine commit range: {e}")
            return ""
    
    def _parse_git_status_code(self, code: str) -> str:
        """
        Parse git status porcelain code to human-readable status.
        
        Args:
            code: Two-character status code (e.g., 'M ', ' M', '??')
            
        Returns:
            Human-readable status description.
        """
        # X = index status, Y = worktree status
        index_status = code[0] if len(code) > 0 else ' '
        worktree_status = code[1] if len(code) > 1 else ' '
        
        status_map = {
            ' ': 'unchanged',
            'M': 'modified',
            'A': 'added',
            'D': 'deleted',
            'R': 'renamed',
            'C': 'copied',
            'U': 'updated',
            '?': 'untracked',
            '!': 'ignored',
        }
        
        index_desc = status_map.get(index_status, 'unknown')
        worktree_desc = status_map.get(worktree_status, 'unknown')
        
        # Build description
        if index_status == '?' and worktree_status == '?':
            return 'untracked'
        elif index_status != ' ' and worktree_status == ' ':
            return f'staged ({index_desc})'
        elif index_status == ' ' and worktree_status != ' ':
            return f'unstaged ({worktree_desc})'
        elif index_status != ' ' and worktree_status != ' ':
            return f'staged + unstaged changes'
        else:
            return 'unknown'
    
    def _categorize_commits(self, commits: List[str], result: Dict):
        """
        Categorize commit messages into added/fixed/performance/other.
        
        Args:
            commits: List of commit message strings
            result: Result dict to populate
        """
        add_patterns = [
            r'add', r'new', r'feature', r'implement', r'ajout', r'nouveau',
            r'création', r'crée', r'implémente', r'✨'
        ]
        fix_patterns = [
            r'fix', r'bug', r'correct', r'resolve', r'repair', r'corrig',
            r'résolu', r'résolution', r'🐛', r'🩹'
        ]
        perf_patterns = [
            r'perf', r'optimiz', r'speed', r'fast', r'cache', r'memory',
            r'optimis', r'rapid', r'performance', r'⚡'
        ]
        major_patterns = [
            r'break', r'remov', r'delet', r'refactor', r'rewrite',
            r'refacto', r'suppress', r'🗑️', r'💥'
        ]
        
        for commit in commits:
            commit_lower = commit.lower()
            
            # Skip merge commits
            if commit_lower.startswith('merge'):
                continue
            
            # Check patterns
            if any(re.search(p, commit_lower) for p in add_patterns):
                result['added'].append(commit)
            elif any(re.search(p, commit_lower) for p in fix_patterns):
                result['fixed'].append(commit)
            elif any(re.search(p, commit_lower) for p in perf_patterns):
                result['performance'].append(commit)
            else:
                result['other'].append(commit)
            
            # Check for major changes
            if any(re.search(p, commit_lower) for p in major_patterns):
                result['suggested_bump'] = 'major'
        
        # Adjust bump type based on categories
        if result['suggested_bump'] != 'major' and result['added']:
            result['suggested_bump'] = 'minor'
    
    def _generate_suggested_title(self, result: Dict) -> str:
        """
        Generate a suggested title based on detected changes.
        
        Args:
            result: Analysis result dict
            
        Returns:
            Suggested title string
        """
        has_committed = result.get('has_committed_changes', False)
        has_uncommitted = result.get('has_uncommitted_changes', False)
        
        # Count all changes
        added_count = len(result.get('added', []))
        fixed_count = len(result.get('fixed', []))
        perf_count = len(result.get('performance', []))
        other_count = len(result.get('other', []))
        uncommitted_count = len(result.get('uncommitted_files', []))
        
        # Build context prefix
        context = ""
        if has_committed and has_uncommitted:
            context = " (commits + local)"
        elif has_uncommitted and not has_committed:
            context = " (local changes)"
        
        # Determine title based on dominant change type
        if added_count > 0:
            if added_count == 1:
                return f"Nouvelle fonctionnalité{context}"
            return f"Nouvelles fonctionnalités - {added_count} ajouts{context}"
        elif fixed_count > 0:
            if fixed_count == 1:
                return f"Correction de bug{context}"
            return f"Corrections - {fixed_count} bugs résolus{context}"
        elif perf_count > 0:
            if perf_count == 1:
                return f"Optimisation{context}"
            return f"Optimisations - {perf_count} améliorations{context}"
        elif uncommitted_count > 0:
            if uncommitted_count == 1:
                return f"Modification en cours{context}"
            return f"Modifications en cours - {uncommitted_count} fichiers{context}"
        elif other_count > 0:
            return f"Mise à jour diverses{context}"
        else:
            return "Mise à jour"
    
    def get_module_changes(self) -> Dict:
        """
        Analyze changes by scanning modules directory.
        Useful when git is not available.
        
        Returns:
            Dict with detected new/modified modules
        """
        result = {
            'files_modified': [],
            'added': [],
            'suggested_title': 'Mise à jour des modules'
        }
        
        try:
            modules_dir = os.path.join(self.project_root, 'modules')
            pages_dir = os.path.join(self.project_root, 'pages')
            
            # Scan for recently modified files (last 7 days)
            cutoff_time = datetime.now().timestamp() - (7 * 24 * 3600)
            
            for directory in [modules_dir, pages_dir]:
                if not os.path.exists(directory):
                    continue
                    
                for root, dirs, files in os.walk(directory):
                    # Skip __pycache__ and backups
                    dirs[:] = [d for d in dirs if d not in ['__pycache__', '.pytest_cache']]
                    
                    for file in files:
                        if not file.endswith('.py'):
                            continue
                        if 'backup' in file.lower():
                            continue
                            
                        filepath = os.path.join(root, file)
                        rel_path = os.path.relpath(filepath, self.project_root)
                        
                        try:
                            mtime = os.path.getmtime(filepath)
                            if mtime > cutoff_time:
                                result['files_modified'].append(rel_path)
                                
                                # Try to extract docstring
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                                    if doc_match:
                                        first_line = doc_match.group(1).strip().split('\n')[0]
                                        if first_line:
                                            result['added'].append(f"{rel_path}: {first_line}")
                        except Exception:
                            pass
                            
        except Exception as e:
            logger.error(f"Failed to scan module changes: {e}")
        
    def _filter_relevant_files(self, files: List[str]) -> List[str]:
        """Filter list of files to keep only relevant extensions."""
        relevant_extensions = ['.py', '.md', '.toml', '.txt', '.css', '.js', '.html']
        return [
            f for f in files 
            if any(f.endswith(ext) for f in [f.lower()] for ext in relevant_extensions)
        ]


# Convenience functions
def get_update_manager() -> UpdateManager:
    """Get singleton update manager instance."""
    return UpdateManager()


def quick_update(title: str, changes: List[str], bump_type: str = "patch") -> Tuple[bool, str]:
    """
    Quick update with default categorization.
    
    Args:
        title: Update title
        changes: List of changes (will be categorized as "added")
        bump_type: Version bump type
        
    Returns:
        Tuple of (success, new_version)
    """
    manager = get_update_manager()
    return manager.create_update(
        title=title,
        changes={"added": changes},
        bump_type=bump_type
    )


__all__ = [
    'UpdateManager',
    'VersionEntry',
    'get_update_manager',
    'quick_update',
]

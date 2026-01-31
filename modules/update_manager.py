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
                     breaking_changes: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Create a complete update across all files.
        
        Args:
            title: Title for this update
            changes: Dict of category -> list of changes
            bump_type: "patch", "minor", or "major"
            files_modified: List of modified files
            breaking_changes: List of breaking changes
            
        Returns:
            Tuple of (success, new_version)
        """
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

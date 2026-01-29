import re
import os
from datetime import datetime

def parse_changelog(file_path):
    """
    Parses a CHANGELOG.md file and returns a list of dictionaries.
    Format:
    [
        {
            "version": "2.2.0",
            "date": "2026-01-29",
            "content": "### Category\n- Note 1\n- Note 2"
        },
        ...
    ]
    """
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by version headers (## [version] - date or ## version - date)
    # Regex to match ## [v1.2.3] - 2023-01-01 or ## v1.2.3 - 2023-01-01
    version_blocks = re.split(r'\n## \[?([^\] ]+)\]?(?: - (\d{4}-\d{2}-\d{2}))?', content)
    
    # re.split with groups returns [prefix, version1, date1, content1, version2, date2, content2, ...]
    # The first element is the preamble (intro text)
    versions = []
    
    # Start from index 1, step by 3
    for i in range(1, len(version_blocks), 3):
        version = version_blocks[i]
        date = version_blocks[i+1] if i+1 < len(version_blocks) else None
        raw_content = version_blocks[i+2] if i+2 < len(version_blocks) else ""
        
        # Clean up content: remove trailing/leading whitespace and separators
        clean_content = raw_content.strip()
        if clean_content.startswith("---"):
            clean_content = clean_content[3:].strip()
            
        versions.append({
            "version": version,
            "date": date,
            "content": clean_content
        })
        
    return versions

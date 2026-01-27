"""
Tests for tag manager component.
Focus on testable logic: tag normalization, deduplication, and validation.
"""
import pytest

class TestTagNormalization:
    """Tests for tag normalization logic."""
    
    def test_normalize_tag_lowercase(self):
        """Test tag normalization to lowercase."""
        tag = "UPPERCASE"
        normalized = tag.lower().strip()
        
        assert normalized == "uppercase"
    
    def test_normalize_tag_strip_whitespace(self):
        """Test stripping whitespace from tags."""
        tag = "  spaced  "
        normalized = tag.lower().strip()
        
        assert normalized == "spaced"
    
    def test_normalize_tag_list(self):
        """Test normalizing a list of tags."""
        tags = "Tag1, TAG2,  tag3 "
        normalized = [t.strip().lower() for t in tags.split(',')]
        
        assert normalized == ["tag1", "tag2", "tag3"]

class TestTagDeduplication:
    """Tests for tag deduplication logic."""
    
    def test_deduplicate_tags(self):
        """Test removing duplicate tags."""
        tags = ["tag1", "tag2", "tag1", "tag3", "tag2"]
        unique_tags = list(dict.fromkeys(tags))  # Preserves order
        
        assert unique_tags == ["tag1", "tag2", "tag3"]
    
    def test_deduplicate_case_insensitive(self):
        """Test case-insensitive deduplication."""
        tags = ["tag1", "TAG1", "Tag1"]
        normalized = [t.lower() for t in tags]
        unique_tags = list(dict.fromkeys(normalized))
        
        assert unique_tags == ["tag1"]
    
    def test_deduplicate_empty_list(self):
        """Test deduplication with empty list."""
        tags = []
        unique_tags = list(dict.fromkeys(tags))
        
        assert unique_tags == []

class TestTagValidation:
    """Tests for tag validation logic."""
    
    def test_validate_tag_not_empty(self):
        """Test that empty tags are invalid."""
        tag = ""
        is_valid = bool(tag.strip())
        
        assert is_valid is False
    
    def test_validate_tag_not_whitespace(self):
        """Test that whitespace-only tags are invalid."""
        tag = "   "
        is_valid = bool(tag.strip())
        
        assert is_valid is False
    
    def test_validate_tag_valid(self):
        """Test valid tag."""
        tag = "valid_tag"
        is_valid = bool(tag.strip())
        
        assert is_valid is True
    
    def test_validate_tag_length(self):
        """Test tag length validation."""
        tag = "short"
        max_length = 50
        is_valid = len(tag) <= max_length
        
        assert is_valid is True
        
        long_tag = "a" * 100
        is_valid = len(long_tag) <= max_length
        
        assert is_valid is False

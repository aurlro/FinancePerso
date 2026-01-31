"""
Feature Flags system for FinancePerso.
Allows gradual rollout of new features and A/B testing.
"""

import os
import json
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
from modules.db.connection import get_db_connection
from modules.logger import logger


@dataclass
class FeatureFlag:
    """Represents a feature flag with its configuration."""
    name: str
    enabled: bool = False
    description: str = ""
    rollout_percentage: int = 0  # 0-100 for gradual rollout
    user_groups: Optional[list] = None  # List of allowed user groups
    
    def is_enabled_for(self, user_id: Optional[str] = None, user_group: Optional[str] = None) -> bool:
        """Check if feature is enabled for specific user."""
        if not self.enabled:
            return False
        
        # Check user group
        if self.user_groups and user_group:
            if user_group not in self.user_groups:
                return False
        
        # Check rollout percentage
        if self.rollout_percentage < 100 and user_id:
            # Deterministic check based on user_id hash
            import hashlib
            user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
            user_percentile = user_hash % 100
            return user_percentile < self.rollout_percentage
        
        return True


class FeatureFlagManager:
    """Manages feature flags with database persistence."""
    
    _instance = None
    _cache: Dict[str, FeatureFlag] = {}
    _cache_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _ensure_table(self):
        """Ensure feature_flags table exists."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feature_flags (
                    name TEXT PRIMARY KEY,
                    enabled INTEGER DEFAULT 0,
                    description TEXT,
                    rollout_percentage INTEGER DEFAULT 0,
                    user_groups TEXT,  -- JSON array
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def load_flags(self, force_refresh: bool = False):
        """Load all flags from database."""
        if self._cache_loaded and not force_refresh:
            return
        
        self._ensure_table()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feature_flags")
            rows = cursor.fetchall()
            
            for row in rows:
                name, enabled, description, rollout, groups_json, _ = row
                groups = json.loads(groups_json) if groups_json else None
                
                self._cache[name] = FeatureFlag(
                    name=name,
                    enabled=bool(enabled),
                    description=description or "",
                    rollout_percentage=rollout or 0,
                    user_groups=groups
                )
        
        self._cache_loaded = True
        logger.info(f"Loaded {len(self._cache)} feature flags")
    
    def is_enabled(self, flag_name: str, user_id: Optional[str] = None, 
                  user_group: Optional[str] = None) -> bool:
        """Check if a feature flag is enabled."""
        self.load_flags()
        
        flag = self._cache.get(flag_name)
        if not flag:
            # Check environment variable as fallback
            env_value = os.getenv(f"FF_{flag_name.upper()}", "false").lower()
            return env_value in ("true", "1", "yes", "on")
        
        return flag.is_enabled_for(user_id, user_group)
    
    def set_flag(self, flag: FeatureFlag):
        """Save or update a feature flag."""
        self._ensure_table()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO feature_flags 
                (name, enabled, description, rollout_percentage, user_groups, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                flag.name,
                int(flag.enabled),
                flag.description,
                flag.rollout_percentage,
                json.dumps(flag.user_groups) if flag.user_groups else None
            ))
            conn.commit()
        
        # Update cache
        self._cache[flag.name] = flag
        logger.info(f"Updated feature flag: {flag.name}")
    
    def get_all_flags(self) -> Dict[str, FeatureFlag]:
        """Get all feature flags."""
        self.load_flags()
        return self._cache.copy()
    
    def delete_flag(self, name: str):
        """Delete a feature flag."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM feature_flags WHERE name = ?", (name,))
            conn.commit()
        
        if name in self._cache:
            del self._cache[name]
    
    def enable(self, name: str, description: str = ""):
        """Quick enable a feature flag."""
        flag = FeatureFlag(name=name, enabled=True, description=description)
        self.set_flag(flag)
    
    def disable(self, name: str):
        """Quick disable a feature flag."""
        flag = self._cache.get(name, FeatureFlag(name=name))
        flag.enabled = False
        self.set_flag(flag)


# Global instance
_feature_manager = None

def get_feature_manager() -> FeatureFlagManager:
    """Get singleton feature flag manager."""
    global _feature_manager
    if _feature_manager is None:
        _feature_manager = FeatureFlagManager()
    return _feature_manager


def is_enabled(flag_name: str, user_id: Optional[str] = None, 
              user_group: Optional[str] = None) -> bool:
    """Quick check if feature is enabled."""
    return get_feature_manager().is_enabled(flag_name, user_id, user_group)


def require_feature(flag_name: str):
    """Decorator to require a feature flag for a function."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_enabled(flag_name):
                raise FeatureDisabledError(f"Feature '{flag_name}' is disabled")
            return func(*args, **kwargs)
        return wrapper
    return decorator


class FeatureDisabledError(Exception):
    """Raised when a required feature is disabled."""
    pass


# Predefined feature flags for the application
FEATURES = {
    'NEW_VALIDATION_UI': 'new_validation_interface',
    'AI_CHAT': 'ai_conversational_chat',
    'BUDGET_PREDICTIONS': 'budget_predictions_ml',
    'MOBILE_OPTIMIZED': 'mobile_responsive_ui',
    'ADVANCED_ANALYTICS': 'advanced_analytics_dashboard',
    'API_ACCESS': 'rest_api_access',
    'BANK_SYNC': 'bank_synchronization',
    'RECEIPT_SCANNER': 'receipt_ocr_scanner',
}


__all__ = [
    'FeatureFlag',
    'FeatureFlagManager',
    'get_feature_manager',
    'is_enabled',
    'require_feature',
    'FeatureDisabledError',
    'FEATURES',
]

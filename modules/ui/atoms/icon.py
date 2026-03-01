"""Atom Icon - Icônes et emojis standardisés.

Usage:
    from modules.ui.atoms import Icon
    
    Icon.success()   # -> "✓"
    Icon.warning()   # -> "⚠"
    Icon.for_category("alimentation")  # -> "🍽️"
"""

from enum import Enum


class IconSize(str, Enum):
    """Tailles d'icônes."""
    SM = "16px"
    MD = "20px"
    LG = "24px"
    XL = "32px"
    XXL = "48px"


class Icon:
    """Icônes standardisées pour toute l'application.
    
    Centralise tous les emojis pour assurer la cohérence visuelle.
    """
    
    # ==================== STATUT ====================
    SUCCESS = "✓"
    ERROR = "✕"
    WARNING = "⚠"
    INFO = "ℹ"
    HELP = "❓"
    LOADING = "🔄"
    PENDING = "⏳"
    
    # ==================== ACTIONS ====================
    ADD = "➕"
    REMOVE = "➖"
    DELETE = "🗑️"
    EDIT = "✏️"
    SAVE = "💾"
    CANCEL = "✕"
    CONFIRM = "✓"
    REFRESH = "🔄"
    SEARCH = "🔍"
    FILTER = "🔽"
    SORT = "↕️"
    EXPORT = "📤"
    IMPORT = "📥"
    DOWNLOAD = "⬇️"
    UPLOAD = "⬆️"
    SHARE = "🔗"
    PRINT = "🖨️"
    
    # ==================== NAVIGATION ====================
    BACK = "←"
    NEXT = "→"
    UP = "↑"
    DOWN = "↓"
    HOME = "🏠"
    MENU = "☰"
    CLOSE = "✕"
    EXPAND = "▼"
    COLLAPSE = "▲"
    
    # ==================== FINANCE ====================
    MONEY = "💰"
    WALLET = "👛"
    CREDIT_CARD = "💳"
    BANK = "🏦"
    CHART = "📊"
    TREND_UP = "📈"
    TREND_DOWN = "📉"
    PIGGY_BANK = "🐷"
    COIN = "🪙"
    DOLLAR = "💵"
    EURO = "💶"
    
    # ==================== CATÉGORIES ====================
    FOOD = "🍽️"
    TRANSPORT = "🚗"
    SHOPPING = "🛍️"
    HEALTH = "🏥"
    ENTERTAINMENT = "🎬"
    EDUCATION = "📚"
    HOUSING = "🏠"
    UTILITIES = "💡"
    INSURANCE = "🛡️"
    TRAVEL = "✈️"
    GIFT = "🎁"
    DONATION = "❤️"
    
    # ==================== TEMPS ====================
    CALENDAR = "📅"
    CLOCK = "🕐"
    HISTORY = "🕐"
    SCHEDULE = "📆"
    RECURRING = "🔄"
    STREAK = "🔥"
    
    # ==================== UTILISATEUR ====================
    USER = "👤"
    USERS = "👥"
    PROFILE = "👤"
    SETTINGS = "⚙️"
    LOGOUT = "🚪"
    LOGIN = "🔑"
    LOCK = "🔒"
    UNLOCK = "🔓"
    
    # ==================== NOTIFICATIONS ====================
    BELL = "🔔"
    EMAIL = "📧"
    MESSAGE = "💬"
    ALERT = "🚨"
    BULB = "💡"
    STAR = "⭐"
    TROPHY = "🏆"
    MEDAL = "🥇"
    
    # ==================== FICHIERS ====================
    FILE = "📄"
    FOLDER = "📁"
    CSV = "📊"
    PDF = "📄"
    IMAGE = "🖼️"
    
    # ==================== ÉTATS ====================
    CHECK = "✓"
    CROSS = "✕"
    DOT = "•"
    HEART = "❤️"
    STAR_FILL = "★"
    FLAG = "🚩"
    PIN = "📌"
    BOOKMARK = "🔖"
    
    @classmethod
    def success(cls, size: IconSize | None = None) -> str:
        """Icône succès."""
        return cls.SUCCESS
    
    @classmethod
    def error(cls, size: IconSize | None = None) -> str:
        """Icône erreur."""
        return cls.ERROR
    
    @classmethod
    def warning(cls, size: IconSize | None = None) -> str:
        """Icône avertissement."""
        return cls.WARNING
    
    @classmethod
    def info(cls, size: IconSize | None = None) -> str:
        """Icône info."""
        return cls.INFO
    
    @classmethod
    def loading(cls, size: IconSize | None = None) -> str:
        """Icône chargement."""
        return cls.LOADING
    
    @classmethod
    def for_category(cls, category: str) -> str:
        """Retourne l'icône appropriée pour une catégorie.
        
        Args:
            category: Nom de la catégorie
        
        Returns:
            Emoji correspondant
        
        Usage:
            icon = Icon.for_category("alimentation")  # -> "🍽️"
        """
        category_icons = {
            # Français
            "alimentation": cls.FOOD,
            "nourriture": cls.FOOD,
            "restaurant": cls.FOOD,
            "courses": cls.FOOD,
            "supermarché": cls.FOOD,
            "transport": cls.TRANSPORT,
            "essence": cls.TRANSPORT,
            "voiture": cls.TRANSPORT,
            "train": cls.TRANSPORT,
            "bus": cls.TRANSPORT,
            "shopping": cls.SHOPPING,
            "habillement": cls.SHOPPING,
            "vêtements": cls.SHOPPING,
            "santé": cls.HEALTH,
            "médecin": cls.HEALTH,
            "pharmacie": cls.HEALTH,
            "loisirs": cls.ENTERTAINMENT,
            "divertissement": cls.ENTERTAINMENT,
            "cinéma": cls.ENTERTAINMENT,
            "éducation": cls.EDUCATION,
            "formation": cls.EDUCATION,
            "livres": cls.EDUCATION,
            "logement": cls.HOUSING,
            "loyer": cls.HOUSING,
            "charges": cls.HOUSING,
            "factures": cls.UTILITIES,
            "électricité": cls.UTILITIES,
            "eau": cls.UTILITIES,
            "gaz": cls.UTILITIES,
            "internet": cls.UTILITIES,
            "téléphone": cls.UTILITIES,
            "assurance": cls.INSURANCE,
            "voyage": cls.TRAVEL,
            "vacances": cls.TRAVEL,
            "cadeaux": cls.GIFT,
            "don": cls.DONATION,
            "donation": cls.DONATION,
            
            # Anglais
            "food": cls.FOOD,
            "groceries": cls.FOOD,
            "dining": cls.FOOD,
            "transportation": cls.TRANSPORT,
            "car": cls.TRANSPORT,
            "fuel": cls.TRANSPORT,
            "health": cls.HEALTH,
            "medical": cls.HEALTH,
            "entertainment": cls.ENTERTAINMENT,
            "education": cls.EDUCATION,
            "housing": cls.HOUSING,
            "rent": cls.HOUSING,
            "utilities": cls.UTILITIES,
            "insurance": cls.INSURANCE,
            "travel": cls.TRAVEL,
            "gifts": cls.GIFT,
        }
        
        return category_icons.get(category.lower(), "📦")
    
    @classmethod
    def for_severity(cls, severity: str) -> str:
        """Retourne l'icône appropriée pour un niveau de sévérité.
        
        Args:
            severity: Niveau de sévérité (low, medium, high, critical)
        
        Returns:
            Emoji correspondant
        
        Usage:
            icon = Icon.for_severity("high")  # -> "🔴"
        """
        severity_icons = {
            "low": "🔵",
            "medium": "🟠",
            "high": "🔴",
            "critical": "🚨",
            "info": cls.INFO,
            "success": cls.SUCCESS,
            "warning": cls.WARNING,
            "error": cls.ERROR,
        }
        return severity_icons.get(severity.lower(), "⚪")

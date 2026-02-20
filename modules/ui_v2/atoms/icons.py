"""Icônes standardisées pour l'application.

Centralise toutes les icônes utilisées dans l'application
pour assurer la cohérence visuelle.
"""

from enum import Enum


class IconSet(Enum):
    """Ensemble d'icônes standardisées."""

    # Actions
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    HELP = "❓"
    SETTINGS = "⚙️"
    EDIT = "✏️"
    DELETE = "🗑️"
    ADD = "➕"
    SAVE = "💾"
    CANCEL = "❌"
    CONFIRM = "✓"
    REFRESH = "🔄"
    SEARCH = "🔍"
    FILTER = "🔽"
    SORT = "📊"
    EXPORT = "📤"
    IMPORT = "📥"
    DOWNLOAD = "⬇️"
    UPLOAD = "⬆️"

    # Finance
    MONEY = "💰"
    WALLET = "👛"
    CREDIT_CARD = "💳"
    BANK = "🏦"
    TREND_UP = "📈"
    TREND_DOWN = "📉"
    CHART = "📊"
    PIE_CHART = "🥧"
    CALCULATOR = "🧮"
    RECEIPT = "🧾"
    INVOICE = "📄"

    # Catégories
    FOOD = "🛒"
    TRANSPORT = "🚗"
    HEALTH = "🏥"
    HOME = "🏠"
    LEISURE = "🎮"
    EDUCATION = "📚"
    SHOPPING = "🛍️"
    TRAVEL = "✈️"
    RESTAURANT = "🍽️"
    SUBSCRIPTION = "📱"
    GIFT = "🎁"
    INSURANCE = "🛡️"

    # Membres
    USER = "👤"
    USERS = "👥"
    FAMILY = "👨‍👩‍👧‍👦"
    PERSON = "🧑"
    CARD = "💳"

    # États
    PENDING = "⏳"
    VALIDATED = "✅"
    ARCHIVED = "📦"
    DELETED = "🗑️"
    LOCKED = "🔒"
    UNLOCKED = "🔓"
    VISIBLE = "👁️"
    HIDDEN = "🙈"
    STAR = "⭐"
    HEART = "❤️"
    FIRE = "🔥"

    # Navigation
    HOME = "🏠"
    BACK = "◀️"
    NEXT = "▶️"
    UP = "⬆️"
    DOWN = "⬇️"
    MENU = "☰"
    CLOSE = "✕"
    EXTERNAL_LINK = "↗️"

    # Temps
    CALENDAR = "📅"
    CLOCK = "🕐"
    HISTORY = "🕰️"
    RECENT = "🆕"
    SCHEDULED = "📆"
    RECURRING = "🔄"

    # Notifications
    BELL = "🔔"
    EMAIL = "📧"
    MESSAGE = "💬"
    ANNOUNCEMENT = "📢"
    ALERT = "🚨"

    # Fichiers
    FILE = "📄"
    FOLDER = "📁"
    PDF = "📕"
    CSV = "📗"
    EXCEL = "📘"
    IMAGE = "🖼️"

    # Spécial
    MAGIC = "✨"
    TARGET = "🎯"
    LIGHTBULB = "💡"
    TOOLS = "🛠️"
    BUG = "🐛"
    ROCKET = "🚀"
    TROPHY = "🏆"
    MEDAL = "🥇"
    FLAG = "🚩"
    PIN = "📌"
    BOOKMARK = "🔖"
    TAG = "🏷️"
    LABEL = "🏷️"
    HASH = "#️⃣"
    LINK = "🔗"
    ATTACHMENT = "📎"


# Alias pour compatibilité
ICONS = IconSet

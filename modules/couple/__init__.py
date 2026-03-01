"""
Module Couple Edition pour FinancePerso.

Gestion de la confidentialité entre partenaires :
- Chacun voit ses propres détails
- L'autre est visible en agrégats uniquement
- Les virements internes sont identifiés et exclus des stats
- Gestion des emprunts communs
"""

from modules.couple.card_mappings import (
    get_all_card_mappings,
    get_card_mapping,
    save_card_mapping,
    delete_card_mapping,
    get_unknown_cards,
    detect_cards_from_transactions,
)
from modules.couple.couple_settings import (
    get_couple_settings,
    save_couple_settings,
    set_current_user,
    get_current_user_role,
    is_couple_configured,
)
from modules.couple.loans import (
    get_all_loans,
    get_loan,
    create_loan,
    update_loan,
    delete_loan,
    link_transaction_to_loan,
    get_loan_transactions,
    detect_loan_payments,
    get_loans_summary,
)
from modules.couple.transfer_detector import (
    detect_internal_transfers,
    validate_transfer,
    get_pending_transfers,
    exclude_transfers_from_stats,
)
from modules.couple.privacy_filters import (
    get_transactions_with_privacy,
    get_aggregated_partner_data,
    get_personal_summary,
    COUPLE_PRIVACY_RULES,
)

__all__ = [
    # Card mappings
    "get_all_card_mappings",
    "get_card_mapping",
    "save_card_mapping",
    "delete_card_mapping",
    "get_unknown_cards",
    "detect_cards_from_transactions",
    # Settings
    "get_couple_settings",
    "save_couple_settings",
    "set_current_user",
    "get_current_user_role",
    "is_couple_configured",
    # Loans
    "get_all_loans",
    "get_loan",
    "create_loan",
    "update_loan",
    "delete_loan",
    "link_transaction_to_loan",
    "get_loan_transactions",
    "detect_loan_payments",
    "get_loans_summary",
    # Transfers
    "detect_internal_transfers",
    "validate_transfer",
    "get_pending_transfers",
    "exclude_transfers_from_stats",
    # Privacy
    "get_transactions_with_privacy",
    "get_aggregated_partner_data",
    "get_personal_summary",
    "COUPLE_PRIVACY_RULES",
]

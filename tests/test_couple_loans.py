"""Tests pour la gestion des emprunts (Module 4)."""


import pytest

from modules.couple.loans import (
    create_loan,
    delete_loan,
    get_all_loans,
    get_loan,
    get_loan_transactions,
    get_loans_summary,
    link_transaction_to_loan,
    update_loan,
)
from modules.db.members import add_member, get_members


class TestLoansCRUD:
    """Test le CRUD des emprunts."""

    def test_create_loan_minimal(self, temp_db):
        """Doit créer un emprunt avec les champs minimum."""
        loan_id = create_loan(name="Test Loan", monthly_payment=1000.0)
        assert loan_id is not None
        assert isinstance(loan_id, int)

    def test_create_loan_complete(self, temp_db):
        """Doit créer un emprunt avec tous les champs."""
        loan_id = create_loan(
            name="Prêt Maison",
            lender="Banque Test",
            principal_amount=250000.0,
            monthly_payment=1200.0,
            interest_rate=2.5,
            total_duration_months=240,
            start_date="2024-01-01",
            notes="Test note",
        )
        assert loan_id is not None

        # Vérifier
        loan = get_loan(loan_id)
        assert loan is not None
        assert loan["name"] == "Prêt Maison"
        assert loan["lender"] == "Banque Test"
        assert loan["principal_amount"] == 250000.0
        assert loan["monthly_payment"] == 1200.0
        assert loan["interest_rate"] == 2.5

    def test_get_all_loans(self, temp_db):
        """Doit récupérer tous les emprunts actifs."""
        # Créer deux emprunts
        id1 = create_loan(name="Loan 1", monthly_payment=500.0)
        id2 = create_loan(name="Loan 2", monthly_payment=800.0)

        loans = get_all_loans(active_only=True)
        assert len(loans) >= 2

        loan_ids = [l["id"] for l in loans]
        assert id1 in loan_ids
        assert id2 in loan_ids

    def test_update_loan(self, temp_db):
        """Doit mettre à jour un emprunt."""
        loan_id = create_loan(name="Original", monthly_payment=500.0)

        # Mettre à jour
        result = update_loan(loan_id, name="Updated", monthly_payment=600.0, notes="New notes")
        assert result is True

        # Vérifier
        loan = get_loan(loan_id)
        assert loan["name"] == "Updated"
        assert loan["monthly_payment"] == 600.0
        assert loan["notes"] == "New notes"

    def test_delete_loan_soft(self, temp_db):
        """Doit désactiver (soft delete) un emprunt."""
        loan_id = create_loan(name="To Delete", monthly_payment=500.0)

        # Soft delete
        result = delete_loan(loan_id, soft=True)
        assert result is True

        # Ne doit plus apparaître dans les actifs
        loans = get_all_loans(active_only=True)
        loan_ids = [l["id"] for l in loans]
        assert loan_id not in loan_ids

        # Mais doit toujours exister
        loan = get_loan(loan_id)
        assert loan is not None
        assert loan["is_active"] == 0


class TestLoansWithMember:
    """Test les emprunts liés à des membres."""

    def test_create_loan_with_member(self, temp_db):
        """Doit créer un emprunt attribué à un membre."""
        add_member("TestMember", "HOUSEHOLD")
        members = get_members()
        member_id = int(members[members["name"] == "TestMember"].iloc[0]["id"])

        loan_id = create_loan(
            name="Perso Loan", monthly_payment=500.0, member_id=member_id, account_type="PERSONAL_A"
        )

        loan = get_loan(loan_id)
        assert loan["member_id"] == member_id
        assert loan["account_type"] == "PERSONAL_A"
        assert loan["member_name"] == "TestMember"


class TestLoanTransactions:
    """Test la liaison transactions/emprunts."""

    def test_link_transaction_to_loan(self, temp_db):
        """Doit lier une transaction à un emprunt."""
        # Créer un emprunt
        loan_id = create_loan(name="Test", monthly_payment=500.0, principal_amount=10000.0)

        # Créer une transaction
        import os
        import sqlite3

        conn = sqlite3.connect(os.environ.get("DB_PATH"))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (date, label, amount, status)
            VALUES ('2024-02-01', 'Mensualité prêt', -500, 'validated')
        """)
        tx_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Lier
        result = link_transaction_to_loan(
            loan_id=loan_id,
            transaction_id=tx_id,
            period="2024-02",
            capital_amount=400.0,
            interest_amount=100.0,
        )
        assert result is True

        # Vérifier la liaison
        tx_links = get_loan_transactions(loan_id)
        assert len(tx_links) == 1
        assert tx_links[0]["transaction_id"] == tx_id


class TestLoansSummary:
    """Test le résumé des emprunts."""

    def test_get_loans_summary_empty(self, temp_db):
        """Doit retourner un résumé vide si pas d'emprunts."""
        summary = get_loans_summary()

        assert summary["total_loans"] == 0
        assert summary["total_principal"] == 0.0
        assert summary["total_remaining"] == 0.0
        assert summary["total_monthly"] == 0.0

    def test_get_loans_summary_with_loans(self, temp_db):
        """Doit calculer correctement le résumé."""
        # Créer deux emprunts
        create_loan(
            name="Loan A", monthly_payment=1000.0, principal_amount=100000.0, account_type="JOINT"
        )
        create_loan(
            name="Loan B",
            monthly_payment=500.0,
            principal_amount=50000.0,
            account_type="PERSONAL_A",
        )

        summary = get_loans_summary()

        assert summary["total_loans"] == 2
        assert summary["total_principal"] == 150000.0
        assert summary["total_monthly"] == 1500.0
        assert summary["by_account_type"]["JOINT"] == 1
        assert summary["by_account_type"]["PERSONAL_A"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

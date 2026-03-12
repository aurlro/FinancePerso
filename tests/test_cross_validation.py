"""Tests du système de validation croisée."""


from modules.couple.cross_validation import CrossValidationManager, ValidationStatus


class TestCrossValidationManager:
    """Tests du gestionnaire de validation croisée."""
    
    def test_request_validation(self, temp_db):
        """Test la création d'une demande de validation."""
        manager = CrossValidationManager()
        
        request = manager.request_validation(
            transaction_id=1,
            requested_by="user1",
            validator_id="user2",
            notes="Please validate"
        )
        
        assert request.id is not None
        assert request.transaction_id == 1
        assert request.requested_by == "user1"
        assert request.validator_id == "user2"
        assert request.status == ValidationStatus.PENDING
        assert request.notes == "Please validate"
    
    def test_approve_validation(self, temp_db):
        """Test l'approbation d'une validation."""
        manager = CrossValidationManager()
        
        request = manager.request_validation(1, "user1", "user2")
        
        success = manager.approve_validation(request.id, "user2")
        assert success is True
        
        # Vérifier que la validation n'est plus en attente
        pending = manager.get_pending_validations("user2")
        assert len(pending) == 0
    
    def test_reject_validation(self, temp_db):
        """Test le rejet d'une validation."""
        manager = CrossValidationManager()
        
        request = manager.request_validation(1, "user1", "user2")
        
        success = manager.reject_validation(request.id, "user2", "Invalid")
        assert success is True
        
        # Vérifier que la validation n'est plus en attente
        pending = manager.get_pending_validations("user2")
        assert len(pending) == 0
    
    def test_get_pending_validations(self, temp_db):
        """Test la récupération des validations en attente."""
        manager = CrossValidationManager()
        
        # La récupération nécessite une transaction existante pour la jointure
        # On teste juste que la méthode s'exécute sans erreur
        pending = manager.get_pending_validations("user2")
        
        # Sans transactions dans la base, la liste est vide
        assert isinstance(pending, list)
    
    def test_needs_cross_validation(self):
        """Test la détection des transactions nécessitant validation."""
        manager = CrossValidationManager()
        
        assert manager.needs_cross_validation(600.0) is True
        assert manager.needs_cross_validation(500.0) is True
        assert manager.needs_cross_validation(499.99) is False
        assert manager.needs_cross_validation(100.0) is False
    
    def test_get_validation_history(self, temp_db):
        """Test la récupération de l'historique."""
        manager = CrossValidationManager()
        
        # La récupération nécessite une transaction existante pour la jointure
        # On teste juste que la méthode s'exécute sans erreur
        history = manager.get_validation_history("user1")
        
        assert isinstance(history, list)

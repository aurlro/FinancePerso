"""Tests du système de commentaires."""


from modules.db.comments import CommentManager


class TestCommentManager:
    """Tests du gestionnaire de commentaires."""
    
    def test_add_comment(self, temp_db):
        """Test l'ajout d'un commentaire."""
        manager = CommentManager()
        
        comment = manager.add_comment(
            transaction_id=1,
            user_id="user1",
            content="Test comment",
            user_name="Test User"
        )
        
        assert comment.id is not None
        assert comment.transaction_id == 1
        assert comment.user_id == "user1"
        assert comment.content == "Test comment"
        assert comment.user_name == "Test User"
    
    def test_get_comments(self, temp_db):
        """Test la récupération des commentaires."""
        manager = CommentManager()
        
        # Ajouter plusieurs commentaires
        manager.add_comment(1, "user1", "Comment 1")
        manager.add_comment(1, "user2", "Comment 2")
        manager.add_comment(2, "user1", "Other transaction")
        
        # Récupérer les commentaires de la transaction 1
        comments = manager.get_comments(1)
        
        assert len(comments) == 2
        assert all(c.transaction_id == 1 for c in comments)
    
    def test_get_comment_count(self, temp_db):
        """Test le comptage des commentaires."""
        manager = CommentManager()
        
        assert manager.get_comment_count(1) == 0
        
        manager.add_comment(1, "user1", "Comment 1")
        manager.add_comment(1, "user2", "Comment 2")
        
        assert manager.get_comment_count(1) == 2
        assert manager.get_comment_count(2) == 0
    
    def test_edit_comment(self, temp_db):
        """Test la modification d'un commentaire."""
        manager = CommentManager()
        
        comment = manager.add_comment(1, "user1", "Original")
        
        success = manager.edit_comment(comment.id, "Edited")
        assert success is True
        
        comments = manager.get_comments(1)
        assert comments[0].content == "Edited"
        assert comments[0].is_edited is True
    
    def test_delete_comment(self, temp_db):
        """Test la suppression d'un commentaire."""
        manager = CommentManager()
        
        comment = manager.add_comment(1, "user1", "To delete")
        
        success = manager.delete_comment(comment.id)
        assert success is True
        
        assert manager.get_comment_count(1) == 0

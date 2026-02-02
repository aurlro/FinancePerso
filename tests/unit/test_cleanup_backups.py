"""
Tests unitaires pour le script cleanup_backups.
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Importer les fonctions du script
import sys
scripts_path = str(Path(__file__).parent.parent.parent / 'scripts')
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# Utiliser importlib pour importer le module
import importlib.util
spec = importlib.util.spec_from_file_location("cleanup_backups", 
    str(Path(__file__).parent.parent.parent / 'scripts' / 'cleanup_backups.py'))
cleanup_backups = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup_backups)

find_backup_files = cleanup_backups.find_backup_files
get_original_file = cleanup_backups.get_original_file
analyze_backup = cleanup_backups.analyze_backup
PROJECT_ROOT = cleanup_backups.PROJECT_ROOT


class TestFindBackupFiles:
    """Tests de la fonction find_backup_files."""
    
    def test_finds_backup_patterns(self, tmp_path):
        """Trouve les fichiers selon les patterns."""
        # Créer des fichiers backup
        (tmp_path / 'file.py.backup').write_text('content')
        (tmp_path / 'file_backup.py').write_text('content')
        (tmp_path / 'file.py.bak').write_text('content')
        (tmp_path / 'file~').write_text('content')
        
        # Créer un fichier normal
        (tmp_path / 'normal.py').write_text('content')
        
        with patch.object(cleanup_backups, 'PROJECT_ROOT', tmp_path):
            files = find_backup_files()
        
        assert len(files) == 4
        names = [f.name for f in files]
        assert 'file.py.backup' in names
        assert 'file_backup.py' in names
        assert 'file.py.bak' in names
        assert 'file~' in names
        assert 'normal.py' not in names
    
    def test_excludes_special_dirs(self, tmp_path):
        """Exclut les dossiers spéciaux."""
        # Créer un dossier __pycache__ avec backup
        pycache = tmp_path / '__pycache__'
        pycache.mkdir()
        (pycache / 'file.py.backup').write_text('content')
        
        # Créer un backup normal
        (tmp_path / 'normal.py.backup').write_text('content')
        
        with patch.object(cleanup_backups, 'PROJECT_ROOT', tmp_path):
            files = find_backup_files()
        
        assert len(files) == 1
        assert files[0].name == 'normal.py.backup'
    
    def test_no_duplicates(self, tmp_path):
        """Pas de doublons dans les résultats."""
        (tmp_path / 'file.py.backup').write_text('content')
        
        with patch.object(cleanup_backups, 'PROJECT_ROOT', tmp_path):
            files = find_backup_files()
        
        # Le fichier pourrait matcher plusieurs patterns mais ne doit apparaître qu'une fois
        assert len(files) == len(set(files))


class TestGetOriginalFile:
    """Tests de la fonction get_original_file."""
    
    def test_backup_extension(self, tmp_path):
        """Trouve l'original pour .backup."""
        original = tmp_path / 'script.py'
        original.write_text('content')
        backup = tmp_path / 'script.py.backup'
        
        result = get_original_file(backup)
        assert result == original
    
    def test_backup_suffix(self, tmp_path):
        """Trouve l'original pour _backup."""
        original = tmp_path / 'script.py'
        original.write_text('content')
        backup = tmp_path / 'script_backup.py'
        
        result = get_original_file(backup)
        assert result == original
    
    def test_bak_extension(self, tmp_path):
        """Trouve l'original pour .bak."""
        original = tmp_path / 'config.ini'
        original.write_text('content')
        backup = tmp_path / 'config.ini.bak'
        
        result = get_original_file(backup)
        assert result == original
    
    def test_tilde_suffix(self, tmp_path):
        """Trouve l'original pour ~."""
        original = tmp_path / 'document.txt'
        original.write_text('content')
        backup = tmp_path / 'document.txt~'
        
        result = get_original_file(backup)
        assert result == original
    
    def test_no_original(self, tmp_path):
        """Retourne None si pas d'original."""
        backup = tmp_path / 'missing.py.backup'
        
        result = get_original_file(backup)
        assert result is None


class TestAnalyzeBackup:
    """Tests de la fonction analyze_backup."""
    
    def test_identical_files(self, tmp_path):
        """Détecte les fichiers identiques."""
        content = 'same content'
        original = tmp_path / 'file.py'
        backup = tmp_path / 'file.py.backup'
        original.write_text(content)
        backup.write_text(content)
        
        result = analyze_backup(backup)
        assert result['status'] == 'identical'
        assert result['action'] == 'delete'
    
    def test_different_files(self, tmp_path):
        """Détecte les fichiers différents (backup plus ancien)."""
        import time
        original = tmp_path / 'file.py'
        backup = tmp_path / 'file.py.backup'
        
        # Créer le backup d'abord (plus ancien)
        backup.write_text('old content')
        time.sleep(0.1)
        # Puis l'original (plus récent)
        original.write_text('new content')
        
        result = analyze_backup(backup)
        assert result['action'] == 'archive'
    
    def test_newer_backup(self, tmp_path):
        """Détecte si le backup est plus récent."""
        import time
        original = tmp_path / 'file.py'
        backup = tmp_path / 'file.py.backup'
        
        original.write_text('content')
        time.sleep(0.1)  # Assurer une différence de temps
        backup.write_text('newer content')
        
        result = analyze_backup(backup)
        assert result['status'] == 'newer'
        assert result['action'] == 'review'
    
    def test_orphan_backup(self, tmp_path):
        """Détecte les backups sans original."""
        backup = tmp_path / 'orphan.py.backup'
        backup.write_text('content')
        
        result = analyze_backup(backup)
        assert result['status'] == 'orphan'
        assert result['action'] == 'archive'


class TestIntegration:
    """Tests d'intégration du script."""
    
    def test_end_to_end_dry_run(self, tmp_path):
        """Test dry-run complet."""
        import time
        
        # Créer une structure de test
        (tmp_path / 'identical.py').write_text('same')
        (tmp_path / 'identical.py.backup').write_text('same')  # Identique
        
        # Pour 'different': backup plus ancien que l'original
        backup = tmp_path / 'app.py.backup'
        original = tmp_path / 'app.py'
        backup.write_text('v1')  # Ancien
        time.sleep(0.1)
        original.write_text('v2')  # Récent
        
        with patch.object(cleanup_backups, 'PROJECT_ROOT', tmp_path):
            backups = find_backup_files()
            assert len(backups) == 2
            
            analysis = [analyze_backup(b) for b in backups]
            actions = {a['action'] for a in analysis}
            
            assert 'delete' in actions  # identical
            assert 'archive' in actions  # different (backup plus ancien)

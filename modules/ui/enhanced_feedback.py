# -*- coding: utf-8 -*-
"""
Composants de feedback UX améliorés pour FinancePerso.

Ce module fournit des wrappers et composants pour améliorer l'expérience utilisateur
avec des messages clairs, des indicateurs de progression et des confirmations.
"""

import streamlit as st
import time
from contextlib import contextmanager
from typing import Callable, Any, Optional
from functools import wraps


def show_action_toast(message: str, type_: str = "success", duration: int = 3):
    """
    Affiche un toast de confirmation après une action.
    
    Args:
        message: Message à afficher
        type_: Type de toast ("success", "error", "warning", "info")
        duration: Durée d'affichage en secondes (défaut: 3)
    """
    icons = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    icon = icons.get(type_, "ℹ️")
    
    # Utiliser toast si disponible (Streamlit >= 1.20)
    try:
        if type_ == "success":
            st.toast(f"{icon} {message}", icon=icon)
        elif type_ == "error":
            st.error(f"{icon} {message}")
        elif type_ == "warning":
            st.warning(f"{icon} {message}")
        else:
            st.info(f"{icon} {message}")
    except:
        # Fallback pour les anciennes versions
        if type_ == "success":
            st.success(f"{icon} {message}")
        elif type_ == "error":
            st.error(f"{icon} {message}")
        elif type_ == "warning":
            st.warning(f"{icon} {message}")
        else:
            st.info(f"{icon} {message}")


@contextmanager
def loading_spinner(text: str = "Chargement en cours...", show_time: bool = True):
    """
    Context manager pour afficher un spinner pendant une opération.
    
    Args:
        text: Texte à afficher dans le spinner
        show_time: Afficher le temps d'exécution à la fin
        
    Example:
        with loading_spinner("Chargement des transactions..."):
            df = load_transactions()
    """
    start_time = time.time()
    
    with st.spinner(text):
        yield
    
    if show_time:
        elapsed = time.time() - start_time
        if elapsed > 1.0:  # N'afficher que si > 1 seconde
            st.caption(f"⏱️ Opération terminée en {elapsed:.2f}s")


def with_feedback(action_name: str, success_msg: Optional[str] = None, 
                  error_msg: Optional[str] = None, show_spinner: bool = True):
    """
    Décorateur pour wrapper une fonction avec feedback utilisateur.
    
    Args:
        action_name: Nom de l'action affiché dans le spinner
        success_msg: Message de succès personnalisé
        error_msg: Message d'erreur personnalisé
        show_spinner: Afficher un spinner pendant l'exécution
        
    Example:
        @with_feedback("Sauvegarde", "Données sauvegardées !")
        def save_data(data):
            return db.save(data)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            spinner_text = f"{action_name} en cours..."
            
            try:
                if show_spinner:
                    with st.spinner(spinner_text):
                        result = func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Message de succès
                msg = success_msg or f"{action_name} réussie !"
                show_action_toast(msg, "success")
                
                return result
                
            except Exception as e:
                # Message d'erreur
                msg = error_msg or f"{action_name} échouée : {str(e)}"
                show_action_toast(msg, "error")
                raise
        
        return wrapper
    return decorator


def confirm_button(label: str, confirmation_text: str, 
                   on_confirm: Callable, on_cancel: Optional[Callable] = None,
                   confirm_label: str = "Confirmer", cancel_label: str = "Annuler"):
    """
    Bouton avec confirmation pour les actions destructrices.
    
    Args:
        label: Label du bouton principal
        confirmation_text: Texte de confirmation affiché
        on_confirm: Fonction à appeler si confirmé
        on_cancel: Fonction à appeler si annulé (optionnel)
        confirm_label: Label du bouton de confirmation
        cancel_label: Label du bouton d'annulation
        
    Example:
        confirm_button(
            "🗑️ Supprimer tout",
            "⚠️ Êtes-vous sûr de vouloir supprimer toutes les données ?",
            on_confirm=lambda: delete_all_data(),
            confirm_label="Oui, supprimer",
            cancel_label="Non, annuler"
        )
    """
    # Utiliser session_state pour gérer l'état
    confirm_key = f"confirm_{label.replace(' ', '_').lower()}"
    
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False
    
    if not st.session_state[confirm_key]:
        # Premier clic - afficher le bouton
        if st.button(label, key=f"btn_{confirm_key}"):
            st.session_state[confirm_key] = True
            st.rerun()
    else:
        # Deuxième clic - demander confirmation
        st.warning(confirmation_text)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(confirm_label, key=f"confirm_yes_{confirm_key}", type="primary"):
                try:
                    on_confirm()
                    show_action_toast("Action confirmée", "success")
                except Exception as e:
                    show_action_toast(f"Erreur : {str(e)}", "error")
                finally:
                    st.session_state[confirm_key] = False
                    st.rerun()
        
        with col2:
            if st.button(cancel_label, key=f"confirm_no_{confirm_key}"):
                st.session_state[confirm_key] = False
                if on_cancel:
                    on_cancel()
                show_action_toast("Action annulée", "info")
                st.rerun()


def progress_with_status(total: int, description: str = "Traitement en cours"):
    """
    Crée une barre de progression avec statut pour les opérations longues.
    
    Args:
        total: Nombre total d'éléments
        description: Description de l'opération
        
    Returns:
        Tuple (progress_bar, status_text, update_func)
        
    Example:
        pbar, status, update = progress_with_status(len(items), "Import des transactions")
        for i, item in enumerate(items):
            process(item)
            update(i + 1, f"Traité {item['label']}")
    """
    st.write(f"**{description}**")
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update(current: int, message: str = ""):
        progress = min(current / total, 1.0)
        progress_bar.progress(progress)
        if message:
            status_text.text(f"{message} ({current}/{total})")
        else:
            status_text.text(f"Progression : {current}/{total} ({progress*100:.0f}%)")
    
    return progress_bar, status_text, update


class ActionLogger:
    """
    Logger d'actions pour déboguer le comportement des boutons.
    Affiche un historique des actions dans la sidebar.
    """
    
    def __init__(self, max_entries: int = 10):
        self.max_entries = max_entries
        if 'action_log' not in st.session_state:
            st.session_state.action_log = []
    
    def log(self, action: str, details: str = ""):
        """Ajoute une entrée au log."""
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {action}"
        if details:
            entry += f" - {details}"
        
        st.session_state.action_log.insert(0, entry)
        
        # Limiter la taille
        if len(st.session_state.action_log) > self.max_entries:
            st.session_state.action_log = st.session_state.action_log[:self.max_entries]
    
    def display(self):
        """Affiche le log dans la sidebar."""
        with st.sidebar:
            with st.expander("📝 Log d'actions (debug)", expanded=False):
                if st.session_state.action_log:
                    for entry in st.session_state.action_log:
                        st.caption(entry)
                else:
                    st.caption("Aucune action enregistrée")
                
                if st.button("Effacer le log", key="clear_log"):
                    st.session_state.action_log = []
                    st.rerun()


# Instance globale pour l'application
action_logger = ActionLogger()


def logged_button(label: str, key: Optional[str] = None, 
                  help: Optional[str] = None, 
                  type_: str = "secondary",
                  on_click: Optional[Callable] = None) -> bool:
    """
    Bouton avec logging automatique pour le débogage.
    
    Args:
        label: Label du bouton
        key: Clé unique
        help: Texte d'aide
        type_: Type de bouton ("primary", "secondary")
        on_click: Fonction à appeler au clic
        
    Returns:
        True si cliqué, False sinon
    """
    btn_key = key or f"btn_{label.replace(' ', '_').lower()}"
    
    # Wrapper pour le on_click avec logging
    def wrapped_click():
        action_logger.log(f"🖱️ Bouton cliqué", label)
        if on_click:
            on_click()
    
    clicked = st.button(label, key=btn_key, help=help, 
                       type=type_, on_click=wrapped_click if on_click else None)
    
    if clicked and not on_click:
        action_logger.log(f"🖱️ Bouton cliqué", label)
    
    return clicked


# Fonction d'initialisation
def init_feedback_system():
    """Initialise le système de feedback (à appeler au début de l'app)."""
    action_logger.display()

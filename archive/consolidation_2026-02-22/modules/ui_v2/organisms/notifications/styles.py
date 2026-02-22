"""
Styles CSS pour le système de notifications UI v2.

Contient toutes les définitions CSS, animations et styles pour les composants
de notification (toasts, inline, spéciaux).
"""

import streamlit as st


def render_toast_container():
    """
    Rend le conteneur de toasts fixe en haut à droite.
    À appeler une fois par page, idéalement dans la sidebar ou en début de page.
    """
    # CSS pour le conteneur de toasts
    st.markdown(
        """
        <style>
        /* ==================== Conteneur de toasts ==================== */
        .fp-toast-container {
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 999999;
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-width: 400px;
            pointer-events: none;
        }
        
        /* ==================== Toast individuel ==================== */
        .fp-toast {
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            padding: 16px;
            pointer-events: all;
            animation: fp-toast-in 0.3s ease-out;
            border-left: 4px solid;
            position: relative;
            overflow: hidden;
        }
        
        /* Animation d'entrée */
        @keyframes fp-toast-in {
            from {
                opacity: 0;
                transform: translateX(100%);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        /* Animation de sortie */
        @keyframes fp-toast-out {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100%);
            }
        }
        
        .fp-toast.exiting {
            animation: fp-toast-out 0.3s ease-in forwards;
        }
        
        /* ==================== Barre de progression ==================== */
        .fp-toast-progress {
            position: absolute;
            bottom: 0;
            left: 0;
            height: 3px;
            background: currentColor;
            opacity: 0.3;
            transition: width 0.1s linear;
        }
        
        /* ==================== Header du toast ==================== */
        .fp-toast-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 6px;
        }
        
        .fp-toast-icon {
            font-size: 20px;
            flex-shrink: 0;
        }
        
        .fp-toast-title {
            font-weight: 600;
            font-size: 14px;
            color: #1f2937;
            margin: 0;
        }
        
        .fp-toast-close {
            position: absolute;
            top: 8px;
            right: 8px;
            background: none;
            border: none;
            cursor: pointer;
            opacity: 0.4;
            transition: opacity 0.2s;
            font-size: 16px;
            padding: 4px;
            line-height: 1;
        }
        
        .fp-toast-close:hover {
            opacity: 0.8;
        }
        
        /* ==================== Message ==================== */
        .fp-toast-message {
            font-size: 13px;
            color: #4b5563;
            line-height: 1.5;
            margin-left: 30px;
        }
        
        /* ==================== Actions ==================== */
        .fp-toast-actions {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            margin-left: 30px;
        }
        
        .fp-toast-action {
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
        }
        
        .fp-toast-action.primary {
            background: #3b82f6;
            color: white;
        }
        
        .fp-toast-action.primary:hover {
            background: #2563eb;
        }
        
        .fp-toast-action.secondary {
            background: #f3f4f6;
            color: #374151;
        }
        
        .fp-toast-action.secondary:hover {
            background: #e5e7eb;
        }
        
        /* ==================== Animation de chargement ==================== */
        @keyframes loading-bounce {
            0%, 100% { 
                transform: translateY(0) rotate(0deg); 
            }
            50% { 
                transform: translateY(-10px) rotate(180deg); 
            }
        }
        
        /* ==================== Animation d'achievement ==================== */
        @keyframes achievement-pulse {
            0%, 100% { 
                transform: scale(1); 
            }
            50% { 
                transform: scale(1.02); 
            }
        }
        
        /* ==================== Responsive ==================== */
        @media (max-width: 640px) {
            .fp-toast-container {
                left: 10px;
                right: 10px;
                max-width: none;
            }
            
            .fp-toast {
                width: 100%;
            }
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

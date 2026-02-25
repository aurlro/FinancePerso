"""
PWA Installation helper for Streamlit.
Provides UI elements for PWA installation.
"""

import streamlit as st


def render_pwa_install_prompt():
    """
    Render a prompt to install the PWA.
    Shows only on mobile browsers that support PWA.
    """
    st.markdown("""
        <script>
        // Check if PWA can be installed
        if ('beforeinstallprompt' in window) {
            window.addEventListener('beforeinstallprompt', (e) => {
                e.preventDefault();
                window.deferredPrompt = e;
                
                // Show install button
                const installDiv = document.getElementById('pwa-install');
                if (installDiv) {
                    installDiv.style.display = 'block';
                }
            });
        }
        
        function installPWA() {
            if (window.deferredPrompt) {
                window.deferredPrompt.prompt();
                window.deferredPrompt.userChoice.then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        console.log('PWA installed');
                    }
                    window.deferredPrompt = null;
                });
            }
        }
        </script>
        
        <div id="pwa-install" style="display: none;">
            <button onclick="installPWA()" 
                    style="background: #1E88E5; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                📲 Installer l'app
            </button>
        </div>
    """, unsafe_allow_html=True)


def is_pwa_installed() -> bool:
    """Check if app is running as installed PWA."""
    # This is checked via JavaScript matchMedia
    return st.session_state.get('is_pwa', False)


def register_service_worker():
    """Register the service worker for PWA functionality."""
    st.markdown("""
        <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('assets/service-worker.js')
                .then((registration) => {
                    console.log('[SW] Registered:', registration);
                })
                .catch((error) => {
                    console.log('[SW] Registration failed:', error);
                });
        }
        </script>
    """, unsafe_allow_html=True)


def check_pwa_status():
    """
    Check and store PWA status in session state.
    Call this once at app initialization.
    """
    st.markdown("""
        <script>
        // Check if running as installed PWA
        const isPWA = window.matchMedia('(display-mode: standalone)').matches ||
                      window.navigator.standalone === true;
        
        // Store in sessionStorage for Streamlit to access
        sessionStorage.setItem('is_pwa', isPWA);
        
        // Dispatch custom event that Streamlit can listen to
        window.dispatchEvent(new CustomEvent('pwa-status', { detail: { isPWA: isPWA } }));
        </script>
    """, unsafe_allow_html=True)


__all__ = [
    'render_pwa_install_prompt',
    'is_pwa_installed',
    'register_service_worker',
    'check_pwa_status',
]

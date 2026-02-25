# PWA Support for MyFinance Companion

## Installation Mobile

### iOS (Safari)
1. Ouvrez l'app dans Safari
2. Tapper le bouton "Partager" (carré avec flèche)
3. Sélectionner "Sur l'écran d'accueil"
4. Confirmer l'ajout

### Android (Chrome)
1. Ouvrez l'app dans Chrome
2. Attendez le popup "Ajouter à l'écran d'accueil"
3. Ou allez dans Menu ⋮ > "Ajouter à l'écran d'accueil"

## Fonctionnalités

- ✅ Icône sur l'écran d'accueil
- ✅ Mode plein écran (sans barre d'adresse)
- ✅ Thème couleur personnalisé
- ⚠️ Mode hors-ligne basique (cache statique)

## Limitations

Le mode hors-ligne est limité car Streamlit nécessite un serveur Python.
Les données ne sont pas sync entre appareils (local-only).

## Architecture PWA

Les fichiers PWA sont situés dans `assets/`:

- `manifest.json` - Configuration PWA (nom, icônes, couleurs)
- `service-worker.js` - Service Worker pour cache et offline
- `pwa.js` - Scripts JavaScript pour l'installation
- `pwa_install.py` - Helper Python pour Streamlit
- `offline.html` - Page de fallback offline

## Configuration

Les meta tags PWA sont injectés dans `app.py` via `st.markdown()` avec `unsafe_allow_html=True`.

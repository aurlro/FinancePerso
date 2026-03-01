"""
Collecteur de métriques métier pour FinancePerso
Calcule les KPIs importants : taux d'import, rétention, etc.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

from modules.db.connection import get_db_connection


class MetricsCollector:
    """Collecte et calcule les métriques métier."""
    
    @classmethod
    def get_import_conversion_rate(cls, days: int = 30) -> Dict[str, Any]:
        """
        Calcule le taux de conversion des imports (nouveaux utilisateurs).
        
        Retourne:
            - total_new_users: Nombre de nouveaux utilisateurs
            - imported_users: Nombre ayant importé
            - conversion_rate: Taux de conversion (%)
        """
        try:
            with get_db_connection() as conn:
                since = (datetime.now() - timedelta(days=days)).isoformat()
                
                # Utilisateurs avec leur première session dans la période
                cursor = conn.execute(
                    """SELECT COUNT(DISTINCT user_id) FROM analytics_sessions
                       WHERE started_at > ? AND user_id IS NOT NULL""",
                    (since,)
                )
                total_new = cursor.fetchone()[0] or 0
                
                # Parmi ceux-ci, ceux qui ont importé
                cursor = conn.execute(
                    """SELECT COUNT(DISTINCT user_id) FROM analytics_events
                       WHERE event_type = 'import_complete'
                       AND timestamp > ?
                       AND user_id IN (
                           SELECT DISTINCT user_id FROM analytics_sessions
                           WHERE started_at > ?
                       )""",
                    (since, since)
                )
                imported = cursor.fetchone()[0] or 0
                
                rate = (imported / total_new * 100) if total_new > 0 else 0
                
                return {
                    "total_new_users": total_new,
                    "imported_users": imported,
                    "conversion_rate": round(rate, 2),
                    "period_days": days
                }
        except Exception:
            return {"total_new_users": 0, "imported_users": 0, 
                   "conversion_rate": 0, "period_days": days}
    
    @classmethod
    def get_retention_rate(cls, days: int = 7) -> Dict[str, Any]:
        """
        Calcule le taux de rétention (utilisateurs revenant après X jours).
        
        Retourne:
            - cohort_size: Taille de la cohorte initiale
            - retained_users: Nombre revenus
            - retention_rate: Taux de rétention (%)
        """
        try:
            analytics_db = Path("Data/analytics.db")
            if not analytics_db.exists():
                return {"cohort_size": 0, "retained_users": 0, 
                       "retention_rate": 0, "period_days": days}
            
            with sqlite3.connect(analytics_db) as conn:
                # Cohorte: utilisateurs actifs il y a 'days' jours
                cohort_date = (datetime.now() - timedelta(days=days*2)).isoformat()
                end_cohort = (datetime.now() - timedelta(days=days)).isoformat()
                
                cursor = conn.execute(
                    """SELECT DISTINCT user_id FROM sessions
                       WHERE started_at > ? AND started_at < ?
                       AND user_id IS NOT NULL""",
                    (cohort_date, end_cohort)
                )
                cohort = [row[0] for row in cursor.fetchall()]
                cohort_size = len(cohort)
                
                if cohort_size == 0:
                    return {"cohort_size": 0, "retained_users": 0,
                           "retention_rate": 0, "period_days": days}
                
                # Combien sont revenus après 'days' jours
                since_return = end_cohort
                placeholders = ','.join('?' * len(cohort))
                cursor = conn.execute(
                    f"""SELECT COUNT(DISTINCT user_id) FROM sessions
                        WHERE started_at > ?
                        AND user_id IN ({placeholders})""",
                    (since_return, *cohort)
                )
                retained = cursor.fetchone()[0] or 0
                
                rate = (retained / cohort_size * 100) if cohort_size > 0 else 0
                
                return {
                    "cohort_size": cohort_size,
                    "retained_users": retained,
                    "retention_rate": round(rate, 2),
                    "period_days": days
                }
        except Exception:
            return {"cohort_size": 0, "retained_users": 0,
                   "retention_rate": 0, "period_days": days}
    
    @classmethod
    def get_feature_adoption(cls, days: int = 30) -> Dict[str, Any]:
        """
        Calcule l'adoption des fonctionnalités clés.
        
        Retourne:
            - features: Dict avec pour chaque feature :
                - users: Nombre d'utilisateurs uniques
                - events: Nombre total d'événements
        """
        try:
            analytics_db = Path("Data/analytics.db")
            if not analytics_db.exists():
                return {}
            
            with sqlite3.connect(analytics_db) as conn:
                since = (datetime.now() - timedelta(days=days)).isoformat()
                
                cursor = conn.execute(
                    """SELECT event_type, COUNT(DISTINCT user_id) as users, 
                       COUNT(*) as events
                       FROM events
                       WHERE timestamp > ?
                       GROUP BY event_type""",
                    (since,)
                )
                
                features = {}
                for row in cursor.fetchall():
                    features[row[0]] = {
                        "users": row[1],
                        "events": row[2]
                    }
                
                return features
        except Exception:
            return {}
    
    @classmethod
    def get_dashboard_summary(cls) -> Dict[str, Any]:
        """Récupère un résumé complet des métriques pour le dashboard."""
        return {
            "import_j1": cls.get_import_conversion_rate(days=1),
            "import_j7": cls.get_import_conversion_rate(days=7),
            "import_j30": cls.get_import_conversion_rate(days=30),
            "retention_j7": cls.get_retention_rate(days=7),
            "retention_j30": cls.get_retention_rate(days=30),
            "feature_adoption": cls.get_feature_adoption(days=30),
            "generated_at": datetime.now().isoformat()
        }


def get_metrics_dashboard() -> None:
    """Affiche un dashboard des métriques dans Streamlit."""
    import streamlit as st
    
    st.title("📊 Métriques FinancePerso")
    
    metrics = MetricsCollector.get_dashboard_summary()
    
    # Section Import
    st.header("📥 Taux d'import")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        j1 = metrics["import_j1"]
        st.metric(
            "Conversion J+1",
            f"{j1['conversion_rate']}%",
            f"{j1['imported_users']}/{j1['total_new_users']}"
        )
    
    with col2:
        j7 = metrics["import_j7"]
        st.metric(
            "Conversion J+7",
            f"{j7['conversion_rate']}%",
            f"{j7['imported_users']}/{j7['total_new_users']}"
        )
    
    with col3:
        j30 = metrics["import_j30"]
        st.metric(
            "Conversion J+30",
            f"{j30['conversion_rate']}%",
            f"{j30['imported_users']}/{j30['total_new_users']}"
        )
    
    # Section Rétention
    st.header("🔄 Rétention")
    col1, col2 = st.columns(2)
    
    with col1:
        r7 = metrics["retention_j7"]
        st.metric(
            "Rétention J+7",
            f"{r7['retention_rate']}%",
            f"{r7['retained_users']}/{r7['cohort_size']}"
        )
    
    with col2:
        r30 = metrics["retention_j30"]
        st.metric(
            "Rétention J+30",
            f"{r30['retention_rate']}%",
            f"{r30['retained_users']}/{r30['cohort_size']}"
        )
    
    # Section Adoption
    st.header("🚀 Adoption des fonctionnalités")
    if metrics["feature_adoption"]:
        st.json(metrics["feature_adoption"])
    else:
        st.info("Pas encore de données sur l'adoption")

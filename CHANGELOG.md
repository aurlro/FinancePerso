# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

---


## [5.2.1] - 2026-02-24

### Nouvelle page fonctionnelle (commits + local)

**ADDED**
- - Feat: Introduce backup/restore, customizable dashboard, audit tools, and AI suggestions, along with various UI and backend refinements.
- - Feat: Migrate views to pages, introduce new UI config, and refactor loading states and database imports.
- - Consolidate UI and DB modules, documentation, and various project files into a new dated archive directory.
- - Feat: Introduce a consolidated application architecture, new core functionalities, expanded test coverage, and updated user documentation, while archiving previous project files.
- - Feat: Introduce AI suggestion analyzers, a new `ui_v2` component library, and a dedicated update management module.
- - And enhance various UI components, database operations, AI features, core modules, and testing infrastructure across the application.
- - Feat: Rework application pages, introduce smart reminders and savings goals, and enhance UX with new components and audit assets.
- - Feat: Introduce comprehensive UI feedback, error handling, and new components for empty states, tooltips, loading, and confirmation dialogs.
- - Feat: Implement comprehensive Git change analysis in UpdateManager to detect committed and uncommitted changes, categorize commits, and suggest version bumps, accompanied by new tests.
- - Feat: Refactor page structure by consolidating rules, recurrences, budgets, and AI audit into a new Intelligence page, and modularize import, validation, and search functionalities.
- - Feat: implement offline mode for categorization, redesign the evolution chart, and reorganize project structure with new tests and scripts.
- - Feat: Implement clickable category buttons in the dashboard to launch the explorer, refactoring parameter passing to use session state.
- - Feat: Introduce new UI components for validation, including avatar and chip selectors, and refactor the notification system to V2.
- - Feat: Implement a comprehensive notification system including UI, management logic, and dedicated pages.
- - Feat: introduce recurrence feedback and management, and add new Explorer and Assistant UI modules
- - ✨ feat: Add scroll-to-top button on all pages
- - ✨ feat: Add comprehensive visual feedback system and quick actions popups
- - Feat: Implement enhanced audit functionality with bulk actions, filtering, and a new analytics module.
- - Feat: Add comprehensive input validation and security utilities
- - Versionning and a new logic to present commits
- - Feat: Implement `st.toast` for user feedback, refactor tag suggestion UI, and enhance rules auditor with stale rule detection and health scoring.
- - Feat: Add a comprehensive AI suite for financial analysis and assistance, including anomaly detection, budget prediction, smart tagging, trend analysis, and a conversational assistant.
- - Feat: Add a profile setup form for initial financial configuration, enhance transaction querying, and refine category management and assistant feedback.
- - Feat: Add a comprehensive test suite for UI and database modules, introduce new UI dashboard and validation components, and update data management logic and dependencies.
- - Feat: Add recurrence analysis page, undo last validation action, logs viewer in configuration, and a new audit script.
- - Feat: Introduce bulk transaction group categorization and refine tag management with category-specific suggestions and creation.
- - Automatic daily backup system with 1-year retention and restore UI
- - Enhanced Import Wizard with duplicate preview, account selection, period filter

**FIXED**
- - (phase2): Corrections selon specifications exactes
- - Feat: Introduce smart suggestions and enhance member identification with default member settings and repair capabilities.
- - Feat(étape 5 - audit final): Correction des derniers fichiers UI et modules
- - Lancement rapide si déjà installé - évite la réinstallation
- - Ci: Ajoute debug et timeout au workflow de test
- - Sépare test_is_enabled en deux tests distincts
- - Améliore test_is_enabled avec meilleur message d'erreur
- - Déplace la fixture reset_encryption_singleton dans conftest.py global
- - Ajoute fixture pour réinitialiser le singleton encryption entre tests
- - Corrige test_is_enabled qui échouait en CI à cause de ENCRYPTION_KEY définie
- - Feat: dashboard personnalisable, recherche globale, onboarding + corrections sécurité
- - Correction vue d'ensemble vide - ajout fallback et messages
- - Déplacement de switch_to_tab avant son utilisation
- - Feat: Update project to version 4.1.0, incorporating new features, bug fixes, and performance enhancements.
- - Correction clés dupliquées dans explorer_filters
- - Correction import update_budget → set_budget
- - Amélioration scroll-to-top et graphique évolution mensuelle
- - Correction imports modules/ui et analyse auto changements
- - 🐛 fix: Correction imports render_scroll_to_top
- - 🐛 fix: Correction erreur SQL merge_categories - colonne id budgets
- - 🐛 fix: Système de logs - fichier et viewer
- - 🔧 fix: Audit corrections - version sync, cleanup, docs
- - 🔧 fix: Improve email notification error handling and user feedback
- - Correct cache invalidation import errors
- - Critical code cleanup - remove dead code and fix bugs
- - Security: Fix critical security issues and improve error handling
- - Audit query persistent flagging and sanitize UI keys
- - Handle Income (Revenus) in transfer audit and fix duplicate SQL bug
- - Allow custom category selection for bulk transfer corrections
- - Enhance transfer audit with intelligent grouping and bulk correction
- - Indentation error and Add dismissible recent import summary in Import page
- - KeyError 'avg_amount' when no recurring items detected
- - SyntaxError in f-string in 1_Import.py
- - Dynamic year range (future-proof from 2024 to current+1)
- - Init_db call + max_date type handling

**FICHIERS MODIFIÉS**
- `modules/ui/assistant/components.py`
- `.env.example`
- `docs/archive/UX_IMPROVEMENTS.md`
- `MyFinance.command`
- `pyproject.toml`
- `migrations/migrate_meta_data.py`
- `modules/performance/__init__.py`
- `modules/performance/cache_advanced.py`
- `docs/archive/COMPLETE_AUDIT_REPORT.md`
- `.agents/skills/financeperso-specific/references/architecture.md`
- `docs/archive/STABILIZATION_PLAN.md`
- `modules/ui/validation/__init__.py`
- `modules/ui/components/local_ml_manager.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/forms/__init__.py`
- `modules/ui/assistant/state.py`
- `scripts/repair_hashes.py`
- `modules/db/members.py`
- `scripts/create_tests_strategy.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/onboarding_modal.py`
- `tests/ui/validation/test_grouping.py`
- `modules/ai/suggestions/analyzers/__init__.py`
- `"pages/99_Syst\303\250me.py"`
- `demos/demo_local_ai.py`
- `docs/archive/NEW_FEATURES.md`
- `modules/ui/dashboard/smart_recommendations.py`
- `modules/ui/dashboard/kpi_cards.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/notifications/special.py`
- `modules/ai/suggestions/__init__.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/notifications/types.py`
- `modules/ui/components/filters.py`
- `modules/update/git.py`
- `modules/ai/suggestions/analyzers/patterns.py`
- `scripts/fix_dashboard_layouts.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/transaction_drill_down.py`
- `tests/ai/test_rules_auditor.py`
- `assets/style.css`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/empty_states.py`
- `modules/ai/suggestions/analyzers/members.py`
- `modules/ui/rules/__init__.py`
- `.github/workflows/release.yml`
- `docs/archive/audit_budgets_ux_archi.md`
- `check_models.py => scripts/check_models.py`
- `modules/ingestion.py`
- `modules/ui/notifications/components.py`
- `modules/ai/conversational_assistant.py`
- `modules/ui/rules/rule_validator.py`
- `pages/5_Assistant.py`
- `docs/archive/PHASE3_RECURRENCE_ENGINE.md`
- `tests/db/test_audit.py`
- `.vscode/settings.json`
- `modules/notifications.py`
- `modules/performance_monitor.py`
- `docs/archive/PROJECT_SUMMARY.md`
- `modules/ui/components/onboarding_modal.py`
- `docs/archive/GUIDE_UTILISATEUR.md`
- `modules/db/migrations.py`
- `scripts/audit_redux.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/widgets/savings_goals.py`
- `docs/archive/IA_LOCALE.md`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/__init__.py`
- `modules/ui/explorer/__init__.py`
- `docs/archive/AUDIT_COHERENCE_360.md`
- `modules/db/maintenance.py`
- `modules/db/audit.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/__init__.py`
- `modules/ai_manager_v2.py`
- `archive/legacy_v5/modules/ai_manager.py`
- `modules/data_manager.py`
- `modules/ui/validation/main.py`
- `modules/ui/recurrence_manager.py`
- `tests/test_essential.py`
- `"4.2 Composant : Table de d\303\251penses.md" => "docs/4.2 Composant : Table de d\303\251penses.md"`
- `modules/savings_goals.py`
- `modules/ui/dashboard/__init__.py`
- `modules/db/transactions_batch.py`
- `tests/db/test_tags.py`
- `archive/consolidation_2026-02-22/docs/PUSH_FINAL.md`
- `modules/ui/layout.py`
- `archive/legacy_v5/modules/data_manager.py`
- `modules/ai/__init__.py`
- `modules/ui/components/empty_states.py`
- `modules/ui/components/tooltips.py`
- `archive/consolidation_2026-02-22/modules/db_v2/repositories/transaction_repository.py`
- `archive/consolidation_2026-02-22/modules/db_v2/base/repository.py`
- `.streamlit/config.toml`
- `2. Palette.md => docs/2. Palette.md`
- `docs/archive/PHASE5_WEALTH_AGENTIC.md`
- `scripts/budget_redesign_prototype.py`
- `setup_local_ai.sh`
- `docs/archive/REPOSITORY_PATTERN_DESIGN.md`
- `scripts/migrate_to_logging.py`
- `modules/cache_monitor.py`
- `modules/notifications_realtime.py`
- `docs/archive/implementation_plan.md`
- `1. PROJET.md => docs/1. PROJET.md`
- `docs/archive/CHANGEMENTS_REVENUS_DEPENSES.md`
- `archive/legacy_v5/modules/legacy_wrapper.py`
- `docs/archive/FINAL_AUDIT_SUMMARY.md`
- `modules/ai/category_insights.py`
- `tests/test_update_manager.py`
- `pages/4_Intelligence.py`
- `tests/db/test_budgets.py`
- `tests/ai/test_anomaly_detector.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/widgets/dashboard/top_expenses.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/empty_states.py`
- `tests/test_local_ai.py`
- `tests/db/__init__.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/notifications/styles.py`
- `modules/ui/notifications/types.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/toasts.py`
- `modules/validators.py`
- `scripts/pre-push.sh`
- `tests/db/test_rules.py`
- `tests/conftest.py`
- `modules/categorization.py`
- `modules/db/tags.py`
- `modules/db/__init__.py`
- `modules/ui/dashboard/top_expenses.py`
- `modules/ai/audit_engine.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/templates/layouts.py`
- `modules/db/settings.py`
- `modules/local_ml.py`
- `docs/archive/AUDIT_CORRECTIONS_IMMEDIATES.md`
- `archive/consolidation_2026-02-22/modules/ui_v2/templates/manager.py`
- `modules/onboarding.py`
- `src/__init__.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/loading_states.py`
- `src/visualizations.py`
- `modules/ui/feedback_wrapper.py`
- `docs/archive/FIX_WIDGETTYPE_V2.md`
- `tests/db/test_migrations.py`
- `modules/ui/intelligence/__init__.py`
- `pages/4_Regles.py`
- `modules/db/recurrence_feedback.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/smart_actions.py`
- `4.4 Composant : Boutons.md => docs/4.4 Composant : Boutons.md`
- `scripts/versioning.py`
- `docs/archive/PROJECT_STATUS.md`
- `docs/archive/ULTIMATE_FINAL_REPORT.md`
- `archive/consolidation_2026-02-22/modules/ui_v2/atoms/icons.py`
- `modules/ui/components/daily_widget.py`
- `modules/update/version.py`
- `modules/ai/suggestions/base.py`
- `archive/consolidation_2026-02-22/modules/db_v2/models/budget.py`
- `docs/archive/TRANSACTION_TYPES_GUIDE.md`
- `archive/consolidation_2026-02-22/modules/db_v2/__init__.py`
- `modules/analytics.py`
- `"pages/1_Op\303\251rations.py"`
- `scripts/Lancer_App.command`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/selectors.py`
- `requirements-ml.txt`
- `docs/archive/ASSISTANT_UX_WIREFRAME.md`
- `modules/ai/suggestions/engine.py`
- `archive/consolidation_2026-02-22/docs/PLAN_ORCHESTRATION_REVISED.md`
- `modules/db/transactions.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/config/notifications.py`
- `modules/analytics_constants.py`
- `requirements.txt`
- `docs/audit_report.json`
- `"4.3 Composant : Carte d\342\200\231insight IA.md" => "docs/4.3 Composant : Carte d\342\200\231insight IA.md"`
- `odules/update/__init__.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/transactions/drill_down.py`
- `archive/consolidation_2026-02-22/modules/ui.py`
- `src/data_cleaning.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/transactions/diagnostic.py`
- `pages/6_Audit.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/config/data_operations.py`
- `modules/ai/suggestions/analyzers/budgets.py`
- `modules/ui/notifications/center.py`
- `archive/legacy_v5/modules/ui/backup_restore.py`
- `docker-compose.yml`
- `modules/ai/trend_analyzer.py`
- `"3.2 Page : D\303\251penses \303\240 valider.md" => "docs/3.2 Page : D\303\251penses \303\240 valider.md"`
- `archive/consolidation_2026-02-22/modules/ui_v2/widgets/dashboard/category_charts.py`
- `docs/archive/UAT_GUIDE.md`
- `docs/archive/AUDIT_DEPENSES_REVENUS.md`
- `modules/ui/components/smart_reminders_widget.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/notifications/__init__.py`
- `4.1 Composant : Navigation principale.md => docs/4.1 Composant : Navigation principale.md`
- `docs/archive/INDISPENSABILITY_UPGRADES.md`
- `modules/encryption.py`
- `tests/test_integration.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/atoms/__init__.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/flash_messages.py`
- `modules/db/categories.py`
- `archive/consolidation_2026-02-22/docs/CONSOLIDATION_FINAL_REPORT.md`
- `docs/archive/PHASE2_NORMALISATION_CASCADE.md`
- `modules/ui/explorer/explorer_main.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/loading_states.py`
- `modules/backup_manager.py`
- `docs/archive/RAPPORT_AUDIT_COMPLET.md`
- `Makefile`
- `modules/ui/config/audit_tools.py`
- `assets/manifest.json`
- `modules/core/events.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/tag_manager.py`
- `modules/analytics_v2.py`
- `modules/feature_flags.py`
- `tests/ui/validation/__init__.py`
- `modules/ui/components/member_selector.py`
- `modules/ui/dashboard/budget_tracker.py`
- `modules/ui/components/tag_manager.py`
- `modules/budgets_dynamic.py`
- `src/security_monitor.py`
- `modules/ui/config/api_settings.py`
- `tests/ui/test_ui_redesign.py`
- `archive/legacy_v5/modules/ui/member_management.py`
- `scripts/doctor.py`
- `modules/ui/importing/main.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/notifications/toast.py`
- `CONTRIBUTING.md`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/quick_actions.py`
- `assets/pwa.js`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/tags/tag_selector_smart.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/widgets/dashboard/filters.py`
- `tests/ui/__init__.py`
- `modules/privacy/gdpr_manager.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/forms/avatar_selector.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/__init__.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/tags/tag_selector_compact.py`
- `archive/legacy_v5/modules/ui/__init__.py`
- `docs/archive/AUDIT_FIXES_SUMMARY.md`
- `modules/ui/global_search.py`
- `scripts/analyze_dependencies.py`
- `tests/integration/test_compliance.py`
- `modules/transactions/__init__.py`
- `pages/2_Validation.py`
- `archive/consolidation_2026-02-22/modules/db_v2/base/unit_of_work.py`
- `"pages/3_Synth\303\250se.py"`
- `archive/consolidation_2026-02-22/docs/GUIDE_EXECUTIF_CONSOLIDATION.md`
- `modules/ui/assistant/audit_tab.py`
- `docs/archive/ARCHITECTURE_EXPLORER.md`
- `scripts/validate_consolidation.py`
- `tests/unit/test_subscriptions.py`
- `docs/archive/audit_report.md`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/config/backup_restore.py`
- `modules/transaction_types.py`
- `pages/5_Budgets.py`
- `modules/ai/suggestions/analyzers/tags.py`
- `migrations/add_meta_data_column.sql`
- `modules/utils.py`
- `archive/consolidation_2026-02-22/modules/db_v2/repositories/budget_repository.py`
- `docs/archive/gemini.md`
- `docs/archive/IMPORTS_AUDIT_REPORT.md`
- `modules/ui/components/confirm_dialog.py`
- `modules/ui/validation/row_view.py`
- `modules/db/repositories/__init__.py`
- `archive/consolidation_2026-02-22/modules/db_v2/models/category.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/widgets/dashboard/budget_tracker.py`
- `modules/ui/components/chip_selector.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/widgets/smart_reminders.py`
- `scripts/setup_dev_env.sh`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/transactions/__init__.py`
- `CHANGELOG.md`
- `docs/archive/AUDIT_COMPLET_V6.md`
- `pages/3_Synthese.py`
- `docs/refactoring/phase1-imports.md`
- `scripts/quick_integrate.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/widgets/dashboard/legacy.py`
- `"pages/10_Nouveaut\303\251s.py"`
- `modules/ui/feedback.py`
- `tests/unit/test_data_cleaning.py`
- `modules/ai/suggestions/analyzers/income.py`
- `modules/ui/components/tag_selector_compact.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/templates/renderer.py`
- `.agents/skills/financeperso-specific/SKILL.md`
- `tests/unit/test_cache.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/widgets/dashboard/evolution_chart.py`
- `docs/archive/PLAN_ORCHESTRATION.md`
- `modules/__init__.py`
- `modules/ui/components/profile_form.py`
- `tests/__init__.py`
- `3.3 Page : Dashboard narratif.md => docs/3.3 Page : Dashboard narratif.md`
- `conftest.py`
- `modules/ui/dashboard/ai_insights.py`
- `modules/ui/components/quick_actions.py`
- `modules/import_analyzer.py`
- `docs/archive/AUDIT_REVENUS_DEPENSES.md`
- `modules/ai/budget_predictor.py`
- `tests/integration/test_security.py`
- `modules/ui/rules/rule_manager.py`
- `modules/cache_manager.py`
- `docs/archive/AGENTS.md`
- `modules/db/dashboard_layouts.py`
- `modules/db/rules.py`
- `modules/ai/suggestions/models.py`
- `tests/README.md`
- `docs/archive/EMAIL_TROUBLESHOOTING.md`
- `modules/ui/notifications/manager.py`
- `tests/run_tests.sh`
- `modules/cache_multitier.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/dialogs.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/templates/__init__.py`
- `docs/archive/FINAL_CORRECTIONS_REPORT.md`
- `docs/ARCHITECTURE.md`
- `tests/e2e/test_wealth_projection.py`
- `scripts/run_production.sh`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/widgets/progress_tracker.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/atoms/colors.py`
- `modules/impact_analyzer.py`
- `modules/db/budgets.py`
- `CLEANUP_REPORT.md`
- `tests/integration/test_performance.py`
- `docs/archive/EXPLORER_INTEGRATION.md`
- `modules/privacy/__init__.py`
- `pages/13_Patrimoine.py`
- `modules/ui/notifications/README.md`
- `modules/ui/dashboard/sections.py`
- `modules/ui/assistant/analytics_tab.py`
- `archive/legacy_v5/modules/ui/customizable_dashboard.py`
- `modules/ui/explorer/explorer_results.py`
- `3.1 Page : Import & Sources.md => docs/3.1 Page : Import & Sources.md`
- `modules/ui/styles/global.css`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/banners.py`
- `assets/service-worker.js`
- `pages/1_Import.py`
- `modules/ui/explorer/explorer_launcher.py`
- `requirements-dev.txt`
- `modules/exceptions.py`
- `archive/legacy_v5/modules/ui/audit_tools.py`
- `modules/update/models.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/notifications/legacy.py`
- `modules/ui/intelligence/suggestions_panel.py`
- `archive/consolidation_2026-02-22/modules/db_v2/repositories/__init__.py`
- `archive/legacy_v5/modules/ui/log_viewer.py`
- `modules/ai/suggestions/analyzers/categories.py`
- `scripts/cleanup_duplicates.py`
- `modules/update/__init__.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/widgets/daily_widget.py`
- `docs/archive/FIX_WIDGET_ERROR.md`
- `modules/ui/config/backup_restore.py`
- `modules/db/stats.py`
- `modules/update/creator.py`
- `scripts/migrate_module.py`
- `archive/legacy_v5/modules/ui/category_management.py`
- `tests/db/test_transactions.py`
- `docs/archive/DASHBOARD_CLEANUP_GUIDE.md`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/config/tags_rules.py`
- `.gitignore`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/confirm_dialog.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/config/member_management.py`
- `archive/consolidation_2026-02-22/modules/db_v2/models/__init__.py`
- `scripts/benchmark.py`
- `docs/archive/REFACTORING_PROGRESS.md`
- `modules/ui/components/loading_states.py`
- `modules/ui/dashboard/customizable_dashboard.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/tags/__init__.py`
- `src/subscription_engine.py`
- `archive/legacy_v5/modules/ui/config_mode.py`
- `archive/consolidation_2026-02-22/docs/CONSOLIDATION_REPORT.md`
- `archive/consolidation_2026-02-22/modules/db_v2/repositories/category_repository.py`
- `docs/archive/N1_FIX_PLAN.md`
- `pages/12_Abonnements.py`
- `tests/db/test_categories.py`
- `modules/ui/validation/sorting.py`
- `docs/archive/MIGRATION_NOTES.md`
- `modules/ui/components/transaction_diagnostic.py`
- `modules/ui/components/transaction_drill_down.py`
- `archive/legacy_v5/modules/ui/notifications.py`
- `modules/ui/rules/budget_manager.py`
- `modules/ui/enhanced_feedback.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/widgets/dashboard/__init__.py`
- `docs/architecture/v6-target.md`
- `modules/ui/components/tag_selector_smart.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/widgets/dashboard/smart_recommendations.py`
- `modules/ui/validation/grouping.py`
- `tests/test_encryption.py`
- `modules/ai/smart_suggestions.py`
- `src/math_engine.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/forms/profile_form.py`
- `modules/transactions/services.py`
- `archive/2026-02-22_cleanup/app.py.backup.20260221_165525`
- `modules/ui/assistant/__init__.py`
- `modules/ui/components/smart_actions.py`
- `.vscode/extensions.json`
- `archive/consolidation_2026-02-22/modules/db_v2/models/member.py`
- `modules/db/connection.py`
- `pages/8_Recherche.py`
- `archive/legacy_v5/modules/ui/config_dashboard.py`
- `docs/archive/PHASE6_FINAL_OPTIMIZATION.md`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/config/category_management.py`
- `scripts/profile_db.py`
- `modules/error_handlers.py`
- `archive/consolidation_2026-02-22/docs/CONSOLIDATION_README.md`
- `archive/consolidation_2026-02-22/modules/db_v2/base/__init__.py`
- `modules/ui/assistant/dashboard_tab.py`
- `modules/gamification.py`
- `modules/logger.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/widgets/dashboard/ai_insights.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/widgets/dashboard/kpi_cards.py`
- `README.md`
- `docs/archive/PHASE4_MONTE_CARLO.md`
- `docs/archive/phase3_repository_pattern.md`
- `modules/ai/anomaly_detector.py`
- `modules/smart_reminders.py`
- `modules/ui/__init__.py`
- `Dockerfile`
- `archive/consolidation_2026-02-22/modules/db_v2/models/transaction.py`
- `archive/legacy_v5/modules/ui/api_settings.py`
- `modules/ui/dashboard/category_charts.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/templates/legacy.py`
- `"3.4 Page : R\303\250gles & M\303\251moire.md" => "docs/3.4 Page : R\303\250gles & M\303\251moire.md"`
- `tests/unit/test_wealth.py`
- `src/agent_core.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/config/audit_tools.py`
- `modules/update/changelog.py`
- `archive/legacy_v5/modules/ui/data_operations.py`
- `modules/update/manager.py`
- `modules/ai/local_slm_provider.py`
- `docs/USER_GUIDE.md`
- `modules/ui/changelog_parser.py`
- `archive/consolidation_2026-02-22/modules/db_v2/repositories/member_repository.py`
- `docs/archive/PLAN_EXPERT.md`
- `modules/ui/assistant/config_tab.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/templates/app_layout.py`
- `tests/unit/test_ui.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/widgets/__init__.py`
- `scripts/audit_codebase.py`
- `modules/milestone_celebrations.py`
- `tests/unit/test_transaction_types.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/config/__init__.py`
- `pages/7_Assistant.py`
- `pytest.ini`
- `modules/ui/components/avatar_selector.py`
- `modules/ui/components/savings_goals_widget.py`
- `modules/ui/recurrence_tabs.py`
- `src/wealth_manager.py`
- `modules/categorization_cascade.py`
- `4.5 Composant : Modale de validation.md => docs/4.5 Composant : Modale de validation.md`
- `tests/db/test_stats.py`
- `tests/core/test_events.py`
- `assets/offline.html`
- `tests/db/test_members.py`
- `scripts/cleanup_backups.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/notifications/inline.py`
- `modules/ui/components/__init__.py`
- `tests/core/__init__.py`
- `docs/refactoring/phase1-modules-god.md`
- `modules/ui/explorer/explorer_filters.py`
- `modules/error_tracking.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/tags/tag_manager.py`
- `docs/archive/AUDIT_DATA_ENGINEERING.md`
- `tests/e2e/test_transaction_lifecycle.py`
- `docs/archive/WIDGETS_STATE_FIXES.md`
- `docs/archive/Optimisation Suivi Financier Plan d'Action.md`
- `archive/legacy_v5/modules/ui/tags_rules.py`
- `modules/ui/rules/rule_audit.py`
- `modules/ui/dashboard/filters.py`
- `archive/legacy_v5/modules/update_manager.py`
- `app.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/__init__.py`
- `tests/core/test_events_extended.py`
- `src/wealth_projection.py`
- `modules/ui/design_system.py`
- `pages/11_Projections.py`
- `pages/9_Configuration.py`
- `docs/archive/PHASE2_DATA_ENGINEERING.md`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/config/legacy.py`
- `modules/ai/smart_tagger.py`
- `modules/constants.py`
- `modules/transactions/constants.py`
- `modules/db/dashboard_cleanup.py`
- `modules/ui/dashboard/evolution_chart.py`
- `modules/core/__init__.py`
- `docs/archive/roadmap.md`
- `modules/ui/config/__init__.py`
- `modules/ai/rules_auditor.py`
- `.github/workflows/ci.yml`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/badges.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/molecules/components/legacy.py`
- `docs/archive/RAPPORT_COMPLET_APPLICATION.md`
- `modules/ui/components/progress_tracker.py`
- `archive/consolidation_2026-02-22/docs/EXECUTION_ROADMAP.md`
- `modules/ui/notifications/__init__.py`
- `archive/consolidation_2026-02-22/modules/ui_v2/organisms/config/api_settings.py`

## [5.2.0] - 2026-02-08

### Nouvelles fonctionnalités - 4 ajouts (commits + local)

**✨ Ajouté**
- - feat: Introduce comprehensive UI enhancements, new AI features, database improvements, and development tooling.
- - feat: Introduce comprehensive UI feedback, error handling, and new components for empty states, tooltips, loading, and confirmation dialogs.
- - ci: Ajoute debug et timeout au workflow de test
- - fix: Ajoute fixture pour réinitialiser le singleton encryption entre tests

**🐛 Corrigé**
- - feat: Introduce smart suggestions and enhance member identification with default member settings and repair capabilities.
- - feat(étape 5 - audit final): Correction des derniers fichiers UI et modules
- - fix: Lancement rapide si déjà installé - évite la réinstallation
- - fix: Sépare test_is_enabled en deux tests distincts
- - fix: Améliore test_is_enabled avec meilleur message d'erreur
- - fix: Déplace la fixture reset_encryption_singleton dans conftest.py global

*Fichiers modifiés* : modules/ui/dashboard/evolution_chart.py, modules/ui/components/local_ml_manager.py, modules/ui/components/progress_tracker.py, modules/ui/dashboard/sections.py, modules/ui/components/tag_manager.py, AGENTS.md, tests/test_link_integrity.py, tests/ui/validation/test_grouping.py, tests/test_onboarding.py, modules/cache_monitor.py, tests/test_components.py, modules/ui/dashboard/filters.py, modules/ui/rules/rule_validator.py, modules/ui/components/quick_actions.py, modules/ai/conversational_assistant.py, modules/transaction_types.py, modules/ui/changelog_parser.py, modules/db/categories.py, modules/ui/components/daily_widget.py, modules/ui/components/smart_actions.py, modules/db/settings.py, modules/ui/config/log_viewer.py, tests/ui/test_tag_manager.py, modules/ui/validation/row_view.py, modules/ui/components/savings_goals_widget.py, CONTRIBUTING.md, modules/budgets_dynamic.py, modules/db/audit.py, tests/db/test_migrations.py, modules/ai/rules_auditor.py, modules/error_handlers.py, modules/ui/assistant/config_tab.py, tests/test_notifications.py, AUDIT_DEPENSES_REVENUS.md, tests/ui/test_filters.py, modules/error_tracking.py, tests/test_update_manager.py, tests/ui/test_category_charts.py, tests/test_global_search.py, modules/ai/smart_suggestions.py, modules/db/dashboard_cleanup.py, modules/savings_goals.py, scripts/audit_codebase.py, app.py, modules/ui.py, modules/ui/components/__init__.py, tests/db/test_stats.py, modules/ui/dashboard/budget_tracker.py, modules/ui/components/member_selector.py, modules/ui/components/transaction_drill_down.py, tests/test_cache_multitier.py, pages/3_Synthese.py, modules/ai/smart_tagger.py, modules/data_manager.py, modules/db/rules.py, modules/ui/global_search.py, modules/ui/components/tag_selector_smart.py, tests/ai/test_anomaly_detector.py, tests/test_analytics.py, tests/db/test_transactions.py, modules/update_manager.py, tests/db/test_members.py, modules/ui/components/profile_form.py, modules/ui/config/api_settings.py, modules/ui/config/config_mode.py, modules/ui/dashboard/top_expenses.py, CHANGELOG.md, modules/analytics_constants.py, modules/ui/components/confirm_dialog.py, tests/db/test_audit.py, modules/logger.py, tests/conftest.py, modules/categorization.py, modules/ai/anomaly_detector.py, modules/db/migrations.py, modules/ui/notifications/components.py, pages/6_Recherche.py, tests/test_data_integrity.py, modules/smart_reminders.py, tests/ai/test_rules_auditor.py, modules/ui/dashboard/kpi_cards.py, modules/ai/__init__.py, modules/ui/explorer/explorer_results.py, UX_IMPROVEMENTS.md, modules/ui/config/notifications.py, modules/ui/components/chip_selector.py, modules/db/maintenance.py, modules/notifications_realtime.py, tests/test_essential.py, modules/ui/config/category_management.py, modules/db/tags.py, tests/test_email.py, modules/db/transactions_batch.py, tests/README.md, tests/ui/test_progress_tracker.py, modules/ui/enhanced_feedback.py, tests/test_validators.py, tests/unit/test_cleanup_backups.py, modules/gamification.py, modules/ui/explorer/explorer_main.py, tests/ui/test_ui_redesign.py, tests/test_utils.py, modules/db/dashboard_layouts.py, PROJECT_STATUS.md, modules/ai_manager.py, modules/onboarding.py, modules/utils.py, modules/impact_analyzer.py, modules/ui/components/empty_states.py, modules/ui/config/backup_restore.py, modules/analytics_v2.py, modules/ui/explorer/explorer_launcher.py, modules/feature_flags.py, modules/db/transactions.py, modules/ai/budget_predictor.py, modules/import_analyzer.py, modules/ui/assistant/analytics_tab.py, modules/ui/explorer/__init__.py, modules/ui/notifications/manager.py, modules/ui/assistant/audit_tab.py, pages/4_Intelligence.py, modules/ui/__init__.py, modules/ui/rules/__init__.py, modules/cache_multitier.py, modules/ui/config/audit_tools.py, modules/backup_manager.py, modules/ui/assistant/__init__.py, modules/ui/components/filters.py, modules/ui/config/config_dashboard.py, PLAN_EXPERT.md, modules/ui/dashboard/category_charts.py, modules/ui/importing/main.py, tests/ai/test_conversational_assistant.py, tests/unit/test_transaction_types.py, modules/notifications.py, modules/ui/assistant/components.py, modules/ui/assistant/dashboard_tab.py, pp.py, modules/ui/rules/rule_manager.py, modules/ui/assistant/state.py, modules/exceptions.py, modules/db/budgets.py, modules/ui/dashboard/customizable_dashboard.py, modules/ui/components/transaction_diagnostic.py, modules/cache_manager.py, scripts/doctor.py, pages/5_Assistant.py, modules/ui/components/loading_states.py, modules/ingestion.py, modules/local_ml.py, tests/test_customizable_dashboard.py, modules/encryption.py, modules/ui/config/member_management.py, modules/db/connection.py, modules/ui/feedback_wrapper.py, modules/ui/recurrence_manager.py, modules/ui/validation/main.py, modules/ui/components/tag_selector_compact.py, tests/db/test_budgets.py, modules/ai/trend_analyzer.py, modules/ui/recurrence_tabs.py, modules/ui/layout.py, tests/ui/validation/test_sorting.py, modules/ui/validation/__init__.py, pages/9_Configuration.py, modules/db/recurrence_feedback.py, modules/ui/components/avatar_selector.py, tests/db/test_categories.py, modules/analytics.py, modules/ai/category_insights.py, modules/ui/components/smart_reminders_widget.py, modules/ui/dashboard/smart_recommendations.py, modules/ui/dashboard/ai_insights.py, tests/ui/test_kpi_cards.py, tests/conftest_enhanced.py, modules/ui/rules/budget_manager.py, modules/ui/config/data_operations.py, modules/ui/validation/grouping.py, modules/ui/config/tags_rules.py, tests/test_encryption.py, modules/ui/components/tooltips.py, modules/ai/audit_engine.py, modules/ui/explorer/explorer_filters.py, modules/ui/rules/rule_audit.py, modules/ui/intelligence/__init__.py, modules/ui/notifications/__init__.py, modules/ui/validation/sorting.py, tests/ui/test_member_selector.py, modules/ui/feedback.py, modules/milestone_celebrations.py, tests/db/test_tags.py, modules/performance_monitor.py, modules/constants.py, modules/ui/components/onboarding_modal.py, tests/test_integration.py, modules/validators.py, modules/db/members.py, tests/db/test_rules.py, modules/db/stats.py, modules/ui/notifications/types.py, modules/ui/intelligence/suggestions_panel.py, modules/ui/notifications/center.py

---

## [5.1.0] - 2026-02-08

### Nouvelles fonctionnalités - 4 ajouts

**✨ Ajouté**
- - feat: Introduce comprehensive UI feedback, error handling, and new components for empty states, tooltips, loading, and confirmation dialogs.
- - ci: Ajoute debug et timeout au workflow de test
- - fix: Ajoute fixture pour réinitialiser le singleton encryption entre tests
- - feat: Implement comprehensive Git change analysis in UpdateManager to detect committed and uncommitted changes, categorize commits, and suggest version bumps, accompanied by new tests.

**🐛 Corrigé**
- - feat(étape 5 - audit final): Correction des derniers fichiers UI et modules
- - fix: Lancement rapide si déjà installé - évite la réinstallation
- - fix: Sépare test_is_enabled en deux tests distincts
- - fix: Améliore test_is_enabled avec meilleur message d'erreur
- - fix: Déplace la fixture reset_encryption_singleton dans conftest.py global
- - fix: Corrige test_is_enabled qui échouait en CI à cause de ENCRYPTION_KEY définie

*Fichiers modifiés* : tests/ui/test_kpi_cards.py, modules/ai/trend_analyzer.py, modules/db/transactions.py, CHANGELOG.md, modules/constants.py, modules/ui/components/empty_states.py, modules/ui/config/data_operations.py, tests/unit/test_cleanup_backups.py, tests/test_analytics.py, tests/test_email.py, modules/ui/dashboard/customizable_dashboard.py, modules/ui/dashboard/sections.py, modules/ai/budget_predictor.py, tests/conftest_enhanced.py, modules/ui/dashboard/budget_tracker.py, tests/test_customizable_dashboard.py, modules/ui/dashboard/smart_recommendations.py, modules/ui/components/onboarding_modal.py, scripts/audit_codebase.py, modules/analytics_v2.py, modules/ui/components/smart_actions.py, modules/ai/category_insights.py, tests/test_notifications.py, tests/conftest.py, tests/ui/test_progress_tracker.py, AGENTS.md, modules/ui/dashboard/category_charts.py, modules/import_analyzer.py, modules/ui/recurrence_tabs.py, modules/ui/assistant/audit_tab.py, modules/ui/components/loading_states.py, tests/test_link_integrity.py, tests/ai/test_conversational_assistant.py, tests/ui/test_member_selector.py, modules/onboarding.py, pages/3_Synthese.py, modules/ui/dashboard/top_expenses.py, modules/ai_manager.py, tests/test_global_search.py, tests/test_validators.py, modules/ui/feedback_wrapper.py, modules/budgets_dynamic.py, tests/README.md, modules/transaction_types.py, modules/ui/validation/main.py, modules/ui/global_search.py, modules/ui/notifications/center.py, tests/test_components.py, modules/notifications.py, modules/ui/components/confirm_dialog.py, tests/test_cache_multitier.py, modules/ui/validation/row_view.py, tests/test_onboarding.py, modules/analytics.py, modules/ui/explorer/explorer_results.py, modules/ui/explorer/explorer_filters.py, modules/ui/rules/rule_validator.py, tests/test_utils.py, tests/test_essential.py, modules/encryption.py, modules/ai/anomaly_detector.py, tests/test_encryption.py, modules/cache_monitor.py, tests/test_data_integrity.py, tests/ui/validation/test_sorting.py, app.py, modules/ui/components/transaction_diagnostic.py, modules/ui/components/tooltips.py, modules/error_handlers.py, modules/impact_analyzer.py, tests/test_update_manager.py, modules/performance_monitor.py, modules/notifications_realtime.py, modules/ui/components/quick_actions.py, modules/update_manager.py, tests/ui/test_tag_manager.py, modules/db/audit.py, modules/db/migrations.py, AUDIT_DEPENSES_REVENUS.md, modules/ui/dashboard/ai_insights.py, modules/db/dashboard_cleanup.py, modules/ui/recurrence_manager.py, tests/ui/test_filters.py, modules/db/members.py, tests/ui/test_category_charts.py, modules/ingestion.py, modules/db/transactions_batch.py, modules/ui/components/tag_manager.py, modules/ai/conversational_assistant.py

---

## [5.0.2] - 2026-02-07

### Nouvelles fonctionnalités - 8 ajouts

**✨ Ajouté**
- - ci: Ajoute debug et timeout au workflow de test
- - fix: Ajoute fixture pour réinitialiser le singleton encryption entre tests
- - feat: Implement comprehensive Git change analysis in UpdateManager to detect committed and uncommitted changes, categorize commits, and suggest version bumps, accompanied by new tests.
- - feat: Refactor page structure by consolidating rules, recurrences, budgets, and AI audit into a new Intelligence page, and modularize import, validation, and search functionalities.
- - feat: implement offline mode for categorization, redesign the evolution chart, and reorganize project structure with new tests and scripts.
- - feat: Implement clickable category buttons in the dashboard to launch the explorer, refactoring parameter passing to use session state.
- - feat: Introduce new UI components for validation, including avatar and chip selectors, and refactor the notification system to V2.
- - feat: Implement a comprehensive notification system including UI, management logic, and dedicated pages.

**🐛 Corrigé**
- - fix: Lancement rapide si déjà installé - évite la réinstallation
- - fix: Sépare test_is_enabled en deux tests distincts
- - fix: Améliore test_is_enabled avec meilleur message d'erreur
- - fix: Déplace la fixture reset_encryption_singleton dans conftest.py global
- - fix: Corrige test_is_enabled qui échouait en CI à cause de ENCRYPTION_KEY définie
- - feat: dashboard personnalisable, recherche globale, onboarding + corrections sécurité

*Fichiers modifiés* : docs/FIX_WIDGETTYPE_V2.md, tests/ui/test_kpi_cards.py, modules/db/transactions.py, CHANGELOG.md, modules/constants.py, modules/ui/dashboard/kpi_cards.py, docs/GUIDE_UTILISATEUR.md, test_results_1769981704.txt, tests/test_analytics.py, docs/EMAIL_TROUBLESHOOTING.md, modules/ui/explorer/explorer_launcher.py, tests/unit/test_transaction_types.py, scripts/budget_redesign_prototype.py, modules/ui/feedback.py, modules/ui/components/chip_selector.py, modules/db/settings.py, modules/ui/dashboard/customizable_dashboard.py, modules/ui/__init__.py, modules/ui/dashboard/sections.py, modules/ui/dashboard/budget_tracker.py, modules/ui/enhanced_feedback.py, docs/STABILIZATION_PLAN.md, scripts/repair_hashes.py, modules/ui/notifications/types.py, scripts/audit_codebase.py, pages/6_Recherche.py, docs/INDISPENSABILITY_UPGRADES.md, modules/analytics_v2.py, modules/ui/components/smart_actions.py, scripts/cleanup_backups.py, modules/categorization.py, tests/conftest.py, tests/test_notifications.py, tests/ui/test_progress_tracker.py, docs/AUDIT_COHERENCE_360.md, tests/db/test_stats.py, AGENTS.md, modules/ui/dashboard/category_charts.py, tests/db/test_rules.py, modules/db/maintenance.py, modules/ui/recurrence_tabs.py, docs/audit_report_20260201.md, tests/ai/test_conversational_assistant.py, tests/ui/test_member_selector.py, pages/98_Tests.py, modules/ui/notifications/README.md, modules/ui/assistant/state.py, modules/ui/config/log_viewer.py, modules/ui/components/avatar_selector.py, modules/onboarding.py, pages/3_Synthese.py, modules/ui/dashboard/top_expenses.py, pages/2_Validation.py, test_results_1769764966.txt, tests/ui/test_ui_redesign.py, modules/ai_manager.py, assets/style.css, tests/test_validators.py, modules/ui/notifications/components.py, pages/1_Import.py, tests/README.md, modules/transaction_types.py, modules/ui/validation/main.py, pages/4_Recurrence.py, test_email.py, docs/DASHBOARD_CLEANUP_GUIDE.md, modules/ui/global_search.py, modules/ui/notifications/center.py, docs/AUDIT_REVENUS_DEPENSES.md, docs/AUDIT_CORRECTIONS_IMMEDIATES.md, modules/ui/config/member_management.py, modules/gamification.py, modules/notifications.py, tests/test_cache_multitier.py, modules/ui/validation/row_view.py, modules/analytics.py, modules/ui/rules/rule_manager.py, modules/ui/explorer/explorer_results.py, tests/test_utils.py, tests/test_essential.py, scripts/cleanup_duplicates.py, docs/FIX_WIDGET_ERROR.md, modules/ui/notifications/__init__.py, pages/5_Assistant.py, tests/test_encryption.py, tests/ui/validation/test_sorting.py, app.py, modules/ui/dashboard/evolution_chart.py, modules/ui/components/transaction_diagnostic.py, pages/4_Intelligence.py, pages/6_Explorer.py, modules/ui/explorer/explorer_main.py, modules/ui/importing/main.py, modules/ui/config/audit_tools.py, scripts/fix_dashboard_layouts.py, tests/test_update_manager.py, pages/4_Regles.py, modules/ui/assistant/dashboard_tab.py, docs/TRANSACTION_TYPES_GUIDE.md, modules/performance_monitor.py, modules/ui/components/quick_actions.py, modules/ui/config/category_management.py, modules/update_manager.py, docs/CHANGEMENTS_REVENUS_DEPENSES.md, modules/ui/notifications/manager.py, tests/ui/test_tag_manager.py, modules/db/connection.py, modules/ui/dashboard/filters.py, modules/db/audit.py, pages/9_Configuration.py, tests/test_integration.py, modules/ui/config/config_dashboard.py, modules/db/migrations.py, modules/db/dashboard_cleanup.py, tests/ui/test_filters.py, modules/db/rules.py, modules/ui/components/transaction_drill_down.py, modules/db/members.py, modules/db/stats.py, modules/feature_flags.py, modules/ingestion.py, modules/ui/components/daily_widget.py, tests/ui/test_category_charts.py, modules/ui/components/tag_manager.py, modules/ui/config/backup_restore.py, test_components.py

---

## [5.0.1] - 2026-02-07

### Nouvelles fonctionnalités - 8 ajouts

**✨ Ajouté**
- - ci: Ajoute debug et timeout au workflow de test
- - fix: Ajoute fixture pour réinitialiser le singleton encryption entre tests
- - feat: Implement comprehensive Git change analysis in UpdateManager to detect committed and uncommitted changes, categorize commits, and suggest version bumps, accompanied by new tests.
- - feat: Refactor page structure by consolidating rules, recurrences, budgets, and AI audit into a new Intelligence page, and modularize import, validation, and search functionalities.
- - feat: implement offline mode for categorization, redesign the evolution chart, and reorganize project structure with new tests and scripts.
- - feat: Implement clickable category buttons in the dashboard to launch the explorer, refactoring parameter passing to use session state.
- - feat: Introduce new UI components for validation, including avatar and chip selectors, and refactor the notification system to V2.
- - feat: Implement a comprehensive notification system including UI, management logic, and dedicated pages.

**🐛 Corrigé**
- - fix: Lancement rapide si déjà installé - évite la réinstallation
- - fix: Sépare test_is_enabled en deux tests distincts
- - fix: Améliore test_is_enabled avec meilleur message d'erreur
- - fix: Déplace la fixture reset_encryption_singleton dans conftest.py global
- - fix: Corrige test_is_enabled qui échouait en CI à cause de ENCRYPTION_KEY définie
- - feat: dashboard personnalisable, recherche globale, onboarding + corrections sécurité

*Fichiers modifiés* : docs/FIX_WIDGETTYPE_V2.md, tests/ui/test_kpi_cards.py, modules/db/transactions.py, CHANGELOG.md, modules/constants.py, modules/ui/dashboard/kpi_cards.py, docs/GUIDE_UTILISATEUR.md, test_results_1769981704.txt, tests/test_analytics.py, docs/EMAIL_TROUBLESHOOTING.md, modules/ui/explorer/explorer_launcher.py, tests/unit/test_transaction_types.py, scripts/budget_redesign_prototype.py, modules/ui/feedback.py, modules/ui/components/chip_selector.py, modules/db/settings.py, modules/ui/dashboard/customizable_dashboard.py, modules/ui/__init__.py, modules/ui/dashboard/sections.py, modules/ui/dashboard/budget_tracker.py, modules/ui/enhanced_feedback.py, docs/STABILIZATION_PLAN.md, scripts/repair_hashes.py, modules/ui/notifications/types.py, scripts/audit_codebase.py, pages/6_Recherche.py, docs/INDISPENSABILITY_UPGRADES.md, modules/analytics_v2.py, modules/ui/components/smart_actions.py, scripts/cleanup_backups.py, modules/categorization.py, tests/conftest.py, tests/test_notifications.py, tests/ui/test_progress_tracker.py, docs/AUDIT_COHERENCE_360.md, tests/db/test_stats.py, AGENTS.md, modules/ui/dashboard/category_charts.py, tests/db/test_rules.py, modules/db/maintenance.py, modules/ui/recurrence_tabs.py, docs/audit_report_20260201.md, tests/ai/test_conversational_assistant.py, tests/ui/test_member_selector.py, pages/98_Tests.py, modules/ui/notifications/README.md, modules/ui/assistant/state.py, modules/ui/config/log_viewer.py, modules/ui/components/avatar_selector.py, modules/onboarding.py, pages/3_Synthese.py, modules/ui/dashboard/top_expenses.py, pages/2_Validation.py, test_results_1769764966.txt, tests/ui/test_ui_redesign.py, modules/ai_manager.py, assets/style.css, tests/test_validators.py, modules/ui/notifications/components.py, pages/1_Import.py, tests/README.md, modules/transaction_types.py, modules/ui/validation/main.py, pages/4_Recurrence.py, test_email.py, docs/DASHBOARD_CLEANUP_GUIDE.md, modules/ui/global_search.py, modules/ui/notifications/center.py, docs/AUDIT_REVENUS_DEPENSES.md, docs/AUDIT_CORRECTIONS_IMMEDIATES.md, modules/ui/config/member_management.py, modules/gamification.py, modules/notifications.py, tests/test_cache_multitier.py, modules/ui/validation/row_view.py, modules/analytics.py, modules/ui/rules/rule_manager.py, modules/ui/explorer/explorer_results.py, tests/test_utils.py, tests/test_essential.py, scripts/cleanup_duplicates.py, docs/FIX_WIDGET_ERROR.md, modules/ui/notifications/__init__.py, pages/5_Assistant.py, tests/test_encryption.py, tests/ui/validation/test_sorting.py, app.py, modules/ui/dashboard/evolution_chart.py, modules/ui/components/transaction_diagnostic.py, pages/4_Intelligence.py, pages/6_Explorer.py, modules/ui/explorer/explorer_main.py, modules/ui/importing/main.py, modules/ui/config/audit_tools.py, scripts/fix_dashboard_layouts.py, tests/test_update_manager.py, pages/4_Regles.py, modules/ui/assistant/dashboard_tab.py, docs/TRANSACTION_TYPES_GUIDE.md, modules/performance_monitor.py, modules/ui/components/quick_actions.py, modules/ui/config/category_management.py, modules/update_manager.py, docs/CHANGEMENTS_REVENUS_DEPENSES.md, modules/ui/notifications/manager.py, tests/ui/test_tag_manager.py, modules/db/connection.py, modules/ui/dashboard/filters.py, modules/db/audit.py, pages/9_Configuration.py, tests/test_integration.py, modules/ui/config/config_dashboard.py, modules/db/migrations.py, modules/db/dashboard_cleanup.py, tests/ui/test_filters.py, modules/db/rules.py, modules/ui/components/transaction_drill_down.py, modules/db/members.py, modules/db/stats.py, modules/feature_flags.py, modules/ingestion.py, modules/ui/components/daily_widget.py, tests/ui/test_category_charts.py, modules/ui/components/tag_manager.py, modules/ui/config/backup_restore.py, test_components.py

---

## [5.0.0] - 2026-02-06

### Nouvelles fonctionnalités - 19 ajouts

**✨ Ajouté**
- - feat: implement offline mode for categorization, redesign the evolution chart, and reorganize project structure with new tests and scripts.
- - feat: Implement clickable category buttons in the dashboard to launch the explorer, refactoring parameter passing to use session state.
- - feat: Introduce new UI components for validation, including avatar and chip selectors, and refactor the notification system to V2.
- - feat: Implement a comprehensive notification system including UI, management logic, and dedicated pages.
- - fix: correction vue d'ensemble vide - ajout fallback et messages
- - feat: Update project to version 4.1.0, incorporating new features, bug fixes, and performance enhancements.
- - feat: introduce recurrence feedback and management, and add new Explorer and Assistant UI modules
- - feat: Implement comprehensive UI/UX redesign, introduce gamification and enhanced feedback, and update core database modules for improved tag, category, rule, and transaction management.
- - ✨ feat: Amélioration feedback actions rapides (quick_actions)
- - ✨ feat: Amélioration UI/UX et feedback - Configuration
- - ✨ feat: ML Local, Mobile Responsive & PWA Mode Hors-ligne
- - ✨ Système de mise à jour complet - v3.6.0
- - ✨ feat: Add scroll-to-top button on all pages
- - ✨ feat: Add comprehensive visual feedback system and quick actions popups
- - feat: Implement enhanced audit functionality with bulk actions, filtering, and a new analytics module.
- - perf: Add database pagination, composite indexes, and selective cache invalidation
- - feat: Add comprehensive input validation and security utilities
- - Add versionning and a new logic to present commits
- - feat: Implement `st.toast` for user feedback, refactor tag suggestion UI, and enhance rules auditor with stale rule detection and health scoring.

**🐛 Corrigé**
- - feat: dashboard personnalisable, recherche globale, onboarding + corrections sécurité
- - fix: déplacement de switch_to_tab avant son utilisation
- - fix: correction clés dupliquées dans explorer_filters
- - fix: correction import update_budget → set_budget
- - fix: amélioration scroll-to-top et graphique évolution mensuelle
- - fix: correction imports modules/ui et analyse auto changements
- - 🐛 fix: Correction imports render_scroll_to_top
- - 🐛 fix: Correction erreur SQL merge_categories - colonne id budgets
- - 🐛 fix: Système de logs - fichier et viewer
- - 🔧 fix: Audit corrections - version sync, cleanup, docs
- - 🔧 fix: Improve email notification error handling and user feedback
- - fix: Correct cache invalidation import errors
- - chore: Critical code cleanup - remove dead code and fix bugs
- - security: Fix critical security issues and improve error handling

**⚡ Performance**
- - 🔒 Implémentation complète : Chiffrement, Cache, Validateurs - v3.5.0
- - 🔒 Sécurité & Optimisation: Refactorisation majeure v3.2.0
- - perf: Critical business logic optimizations (90-95% faster)
- - refactor: Phase 2 - Code cleanup and optimization

*Fichiers modifiés* : .agents/skills/financeperso-specific/SKILL.md, .agents/skills/financeperso-specific/references/architecture.md, AGENTS.md, CHANGELOG.md, CONTRIBUTING.md, README.md, app.py, assets/offline.html, assets/pwa.js, assets/service-worker.js, assets/style.css, docs/ARCHITECTURE_EXPLORER.md, docs/ASSISTANT_UX_WIREFRAME.md, docs/AUDIT_COHERENCE_360.md, docs/AUDIT_CORRECTIONS_IMMEDIATES.md, docs/AUDIT_FIXES_SUMMARY.md, docs/AUDIT_REVENUS_DEPENSES.md, docs/CHANGEMENTS_REVENUS_DEPENSES.md, docs/COMPLETE_AUDIT_REPORT.md, docs/DASHBOARD_CLEANUP_GUIDE.md, docs/EMAIL_TROUBLESHOOTING.md, docs/EXPLORER_INTEGRATION.md, docs/FINAL_AUDIT_SUMMARY.md, docs/FINAL_CORRECTIONS_REPORT.md, docs/FIX_WIDGETTYPE_V2.md, docs/FIX_WIDGET_ERROR.md, docs/GUIDE_UTILISATEUR.md, docs/INDISPENSABILITY_UPGRADES.md, docs/N1_FIX_PLAN.md, docs/NEW_FEATURES.md, docs/ROADMAP.md, docs/STABILIZATION_PLAN.md, docs/TRANSACTION_TYPES_GUIDE.md, docs/ULTIMATE_FINAL_REPORT.md, docs/UX_IMPROVEMENTS.md, docs/WIDGETS_STATE_FIXES.md, docs/audit_budgets_ux_archi.md, docs/audit_report.md, docs/gemini.md, modules/ai/audit_engine.py, modules/ai/category_insights.py, modules/ai/rules_auditor.py, modules/ai_manager.py, modules/analytics.py, modules/analytics_constants.py, modules/analytics_v2.py, modules/budgets_dynamic.py, modules/cache_manager.py, modules/cache_multitier.py, modules/categorization.py, modules/constants.py, modules/data_manager_OLD_BACKUP.py, modules/db/audit.py, modules/db/categories.py, modules/db/connection.py, modules/db/dashboard_cleanup.py, modules/db/dashboard_layouts.py, modules/db/members.py, modules/db/migrations.py, modules/db/recurrence_feedback.py, modules/db/rules.py, modules/db/settings.py, modules/db/stats.py, modules/db/tags.py, modules/db/transactions.py, modules/db/transactions_batch.py, modules/encryption.py, modules/error_tracking.py, modules/exceptions.py, modules/feature_flags.py, modules/gamification.py, modules/impact_analyzer.py, modules/import_analyzer.py, modules/ingestion.py, modules/local_ml.py, modules/logger.py, modules/notifications.py, modules/notifications_realtime.py, modules/onboarding.py, modules/performance_monitor.py, modules/transaction_types.py, modules/ui/__init__.py, modules/ui/assistant/__init__.py, modules/ui/assistant/analytics_tab.py, modules/ui/assistant/audit_tab.py, modules/ui/assistant/components.py, modules/ui/assistant/config_tab.py, modules/ui/assistant/dashboard_tab.py, modules/ui/assistant/state.py, modules/ui/changelog_parser.py, modules/ui/components/__init__.py, modules/ui/components/avatar_selector.py, modules/ui/components/chip_selector.py, modules/ui/components/daily_widget.py, modules/ui/components/local_ml_manager.py, modules/ui/components/onboarding_modal.py, modules/ui/components/quick_actions.py, modules/ui/components/smart_actions.py, modules/ui/components/tag_manager.py, modules/ui/components/tag_selector_compact.py, modules/ui/components/tag_selector_smart.py, modules/ui/components/transaction_diagnostic.py, modules/ui/components/transaction_drill_down.py, modules/ui/config/api_settings.py, modules/ui/config/audit_tools.py, modules/ui/config/backup_restore.py, modules/ui/config/category_management.py, modules/ui/config/config_dashboard.py, modules/ui/config/config_mode.py, modules/ui/config/data_operations.py, modules/ui/config/log_viewer.py, modules/ui/config/member_management.py, modules/ui/config/notifications.py, modules/ui/config/tags_rules.py, modules/ui/dashboard/ai_insights.py, modules/ui/dashboard/budget_tracker.py, modules/ui/dashboard/category_charts.py, modules/ui/dashboard/customizable_dashboard.py, modules/ui/dashboard/evolution_chart.py, modules/ui/dashboard/filters.py, modules/ui/dashboard/kpi_cards.py, modules/ui/dashboard/sections.py, modules/ui/dashboard/smart_recommendations.py, modules/ui/dashboard/top_expenses.py, modules/ui/enhanced_feedback.py, modules/ui/explorer/__init__.py, modules/ui/explorer/explorer_filters.py, modules/ui/explorer/explorer_launcher.py, modules/ui/explorer/explorer_main.py, modules/ui/explorer/explorer_results.py, modules/ui/feedback.py, modules/ui/global_search.py, modules/ui/notifications/README.md, modules/ui/notifications/__init__.py, modules/ui/notifications/center.py, modules/ui/notifications/components.py, modules/ui/notifications/manager.py, modules/ui/notifications/types.py, modules/ui/recurrence_manager.py, modules/ui/recurrence_tabs.py, modules/ui/rules/__init__.py, modules/ui/rules/budget_manager.py, modules/ui/rules/rule_audit.py, modules/ui/rules/rule_manager.py, modules/ui/rules/rule_validator.py, modules/ui/styles/global.css, modules/ui/validation/row_view.py, modules/update_manager.py, modules/utils.py, modules/validators.py, pages/12_Recherche.py, pages/1_Import.py, pages/2_Validation.py, pages/3_Synthese.py, pages/4_Recurrence.py, pages/4_Regles.py, pages/5_Assistant.py, pages/6_Explorer.py, pages/98_Tests.py, pages/99_Debug.py, pages/99_Notifications.py, pages/9_Configuration.py, requirements-ml.txt, requirements.txt, scripts/audit_codebase.py, scripts/budget_redesign_prototype.py, scripts/cleanup_backups.py, scripts/cleanup_duplicates.py, scripts/fix_dashboard_layouts.py, scripts/migrate_to_logging.py, scripts/profile_db.py, scripts/repair_hashes.py, scripts/versioning.py, tests/conftest.py, tests/conftest_enhanced.py, tests/db/test_categories.py, tests/db/test_rules.py, tests/db/test_stats.py, tests/test_cache_multitier.py, tests/test_components.py, tests/test_customizable_dashboard.py, tests/test_data_integrity.py, tests/test_email.py, tests/test_encryption.py, tests/test_global_search.py, tests/test_integration.py, tests/test_notifications.py, tests/test_onboarding.py, tests/test_update_manager.py, tests/test_validators.py, tests/ui/test_kpi_cards.py, tests/ui/test_ui_redesign.py, tests/unit/test_cleanup_backups.py, tests/unit/test_transaction_types.py

---

## [4.2.2] - 2026-02-06

### Nouvelles fonctionnalités - 9 ajouts

**✨ Ajouté**
- - feat: implement offline mode for categorization, redesign the evolution chart, and reorganize project structure with new tests and scripts.
- - feat: Implement clickable category buttons in the dashboard to launch the explorer, refactoring parameter passing to use session state.
- - feat: Introduce new UI components for validation, including avatar and chip selectors, and refactor the notification system to V2.
- - feat: Implement a comprehensive notification system including UI, management logic, and dedicated pages.
- - fix: correction vue d'ensemble vide - ajout fallback et messages
- - feat: Update project to version 4.1.0, incorporating new features, bug fixes, and performance enhancements.
- - feat: introduce recurrence feedback and management, and add new Explorer and Assistant UI modules
- - feat: Implement comprehensive UI/UX redesign, introduce gamification and enhanced feedback, and update core database modules for improved tag, category, rule, and transaction management.
- - ✨ feat: Amélioration feedback actions rapides (quick_actions)

**🐛 Corrigé**
- - feat: dashboard personnalisable, recherche globale, onboarding + corrections sécurité
- - fix: déplacement de switch_to_tab avant son utilisation
- - fix: correction clés dupliquées dans explorer_filters
- - fix: correction import update_budget → set_budget
- - fix: amélioration scroll-to-top et graphique évolution mensuelle
- - fix: correction imports modules/ui et analyse auto changements

*Fichiers modifiés* : .agents/skills/financeperso-specific/SKILL.md, .agents/skills/financeperso-specific/references/architecture.md, AGENTS.md, CHANGELOG.md, CONTRIBUTING.md, README.md, app.py, assets/style.css, docs/ARCHITECTURE_EXPLORER.md, docs/ASSISTANT_UX_WIREFRAME.md, docs/AUDIT_COHERENCE_360.md, docs/AUDIT_CORRECTIONS_IMMEDIATES.md, docs/AUDIT_FIXES_SUMMARY.md, docs/AUDIT_REVENUS_DEPENSES.md, docs/CHANGEMENTS_REVENUS_DEPENSES.md, docs/COMPLETE_AUDIT_REPORT.md, docs/DASHBOARD_CLEANUP_GUIDE.md, docs/EMAIL_TROUBLESHOOTING.md, docs/EXPLORER_INTEGRATION.md, docs/FINAL_AUDIT_SUMMARY.md

---

## [4.2.1] - 2026-02-04

### Nouvelles fonctionnalités - 7 ajouts

**✨ Ajouté**
- - feat: Implement a comprehensive notification system including UI, management logic, and dedicated pages.
- - fix: correction vue d'ensemble vide - ajout fallback et messages
- - feat: Update project to version 4.1.0, incorporating new features, bug fixes, and performance enhancements.
- - feat: introduce recurrence feedback and management, and add new Explorer and Assistant UI modules
- - feat: Implement comprehensive UI/UX redesign, introduce gamification and enhanced feedback, and update core database modules for improved tag, category, rule, and transaction management.
- - ✨ feat: Amélioration feedback actions rapides (quick_actions)
- - ✨ feat: Amélioration UI/UX et feedback - Configuration

**🐛 Corrigé**
- - feat: dashboard personnalisable, recherche globale, onboarding + corrections sécurité
- - fix: déplacement de switch_to_tab avant son utilisation
- - fix: correction clés dupliquées dans explorer_filters
- - fix: correction import update_budget → set_budget
- - fix: amélioration scroll-to-top et graphique évolution mensuelle
- - fix: correction imports modules/ui et analyse auto changements
- - 🐛 fix: Correction imports render_scroll_to_top
- - 🐛 fix: Correction erreur SQL merge_categories - colonne id budgets

*Fichiers modifiés* : .agents/skills/financeperso-specific/SKILL.md, .agents/skills/financeperso-specific/references/architecture.md, AGENTS.md, CHANGELOG.md, CONTRIBUTING.md, EMAIL_TROUBLESHOOTING.md, INDISPENSABILITY_UPGRADES.md, README.md, STABILIZATION_PLAN.md, app.py, docs/ARCHITECTURE_EXPLORER.md, docs/ASSISTANT_UX_WIREFRAME.md, docs/AUDIT_COHERENCE_360.md, docs/AUDIT_CORRECTIONS_IMMEDIATES.md, docs/AUDIT_FIXES_SUMMARY.md, docs/AUDIT_REVENUS_DEPENSES.md, docs/CHANGEMENTS_REVENUS_DEPENSES.md, docs/COMPLETE_AUDIT_REPORT.md, docs/DASHBOARD_CLEANUP_GUIDE.md, docs/EXPLORER_INTEGRATION.md

---

## [4.2.0] - 2026-02-03

### Nouvelles fonctionnalités - 7 ajouts

**✨ Ajouté**
- - feat: Implement a comprehensive notification system including UI, management logic, and dedicated pages.
- - fix: correction vue d'ensemble vide - ajout fallback et messages
- - feat: Update project to version 4.1.0, incorporating new features, bug fixes, and performance enhancements.
- - feat: introduce recurrence feedback and management, and add new Explorer and Assistant UI modules
- - feat: Implement comprehensive UI/UX redesign, introduce gamification and enhanced feedback, and update core database modules for improved tag, category, rule, and transaction management.
- - ✨ feat: Amélioration feedback actions rapides (quick_actions)
- - ✨ feat: Amélioration UI/UX et feedback - Configuration

**🐛 Corrigé**
- - feat: dashboard personnalisable, recherche globale, onboarding + corrections sécurité
- - fix: déplacement de switch_to_tab avant son utilisation
- - fix: correction clés dupliquées dans explorer_filters
- - fix: correction import update_budget → set_budget
- - fix: amélioration scroll-to-top et graphique évolution mensuelle
- - fix: correction imports modules/ui et analyse auto changements
- - 🐛 fix: Correction imports render_scroll_to_top
- - 🐛 fix: Correction erreur SQL merge_categories - colonne id budgets

*Fichiers modifiés* : .agents/skills/financeperso-specific/SKILL.md, .agents/skills/financeperso-specific/references/architecture.md, AGENTS.md, CHANGELOG.md, CONTRIBUTING.md, EMAIL_TROUBLESHOOTING.md, INDISPENSABILITY_UPGRADES.md, README.md, STABILIZATION_PLAN.md, app.py, docs/ARCHITECTURE_EXPLORER.md, docs/ASSISTANT_UX_WIREFRAME.md, docs/AUDIT_COHERENCE_360.md, docs/AUDIT_CORRECTIONS_IMMEDIATES.md, docs/AUDIT_FIXES_SUMMARY.md, docs/AUDIT_REVENUS_DEPENSES.md, docs/CHANGEMENTS_REVENUS_DEPENSES.md, docs/COMPLETE_AUDIT_REPORT.md, docs/DASHBOARD_CLEANUP_GUIDE.md, docs/EXPLORER_INTEGRATION.md

---

## [4.1.0] - 2026-02-02

### Nouvelles fonctionnalités - 8 ajouts

**✨ Ajouté**
- - feat: introduce recurrence feedback and management, and add new Explorer and Assistant UI modules
- - feat: Implement comprehensive UI/UX redesign, introduce gamification and enhanced feedback, and update core database modules for improved tag, category, rule, and transaction management.
- - ✨ feat: Amélioration feedback actions rapides (quick_actions)
- - ✨ feat: Amélioration UI/UX et feedback - Configuration
- - ✨ feat: ML Local, Mobile Responsive & PWA Mode Hors-ligne
- - ✨ Système de mise à jour complet - v3.6.0
- - ✨ feat: Add scroll-to-top button on all pages
- - ✨ feat: Add comprehensive visual feedback system and quick actions popups

**🐛 Corrigé**
- - fix: amélioration scroll-to-top et graphique évolution mensuelle
- - fix: correction imports modules/ui et analyse auto changements
- - 🐛 fix: Correction imports render_scroll_to_top
- - 🐛 fix: Correction erreur SQL merge_categories - colonne id budgets
- - 🐛 fix: Système de logs - fichier et viewer
- - 🔧 fix: Audit corrections - version sync, cleanup, docs
- - 🔧 fix: Improve email notification error handling and user feedback

**⚡ Performance**
- - 🔒 Implémentation complète : Chiffrement, Cache, Validateurs - v3.5.0

*Fichiers modifiés* : .agents/skills/financeperso-specific/SKILL.md, .agents/skills/financeperso-specific/references/architecture.md, AGENTS.md, CHANGELOG.md, CONTRIBUTING.md, EMAIL_TROUBLESHOOTING.md, INDISPENSABILITY_UPGRADES.md, README.md, app.py, assets/offline.html, assets/pwa.js, assets/service-worker.js, assets/style.css, docs/ARCHITECTURE_EXPLORER.md, docs/ASSISTANT_UX_WIREFRAME.md, docs/AUDIT_FIXES_SUMMARY.md, docs/COMPLETE_AUDIT_REPORT.md, docs/EXPLORER_INTEGRATION.md, docs/FINAL_AUDIT_SUMMARY.md, docs/FINAL_CORRECTIONS_REPORT.md

---

## [4.0.0] - 2026-02-02

### Nouvelles fonctionnalités - 8 ajouts

**✨ Ajouté**
- - feat: Implement comprehensive UI/UX redesign, introduce gamification and enhanced feedback, and update core database modules for improved tag, category, rule, and transaction management.
- - ✨ feat: Amélioration feedback actions rapides (quick_actions)
- - ✨ feat: Amélioration UI/UX et feedback - Configuration
- - ✨ feat: ML Local, Mobile Responsive & PWA Mode Hors-ligne
- - ✨ Système de mise à jour complet - v3.6.0
- - ✨ feat: Add scroll-to-top button on all pages
- - ✨ feat: Add comprehensive visual feedback system and quick actions popups
- - feat: Implement enhanced audit functionality with bulk actions, filtering, and a new analytics module.

**🐛 Corrigé**
- - fix: correction imports modules/ui et analyse auto changements
- - 🐛 fix: Correction imports render_scroll_to_top
- - 🐛 fix: Correction erreur SQL merge_categories - colonne id budgets
- - 🐛 fix: Système de logs - fichier et viewer
- - 🔧 fix: Audit corrections - version sync, cleanup, docs
- - 🔧 fix: Improve email notification error handling and user feedback
- - fix: Correct cache invalidation import errors

**⚡ Performance**
- - 🔒 Implémentation complète : Chiffrement, Cache, Validateurs - v3.5.0
- - 🔒 Sécurité & Optimisation: Refactorisation majeure v3.2.0

*Fichiers modifiés* : .agents/skills/financeperso-specific/SKILL.md, .agents/skills/financeperso-specific/references/architecture.md, AGENTS.md, CHANGELOG.md, CONTRIBUTING.md, EMAIL_TROUBLESHOOTING.md, GUIDE_UTILISATEUR.md, INDISPENSABILITY_UPGRADES.md, README.md, app.py, assets/offline.html, assets/pwa.js, assets/service-worker.js, assets/style.css, docs/AUDIT_FIXES_SUMMARY.md, docs/COMPLETE_AUDIT_REPORT.md, docs/FINAL_AUDIT_SUMMARY.md, docs/FINAL_CORRECTIONS_REPORT.md, docs/N1_FIX_PLAN.md, docs/NEW_FEATURES.md

---

## [3.1.0] - 2026-01-30

### ✨ Analyse des Récurrences V2 - Refonte Complète

**🔧 Corrections de Bugs**
- **Drill-down fonctionnel** : Correction du bug "Aucune transaction trouvée" dans l'historique détaillé
- Stockage des IDs de transactions pour un affichage fiable
- Matching précis entre récurrences détectées et transactions réelles

**💰 Détection des Revenus Améliorée**
- Détection des salaires (patterns : SALAIRE, REMUNERATION, CAPGEMINI...)
- Détection des allocations chômage (patterns : FRANCE TRAVAIL, POLE EMPLOI, ARE)
- Détection des pensions (patterns : CNAV, CARSAT, RETRAITE)
- Tolérance accrue pour les variations de montant sur les revenus

**📂 Nouvelles Vues d'Analyse**
- **Vue "Par opération"** : Liste détaillée avec filtres (Type, Fréquence, Montant)
- **Vue "Par catégorie"** : Regroupement et agrégation par catégorie
- **Vue "Par tag"** : Analyse des récurrences par tags associés

**🎨 Améliorations UX**
- Cartes de résumé mensuel (charges, revenus, balance)
- Indicateurs visuels 🟢 Fixe / 🟡 Variable
- Affichage des variantes de libellés (+N variantes)
- Filtres interactifs dans la sidebar
- Expandables avec transactions éditables

*Fichiers modifiés* : `pages/4_Recurrence.py`, `modules/analytics_v2.py` (nouveau)

---

## [3.0.1] - 2026-01-30

### 🔄 Améliorations Techniques

**Phase 3 - Function extraction and type safety**
- ## Refactorisation Majeure
- Reduce render_transaction_drill_down() from 341 to ~40 lines
- Extract 5 helper functions for better separation of concerns:
- * _fetch_and_filter_transactions() - Data fetching (16 lines)
- * _display_summary_metrics() - Metrics display (15 lines)
- * _render_transaction_row() - Single row rendering (31 lines)
- * _handle_validated_transactions() - Validated section (81 lines)
- * _handle_pending_transactions() - Pending section (67 lines)
- Replace st.cache_data.clear() with selective invalidation
- ## Extraction de Fonction Analytics
- Extract detect_frequency() from detect_recurring_payments()

*Fichiers modifiés* : `- Reduce cyclomatic complexity in analytics.py`, `modules/analytics.py`, `modules/ingestion.py` (+1 autres)

**Phase 2 - Code cleanup and optimization**
- ## Extraction et Réutilisabilité


### ⚡ Performances

**Critical business logic optimizations (90-95% faster)**
- Implemented two major performance optimizations based on comprehensive analysis:
- 1. Rule Caching with Pre-compiled Regex (90-95% gain)


---

## [3.0.0] - 2026-01-30

### ✨ Nouvelles Fonctionnalités

**Improve versioning script to generate detailed changelog entries**
- Parse full commit bodies and extract detailed bullet points
- Add emoji-based sections (🔒 Security, ✨ Features, 🐛 Fixes, etc.)
- Include file modification information
- Generate rich, narrative changelog entries like v2.0-2.2 format
- Add breaking changes section with detailed explanations
- Support multiple commit types (security, perf, refactor, etc.)
- The new script generates comprehensive changelogs automatically from git
- commits with proper formatting, sections, and context, matching the detailed
- style of historical changelog entries.

*Fichiers modifiés* : `scripts/versioning.py`


### ⚡ Performances

**Add database pagination, composite indexes, and selective cache invalidation**
- **Database Query Pagination**

*Fichiers modifiés* : `- Add pagination support to get_all_transactions() with limit/offset parameters`, `*Fichiers modifiés* : `modules/db/transactions.py`, `modules/db/migrations.py`, `modules/cache_manager.py` (nouveau)`, `modules/cache_manager.py` (+2 autres)


### ⚠️ Breaking Changes

**Improve versioning script to generate detailed changelog entries**

- - Add breaking changes section with detailed explanations
- - Parse full commit bodies and extract detailed bullet points
- - Add emoji-based sections (🔒 Security, ✨ Features, 🐛 Fixes, etc.)
- - Include file modification information
- - Generate rich, narrative changelog entries like v2.0-2.2 format
- - Support multiple commit types (security, perf, refactor, etc.)
- The new script generates comprehensive changelogs automatically from git
- commits with proper formatting, sections, and context, matching the detailed
- style of historical changelog entries.

---

## [2.8.0] - 2026-01-30

### 🔒 Sécurité et Validation Renforcées

**Gestion sécurisée des secrets**
- Implémentation de `python-dotenv` pour la gestion du fichier `.env`
- Permissions sécurisées automatiques (0600) sur le fichier de configuration
- Validation des formats de clés API (Gemini, OpenAI, DeepSeek)
- Messages d'erreur clairs et informatifs pour la configuration

**Validation des entrées utilisateur**
- Validation complète des patterns regex pour les règles d'apprentissage
- Détection des patterns dangereux (catastrophic backtracking)
- Validation du mapping CSV avec vérification des données échantillons
- Vérification de la cohérence des colonnes sélectionnées

**Gestion d'erreurs améliorée**
- Remplacement de toutes les clauses `except:` nues (6 occurrences)
- Gestion spécifique des exceptions (subprocess, réseau, parsing dates)
- Nouvelles classes d'exceptions personnalisées (`modules/exceptions.py`)
- Logging amélioré dans l'AI manager et l'auditeur de règles

### ✨ Nouvelles Fonctionnalités

**Configuration des virements internes**
- Table `settings` créée pour stocker la configuration utilisateur
- Module de gestion des paramètres (`modules/db/settings.py`)
- Interface utilisateur complète dans Configuration → Tags & Règles
- Migration des données personnelles hardcodées vers la base de données
- Possibilité d'ajouter/supprimer des mots-clés de détection

**Utilitaires de sécurité**
- `escape_html()` - Protection contre les attaques XSS
- `safe_html_template()` - Interpolation sécurisée dans les templates HTML
- Documentation complète avec exemples d'utilisation

### 🔄 Améliorations Techniques

- Centralisation de la configuration (plus de données personnelles dans le code)
- Amélioration de la modularité avec les nouvelles classes d'exceptions
- Retro-compatibilité assurée avec valeurs par défaut automatiques
- Feedback utilisateur amélioré avec validation temps réel

### ⚠️ Notes de Migration

**BREAKING CHANGE** : La détection des virements internes utilise maintenant la configuration en base de données. Les installations existantes recevront automatiquement les valeurs par défaut lors de la première exécution.

---

## [2.7.0] - 2026-01-30

### Ajouté
- Add comprehensive input validation and security utilities

---

## [2.6.0] - 2026-01-29

### Ajouté
- Implement `st.toast` for user feedback, refactor tag suggestion UI, and enhance rules auditor with stale rule detection and health scoring.

---

## [2.5.0] - 2026-01-29

### Ajouté
- Implement `st.toast` for user feedback, refactor tag suggestion UI, and enhance rules auditor with stale rule detection and health scoring.

---

## [2.4.0] - 2026-01-29

### Ajouté
- Implement `st.toast` for user feedback, refactor tag suggestion UI, and enhance rules auditor with stale rule detection and health scoring.

---

## [2.2.0] - 2026-01-29

### 🕵️ Audit et Qualité des Données
- **Audit Assistant IA** (`pages/4_Regles.py`) : Nouvelle fonctionnalité pour analyser la base de règles.
- Détection automatique des **conflits** (même mot-clé, catégories différentes).
- Identification des **doublons** et des patterns **trop vagues**.
- Affichage de la date de dernière mise à jour de l'analyse.

### 🧠 Apprentissage
- Amélioration de l'apprentissage automatique depuis les corrections manuelles (v2.1 feature refined).

---

## [2.1.0] - 2026-01-29

### 🎨 Amélioration de l'Expérience Utilisateur

#### 💎 Édition en Masse dans le Drill-Down
- Modification des catégories de transactions **validées** directement depuis le drill-down
- Sélecteur de catégorie individuel pour chaque transaction
- Bouton "💾 Sauvegarder" pour appliquer toutes les modifications en une fois
- Fonctionne pour les insights de tendances dans l'onglet Assistant

#### 🔄 Détection des Virements Internes
- Nouvelle fonction `detect_internal_transfers()` dans `modules/analytics.py`
- Patterns détectés : "VIR SEPA AURELIEN", "ALIMENTATION COMPTE JOINT", "VIREMENT", etc.
- Fonction `exclude_internal_transfers()` pour nettoyer les analyses
- Toggle "🔄 Exclure les virements internes" dans l'onglet Tendances

#### 🧠 Apprentissage depuis les Corrections (Nouveau)
- Option "**🧠 Mémoriser ces choix pour le futur**" dans le drill-down
- Génère automatiquement des règles d'apprentissage lors de la correction manuelle
- Priorité haute (5) pour les règles générées afin de remplacer les anciennes habitudes
- Transforme la session de correction en session d'entraînement de l'IA

#### 📅 Contexte Temporel Enrichi
- Affichage précis des périodes comparées dans l'analyse de tendances
- Format : "2026-01-01 → 2026-01-31 (31 jours) vs 2025-12-01 → 2025-12-31 (31 jours)"
- Meilleure compréhension des variations détectées

### 🐛 Corrections
- **Anomaly Detector** : Correction du conflit de nom de variable `clean_label`

---

## [2.0.0] - 2026-01-28

### 🚀 Nouvelles Fonctionnalités Majeures - Assistant IA Enrichi

#### 🎯 Détection d'Anomalies de Montant
- Analyse statistique automatique des transactions
- Identification des montants inhabituels (> 2σ)
- Classification par sévérité (high/medium)
- Nouvel onglet "🎯 Anomalies" dans l'Assistant

#### 💡 Suggestions de Tags Intelligentes
- Analyse contextuelle par IA (libellé, montant, catégorie)
- Suggestions parmi: Remboursement, Professionnel, Cadeau, Urgent, Récurrent, etc.
- Mode batch pour traiter plusieurs transactions

#### 📊 Analyse de Tendances
- Comparaison automatique période actuelle vs précédente
- Détection des variations significatives (> 30%)
- Insights narratifs générés par IA
- Nouvel onglet "📊 Tendances" dans l'Assistant

#### 💬 Assistant Conversationnel
- Chat IA pour interroger vos finances en langage naturel
- Fonctions outils: dépenses par catégorie, statut budgets, top dépenses
- Historique de conversation
- Nouvel onglet "💬 Chat IA" dans l'Assistant

#### 📈 Prédictions Budgétaires
- Projection linéaire des dépenses jusqu'à fin de mois
- Alertes: 🟢 OK (<80%), 🟠 Attention (80-100%), 🔴 Dépassement (>100%)
- Widget "Alertes Budgétaires" dans la page Synthèse
- Calcul de moyenne journalière

### 🏗️ Architecture
- Nouveau module `modules/ai/` avec 5 sous-modules
- Structure modulaire et extensible
- Exports centralisés dans `modules/ai/__init__.py`

### 📝 Configuration Manuelle du Profil Financier
- Formulaire de configuration pour Revenus, Logement, Abonnements
- Intégré dans l'onboarding initial
- Accessible dans l'Assistant (Configuration Assistée)
- Création automatique de règles et budgets

### 🐛 Corrections
- **Fusion de catégories** : Ajout de `COLLATE NOCASE` pour insensibilité à la casse
- **Persistance Audit** : Corrections dans l'Assistant d'Audit maintenant sauvegardées correctement
- Cast explicite des IDs de transaction en `int`
- Nettoyage du cache Streamlit après modifications

---

## [1.5.0] - 2026-01-XX

### Ajouté
- Support multi-fournisseurs IA (Gemini, Ollama, DeepSeek, OpenAI)
- Gestion des membres du foyer avec mapping de cartes
- Tags personnalisés pour transactions
- Détection automatique du profil financier
- Analyse des abonnements récurrents

### Amélioré
- Interface de validation avec regroupement intelligent
- Tableaux de bord avec filtres avancés
- Système de sauvegardes automatiques

---

## [1.0.0] - 2026-01-XX

### Première version stable
- Import CSV multi-formats
- Catégorisation IA avec apprentissage
- Validation en masse
- Tableaux de bord interactifs
- Gestion des budgets
- Base de données SQLite locale

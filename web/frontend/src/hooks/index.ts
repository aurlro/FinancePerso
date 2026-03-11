/**
 * @file index.ts
 * @description Export centralisé de tous les hooks
 * 
 * ARCHITECTURE:
 * - Hooks API (FastAPI): Source de vérité pour les données
 * - Hooks Supabase: Pour fonctionnalités temps réel (notifications, comments)
 * - Hooks Mock: Fallback temporaire pendant la migration
 */

// ============================================
// AUTHENTIFICATION
// ============================================
export { useAuth } from "./useAuth";

// ============================================
// TRANSACTIONS (via API FastAPI)
// ============================================
export {
  useTransactions,
  useTransaction,
  useUpdateTransaction,
  useDeleteTransaction,
  useCategorizeTransactions,
  useBulkUpdateStatus,
} from "./useTransactionsApi";

// Fallback mock (temporaire)
export {
  useCreateTransaction as useCreateTransactionMock,
  useDeleteTransaction as useDeleteTransactionMock,
  useImportTransactions as useImportTransactionsMock,
} from "./useTransactions";

// ============================================
// COMPTES BANCAIRES (via Mock → API à venir)
// ============================================
export {
  useAccounts,
  useCreateAccount,
  useUpdateAccount,
  useDeleteAccount,
  useHouseholdId,
} from "./useAccounts";

// ============================================
// CATÉGORIES (via API FastAPI)
// ============================================
export {
  useCategories,
  useCreateCategory,
  useUpdateCategory,
  useDeleteCategory,
} from "./useCategoriesApi";

// Fallback mock (temporaire)
export {
  useCategories as useCategoriesMock,
  useCategory as useCategoryMock,
} from "./useCategories";

// Gestion catégories via Supabase (fonctionnalités avancées)
export {
  useCreateCategory as useCreateCategorySupabase,
  useUpdateCategory as useUpdateCategorySupabase,
  useDeleteCategory as useDeleteCategorySupabase,
} from "./useCategoryManagement";

// ============================================
// BUDGETS (via API FastAPI)
// ============================================
export {
  useBudgets,
  useCreateOrUpdateBudget,
  useUpdateBudget,
  useDeleteBudget,
} from "./useBudgetsApi";

// Fallback mock (temporaire)
export {
  useBudgets as useBudgetsMock,
  useBudget as useBudgetMock,
  useCreateBudget as useCreateBudgetMock,
  useUpsertBudget as useUpsertBudgetMock,
} from "./useBudgets";

// ============================================
// MEMBRES (via API FastAPI)
// ============================================
export {
  useMembers,
  useCreateMember,
  useUpdateMember,
  useDeleteMember,
} from "./useMembersApi";

// Fallback mock (temporaire) - Household legacy
export {
  useHouseholdMembers,
  useHousehold,
  useAddMember as useAddMemberMock,
  useUpdateMember as useUpdateMemberMock,
  useDeleteMember as useDeleteMemberMock,
  useToggleMemberActive,
  useSendInvitation,
  useInvitations,
  useCancelInvitation,
  useAcceptInvitation,
  useLeaveHousehold,
  useUpdateProfile,
  useRemoveMember,
  useUpdateGhostMember,
  useDeleteGhostMember,
  useUpdateMemberCard,
  useUpdateHousehold,
  useAddGhostMember,
  useUpdateHouseholdId,
} from "./useHousehold";

// ============================================
// RÈGLES DE CATÉGORISATION (via API FastAPI)
// ============================================
export {
  useRules,
  useCreateRule,
  useUpdateRule,
  useDeleteRule,
  useTestRule,
} from "./useRulesApi";

// Fallback mock (temporaire)
export {
  useRules as useRulesMock,
  useRule as useRuleMock,
  useCreateRule as useCreateRuleMock,
  useUpdateRule as useUpdateRuleMock,
  useDeleteRule as useDeleteRuleMock,
  useTestRule as useTestRuleMock,
} from "./useRules";

// Règles d'attribution (via Supabase)
export { useAttributionRules } from "./useAttributionRules";

// ============================================
// DASHBOARD (via API FastAPI)
// ============================================
export {
  useDashboardStats,
  useCategoryBreakdown,
  useMonthlyEvolution,
  useAccountTypeBreakdown,
} from "./useDashboardApi";

// Dashboard legacy (mock)
export {
  useDashboardMetrics as useDashboardMock,
  useMonthlyTrends as useMonthlyTrendsMock,
  useCategoryBreakdown as useCategoryBreakdownMock,
} from "./useDashboard";

// ============================================
// NOTIFICATIONS (PR #6 - via API FastAPI + WebSocket)
// ============================================
export {
  useNotifications,
  useUnreadNotificationsCount,
  useMarkNotificationAsRead,
  useMarkAllNotificationsAsRead,
  useDeleteNotification,
  useNotificationsWebSocket,
} from "./useNotificationsApi";

// Fallback Supabase (legacy)
export { useNotifications as useNotificationsLegacy, createNotification } from "./useNotifications";

// ============================================
// HOUSEHOLDS (PR #7 - via API FastAPI)
// ============================================
export {
  useMyHousehold,
  useCreateHousehold,
  useUpdateHousehold,
  useDeleteHousehold,
  useHouseholdMembers,
  useRemoveHouseholdMember,
  useCreateInvitation,
  useHouseholdInvitations,
  useAcceptInvitation,
  useDeclineInvitation,
  useCancelInvitation,
} from "./useHouseholdsApi";

// ============================================
// EXPORT (PR #8 - via API FastAPI)
// ============================================
export {
  useExportTransactionsCsv,
  useExportTransactionsJson,
  useMonthlyReport,
  useAnnualReport,
  useFullBackup,
  downloadFile,
} from "./useExportApi";

// ============================================
// ANALYTICS AVANCÉS (PR #9 - via API FastAPI)
// ============================================
export {
  useAnomalies,
  useCashflowPredictions,
  useRecurringTransactions,
  useCategoryTrends,
  useSeasonality,
  useSpendingInsights,
  usePeriodComparison,
} from "./useAnalyticsApi";

// ============================================
// FONCTIONNALITÉS SUPABASE (Temps réel - Legacy)
// ============================================
export { useCoupleBalance } from "./useCoupleBalance";
export { useForecast } from "./useForecast";
export { useSavingsGoals } from "./useSavingsGoals";
export { useTransactionComments, useTransactionCommentCounts } from "./useTransactionComments";

// ============================================
// IMPORT
// ============================================
export { useImportTransactions } from "./useImport";

// ============================================
// ONBOARDING
// ============================================
export { useOnboardingStatus } from "./useOnboardingStatus";

// ============================================
// UI
// ============================================
export { useToast } from "./use-toast";
export { useIsMobile } from "./use-mobile";

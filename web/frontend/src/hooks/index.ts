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
// CATÉGORIES (via Mock → API à venir)
// ============================================
export {
  useCategories,
  useCategory,
  useCreateCategory,
  useUpdateCategory,
  useDeleteCategory,
} from "./useCategories";

// Gestion catégories via Supabase (fonctionnalités avancées)
export {
  useCreateCategory as useCreateCategorySupabase,
  useUpdateCategory as useUpdateCategorySupabase,
  useDeleteCategory as useDeleteCategorySupabase,
} from "./useCategoryManagement";

// ============================================
// BUDGETS (via Mock → API à venir)
// ============================================
export {
  useBudgets,
  useBudget,
  useCreateBudget,
  useUpdateBudget,
  useDeleteBudget,
  useUpsertBudget,
} from "./useBudgets";

// ============================================
// FOyer / MEMBRES (via Mock → API à venir)
// ============================================
export {
  useHouseholdMembers,
  useHousehold,
  useAddMember,
  useUpdateMember,
  useDeleteMember,
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
// RÈGLES DE CATÉGORISATION (via Mock → API à venir)
// ============================================
export {
  useRules,
  useRule,
  useCreateRule,
  useUpdateRule,
  useDeleteRule,
  useTestRule,
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
// FONCTIONNALITÉS SUPABASE (Temps réel)
// ============================================
export { useCoupleBalance } from "./useCoupleBalance";
export { useForecast } from "./useForecast";
export { useNotifications, createNotification } from "./useNotifications";
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

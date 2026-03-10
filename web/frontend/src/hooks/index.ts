/**
 * @file index.ts
 * @description Export centralisé de tous les hooks
 */

// Hooks de base
export { useAuth } from "./useAuth";
export { useDashboard, useMonthlyTrends, useCategoryBreakdown } from "./useDashboard";
export {
  useTransactions,
  useTransaction,
  useCreateTransaction,
  useUpdateTransaction,
  useDeleteTransaction,
  useImportTransactions,
} from "./useTransactions";
export {
  useCategories,
  useCategory,
  useCreateCategory,
  useUpdateCategory,
  useDeleteCategory,
} from "./useCategories";
export {
  useBudgets,
  useBudget,
  useCreateBudget,
  useUpdateBudget,
  useDeleteBudget,
} from "./useBudgets";
export {
  useHouseholdMembers,
  useCreateMember,
  useUpdateMember,
  useDeleteMember,
} from "./useHousehold";
export {
  useRules,
  useRule,
  useCreateRule,
  useUpdateRule,
  useDeleteRule,
  useTestRule,
} from "./useRules";

// Hooks UI (inchangés)
export { useToast } from "./use-toast";
export { useMobile } from "./use-mobile";

// TODO: Adapter les hooks suivants
export { useAccounts } from "./useAccounts";
export { useAttributionRules } from "./useAttributionRules";
export { useCategoryManagement } from "./useCategoryManagement";
export { useCoupleBalance } from "./useCoupleBalance";
export { useForecast } from "./useForecast";
export { useNotifications } from "./useNotifications";
export { useOnboardingStatus } from "./useOnboardingStatus";
export { useSavingsGoals } from "./useSavingsGoals";
export { useTransactionComments } from "./useTransactionComments";

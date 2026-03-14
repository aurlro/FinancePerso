import { useCallback } from 'react';
import type { ImportResult, Budget, BudgetStatus, Member, MemberStats, Subscription } from '../types';

// Types de l'API Electron
declare global {
  interface Window {
    electronAPI: {
      db: {
        getAllTransactions: (limit?: number, offset?: number) => Promise<any[]>;
        getTransaction: (id: number) => Promise<any>;
        createTransaction: (data: any) => Promise<any>;
        updateTransaction: (id: number, data: any) => Promise<any>;
        deleteTransaction: (id: number) => Promise<any>;
        getStatsByMonth: (year: number, month: number) => Promise<any[]>;
        getCategoriesStats: (year: number, month: number) => Promise<any[]>;
        getCategories: () => Promise<any[]>;
        getBudgets: () => Promise<Budget[]>;
        createBudget: (data: Partial<Budget>) => Promise<Budget>;
        updateBudget: (id: number, data: Partial<Budget>) => Promise<Budget>;
        deleteBudget: (id: number) => Promise<{ success: boolean }>;
        getBudgetStatus: (year: number, month: number) => Promise<BudgetStatus[]>;
        getPendingTransactions: () => Promise<any[]>;
        validateBatch: (ids: number[], category: string) => Promise<any>;
        ignoreTransactions: (ids: number[]) => Promise<any>;
        // AI-related methods
        categorizeWithAI: (label: string, amount: number) => Promise<any>;
        getAISettings: () => Promise<any>;
        saveAISettings: (settings: any) => Promise<boolean>;
        testAIConnection: () => Promise<{ success: boolean; message: string }>;
        getLearningRules: () => Promise<any[]>;
        createLearningRule: (pattern: string, category: string, confidence?: number) => Promise<any>;
        // Members
        getMembers: () => Promise<Member[]>;
        getMember: (id: number) => Promise<Member>;
        createMember: (data: Partial<Member>) => Promise<Member>;
        updateMember: (id: number, data: Partial<Member>) => Promise<Member>;
        deleteMember: (id: number) => Promise<{ success: boolean }>;
        getTransactionsByMember: (memberId: number, year?: number, month?: number) => Promise<any[]>;
        assignTransactionMember: (transactionId: number, memberId: number, splitAmount?: number | null) => Promise<any>;
        getMemberStats: (year: number, month: number) => Promise<MemberStats[]>;
        getTransactionMember: (transactionId: number) => Promise<Member | null>;
        // Wealth Accounts
        getWealthAccounts: () => Promise<any[]>;
        createWealthAccount: (data: any) => Promise<any>;
        updateWealthAccount: (id: number, data: any) => Promise<any>;
        deleteWealthAccount: (id: number) => Promise<{ success: boolean }>;
        // Savings Goals
        getSavingsGoals: () => Promise<any[]>;
        createSavingsGoal: (data: any) => Promise<any>;
        updateSavingsGoal: (id: number, data: any) => Promise<any>;
        deleteSavingsGoal: (id: number) => Promise<{ success: boolean }>;
      };
      file: {
        importCSV: (filePath: string, options?: any) => Promise<ImportResult>;
        selectCSV: () => Promise<string | null>;
      };
      app: {
        getVersion: () => Promise<string>;
        getPath: (name: string) => Promise<string>;
      };
    };
  }
}

export function useIPC() {
  const api = window.electronAPI;

  // Database operations
  const getAllTransactions = useCallback(async (limit = 100, offset = 0) => {
    return api.db.getAllTransactions(limit, offset);
  }, []);

  const getTransaction = useCallback(async (id: number) => {
    return api.db.getTransaction(id);
  }, []);

  const createTransaction = useCallback(async (data: any) => {
    return api.db.createTransaction(data);
  }, []);

  const updateTransaction = useCallback(async (id: number, data: any) => {
    return api.db.updateTransaction(id, data);
  }, []);

  const deleteTransaction = useCallback(async (id: number) => {
    return api.db.deleteTransaction(id);
  }, []);

  const getStatsByMonth = useCallback(async (year: number, month: number) => {
    return api.db.getStatsByMonth(year, month);
  }, []);

  const getCategoriesStats = useCallback(async (year: number, month: number) => {
    return api.db.getCategoriesStats(year, month);
  }, []);

  const getCategories = useCallback(async () => {
    return api.db.getCategories();
  }, []);

  // Budget operations
  const getBudgets = useCallback(async () => {
    return api.db.getBudgets();
  }, []);

  const createBudget = useCallback(async (data: Partial<Budget>) => {
    return api.db.createBudget(data);
  }, []);

  const updateBudget = useCallback(async (id: number, data: Partial<Budget>) => {
    return api.db.updateBudget(id, data);
  }, []);

  const deleteBudget = useCallback(async (id: number) => {
    return api.db.deleteBudget(id);
  }, []);

  const getBudgetStatus = useCallback(async (year: number, month: number) => {
    return api.db.getBudgetStatus(year, month);
  }, []);

  const getPendingTransactions = useCallback(async () => {
    return api.db.getPendingTransactions();
  }, []);

  const validateBatch = useCallback(async (ids: number[], category: string) => {
    return api.db.validateBatch(ids, category);
  }, []);

  const ignoreTransactions = useCallback(async (ids: number[]) => {
    return api.db.ignoreTransactions(ids);
  }, []);

  // AI operations
  const categorizeWithAI = useCallback(async (label: string, amount: number) => {
    return api.db.categorizeWithAI(label, amount);
  }, []);

  const getAISettings = useCallback(async () => {
    return api.db.getAISettings();
  }, []);

  const saveAISettings = useCallback(async (settings: any) => {
    return api.db.saveAISettings(settings);
  }, []);

  const testAIConnection = useCallback(async () => {
    return api.db.testAIConnection();
  }, []);

  const getLearningRules = useCallback(async () => {
    return api.db.getLearningRules();
  }, []);

  const createLearningRule = useCallback(async (pattern: string, category: string, confidence?: number) => {
    return api.db.createLearningRule(pattern, category, confidence);
  }, []);

  // Member operations
  const getMembers = useCallback(async () => {
    return api.db.getMembers();
  }, []);

  const getMember = useCallback(async (id: number) => {
    return api.db.getMember(id);
  }, []);

  const createMember = useCallback(async (data: Partial<Member>) => {
    return api.db.createMember(data);
  }, []);

  const updateMember = useCallback(async (id: number, data: Partial<Member>) => {
    return api.db.updateMember(id, data);
  }, []);

  const deleteMember = useCallback(async (id: number) => {
    return api.db.deleteMember(id);
  }, []);

  const getTransactionsByMember = useCallback(async (memberId: number, year?: number, month?: number) => {
    return api.db.getTransactionsByMember(memberId, year, month);
  }, []);

  const assignTransactionMember = useCallback(async (transactionId: number, memberId: number, splitAmount?: number | null) => {
    return api.db.assignTransactionMember(transactionId, memberId, splitAmount ?? null);
  }, []);

  const getMemberStats = useCallback(async (year: number, month: number) => {
    return api.db.getMemberStats(year, month);
  }, []);

  const getTransactionMember = useCallback(async (transactionId: number) => {
    return api.db.getTransactionMember(transactionId);
  }, []);

  // Wealth Account operations
  const getWealthAccounts = useCallback(async () => {
    return api.db.getWealthAccounts();
  }, []);

  const createWealthAccount = useCallback(async (data: any) => {
    return api.db.createWealthAccount(data);
  }, []);

  const updateWealthAccount = useCallback(async (id: number, data: any) => {
    return api.db.updateWealthAccount(id, data);
  }, []);

  const deleteWealthAccount = useCallback(async (id: number) => {
    return api.db.deleteWealthAccount(id);
  }, []);

  // Savings Goal operations
  const getSavingsGoals = useCallback(async () => {
    return api.db.getSavingsGoals();
  }, []);

  const createSavingsGoal = useCallback(async (data: any) => {
    return api.db.createSavingsGoal(data);
  }, []);

  const updateSavingsGoal = useCallback(async (id: number, data: any) => {
    return api.db.updateSavingsGoal(id, data);
  }, []);

  const deleteSavingsGoal = useCallback(async (id: number) => {
    return api.db.deleteSavingsGoal(id);
  }, []);

  // Subscription operations
  const getSubscriptions = useCallback(async () => {
    return api.db.getSubscriptions();
  }, []);

  const createSubscription = useCallback(async (data: Partial<Subscription>) => {
    return api.db.createSubscription(data);
  }, []);

  const updateSubscription = useCallback(async (id: number, data: Partial<Subscription>) => {
    return api.db.updateSubscription(id, data);
  }, []);

  const deleteSubscription = useCallback(async (id: number) => {
    return api.db.deleteSubscription(id);
  }, []);

  const detectSubscriptions = useCallback(async () => {
    return api.db.detectSubscriptions();
  }, []);

  const getUpcomingPayments = useCallback(async (days?: number) => {
    return api.db.getUpcomingPayments(days);
  }, []);

  // File operations
  const selectCSV = useCallback(async () => {
    return api.file.selectCSV();
  }, []);

  const importCSV = useCallback(async (filePath: string, options?: any) => {
    return api.file.importCSV(filePath, options);
  }, []);

  // App info
  const getVersion = useCallback(async () => {
    return api.app.getVersion();
  }, []);

  const getPath = useCallback(async (name: string) => {
    return api.app.getPath(name);
  }, []);

  return {
    // Database
    getAllTransactions,
    getTransaction,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    getStatsByMonth,
    getCategoriesStats,
    getCategories,
    // Budgets
    getBudgets,
    createBudget,
    updateBudget,
    deleteBudget,
    getBudgetStatus,
    // Validation
    getPendingTransactions,
    validateBatch,
    ignoreTransactions,
    // AI
    categorizeWithAI,
    getAISettings,
    saveAISettings,
    testAIConnection,
    getLearningRules,
    createLearningRule,
    // Members
    getMembers,
    getMember,
    createMember,
    updateMember,
    deleteMember,
    getTransactionsByMember,
    assignTransactionMember,
    getMemberStats,
    getTransactionMember,
    // Wealth Accounts
    getWealthAccounts,
    createWealthAccount,
    updateWealthAccount,
    deleteWealthAccount,
    // Savings Goals
    getSavingsGoals,
    createSavingsGoal,
    updateSavingsGoal,
    deleteSavingsGoal,
    // Subscriptions
    getSubscriptions,
    createSubscription,
    updateSubscription,
    deleteSubscription,
    detectSubscriptions,
    getUpcomingPayments,
    // File
    selectCSV,
    importCSV,
    // App
    getVersion,
    getPath,
  };
}

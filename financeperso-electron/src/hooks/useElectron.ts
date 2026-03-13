import { useCallback } from 'react';
import type { Transaction, Category, DashboardStats, ImportResult } from '@/types';

export function useElectron() {
  const api = window.electronAPI;

  // Database operations
  const queryDB = useCallback(async (sql: string, params?: unknown[]) => {
    return api.db.query(sql, params);
  }, []);

  const getTransactions = useCallback(async (options?: { limit?: number; offset?: number }) => {
    return api.db.getTransactions(options) as Promise<Transaction[]>;
  }, []);

  const getTransactionsByMonth = useCallback(async (year: number, month: number) => {
    return api.db.getTransactionsByMonth(year, month) as Promise<Transaction[]>;
  }, []);

  const getDashboardStats = useCallback(async (year: number, month: number) => {
    return api.db.getDashboardStats(year, month) as Promise<DashboardStats>;
  }, []);

  const insertTransaction = useCallback(async (data: Omit<Transaction, 'id'>) => {
    return api.db.insertTransaction(data) as Promise<Transaction>;
  }, []);

  const updateTransaction = useCallback(async (id: number, data: Partial<Transaction>) => {
    return api.db.updateTransaction(id, data) as Promise<Transaction>;
  }, []);

  const deleteTransaction = useCallback(async (id: number) => {
    return api.db.deleteTransaction(id);
  }, []);

  const getCategories = useCallback(async () => {
    return api.db.getCategories() as Promise<Category[]>;
  }, []);

  // File operations
  const selectCSV = useCallback(async () => {
    return api.file.selectCSV();
  }, []);

  const importCSV = useCallback(async (filePath: string, options?: unknown) => {
    return api.file.importCSV(filePath, options) as Promise<ImportResult>;
  }, []);

  // App info
  const getVersion = useCallback(async () => {
    return api.app.getVersion();
  }, []);

  const getPath = useCallback(async (name: string) => {
    return api.app.getPath(name);
  }, []);

  // Theme
  const setTheme = useCallback(async (theme: 'light' | 'dark' | 'system') => {
    return api.theme.set(theme);
  }, []);

  const getTheme = useCallback(async () => {
    return api.theme.get();
  }, []);

  const onThemeChanged = useCallback((callback: (theme: 'light' | 'dark') => void) => {
    return api.theme.onChanged(callback);
  }, []);

  return {
    // Database
    queryDB,
    getTransactions,
    getTransactionsByMonth,
    getDashboardStats,
    insertTransaction,
    updateTransaction,
    deleteTransaction,
    getCategories,
    
    // File
    selectCSV,
    importCSV,
    
    // App
    getVersion,
    getPath,
    
    // Theme
    setTheme,
    getTheme,
    onThemeChanged,
  };
}

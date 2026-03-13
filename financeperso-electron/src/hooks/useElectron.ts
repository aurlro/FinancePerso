import { useCallback } from 'react';
import type { Transaction, Category, ImportResult } from '@/types';

// Types pour l'API Electron
declare global {
  interface Window {
    electronAPI: {
      db: {
        getAllTransactions: (limit?: number, offset?: number) => Promise<Transaction[]>;
        getTransaction: (id: number) => Promise<Transaction>;
        createTransaction: (data: any) => Promise<Transaction>;
        updateTransaction: (id: number, data: any) => Promise<Transaction>;
        deleteTransaction: (id: number) => Promise<void>;
        getStatsByMonth: (year: number, month: number) => Promise<any[]>;
        getCategoriesStats: (year: number, month: number) => Promise<any[]>;
        getCategories: () => Promise<Category[]>;
      };
      file: {
        importCSV: (filePath: string, options?: any) => Promise<ImportResult>;
        selectCSV: () => Promise<string | null>;
      };
      app: {
        getVersion: () => Promise<string>;
        getPath: (name: string) => Promise<string>;
      };
      platform: string;
    };
  }
}

export interface DashboardStats {
  income: number;
  expense: number;
  balance: number;
}

export function useElectron() {
  const api = window.electronAPI;

  // Database operations
  const getAllTransactions = useCallback(async (limit?: number, offset?: number) => {
    return api.db.getAllTransactions(limit, offset);
  }, []);

  const getTransaction = useCallback(async (id: number) => {
    return api.db.getTransaction(id);
  }, []);

  const createTransaction = useCallback(async (data: Omit<Transaction, 'id'>) => {
    return api.db.createTransaction(data);
  }, []);

  const updateTransaction = useCallback(async (id: number, data: Partial<Transaction>) => {
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

  // Helper pour obtenir les stats du dashboard
  const getDashboardStats = useCallback(async (year: number, month: number): Promise<DashboardStats> => {
    const stats = await api.db.getStatsByMonth(year, month);
    
    let income = 0;
    let expense = 0;
    
    for (const stat of stats) {
      if (stat.type === 'income') {
        income = stat.total || 0;
      } else if (stat.type === 'expense') {
        expense = stat.total || 0;
      }
    }
    
    return {
      income,
      expense,
      balance: income - expense,
    };
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
    getDashboardStats,
    
    // File
    selectCSV,
    importCSV,
    
    // App
    getVersion,
    getPath,
  };
}

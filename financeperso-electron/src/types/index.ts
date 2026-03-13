// Types pour FinancePerso Electron

export interface Transaction {
  id: number;
  date: string;
  label: string;
  amount: number;
  category?: string;
  subcategory?: string;
  type: 'debit' | 'credit';
  account?: string;
  notes?: string;
  beneficiary?: string;
  member_id?: number;
  is_recurring?: boolean;
  is_validated?: boolean;
  sync_status?: string;
  emoji?: string;
  color?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Category {
  id: number;
  name: string;
  emoji: string;
  color: string;
  type: 'fixed' | 'variable' | 'income' | 'savings';
  budget_amount?: number;
  is_active: boolean;
}

export interface Member {
  id: number;
  name: string;
  type: 'primary' | 'secondary';
  email?: string;
  color?: string;
  is_active: boolean;
}

export interface DashboardStats {
  stats: {
    total_income: number;
    total_expense: number;
    balance: number;
  };
  byCategory: Array<{
    category: string;
    total: number;
  }>;
}

export interface ImportResult {
  success: boolean;
  total?: number;
  imported?: number;
  duplicates?: number;
  errors?: number;
  errorDetails?: Array<{ row: number | string; error: string }>;
  fileName?: string;
  mappings?: Record<string, string>;
  error?: string;
}

// API Types
declare global {
  interface Window {
    electronAPI: {
      db: {
        query: (sql: string, params?: unknown[]) => Promise<unknown[]>;
        transaction: (operations: Array<{ sql: string; params?: unknown[] }>) => Promise<unknown[]>;
        getTransactions: (options?: { limit?: number; offset?: number }) => Promise<Transaction[]>;
        getTransactionsByMonth: (year: number, month: number) => Promise<Transaction[]>;
        getDashboardStats: (year: number, month: number) => Promise<DashboardStats>;
        insertTransaction: (data: Omit<Transaction, 'id'>) => Promise<Transaction>;
        updateTransaction: (id: number, data: Partial<Transaction>) => Promise<Transaction>;
        deleteTransaction: (id: number) => Promise<void>;
        getCategories: () => Promise<Category[]>;
      };
      file: {
        selectCSV: () => Promise<string | null>;
        importCSV: (filePath: string, options?: unknown) => Promise<ImportResult>;
      };
      app: {
        getVersion: () => Promise<string>;
        getPath: (name: string) => Promise<string>;
      };
      theme: {
        set: (theme: 'light' | 'dark' | 'system') => Promise<void>;
        get: () => Promise<'light' | 'dark'>;
        onChanged: (callback: (theme: 'light' | 'dark') => void) => void;
      };
      // Legacy
      getVersion: () => Promise<string>;
      getPath: (name: string) => Promise<string>;
      ping: () => string;
      platform: string;
    };
  }
}

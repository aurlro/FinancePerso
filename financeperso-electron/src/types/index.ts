// Types communs pour FinancePerso Electron

export interface Transaction {
  id: number;
  date: string;
  description: string;
  amount: number;
  category?: string;
  type: 'income' | 'expense';
  account?: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Category {
  id: number;
  name: string;
  emoji: string;
  color: string;
  is_fixed?: boolean;
  budget_limit?: number;
}

export interface Account {
  id: number;
  name: string;
  type: 'checking' | 'savings' | 'credit';
  balance: number;
  currency: string;
}

export interface DashboardStats {
  income: number;
  expense: number;
  balance: number;
}

export interface CategoryStat {
  category: string;
  total: number;
  count: number;
}

export interface ImportResult {
  success: boolean;
  total: number;
  imported: number;
  errors: number;
  fileName: string;
  error?: string;
}

export interface CSVColumnMapping {
  date: string;
  description: string;
  amount: string;
  category?: string;
  type?: string;
}

export interface ImportOptions {
  delimiter?: string;
  encoding?: string;
  mappings?: CSVColumnMapping;
  skipHeader?: boolean;
}

export interface Budget {
  id: number;
  category: string;
  amount: number;
  period: 'monthly' | 'yearly' | 'weekly';
  year?: number;
  month?: number;
}

export interface BudgetStatus extends Budget {
  spent_amount: number;
  remaining: number;
  percentage: number;
  status: 'ok' | 'warning' | 'exceeded';
  transaction_count: number;
}

export interface Member {
  id: number;
  name: string;
  type: 'primary' | 'secondary';
  color: string;
  emoji: string;
  email?: string;
  is_active: number;
  created_at?: string;
}

export interface TransactionMember {
  transaction_id: number;
  member_id: number;
  split_amount?: number;
}

export interface MemberStats {
  id: number;
  name: string;
  color: string;
  emoji: string;
  type: 'primary' | 'secondary';
  total: number;
  transaction_count: number;
}

/**
 * Shared TypeScript Schemas
 * Mirror of Python Pydantic models for type safety across the stack
 */

// ============================================================================
// ENUMS
// ============================================================================

export type TransactionType = 'income' | 'expense' | 'transfer';
export type TransactionStatus = 'pending' | 'validated' | 'imported';
export type AccountType = 'checking' | 'savings' | 'credit' | 'cash' | 'investment';
export type CategoryType = 'fixed' | 'variable' | 'income' | 'savings';

// ============================================================================
// BASE INTERFACES
// ============================================================================

export interface Timestamped {
  id: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// CATEGORY
// ============================================================================

export interface Category extends Timestamped {
  name: string;
  emoji: string;
  color: string;
  type: CategoryType;
  is_fixed: boolean;
  budget_limit: number | null;
  description: string | null;
  parent_id: string | null;
}

export interface CategoryCreate {
  name: string;
  emoji?: string;
  color?: string;
  type?: CategoryType;
  is_fixed?: boolean;
  budget_limit?: number;
  description?: string;
  parent_id?: string;
}

export interface CategoryUpdate extends Partial<CategoryCreate> {}

// ============================================================================
// ACCOUNT
// ============================================================================

export interface Account extends Timestamped {
  name: string;
  type: AccountType;
  balance: number;
  currency: string;
  bank_name: string | null;
  account_number: string | null;
  is_active: boolean;
  description: string | null;
}

export interface AccountCreate {
  name: string;
  type: AccountType;
  balance?: number;
  currency?: string;
  bank_name?: string;
  account_number?: string;
  description?: string;
}

export interface AccountUpdate extends Partial<AccountCreate> {}

// ============================================================================
// TRANSACTION
// ============================================================================

export interface Transaction extends Timestamped {
  date: string;
  amount: number;
  description: string;
  type: TransactionType;
  status: TransactionStatus;
  category_id: string | null;
  category: Category | null;
  account_id: string;
  account: Account;
  beneficiary: string | null;
  notes: string | null;
  tags: string[];
  is_recurring: boolean;
  hash: string; // For deduplication
}

export interface TransactionCreate {
  date: string;
  amount: number;
  description: string;
  type?: TransactionType;
  category_id?: string;
  account_id: string;
  beneficiary?: string;
  notes?: string;
  tags?: string[];
  is_recurring?: boolean;
}

export interface TransactionUpdate extends Partial<TransactionCreate> {}

export interface TransactionBulkUpdate {
  ids: string[];
  category_id?: string;
  status?: TransactionStatus;
  tags?: string[];
}

// ============================================================================
// MEMBER (Household)
// ============================================================================

export interface Member extends Timestamped {
  name: string;
  email: string | null;
  color: string;
  share_percentage: number;
  is_primary: boolean;
  monthly_income: number | null;
}

export interface MemberCreate {
  name: string;
  email?: string;
  color?: string;
  share_percentage?: number;
  monthly_income?: number;
}

// ============================================================================
// BUDGET
// ============================================================================

export interface Budget extends Timestamped {
  category_id: string;
  category: Category;
  amount: number;
  period: 'monthly' | 'yearly';
  alert_threshold: number; // Percentage (e.g., 80 for 80%)
}

export interface BudgetWithSpending extends Budget {
  spent: number;
  remaining: number;
  percentage_used: number;
  is_over_budget: boolean;
}

// ============================================================================
// DASHBOARD
// ============================================================================

export interface DashboardStats {
  total_balance: number;
  monthly_income: number;
  monthly_expenses: number;
  monthly_savings: number;
  savings_rate: number; // Percentage
  pending_transactions: number;
}

export interface SpendingByCategory {
  category_id: string;
  category_name: string;
  category_emoji: string;
  category_color: string;
  amount: number;
  percentage: number;
  transaction_count: number;
}

export interface MonthlyTrend {
  month: string;
  income: number;
  expenses: number;
  savings: number;
}

export interface CashflowForecast {
  date: string;
  predicted_balance: number;
  confidence_lower: number;
  confidence_upper: number;
}

// ============================================================================
// IMPORT
// ============================================================================

export interface CSVImportMapping {
  date_column: string;
  amount_column: string;
  description_column: string;
  date_format: string;
  delimiter: string;
  has_header: boolean;
  encoding: string;
}

export interface ImportPreview {
  transactions: TransactionCreate[];
  total_count: number;
  duplicates_count: number;
  errors: ImportError[];
}

export interface ImportError {
  row: number;
  message: string;
}

export interface ImportResult {
  imported: number;
  duplicates: number;
  errors: number;
  transactions: Transaction[];
}

// ============================================================================
// API RESPONSES
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  code?: string;
  field?: string;
}

// ============================================================================
// SETTINGS
// ============================================================================

export interface UserSettings {
  currency: string;
  language: string;
  theme: 'light' | 'dark' | 'system';
  date_format: string;
  ai_provider: 'gemini' | 'openai' | 'local' | 'none';
  ai_api_key: string | null;
  enable_auto_categorization: boolean;
  monthly_budget_alert: number;
}

// ============================================================================
// SEARCH & FILTERS
// ============================================================================

export interface TransactionFilters {
  start_date?: string;
  end_date?: string;
  category_id?: string;
  account_id?: string;
  type?: TransactionType;
  status?: TransactionStatus;
  min_amount?: number;
  max_amount?: number;
  search?: string;
  tags?: string[];
}

export interface SearchResult {
  transactions: Transaction[];
  categories: Category[];
  total_count: number;
}

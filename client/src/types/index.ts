// Re-export shared types for frontend use
// This mirrors server/app/schemas for type consistency

export * from '../../../shared/schemas';

// Additional frontend-specific types

export interface NavItem {
  label: string;
  href: string;
  icon: string;
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}

export interface FilterState {
  startDate?: string;
  endDate?: string;
  categoryId?: string;
  accountId?: string;
  type?: 'income' | 'expense' | 'transfer';
  status?: 'pending' | 'validated' | 'imported';
  search?: string;
}

export interface SortState {
  column: string;
  direction: 'asc' | 'desc';
}

export interface SelectOption {
  value: string;
  label: string;
  icon?: string;
  color?: string;
}

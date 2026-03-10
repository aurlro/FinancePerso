/**
 * Client API pour communiquer avec le backend FastAPI
 * Remplace les appels Supabase par des fetch vers l'API Python
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

// Token d'authentification (à remplacer par vraie auth JWT)
let authToken: string | null = localStorage.getItem("auth_token");

export function setAuthToken(token: string) {
  authToken = token;
  localStorage.setItem("auth_token", token);
}

export function clearAuthToken() {
  authToken = null;
  localStorage.removeItem("auth_token");
}

/**
 * Fonction fetch avec gestion d'erreurs standardisée
 */
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };
  
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
  }
  
  // Gestion des réponses vides (204 No Content)
  if (response.status === 204) {
    return undefined as T;
  }
  
  return response.json();
}

// ============================================================================
// DASHBOARD API
// ============================================================================

export interface DashboardStats {
  reste_a_vivre: number;
  total_expenses: number;
  total_income: number;
  epargne_nette: number;
  period: string;
}

export interface CategoryBreakdown {
  categories: Array<{
    name: string;
    amount: number;
    percentage: number;
    emoji?: string;
    color?: string;
  }>;
}

export interface MonthlyEvolution {
  months: string[];
  expenses: number[];
  income: number[];
  savings: number[];
}

export const dashboardApi = {
  getStats: (month: string) =>
    fetchApi<DashboardStats>(`/dashboard/stats?month=${month}`),
  
  getBreakdown: (month: string) =>
    fetchApi<CategoryBreakdown>(`/dashboard/breakdown?month=${month}`),
  
  getEvolution: (months: number = 12) =>
    fetchApi<MonthlyEvolution>(`/dashboard/evolution?months=${months}`),
};

// ============================================================================
// TRANSACTIONS API
// ============================================================================

export interface Transaction {
  id: number;
  label: string;
  amount: number;
  date: string;
  category?: string;
  status: "pending" | "categorized" | "validated";
  member_id?: number;
  account_id?: number;
  created_at?: string;
}

export interface TransactionsList {
  items: Transaction[];
  total: number;
  limit: number;
  offset: number;
}

export interface CategorizeResult {
  id: number;
  category: string;
  source: string;
  confidence: number;
}

export const transactionsApi = {
  list: (params?: {
    limit?: number;
    offset?: number;
    category?: string;
    month?: string;
    status?: string;
    search?: string;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.set("limit", params.limit.toString());
    if (params?.offset) queryParams.set("offset", params.offset.toString());
    if (params?.category) queryParams.set("category", params.category);
    if (params?.month) queryParams.set("month", params.month);
    if (params?.status) queryParams.set("status", params.status);
    if (params?.search) queryParams.set("search", params.search);
    
    return fetchApi<TransactionsList>(`/transactions?${queryParams.toString()}`);
  },
  
  getById: (id: number) =>
    fetchApi<Transaction>(`/transactions/${id}`),
  
  update: (id: number, data: Partial<Transaction>) =>
    fetchApi<Transaction>(`/transactions/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  
  categorize: (ids: number[]) =>
    fetchApi<{ categorized: CategorizeResult[] }>(`/transactions/categorize`, {
      method: "POST",
      body: JSON.stringify({ transaction_ids: ids }),
    }),
  
  bulkUpdateStatus: (ids: number[], status: string) =>
    fetchApi<void>(`/transactions/bulk-update`, {
      method: "POST",
      body: JSON.stringify({ ids, status }),
    }),
};

// ============================================================================
// CATEGORIES API
// ============================================================================

export interface Category {
  id: number;
  name: string;
  emoji: string;
  color?: string;
  is_fixed: boolean;
  budget?: number;
}

export const categoriesApi = {
  list: () => fetchApi<Category[]>(`/categories`),
  
  create: (data: Omit<Category, "id">) =>
    fetchApi<Category>(`/categories`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  
  update: (id: number, data: Partial<Category>) =>
    fetchApi<Category>(`/categories/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
};

// ============================================================================
// BUDGETS API
// ============================================================================

export interface Budget {
  category: string;
  amount: number;
  spent: number;
  percentage: number;
  alert?: boolean;
}

export const budgetsApi = {
  list: (month?: string) => {
    const query = month ? `?month=${month}` : "";
    return fetchApi<Budget[]>(`/budgets${query}`);
  },
  
  setBudget: (category: string, amount: number) =>
    fetchApi<Budget>(`/budgets`, {
      method: "POST",
      body: JSON.stringify({ category, amount }),
    }),
};

// ============================================================================
// HEALTH CHECK
// ============================================================================

export const healthApi = {
  check: () => fetchApi<{ status: string; version: string }>("/health"),
};

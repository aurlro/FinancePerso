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
// AUTHENTICATION API
// ============================================================================

export interface User {
  id: number;
  email: string;
  name: string;
  household_id: number | null;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  name: string;
}

async function fetchAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };
  
  // Don't add auth token for login/register endpoints
  if (authToken && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/register')) {
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
  
  if (response.status === 204) {
    return undefined as T;
  }
  
  return response.json();
}

export const authApi = {
  register: (credentials: RegisterCredentials) =>
    fetchAuth<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify(credentials),
    }),
  
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    // Use form data for OAuth2 compatibility
    const formData = new URLSearchParams();
    formData.append("username", credentials.email);
    formData.append("password", credentials.password);
    
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || "Invalid credentials");
    }
    
    const data = await response.json() as AuthTokens;
    
    // Store tokens
    setAuthToken(data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    
    return data;
  },
  
  logout: () => {
    clearAuthToken();
    localStorage.removeItem("refresh_token");
  },
  
  me: () =>
    fetchApi<User>("/auth/me"),
  
  refreshToken: async (): Promise<AuthTokens> => {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      throw new Error("No refresh token available");
    }
    
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    
    if (!response.ok) {
      throw new Error("Failed to refresh token");
    }
    
    const data = await response.json() as AuthTokens;
    setAuthToken(data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    
    return data;
  },
  
  changePassword: (currentPassword: string, newPassword: string) =>
    fetchApi<void>("/auth/change-password", {
      method: "POST",
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    }),
};

// ============================================================================
// ACCOUNTS API
// ============================================================================

export interface Account {
  id: number;
  name: string;
  bank_name?: string;
  account_type: "perso_a" | "perso_b" | "joint";
  balance: number;
  household_id?: number;
  created_at: string;
  updated_at?: string;
}

export interface CreateAccountInput {
  name: string;
  bank_name?: string;
  account_type: "perso_a" | "perso_b" | "joint";
  balance?: number;
}

export interface UpdateAccountInput {
  name?: string;
  bank_name?: string;
  account_type?: "perso_a" | "perso_b" | "joint";
  balance?: number;
}

export const accountsApi = {
  list: () =>
    fetchApi<{ items: Account[]; total: number }>("/accounts"),
  
  getById: (id: number) =>
    fetchApi<Account>(`/accounts/${id}`),
  
  create: (data: CreateAccountInput) =>
    fetchApi<Account>("/accounts", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  
  update: (id: number, data: UpdateAccountInput) =>
    fetchApi<Account>(`/accounts/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  
  delete: (id: number) =>
    fetchApi<void>(`/accounts/${id}`, {
      method: "DELETE",
    }),
};

// ============================================================================
// HEALTH CHECK
// ============================================================================

export const healthApi = {
  check: () => fetchApi<{ status: string; version: string }>("/health"),
};

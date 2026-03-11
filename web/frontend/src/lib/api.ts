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
  
  delete: (id: number) =>
    fetchApi<{ deleted: boolean; id: number }>(`/transactions/${id}`, {
      method: "DELETE",
    }),
};

// ============================================================================
// CATEGORIES API
// ============================================================================

export interface Category {
  id: number;
  name: string;
  emoji: string;
  is_fixed: number;
  suggested_tags?: string;
  created_at: string;
}

export interface CategoriesList {
  items: Category[];
  total: number;
}

export const categoriesApi = {
  list: () => fetchApi<CategoriesList>(`/categories`).then(r => r.items),
  
  create: (data: { name: string; emoji?: string; is_fixed?: number; suggested_tags?: string }) =>
    fetchApi<Category>(`/categories`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  
  update: (id: number, data: Partial<Category>) =>
    fetchApi<Category>(`/categories/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  
  delete: (id: number) =>
    fetchApi<{ deleted: boolean; id: number }>(`/categories/${id}`, {
      method: "DELETE",
    }),
};

// ============================================================================
// BUDGETS API
// ============================================================================

export interface Budget {
  category: string;
  amount: number;
  updated_at: string;
  spent?: number;
  remaining?: number;
}

export interface BudgetsList {
  items: Budget[];
  total: number;
}

export const budgetsApi = {
  list: (month?: string) =>
    fetchApi<BudgetsList>(`/budgets${month ? `?month=${month}` : ""}`).then(r => r.items),
  
  createOrUpdate: (data: { category: string; amount: number }) =>
    fetchApi<Budget>(`/budgets`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  
  update: (category: string, data: { amount: number }) =>
    fetchApi<Budget>(`/budgets/${encodeURIComponent(category)}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  
  delete: (category: string) =>
    fetchApi<{ deleted: boolean; category: string }>(`/budgets/${encodeURIComponent(category)}`, {
      method: "DELETE",
    }),
};

// ============================================================================
// MEMBERS API
// ============================================================================

export interface Member {
  id: number;
  name: string;
  member_type: string;
  created_at: string;
}

export interface MembersList {
  items: Member[];
  total: number;
}

export const membersApi = {
  list: () => fetchApi<MembersList>(`/members`).then(r => r.items),
  
  create: (data: { name: string; member_type?: string }) =>
    fetchApi<Member>(`/members`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  
  update: (id: number, data: Partial<Member>) =>
    fetchApi<Member>(`/members/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  
  delete: (id: number) =>
    fetchApi<{ deleted: boolean; id: number }>(`/members/${id}`, {
      method: "DELETE",
    }),
};

// ============================================================================
// RULES API
// ============================================================================

export interface Rule {
  id: number;
  pattern: string;
  category: string;
  priority: number;
  created_at: string;
  match_count?: number;
}

export interface RulesList {
  items: Rule[];
  total: number;
}

export interface RuleTestResult {
  pattern: string;
  matches: string[];
  match_count: number;
  total_tested: number;
}

export const rulesApi = {
  list: () => fetchApi<RulesList>(`/rules`).then(r => r.items),
  
  create: (data: { pattern: string; category: string; priority?: number }) =>
    fetchApi<Rule>(`/rules`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  
  update: (id: number, data: Partial<Rule>) =>
    fetchApi<Rule>(`/rules/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  
  delete: (id: number) =>
    fetchApi<{ deleted: boolean; id: number }>(`/rules/${id}`, {
      method: "DELETE",
    }),
  
  test: (data: { pattern: string; testLabels?: string[] }) =>
    fetchApi<RuleTestResult>(`/rules/test`, {
      method: "POST",
      body: JSON.stringify(data),
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
// IMPORT API
// ============================================================================

export interface CsvMapping {
  date_column: string;
  label_column: string;
  amount_column?: string;
  debit_column?: string;
  credit_column?: string;
  use_debit_credit: boolean;
}

export interface ImportResultItem {
  row_index: number;
  status: "imported" | "duplicate" | "error";
  transaction_id?: number;
  error_message?: string;
  label: string;
  amount: number;
}

export interface ImportResponse {
  total_rows: number;
  imported: number;
  duplicates: number;
  errors: number;
  transactions: ImportResultItem[];
  transfer_detected_count: number;
  attributed_count: number;
}

export const importApi = {
  importCsv: (
    accountId: number,
    csvContent: string,
    mapping: CsvMapping,
    skipDuplicates: boolean = true
  ) =>
    fetchApi<ImportResponse>("/transactions/import", {
      method: "POST",
      body: JSON.stringify({
        account_id: accountId,
        csv_content: csvContent,
        mapping,
        skip_duplicates: skipDuplicates,
      }),
    }),
};

// ============================================================================
// NOTIFICATIONS API (PR #6)
// ============================================================================

export interface Notification {
  id: number;
  user_id: number;
  type: "info" | "warning" | "success" | "error";
  category: "transaction" | "budget" | "invitation" | "system";
  title: string;
  message: string;
  data?: Record<string, any>;
  is_read: boolean;
  read_at?: string;
  created_at: string;
}

export interface NotificationsList {
  items: Notification[];
  total: number;
  unread_count: number;
}

export const notificationsApi = {
  list: (params?: { unreadOnly?: boolean; limit?: number; offset?: number }) => {
    const query = new URLSearchParams();
    if (params?.unreadOnly) query.set("unread_only", "true");
    if (params?.limit) query.set("limit", params.limit.toString());
    if (params?.offset) query.set("offset", params.offset.toString());
    return fetchApi<NotificationsList>(`/notifications?${query.toString()}`);
  },
  
  getUnreadCount: () =>
    fetchApi<{ unread_count: number }>("/notifications/unread-count"),
  
  markAsRead: (id: number) =>
    fetchApi<{ success: boolean; id: number }>(`/notifications/${id}/read`, {
      method: "POST",
    }),
  
  markAllAsRead: () =>
    fetchApi<{ success: boolean; marked_read: number }>("/notifications/mark-all-read", {
      method: "POST",
    }),
  
  delete: (id: number) =>
    fetchApi<{ deleted: boolean; id: number }>(`/notifications/${id}`, {
      method: "DELETE",
    }),
};

// ============================================================================
// HOUSEHOLDS API (PR #7)
// ============================================================================

export interface Household {
  id: number;
  name: string;
  description?: string;
  owner_id: number;
  created_at: string;
  updated_at: string;
  member_count: number;
}

export interface HouseholdMember {
  id: number;
  user_id: number;
  name: string;
  email: string;
  role: "owner" | "admin" | "member";
  is_active: boolean;
  joined_at: string;
}

export interface Invitation {
  id: number;
  household_id: number;
  email: string;
  status: "pending" | "accepted" | "declined" | "expired";
  role: string;
  expires_at: string;
  created_at: string;
}

export const householdsApi = {
  getMyHousehold: () =>
    fetchApi<Household | null>("/households/my"),
  
  create: (data: { name: string; description?: string }) =>
    fetchApi<Household>("/households", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  
  update: (id: number, data: { name?: string; description?: string }) =>
    fetchApi<Household>(`/households/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  
  delete: (id: number) =>
    fetchApi<{ deleted: boolean; id: number }>(`/households/${id}`, {
      method: "DELETE",
    }),
  
  // Members
  listMembers: (householdId: number) =>
    fetchApi<HouseholdMember[]>(`/households/${householdId}/members`),
  
  removeMember: (householdId: number, userId: number) =>
    fetchApi<{ removed: boolean; user_id: number }>(
      `/households/${householdId}/members/${userId}`,
      { method: "DELETE" }
    ),
  
  // Invitations
  createInvitation: (householdId: number, data: { email: string; role?: string }) =>
    fetchApi<Invitation>(`/households/${householdId}/invitations`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  
  listInvitations: (householdId: number) =>
    fetchApi<Invitation[]>(`/households/${householdId}/invitations`),
  
  acceptInvitation: (token: string) =>
    fetchApi<{ success: boolean; household_id: number }>("/households/invitations/accept", {
      method: "POST",
      body: JSON.stringify({ token }),
    }),
  
  declineInvitation: (token: string) =>
    fetchApi<{ success: boolean }>("/households/invitations/decline", {
      method: "POST",
      body: JSON.stringify({ token }),
    }),
  
  cancelInvitation: (householdId: number, invitationId: number) =>
    fetchApi<{ cancelled: boolean; id: number }>(
      `/households/${householdId}/invitations/${invitationId}`,
      { method: "DELETE" }
    ),
};

// ============================================================================
// EXPORT API (PR #8)
// ============================================================================

export interface MonthlyReport {
  month: string;
  generated_at: string;
  summary: {
    total_income: number;
    total_expenses: number;
    balance: number;
    transaction_count: number;
  };
  by_category: Record<string, { income: number; expenses: number; count: number }>;
  transactions: any[];
}

export interface AnnualReport {
  year: number;
  generated_at: string;
  summary: {
    total_income: number;
    total_expenses: number;
    balance: number;
    transaction_count: number;
    average_monthly_income: number;
    average_monthly_expenses: number;
  };
  monthly_breakdown: Record<string, { income: number; expenses: number; count: number }>;
  top_categories: Record<string, { income: number; expenses: number; count: number }>;
}

export const exportApi = {
  exportCsv: (params: {
    startDate?: string;
    endDate?: string;
    category?: string;
    status?: string;
  }) => {
    const query = new URLSearchParams();
    if (params.startDate) query.set("start_date", params.startDate);
    if (params.endDate) query.set("end_date", params.endDate);
    if (params.category) query.set("category", params.category);
    if (params.status) query.set("status", params.status);
    
    return fetch(`/api/export/transactions/csv?${query.toString()}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
      },
    }).then((res) => {
      if (!res.ok) throw new Error("Export failed");
      return res.blob();
    });
  },
  
  exportJson: (params: {
    startDate?: string;
    endDate?: string;
    category?: string;
    status?: string;
  }) => {
    const query = new URLSearchParams();
    if (params.startDate) query.set("start_date", params.startDate);
    if (params.endDate) query.set("end_date", params.endDate);
    if (params.category) query.set("category", params.category);
    if (params.status) query.set("status", params.status);
    
    return fetchApi<{ exported_at: string; count: number; transactions: any[] }>(
      `/export/transactions/json?${query.toString()}`
    );
  },
  
  getMonthlyReport: (month: string) =>
    fetchApi<MonthlyReport>(`/export/report/monthly?month=${month}`),
  
  getAnnualReport: (year: number) =>
    fetchApi<AnnualReport>(`/export/report/annual?year=${year}`),
  
  getFullBackup: () =>
    fetchApi<{ exported_at: string; version: string; user: any; accounts: any[]; transactions: any[]; categories: any[]; budgets: any[]; rules: any[] }>(
      "/export/backup/full"
    ),
};

// ============================================================================
// ANALYTICS API (PR #9)
// ============================================================================

export interface Anomaly {
  type: string;
  label: string;
  details: string;
  expected_mean: number;
  expected_std: number;
  transactions: Array<{
    id: number;
    date: string;
    label: string;
    amount: number;
    category: string;
  }>;
  transaction_count: number;
}

export interface CashflowPrediction {
  start_date: string;
  end_date: string;
  starting_balance: number;
  predicted_income: number;
  predicted_expenses: number;
  predicted_balance: number;
  confidence: number;
  warnings: string[];
}

export interface RecurringTransaction {
  label: string;
  category: string;
  amount: number;
  frequency: string;
  confidence: number;
  occurrence_count: number;
  first_seen: string;
  last_seen: string;
}

export interface CategoryTrend {
  category: string;
  trend: "increasing" | "decreasing" | "stable";
  slope: number;
  avg_monthly: number;
  current_month: number;
  previous_month: number;
  change_percent: number;
}

export interface SpendingInsight {
  type: "info" | "warning" | "success";
  title: string;
  message: string;
  priority: "high" | "medium" | "low";
}

export interface PeriodComparison {
  period: string;
  current: {
    start_date: string;
    income: number;
    expenses: number;
    balance: number;
    transaction_count: number;
  };
  previous: {
    start_date: string;
    end_date: string;
    income: number;
    expenses: number;
    balance: number;
    transaction_count: number;
  };
  changes_percent: {
    income: number;
    expenses: number;
    balance: number;
  };
}

export const analyticsApi = {
  getAnomalies: (threshold: number = 2.0) =>
    fetchApi<{ anomalies: Anomaly[]; total_checked: number; threshold_sigma: number }>(
      `/analytics/anomalies?threshold=${threshold}`
    ),
  
  getCashflowPredictions: (monthsAhead: number = 3) =>
    fetchApi<{ predictions: CashflowPrediction[]; months_ahead: number }>(
      `/analytics/predictions/cashflow?months_ahead=${monthsAhead}`
    ),
  
  getRecurringTransactions: () =>
    fetchApi<{ recurring: RecurringTransaction[]; total_count: number }>(
      "/analytics/recurring"
    ),
  
  getCategoryTrends: (months: number = 6, category?: string) => {
    const query = new URLSearchParams();
    query.set("months", months.toString());
    if (category) query.set("category", category);
    return fetchApi<{ trends: CategoryTrend[]; months_analyzed: number; categories_count: number }>(
      `/analytics/trends/categories?${query.toString()}`
    );
  },
  
  getSeasonality: (category?: string) => {
    const query = category ? `?category=${encodeURIComponent(category)}` : "";
    return fetchApi<{
      seasonality: Record<string, number>;
      peak_months: string[];
      low_months: string[];
      has_pattern: boolean;
      category?: string;
    }>(`/analytics/seasonality${query}`);
  },
  
  getSpendingInsights: () =>
    fetchApi<{
      insights: SpendingInsight[];
      score: number;
      metrics: {
        total_income: number;
        total_expenses: number;
        savings_rate: number;
        transaction_count: number;
      };
      top_expense_categories: Record<string, number>;
    }>("/analytics/insights"),
  
  getPeriodComparison: (period: "month" | "quarter" | "year") =>
    fetchApi<PeriodComparison>(`/analytics/comparison?period=${period}`),
};

// ============================================================================
// HEALTH CHECK
// ============================================================================

export const healthApi = {
  check: () => fetchApi<{ status: string; version: string }>("/health"),
};

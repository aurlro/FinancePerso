/**
 * @file client.ts
 * @description Stub Supabase compatible pour le mode Mock/FastAPI
 * 
 * Ce stub remplace le client Supabase et retourne des données mock
 * tout en supportant l'API de chaînage de Supabase.
 * 
 * TODO: Remplacer par des appels API réels vers FastAPI
 */

import { toast } from "sonner";

// ============================================
// MOCK DATABASE EN MÉMOIRE
// ============================================

interface MockTransaction {
  id: string;
  date: string;
  label: string;
  amount: number;
  bank_account_id: string;
  category_id?: string;
  member_id?: string;
  is_internal_transfer?: boolean;
  matched_transfer_id?: string;
  import_hash?: string;
  is_subscription?: boolean;
  is_recurring?: boolean;
  created_at: string;
  updated_at: string;
}

interface MockAccount {
  id: string;
  name: string;
  bank_name?: string;
  account_type: "perso_a" | "perso_b" | "joint";
  balance: number;
  household_id: string;
  created_at: string;
}

interface MockCategory {
  id: string;
  name: string;
  emoji: string;
  color: string;
  type: "income" | "expense" | "both";
  is_fixed?: boolean;
  budget_amount?: number;
  created_at: string;
  updated_at: string;
}

interface MockRule {
  id: string;
  name: string;
  pattern: string;
  pattern_type: string;
  category_id: string;
  member_id?: string;
  priority: number;
  is_active: boolean;
  match_count: number;
  created_at: string;
  updated_at: string;
}

interface MockSavingsGoal {
  id: string;
  name: string;
  target_amount: number;
  current_amount: number;
  deadline?: string;
  household_id: string;
  created_at: string;
  updated_at: string;
}

interface MockComment {
  id: string;
  transaction_id: string;
  user_id: string;
  content: string;
  created_at: string;
}

interface MockNotification {
  id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  user_id: string;
  created_at: string;
}

// Données mock initiales
const MOCK_DB = {
  transactions: [] as MockTransaction[],
  bank_accounts: [] as MockAccount[],
  categories: [
    { id: "cat-001", name: "Alimentation", emoji: "🍽️", color: "#22c55e", type: "expense", is_fixed: false, budget_amount: 500, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
    { id: "cat-002", name: "Transport", emoji: "🚗", color: "#3b82f6", type: "expense", is_fixed: false, budget_amount: 200, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
    { id: "cat-003", name: "Logement", emoji: "🏠", color: "#f59e0b", type: "expense", is_fixed: true, budget_amount: 800, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
    { id: "cat-004", name: "Loisirs", emoji: "🎮", color: "#ef4444", type: "expense", is_fixed: false, budget_amount: 150, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
    { id: "cat-005", name: "Santé", emoji: "💊", color: "#ec4899", type: "expense", is_fixed: false, budget_amount: 100, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
    { id: "cat-006", name: "Salaire", emoji: "💰", color: "#10b981", type: "income", is_fixed: true, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
    { id: "cat-007", name: "Transferts", emoji: "🔄", color: "#6b7280", type: "both", is_fixed: false, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  ] as MockCategory[],
  categorization_rules: [
    { id: "rule-001", name: "Supermarchés", pattern: "CARREFOUR|CASINO|LIDL|AUCHAN", pattern_type: "regex", category_id: "cat-001", priority: 10, is_active: true, match_count: 45, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
    { id: "rule-002", name: "Transport", pattern: "TOTAL|ESSO|SHELL", pattern_type: "regex", category_id: "cat-002", priority: 10, is_active: true, match_count: 23, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
  ] as MockRule[],
  attribution_rules: [] as MockRule[],
  savings_goals: [] as MockSavingsGoal[],
  transaction_comments: [] as MockComment[],
  notifications: [] as MockNotification[],
  households: [{ id: "household-1", name: "Mon Foyer", created_at: new Date().toISOString() }],
  profiles: [{ id: "user-1", email: "demo@fincouple.app", household_id: "household-1", created_at: new Date().toISOString() }],
};

// ============================================
// BUILDER DE REQUÊTES MOCK
// ============================================

class MockQueryBuilder<T extends Record<string, any>> {
  private table: string;
  private data: T[];
  private filters: Array<(item: T) => boolean> = [];
  private selectFields: string[] = ["*"];
  private singleMode = false;
  private limitCount: number | null = null;
  private orderConfig: { column: string; ascending: boolean } | null = null;

  constructor(table: string, data: T[]) {
    this.table = table;
    this.data = [...data];
  }

  select(fields?: string): this {
    if (fields) {
      this.selectFields = fields.split(",").map(f => f.trim());
    }
    return this;
  }

  insert(values: T | T[]): this {
    const items = Array.isArray(values) ? values : [values];
    for (const item of items) {
      const newItem = {
        ...item,
        id: item.id || `${this.table.slice(0, -1)}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        created_at: new Date().toISOString(),
      } as T;
      this.data.push(newItem);
      (MOCK_DB as any)[this.table] = this.data;
    }
    return this;
  }

  update(values: Partial<T>): this {
    const itemsToUpdate = this.applyFilters();
    for (const item of itemsToUpdate) {
      Object.assign(item, values, { updated_at: new Date().toISOString() });
    }
    (MOCK_DB as any)[this.table] = this.data;
    return this;
  }

  delete(): this {
    const itemsToDelete = this.applyFilters();
    this.data = this.data.filter(item => !itemsToDelete.includes(item));
    (MOCK_DB as any)[this.table] = this.data;
    return this;
  }

  // Filters
  eq(column: keyof T, value: any): this {
    this.filters.push((item) => item[column] === value);
    return this;
  }

  neq(column: keyof T, value: any): this {
    this.filters.push((item) => item[column] !== value);
    return this;
  }

  gt(column: keyof T, value: any): this {
    this.filters.push((item) => item[column] > value);
    return this;
  }

  gte(column: keyof T, value: any): this {
    this.filters.push((item) => item[column] >= value);
    return this;
  }

  lt(column: keyof T, value: any): this {
    this.filters.push((item) => item[column] < value);
    return this;
  }

  lte(column: keyof T, value: any): this {
    this.filters.push((item) => item[column] <= value);
    return this;
  }

  in(column: keyof T, values: any[]): this {
    this.filters.push((item) => values.includes(item[column]));
    return this;
  }

  is(column: keyof T, value: null | boolean): this {
    this.filters.push((item) => item[column] === value);
    return this;
  }

  like(column: keyof T, pattern: string): this {
    const regex = new RegExp(pattern.replace(/%/g, ".*"), "i");
    this.filters.push((item) => regex.test(String(item[column])));
    return this;
  }

  ilike(column: keyof T, pattern: string): this {
    return this.like(column, pattern);
  }

  contains(column: keyof T, value: any): this {
    this.filters.push((item) => {
      const colValue = item[column];
      if (Array.isArray(colValue)) {
        return colValue.includes(value);
      }
      if (typeof colValue === "string") {
        return colValue.toLowerCase().includes(String(value).toLowerCase());
      }
      return false;
    });
    return this;
  }

  or(conditions: string): this {
    // Simplification: supporte uniquement "column.eq.value,column2.eq.value2"
    const parts = conditions.split(",");
    this.filters.push((item) => {
      return parts.some(part => {
        const [col, op, ...valParts] = part.split(".");
        const val = valParts.join(".");
        if (op === "eq") return item[col] === val;
        if (op === "neq") return item[col] !== val;
        return false;
      });
    });
    return this;
  }

  // Ordering & Pagination
  order(column: keyof T, { ascending = true } = {}): this {
    this.orderConfig = { column: column as string, ascending };
    return this;
  }

  limit(count: number): this {
    this.limitCount = count;
    return this;
  }

  single(): this {
    this.singleMode = true;
    this.limitCount = 1;
    return this;
  }

  maybeSingle(): this {
    this.singleMode = true;
    this.limitCount = 1;
    return this;
  }

  // Execution
  async then<TResult1 = any, TResult2 = never>(
    onfulfilled?: ((value: { data: any; error: null } | { data: null; error: any }) => TResult1 | PromiseLike<TResult1>),
    onrejected?: ((reason: any) => TResult2 | PromiseLike<TResult2>)
  ): Promise<TResult1 | TResult2> {
    try {
      const result = await this.execute();
      return onfulfilled ? onfulfilled(result) : result as any;
    } catch (error) {
      return onrejected ? onrejected(error) : Promise.reject(error);
    }
  }

  private applyFilters(): T[] {
    return this.data.filter(item => this.filters.every(f => f(item)));
  }

  private applyProjection(items: T[]): any[] {
    if (this.selectFields.includes("*")) {
      return items;
    }
    return items.map(item => {
      const projected: any = {};
      for (const field of this.selectFields) {
        if (field in item) {
          projected[field] = item[field];
        }
      }
      return projected;
    });
  }

  private applyOrdering(items: T[]): T[] {
    if (!this.orderConfig) return items;
    return [...items].sort((a, b) => {
      const aVal = a[this.orderConfig!.column];
      const bVal = b[this.orderConfig!.column];
      if (aVal < bVal) return this.orderConfig!.ascending ? -1 : 1;
      if (aVal > bVal) return this.orderConfig!.ascending ? 1 : -1;
      return 0;
    });
  }

  private applyLimit(items: T[]): T[] {
    if (this.limitCount === null) return items;
    return items.slice(0, this.limitCount);
  }

  async execute(): Promise<{ data: any; error: null } | { data: null; error: any }> {
    // Simuler un délai réseau
    await new Promise(resolve => setTimeout(resolve, 100));

    try {
      let result = this.applyFilters();
      result = this.applyOrdering(result);
      result = this.applyLimit(result);
      
      const projected = this.applyProjection(result);
      
      return { 
        data: this.singleMode ? projected[0] || null : projected, 
        error: null 
      };
    } catch (err) {
      return { data: null, error: err };
    }
  }
}

// ============================================
// AUTH MOCK
// ============================================

const MOCK_SESSION = {
  access_token: "mock-token",
  refresh_token: "mock-refresh",
  expires_at: Date.now() + 3600000,
  user: {
    id: "user-1",
    email: "demo@fincouple.app",
    user_metadata: { name: "Démo" },
  },
};

const authListeners: Array<(event: string, session: any) => void> = [];

const mockAuth = {
  getSession: async () => ({
    data: { session: MOCK_SESSION },
    error: null,
  }),
  
  getUser: async () => ({
    data: { user: MOCK_SESSION.user },
    error: null,
  }),
  
  onAuthStateChange: (callback: (event: string, session: any) => void) => {
    authListeners.push(callback);
    // Émettre l'état initial
    setTimeout(() => callback("SIGNED_IN", MOCK_SESSION), 0);
    
    return {
      data: {
        subscription: {
          unsubscribe: () => {
            const idx = authListeners.indexOf(callback);
            if (idx > -1) authListeners.splice(idx, 1);
          },
        },
      },
    };
  },
  
  signInWithPassword: async ({ email, password }: { email: string; password: string }) => {
    console.log("[MOCK AUTH] signInWithPassword", email);
    return { data: { user: MOCK_SESSION.user, session: MOCK_SESSION }, error: null };
  },
  
  signUp: async ({ email, password, options }: any) => {
    console.log("[MOCK AUTH] signUp", email);
    return { data: { user: MOCK_SESSION.user, session: MOCK_SESSION }, error: null };
  },
  
  signOut: async () => {
    console.log("[MOCK AUTH] signOut");
    authListeners.forEach(cb => cb("SIGNED_OUT", null));
    return { error: null };
  },
  
  resetPasswordForEmail: async (email: string) => {
    console.log("[MOCK AUTH] resetPasswordForEmail", email);
    toast.success("Email de réinitialisation envoyé (mock)");
    return { error: null };
  },
  
  updateUser: async (attributes: any) => {
    console.log("[MOCK AUTH] updateUser", attributes);
    return { data: { user: { ...MOCK_SESSION.user, ...attributes } }, error: null };
  },
};

// ============================================
// REALTIME MOCK
// ============================================

class MockChannel {
  private channelName: string;
  private callbacks: Record<string, Function[]> = {};

  constructor(name: string) {
    this.channelName = name;
  }

  on(event: string, config: any, callback?: Function) {
    if (!this.callbacks[event]) {
      this.callbacks[event] = [];
    }
    this.callbacks[event].push(callback || config);
    return this;
  }

  subscribe(callback?: (status: string) => void) {
    console.log(`[MOCK REALTIME] Subscribed to ${this.channelName}`);
    if (callback) callback("SUBSCRIBED");
    return this;
  }

  unsubscribe() {
    console.log(`[MOCK REALTIME] Unsubscribed from ${this.channelName}`);
    return this;
  }
}

// ============================================
// FUNCTIONS MOCK
// ============================================

const mockFunctions = {
  invoke: async (name: string, params?: any) => {
    console.log("[MOCK FUNCTIONS] invoke", name, params);
    return { data: null, error: null };
  },
};

// ============================================
// CLIENT SUPABASE EXPORTÉ
// ============================================

export const supabase = {
  from: <T extends Record<string, any> = any>(table: string) => {
    const data = (MOCK_DB as any)[table] || [];
    return new MockQueryBuilder<T>(table, data);
  },
  
  auth: mockAuth,
  
  functions: mockFunctions,
  
  channel: (name: string) => new MockChannel(name),
  
  removeChannel: (channel: MockChannel) => {
    channel.unsubscribe();
  },
  
  // Pour debugging
  _mockDb: MOCK_DB,
  
  // Méthode pour réinitialiser les données (utile pour les tests)
  _resetMockData: () => {
    MOCK_DB.transactions = [];
    MOCK_DB.bank_accounts = [];
    MOCK_DB.savings_goals = [];
    MOCK_DB.transaction_comments = [];
    MOCK_DB.notifications = [];
    console.log("[MOCK DB] Reset");
  },
};

// Types exportés pour compatibilité
export type User = typeof MOCK_SESSION.user;
export type Session = typeof MOCK_SESSION;
export type SupabaseClient = typeof supabase;

import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { startOfMonth, endOfMonth, format, subMonths } from "date-fns";

export interface DashboardStats {
  totalExpenses: number;
  totalIncome: number;
  resteAVivre: number;
  epargneNette: number;
  excludedTransfers: number;
  excludedContributions: number;
}

export interface CategoryBreakdown {
  id: string | null;
  name: string;
  color: string;
  amount: number;
}

export interface MonthlyEvolution {
  month: string;
  depenses: number;
  revenus: number;
}

export interface AccountTypeBreakdown {
  type: string;
  label: string;
  amount: number;
  categories: { name: string; amount: number }[];
}

function getMonthRange(ref: Date) {
  return {
    start: format(startOfMonth(ref), "yyyy-MM-dd"),
    end: format(endOfMonth(ref), "yyyy-MM-dd"),
  };
}

/** Check if a transaction counts as real income (not transfer, not excluded category) */
function isRealIncome(t: { amount: number; is_internal_transfer: boolean; categories?: any }) {
  if (t.amount <= 0) return false;
  if (t.is_internal_transfer) return false;
  if ((t.categories as any)?.exclude_from_income) return false;
  return true;
}

/** Check if a transaction counts as real expense (not transfer, not internal-movement category) */
function isRealExpense(t: { amount: number; is_internal_transfer: boolean; categories?: any }) {
  if (t.amount >= 0) return false;
  if (t.is_internal_transfer) return false;
  if ((t.categories as any)?.exclude_from_income) return false;
  if ((t.categories as any)?.exclude_from_expenses) return false;
  return true;
}

export function useDashboardStats(month: Date = new Date()) {
  return useQuery({
    queryKey: ["dashboard-stats", format(month, "yyyy-MM")],
    queryFn: async () => {
      const { start, end } = getMonthRange(month);
      const { data, error } = await supabase
        .from("transactions")
        .select("amount, is_internal_transfer, categories(exclude_from_income, exclude_from_expenses)")
        .gte("date", start)
        .lte("date", end)
        .limit(10000);
      if (error) throw error;

      const totalExpenses = (data || []).filter((t) => isRealExpense(t)).reduce((s, t) => s + Math.abs(t.amount), 0);
      const totalIncome = (data || []).filter((t) => isRealIncome(t)).reduce((s, t) => s + t.amount, 0);

      const excludedTransfers = (data || [])
        .filter((t) => t.is_internal_transfer)
        .reduce((s, t) => s + Math.abs(t.amount), 0);
      const excludedContributions = (data || [])
        .filter((t) => !t.is_internal_transfer && (t.categories as any)?.exclude_from_income)
        .reduce((s, t) => s + Math.abs(t.amount), 0);

      return { totalExpenses, totalIncome, resteAVivre: totalIncome - totalExpenses, epargneNette: totalIncome - totalExpenses, excludedTransfers, excludedContributions } as DashboardStats;
    },
  });
}

export function useCategoryBreakdown(month: Date = new Date()) {
  return useQuery({
    queryKey: ["dashboard-category-breakdown", format(month, "yyyy-MM")],
    queryFn: async () => {
      const { start, end } = getMonthRange(month);
      const { data, error } = await supabase
        .from("transactions")
        .select("amount, is_internal_transfer, category_id, categories(name, color, exclude_from_income, exclude_from_expenses)")
        .gte("date", start)
        .lte("date", end)
        .limit(10000);
      if (error) throw error;

      const map = new Map<string, { id: string | null; name: string; color: string; amount: number }>();
      for (const t of data || []) {
        if (!isRealExpense(t)) continue;
        const cat = t.categories as any;
        const name = cat?.name || "Non catégorisé";
        const color = cat?.color || "#94a3b8";
        const id = t.category_id || null;
        const entry = map.get(name) || { id, name, color, amount: 0 };
        entry.amount += Math.abs(t.amount);
        map.set(name, entry);
      }

      return Array.from(map.values()).sort((a, b) => b.amount - a.amount) as CategoryBreakdown[];
    },
  });
}

export function useMonthlyEvolution() {
  return useQuery({
    queryKey: ["dashboard-monthly-evolution"],
    queryFn: async () => {
      const now = new Date();
      const months: MonthlyEvolution[] = [];
      const sixMonthsAgo = format(startOfMonth(subMonths(now, 5)), "yyyy-MM-dd");
      const endDate = format(endOfMonth(now), "yyyy-MM-dd");

      const { data, error } = await supabase
        .from("transactions")
        .select("date, amount, is_internal_transfer, categories(exclude_from_income, exclude_from_expenses)")
        .gte("date", sixMonthsAgo)
        .lte("date", endDate)
        .limit(10000);
      if (error) throw error;

      for (let i = 5; i >= 0; i--) {
        const m = subMonths(now, i);
        const mStart = startOfMonth(m);
        const mEnd = endOfMonth(m);
        const label = format(m, "MMM yy");
        const monthTx = (data || []).filter((t) => {
          const d = new Date(t.date);
          return d >= mStart && d <= mEnd;
        });
        months.push({
          month: label,
          depenses: monthTx.filter((t) => isRealExpense(t)).reduce((s, t) => s + Math.abs(t.amount), 0),
          revenus: monthTx.filter((t) => isRealIncome(t)).reduce((s, t) => s + t.amount, 0),
        });
      }
      return months;
    },
  });
}

export function useAccountTypeBreakdown(month: Date = new Date()) {
  return useQuery({
    queryKey: ["dashboard-account-type-breakdown", format(month, "yyyy-MM")],
    queryFn: async () => {
      const { start, end } = getMonthRange(month);
      const { data, error } = await supabase
        .from("transactions")
        .select("amount, is_internal_transfer, bank_accounts(account_type), categories(name, exclude_from_income, exclude_from_expenses)")
        .gte("date", start)
        .lte("date", end)
        .limit(10000);
      if (error) throw error;

      const labels: Record<string, string> = { perso_a: "Perso A", perso_b: "Perso B", joint: "Compte Joint" };
      const typeMap = new Map<string, { amount: number; cats: Map<string, number> }>();
      for (const t of data || []) {
        if (!isRealExpense(t)) continue;
        const accType = (t.bank_accounts as any)?.account_type || "joint";
        const catName = (t.categories as any)?.name || "Non catégorisé";
        const entry = typeMap.get(accType) || { amount: 0, cats: new Map() };
        entry.amount += Math.abs(t.amount);
        entry.cats.set(catName, (entry.cats.get(catName) || 0) + Math.abs(t.amount));
        typeMap.set(accType, entry);
      }

      return ["perso_a", "perso_b", "joint"]
        .filter((type) => typeMap.has(type))
        .map((type) => {
          const entry = typeMap.get(type)!;
          return {
            type,
            label: labels[type],
            amount: entry.amount,
            categories: Array.from(entry.cats.entries())
              .map(([name, amount]) => ({ name, amount }))
              .sort((a, b) => b.amount - a.amount)
              .slice(0, 5),
          } as AccountTypeBreakdown;
        });
    },
  });
}

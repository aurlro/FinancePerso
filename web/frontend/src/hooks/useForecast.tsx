import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { startOfMonth, endOfMonth, format, subMonths, getDaysInMonth, getDate } from "date-fns";

export interface CategoryForecast {
  categoryId: string | null;
  name: string;
  color: string;
  spentThisMonth: number;
  avgMonthly: number;
  projected: number;
  budget: number | null;
}

export interface ForecastData {
  categories: CategoryForecast[];
  totalSpent: number;
  totalProjected: number;
  totalBudget: number;
  dayOfMonth: number;
  daysInMonth: number;
}

export function useForecast(month: Date = new Date()) {
  return useQuery({
    queryKey: ["budget-forecast", format(month, "yyyy-MM")],
    queryFn: async (): Promise<ForecastData> => {
      const now = month;
      const dayOfMonth = getDate(now);
      const daysInMonth = getDaysInMonth(now);

      // Fetch current month transactions
      const curStart = format(startOfMonth(now), "yyyy-MM-dd");
      const curEnd = format(endOfMonth(now), "yyyy-MM-dd");

      // Fetch last 3 complete months
      const histStart = format(startOfMonth(subMonths(now, 3)), "yyyy-MM-dd");
      const histEnd = format(endOfMonth(subMonths(now, 1)), "yyyy-MM-dd");

      const [curRes, histRes, budgetRes] = await Promise.all([
        supabase
          .from("transactions")
          .select("amount, is_internal_transfer, category_id, categories(name, color, exclude_from_income, exclude_from_expenses)")
          .gte("date", curStart)
          .lte("date", curEnd)
          .limit(10000),
        supabase
          .from("transactions")
          .select("date, amount, is_internal_transfer, category_id, categories(name, color, exclude_from_income, exclude_from_expenses)")
          .gte("date", histStart)
          .lte("date", histEnd)
          .limit(10000),
        supabase
          .from("category_budgets")
          .select("category_id, monthly_amount"),
      ]);

      if (curRes.error) throw curRes.error;
      if (histRes.error) throw histRes.error;

      const isExpense = (t: any) =>
        t.amount < 0 && !t.is_internal_transfer &&
        !(t.categories as any)?.exclude_from_income &&
        !(t.categories as any)?.exclude_from_expenses;

      // Current month spending by category
      const curMap = new Map<string, { name: string; color: string; amount: number }>();
      for (const t of curRes.data || []) {
        if (!isExpense(t)) continue;
        const cat = t.categories as any;
        const key = t.category_id || "uncategorized";
        const entry = curMap.get(key) || { name: cat?.name || "Non catégorisé", color: cat?.color || "#94a3b8", amount: 0 };
        entry.amount += Math.abs(t.amount);
        curMap.set(key, entry);
      }

      // Historical average by category (over 3 months)
      const histMap = new Map<string, number>();
      for (const t of histRes.data || []) {
        if (!isExpense(t)) continue;
        const key = t.category_id || "uncategorized";
        histMap.set(key, (histMap.get(key) || 0) + Math.abs(t.amount));
      }
      // Divide by 3 for monthly average
      for (const [k, v] of histMap) histMap.set(k, v / 3);

      // Budgets map
      const budgetMap = new Map<string, number>();
      for (const b of budgetRes.data || []) {
        budgetMap.set(b.category_id, b.monthly_amount);
      }

      // Build forecasts: union of current + historical categories
      const allKeys = new Set([...curMap.keys(), ...histMap.keys()]);
      const categories: CategoryForecast[] = [];

      for (const key of allKeys) {
        const cur = curMap.get(key);
        const avg = histMap.get(key) || 0;
        const spent = cur?.amount || 0;

        // Project: linear extrapolation from current pace
        const projected = dayOfMonth > 0 ? (spent / dayOfMonth) * daysInMonth : avg;

        categories.push({
          categoryId: key === "uncategorized" ? null : key,
          name: cur?.name || "Non catégorisé",
          color: cur?.color || "#94a3b8",
          spentThisMonth: spent,
          avgMonthly: avg,
          projected,
          budget: budgetMap.get(key) ?? null,
        });
      }

      categories.sort((a, b) => b.projected - a.projected);

      const totalSpent = categories.reduce((s, c) => s + c.spentThisMonth, 0);
      const totalProjected = categories.reduce((s, c) => s + c.projected, 0);
      const totalBudget = categories.filter(c => c.budget !== null).reduce((s, c) => s + (c.budget || 0), 0);

      return { categories, totalSpent, totalProjected, totalBudget, dayOfMonth, daysInMonth };
    },
  });
}

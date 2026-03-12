import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowUpRight, ArrowDownRight, ArrowRight } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { format, startOfMonth, endOfMonth, subMonths } from "date-fns";
import { fr } from "date-fns/locale";
import { Link } from "react-router-dom";

function fmt(n: number) {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + " €";
}

function usePreviousMonthSummary() {
  const prevMonth = subMonths(new Date(), 1);
  const prevPrevMonth = subMonths(new Date(), 2);

  return useQuery({
    queryKey: ["recap-widget", format(prevMonth, "yyyy-MM")],
    queryFn: async () => {
      const [cur, prev] = await Promise.all([
        supabase.from("transactions")
          .select("amount, is_internal_transfer, categories(name, exclude_from_income)")
          .gte("date", format(startOfMonth(prevMonth), "yyyy-MM-dd"))
          .lte("date", format(endOfMonth(prevMonth), "yyyy-MM-dd")),
        supabase.from("transactions")
          .select("amount, is_internal_transfer")
          .gte("date", format(startOfMonth(prevPrevMonth), "yyyy-MM-dd"))
          .lte("date", format(endOfMonth(prevPrevMonth), "yyyy-MM-dd")),
      ]);
      if (cur.error) throw cur.error;

      const curTxs = (cur.data || []).filter(t => !t.is_internal_transfer);
      const prevTxs = (prev.data || []).filter(t => !t.is_internal_transfer);

      const expenses = curTxs.filter(t => t.amount < 0).reduce((s, t) => s + Math.abs(t.amount), 0);
      const income = curTxs.filter(t => t.amount > 0 && !(t.categories as any)?.exclude_from_income).reduce((s, t) => s + t.amount, 0);
      const prevExpenses = prevTxs.filter(t => t.amount < 0).reduce((s, t) => s + Math.abs(t.amount), 0);

      const delta = prevExpenses > 0 ? ((expenses - prevExpenses) / prevExpenses) * 100 : 0;

      // Top 3 categories
      const catMap = new Map<string, number>();
      for (const t of curTxs) {
        if (t.amount >= 0) continue;
        const name = (t.categories as any)?.name || "Non catégorisé";
        catMap.set(name, (catMap.get(name) || 0) + Math.abs(t.amount));
      }
      const topCats = Array.from(catMap.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
        .map(([name, amount]) => ({ name, amount }));

      return { expenses, income, savings: income - expenses, delta, topCats, month: prevMonth };
    },
  });
}

export function MonthlyRecapWidget() {
  const { data, isLoading } = usePreviousMonthSummary();

  if (isLoading) return <Skeleton className="h-32 w-full" />;
  if (!data || (data.expenses === 0 && data.income === 0)) return null;

  return (
    <Card className="border-primary/20 bg-primary/5">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium capitalize">
            Bilan {format(data.month, "MMMM yyyy", { locale: fr })}
          </CardTitle>
          <Button variant="ghost" size="sm" className="h-7 text-xs gap-1" asChild>
            <Link to="/recap">Voir le détail <ArrowRight className="h-3 w-3" /></Link>
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-6">
          <div>
            <p className="text-xs text-muted-foreground">Dépenses</p>
            <p className="text-lg font-bold text-destructive">{fmt(data.expenses)}</p>
            <div className="flex items-center gap-1">
              {data.delta <= 0 ? <ArrowDownRight className="h-3 w-3 text-primary" /> : <ArrowUpRight className="h-3 w-3 text-destructive" />}
              <span className={`text-xs ${data.delta <= 0 ? "text-primary" : "text-destructive"}`}>
                {data.delta >= 0 ? "+" : ""}{data.delta.toFixed(1)}%
              </span>
            </div>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Épargne</p>
            <p className={`text-lg font-bold ${data.savings >= 0 ? "text-primary" : "text-destructive"}`}>{fmt(data.savings)}</p>
          </div>
          <div className="ml-auto space-y-1">
            {data.topCats.map(c => (
              <div key={c.name} className="flex items-center justify-between gap-3 text-xs">
                <span className="text-muted-foreground truncate max-w-[100px]">{c.name}</span>
                <span className="font-medium">{fmt(c.amount)}</span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

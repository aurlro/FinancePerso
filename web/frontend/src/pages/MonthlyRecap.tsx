import { AppLayout } from "@/components/AppLayout";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { format, startOfMonth, endOfMonth, subMonths } from "date-fns";
import { fr } from "date-fns/locale";
import { TrendingDown, TrendingUp, ArrowUpRight, ArrowDownRight, ChevronLeft, ChevronRight } from "lucide-react";
import { useBudgets } from "@/hooks/useBudgets";
import { useCategories } from "@/hooks/useCategories";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

function fmt(n: number) {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";
}

function fmtPct(n: number) {
  const sign = n >= 0 ? "+" : "";
  return `${sign}${n.toFixed(1)}%`;
}

const COLORS = [
  "hsl(160, 84%, 39%)", "hsl(217, 91%, 60%)", "hsl(38, 92%, 50%)",
  "hsl(280, 65%, 60%)", "hsl(0, 72%, 51%)", "hsl(190, 80%, 42%)",
  "hsl(330, 70%, 55%)", "hsl(95, 60%, 45%)",
];

function useMonthlyRecap(month: Date) {
  return useQuery({
    queryKey: ["monthly-recap", format(month, "yyyy-MM")],
    queryFn: async () => {
      const start = format(startOfMonth(month), "yyyy-MM-dd");
      const end = format(endOfMonth(month), "yyyy-MM-dd");
      const prevMonth = subMonths(month, 1);
      const prevStart = format(startOfMonth(prevMonth), "yyyy-MM-dd");
      const prevEnd = format(endOfMonth(prevMonth), "yyyy-MM-dd");

      const [current, previous] = await Promise.all([
        supabase.from("transactions")
          .select("amount, is_internal_transfer, category_id, categories(name, color, exclude_from_income), bank_accounts(account_type)")
          .gte("date", start).lte("date", end),
        supabase.from("transactions")
          .select("amount, is_internal_transfer, category_id, categories(name, color, exclude_from_income), bank_accounts(account_type)")
          .gte("date", prevStart).lte("date", prevEnd),
      ]);

      if (current.error) throw current.error;
      if (previous.error) throw previous.error;

      const process = (data: any[]) => {
        const txs = data.filter(t => !t.is_internal_transfer);
        const expenses = txs.filter(t => t.amount < 0 && !(t.categories as any)?.exclude_from_income).reduce((s, t) => s + Math.abs(t.amount), 0);
        const income = txs.filter(t => t.amount > 0 && !(t.categories as any)?.exclude_from_income).reduce((s, t) => s + t.amount, 0);

        const catMap = new Map<string, { name: string; color: string; amount: number; categoryId: string | null }>();
        const typeMap = new Map<string, number>();

        for (const t of txs) {
          if (t.amount >= 0 || (t.categories as any)?.exclude_from_income) continue;
          const cat = t.categories as any;
          const name = cat?.name || "Non catégorisé";
          const color = cat?.color || "#94a3b8";
          const categoryId = t.category_id || null;
          const entry = catMap.get(name) || { name, color, amount: 0, categoryId };
          entry.amount += Math.abs(t.amount);
          catMap.set(name, entry);

          const accType = (t.bank_accounts as any)?.account_type || "joint";
          typeMap.set(accType, (typeMap.get(accType) || 0) + Math.abs(t.amount));
        }

        return {
          expenses, income, savings: income - expenses,
          categories: Array.from(catMap.values()).sort((a, b) => b.amount - a.amount),
          byAccount: typeMap,
          txCount: txs.length,
        };
      };

      const cur = process(current.data || []);
      const prev = process(previous.data || []);

      const expensesDelta = prev.expenses > 0 ? ((cur.expenses - prev.expenses) / prev.expenses) * 100 : 0;
      const incomeDelta = prev.income > 0 ? ((cur.income - prev.income) / prev.income) * 100 : 0;

      return { current: cur, previous: prev, expensesDelta, incomeDelta };
    },
  });
}

export default function MonthlyRecap() {
  const navigate = useNavigate();
  const [month, setMonth] = useState(subMonths(new Date(), 1));
  const { data, isLoading } = useMonthlyRecap(month);
  const { data: budgets } = useBudgets();
  const { data: categories } = useCategories();

  const navigateToCategory = (categoryId: string | null) => {
    if (!categoryId) return;
    const params = new URLSearchParams();
    params.set("category", categoryId);
    params.set("month", format(month, "yyyy-MM"));
    navigate(`/transactions?${params.toString()}`);
  };

  const budgetComparison = budgets?.length && data
    ? budgets.map(b => {
        const cat = categories?.find(c => c.id === b.category_id);
        if (!cat) return null;
        const spent = data.current.categories.find(tc => tc.name === cat.name)?.amount || 0;
        const pct = b.monthly_amount > 0 ? (spent / b.monthly_amount) * 100 : 0;
        return { name: cat.name, color: cat.color || "#94a3b8", budget: b.monthly_amount, spent, pct };
      }).filter(Boolean) as { name: string; color: string; budget: number; spent: number; pct: number }[]
    : [];

  const labels: Record<string, string> = { perso_a: "Perso A", perso_b: "Perso B", joint: "Compte Joint" };

  return (
    <AppLayout title="Bilan mensuel">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold tracking-tight capitalize">
              Bilan {format(month, "MMMM yyyy", { locale: fr })}
            </h2>
            <p className="text-muted-foreground">Récapitulatif complet du mois</p>
          </div>
          <div className="flex items-center gap-1">
            <Button variant="outline" size="icon" className="h-8 w-8" onClick={() => setMonth(m => subMonths(m, 1))}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" className="h-8 px-3 text-xs" onClick={() => setMonth(subMonths(new Date(), 1))}>
              Mois dernier
            </Button>
            <Button variant="outline" size="icon" className="h-8 w-8" onClick={() => setMonth(m => {
              const next = subMonths(m, -1);
              return next > new Date() ? m : next;
            })}>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
        ) : !data ? (
          <Card><CardContent className="py-12 text-center text-muted-foreground">Aucune donnée disponible</CardContent></Card>
        ) : (
          <>
            {/* KPI cards with comparison */}
            <div className="grid gap-4 sm:grid-cols-4">
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Dépenses</CardTitle></CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold text-destructive">{fmt(data.current.expenses)}</p>
                  <div className="flex items-center gap-1 mt-1">
                    {data.expensesDelta <= 0 ? <ArrowDownRight className="h-3.5 w-3.5 text-primary" /> : <ArrowUpRight className="h-3.5 w-3.5 text-destructive" />}
                    <span className={`text-xs font-medium ${data.expensesDelta <= 0 ? "text-primary" : "text-destructive"}`}>{fmtPct(data.expensesDelta)}</span>
                    <span className="text-xs text-muted-foreground">vs mois précédent</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Revenus</CardTitle></CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold text-primary">{fmt(data.current.income)}</p>
                  <div className="flex items-center gap-1 mt-1">
                    {data.incomeDelta >= 0 ? <ArrowUpRight className="h-3.5 w-3.5 text-primary" /> : <ArrowDownRight className="h-3.5 w-3.5 text-destructive" />}
                    <span className={`text-xs font-medium ${data.incomeDelta >= 0 ? "text-primary" : "text-destructive"}`}>{fmtPct(data.incomeDelta)}</span>
                    <span className="text-xs text-muted-foreground">vs mois précédent</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Épargne</CardTitle></CardHeader>
                <CardContent>
                  <p className={`text-2xl font-bold ${data.current.savings >= 0 ? "text-primary" : "text-destructive"}`}>{fmt(data.current.savings)}</p>
                  <p className="text-xs text-muted-foreground mt-1">{data.current.txCount} transactions</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Par compte</CardTitle></CardHeader>
                <CardContent className="space-y-1.5">
                  {["perso_a", "perso_b", "joint"].map(type => {
                    const amount = data.current.byAccount.get(type);
                    if (!amount) return null;
                    return (
                      <div key={type} className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">{labels[type]}</span>
                        <span className="font-medium">{fmt(amount)}</span>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              {/* Category donut */}
              <Card>
                <CardHeader><CardTitle className="text-base">Répartition par catégorie</CardTitle></CardHeader>
                <CardContent>
                  {!data.current.categories.length ? (
                    <p className="text-sm text-muted-foreground text-center py-8">Aucune dépense</p>
                  ) : (
                    <div className="flex flex-col items-center gap-4">
                      <ChartContainer config={{}} className="h-[200px] w-full">
                        <PieChart>
                          <Pie data={data.current.categories.slice(0, 8)} dataKey="amount" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={2} strokeWidth={2} stroke="hsl(var(--background))" className="cursor-pointer">
                            {data.current.categories.slice(0, 8).map((c, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} onClick={() => navigateToCategory(c.categoryId)} />)}
                          </Pie>
                          <ChartTooltip content={<ChartTooltipContent formatter={(v) => fmt(Number(v))} />} />
                        </PieChart>
                      </ChartContainer>
                      <div className="grid grid-cols-2 gap-x-6 gap-y-1 w-full">
                        {data.current.categories.slice(0, 8).map((c, i) => (
                          <button key={c.name} className="flex items-center justify-between text-xs rounded-md px-1.5 py-1 hover:bg-muted/50 transition-colors cursor-pointer" onClick={() => navigateToCategory(c.categoryId)}>
                            <div className="flex items-center gap-1.5">
                              <div className="h-2.5 w-2.5 rounded-full shrink-0" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                              <span className="text-muted-foreground truncate">{c.name}</span>
                            </div>
                            <span className="font-medium ml-2">{fmt(c.amount)}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Budget vs actual */}
              <Card>
                <CardHeader><CardTitle className="text-base">Budget vs Réel</CardTitle></CardHeader>
                <CardContent>
                  {!budgetComparison.length ? (
                    <div className="text-center py-8 space-y-3">
                      <p className="text-sm text-muted-foreground">Aucun budget défini.</p>
                      <Button variant="outline" size="sm" asChild>
                        <Link to="/settings?tab=budgets">Configurer les budgets</Link>
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {budgetComparison.map(a => (
                        <div key={a.name} className="space-y-1">
                          <div className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                              <div className="h-3 w-3 rounded-full" style={{ backgroundColor: a.color }} />
                              <span className="font-medium">{a.name}</span>
                            </div>
                            <span className={`font-mono text-xs ${a.pct >= 100 ? "text-destructive font-bold" : "text-muted-foreground"}`}>
                              {fmt(a.spent)} / {fmt(a.budget)}
                            </span>
                          </div>
                          <Progress value={Math.min(a.pct, 100)} className={`h-2 ${a.pct >= 100 ? "[&>div]:bg-destructive" : ""}`} />
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Comparison bar chart */}
            <Card>
              <CardHeader><CardTitle className="text-base">Comparaison avec le mois précédent</CardTitle></CardHeader>
              <CardContent>
                <ChartContainer
                  config={{
                    current: { label: format(month, "MMM yy", { locale: fr }), color: "hsl(var(--primary))" },
                    previous: { label: format(subMonths(month, 1), "MMM yy", { locale: fr }), color: "hsl(var(--muted-foreground))" },
                  }}
                  className="h-[200px] w-full"
                >
                  <BarChart data={[
                    { name: "Dépenses", current: data.current.expenses, previous: data.previous.expenses },
                    { name: "Revenus", current: data.current.income, previous: data.previous.income },
                    { name: "Épargne", current: Math.max(data.current.savings, 0), previous: Math.max(data.previous.savings, 0) },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border/50" />
                    <XAxis dataKey="name" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
                    <YAxis tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} tickFormatter={v => `${(v / 1000).toFixed(0)}k`} />
                    <ChartTooltip content={<ChartTooltipContent formatter={(v) => fmt(Number(v))} />} />
                    <Bar dataKey="previous" fill="hsl(var(--muted-foreground))" radius={[4, 4, 0, 0]} opacity={0.4} />
                    <Bar dataKey="current" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ChartContainer>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </AppLayout>
  );
}

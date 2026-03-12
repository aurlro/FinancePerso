import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, PieChart, Pie, Cell, Label } from "recharts";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { format, startOfYear, endOfYear, startOfMonth, endOfMonth, eachMonthOfInterval } from "date-fns";
import { fr } from "date-fns/locale";
import { ChevronLeft, ChevronRight, Download, TrendingDown, Users, CalendarDays } from "lucide-react";
import { toast } from "sonner";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BudgetAlerts } from "@/components/BudgetAlerts";
import { useBudgets } from "@/hooks/useBudgets";
import { useCategories } from "@/hooks/useCategories";
import { Progress } from "@/components/ui/progress";

function fmt(n: number) {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";
}

const MONTH_OPTIONS = [
  { value: "all", label: "Année complète" },
  ...Array.from({ length: 12 }, (_, i) => ({
    value: String(i),
    label: format(new Date(2000, i), "MMMM", { locale: fr }),
  })),
];

function useFilteredData(year: number, monthFilter: string) {
  return useQuery({
    queryKey: ["analytics-filtered", year, monthFilter],
    queryFn: async () => {
      let start: string, end: string;
      if (monthFilter === "all") {
        start = format(startOfYear(new Date(year, 0)), "yyyy-MM-dd");
        end = format(endOfYear(new Date(year, 0)), "yyyy-MM-dd");
      } else {
        const m = parseInt(monthFilter);
        start = format(startOfMonth(new Date(year, m)), "yyyy-MM-dd");
        end = format(endOfMonth(new Date(year, m)), "yyyy-MM-dd");
      }

      const { data, error } = await supabase
        .from("transactions")
        .select("date, amount, is_internal_transfer, category_id, bank_accounts(account_type, name), categories(name, color, exclude_from_income)")
        .gte("date", start)
        .lte("date", end);
      if (error) throw error;

      const txs = (data || []).filter(t => !t.is_internal_transfer && !(t.categories as any)?.exclude_from_income);

      // Monthly evolution (only for full year)
      let monthly: { month: string; depenses: number; revenus: number }[] = [];
      if (monthFilter === "all") {
        const months = eachMonthOfInterval({ start: new Date(year, 0), end: new Date(year, 11) });
        monthly = months.map(m => {
          const mStart = startOfMonth(m);
          const mEnd = endOfMonth(m);
          const mTxs = txs.filter(t => {
            const d = new Date(t.date);
            return d >= mStart && d <= mEnd;
          });
          return {
            month: format(m, "MMM", { locale: fr }),
            depenses: mTxs.filter(t => t.amount < 0).reduce((s, t) => s + Math.abs(t.amount), 0),
            revenus: mTxs.filter(t => t.amount > 0 && !(t.categories as any)?.exclude_from_income).reduce((s, t) => s + t.amount, 0),
          };
        });
      }

      // Top categories
      const catMap = new Map<string, { name: string; color: string; amount: number; categoryId: string | null; icon: string | null }>();
      for (const t of txs) {
        if (t.amount >= 0) continue;
        const cat = t.categories as any;
        const name = cat?.name || "Non catégorisé";
        const color = cat?.color || "#94a3b8";
        const icon = cat?.icon || null;
        const categoryId = t.category_id || null;
        const entry = catMap.get(name) || { name, color, amount: 0, categoryId, icon };
        entry.amount += Math.abs(t.amount);
        catMap.set(name, entry);
      }
      const topCategories = Array.from(catMap.values()).sort((a, b) => b.amount - a.amount);

      // Partner comparison
      const labels: Record<string, string> = { perso_a: "Perso A", perso_b: "Perso B", joint: "Compte Joint" };
      const byType: Record<string, { total: number; cats: Map<string, number> }> = {};
      for (const t of txs) {
        if (t.amount >= 0) continue;
        const accType = (t.bank_accounts as any)?.account_type || "joint";
        if (!byType[accType]) byType[accType] = { total: 0, cats: new Map() };
        byType[accType].total += Math.abs(t.amount);
        const catName = (t.categories as any)?.name || "Non catégorisé";
        byType[accType].cats.set(catName, (byType[accType].cats.get(catName) || 0) + Math.abs(t.amount));
      }
      const partnerData = Object.entries(byType).map(([type, d]) => ({
        type, label: labels[type] || type, total: d.total,
        categories: Array.from(d.cats.entries()).map(([name, amount]) => ({ name, amount })).sort((a, b) => b.amount - a.amount).slice(0, 8),
      }));

      const totalExpenses = txs.filter(t => t.amount < 0).reduce((s, t) => s + Math.abs(t.amount), 0);
      const totalIncome = txs.filter(t => t.amount > 0 && !(t.categories as any)?.exclude_from_income).reduce((s, t) => s + t.amount, 0);

      return { monthly, topCategories, partnerData, totalExpenses, totalIncome };
    },
  });
}

async function exportCSV() {
  const { data, error } = await supabase
    .from("transactions")
    .select("date, label, amount, is_internal_transfer, bank_accounts(name, account_type), categories(name)")
    .order("date", { ascending: false })
    .limit(10000);
  if (error) { toast.error("Erreur export"); return; }

  const header = "Date;Libellé;Montant;Compte;Type;Catégorie;Virement interne\n";
  const rows = (data || []).map(t =>
    `${t.date};${t.label.replace(/;/g, ",")};${t.amount};${(t.bank_accounts as any)?.name || ""};${(t.bank_accounts as any)?.account_type || ""};${(t.categories as any)?.name || ""};${t.is_internal_transfer ? "Oui" : "Non"}`
  ).join("\n");

  const blob = new Blob(["\uFEFF" + header + rows], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `export-transactions-${format(new Date(), "yyyy-MM-dd")}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  toast.success("Export CSV téléchargé");
}

const COLORS = [
  "hsl(160, 84%, 39%)", "hsl(217, 91%, 60%)", "hsl(38, 92%, 50%)",
  "hsl(280, 65%, 60%)", "hsl(0, 72%, 51%)", "hsl(190, 80%, 42%)",
  "hsl(330, 70%, 55%)", "hsl(95, 60%, 45%)",
];

export default function Analytics() {
  const navigate = useNavigate();
  const [year, setYear] = useState(new Date().getFullYear());
  const [monthFilter, setMonthFilter] = useState("all");

  const navigateToCategory = useCallback((categoryId: string | null) => {
    const params = new URLSearchParams();
    if (monthFilter === "all") {
      // No month filter for full year
    } else {
      params.set("month", format(new Date(year, parseInt(monthFilter)), "yyyy-MM"));
    }
    if (categoryId) params.set("category", categoryId);
    navigate(`/transactions?${params.toString()}`);
  }, [navigate, year, monthFilter]);

  const { data, isLoading } = useFilteredData(year, monthFilter);
  const { data: budgets } = useBudgets();
  const { data: categories } = useCategories();

  const totalExpenses = data?.totalExpenses || 0;
  const totalIncome = data?.totalIncome || 0;

  // Budget vs actual for selected month
  const budgetComparison = monthFilter !== "all" && budgets?.length
    ? budgets.map(b => {
        const cat = categories?.find(c => c.id === b.category_id);
        if (!cat) return null;
        const spent = data?.topCategories.find(tc => tc.name === cat.name)?.amount || 0;
        const pct = b.monthly_amount > 0 ? (spent / b.monthly_amount) * 100 : 0;
        return { cat, budget: b.monthly_amount, spent, pct };
      }).filter(Boolean) as { cat: { name: string; color: string }; budget: number; spent: number; pct: number }[] | undefined
    : undefined;

  const periodLabel = monthFilter === "all"
    ? String(year)
    : format(new Date(year, parseInt(monthFilter)), "MMMM yyyy", { locale: fr });

  return (
    <AppLayout title="Analytics">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h2 className="text-2xl font-semibold tracking-tight capitalize">{periodLabel}</h2>
            <p className="text-muted-foreground">Analyse détaillée de vos finances</p>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <Button variant="outline" size="icon" className="h-8 w-8" onClick={() => setYear(y => y - 1)}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" className="h-8 px-3 text-xs" disabled={year === new Date().getFullYear()} onClick={() => setYear(new Date().getFullYear())}>
              {new Date().getFullYear()}
            </Button>
            <Button variant="outline" size="icon" className="h-8 w-8" disabled={year >= new Date().getFullYear()} onClick={() => setYear(y => y + 1)}>
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Select value={monthFilter} onValueChange={setMonthFilter}>
              <SelectTrigger className="w-[160px] h-8">
                <CalendarDays className="h-3.5 w-3.5 mr-1.5" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {MONTH_OPTIONS.map(o => (
                  <SelectItem key={o.value} value={o.value} className="capitalize">{o.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm" className="gap-2 h-8" onClick={exportCSV}>
              <Download className="h-4 w-4" /> Export CSV
            </Button>
          </div>
        </div>

        {/* Budget alerts for selected month */}
        {monthFilter !== "all" && (
          <BudgetAlerts month={new Date(year, parseInt(monthFilter))} />
        )}

        {/* Summary cards */}
        <div className="grid gap-4 sm:grid-cols-3">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Total dépenses</CardTitle></CardHeader>
            <CardContent>
              {isLoading ? <Skeleton className="h-8 w-28" /> : <p className="text-2xl font-bold text-destructive">{fmt(totalExpenses)}</p>}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Total revenus</CardTitle></CardHeader>
            <CardContent>
              {isLoading ? <Skeleton className="h-8 w-28" /> : <p className="text-2xl font-bold text-primary">{fmt(totalIncome)}</p>}
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Épargne nette</CardTitle></CardHeader>
            <CardContent>
              {isLoading ? <Skeleton className="h-8 w-28" /> : (
                <p className={`text-2xl font-bold ${totalIncome - totalExpenses >= 0 ? "text-primary" : "text-destructive"}`}>
                  {fmt(totalIncome - totalExpenses)}
                </p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Annual bar chart - only for full year */}
        {monthFilter === "all" && (
          <Card>
            <CardHeader><CardTitle className="text-base flex items-center gap-2"><TrendingDown className="h-4 w-4" /> Évolution annuelle</CardTitle></CardHeader>
            <CardContent>
              {isLoading ? <Skeleton className="h-[300px] w-full" /> : (
                <ChartContainer
                  config={{
                    depenses: { label: "Dépenses", color: "hsl(var(--destructive))" },
                    revenus: { label: "Revenus", color: "hsl(var(--primary))" },
                  }}
                  className="h-[300px] w-full"
                >
                  <BarChart data={data?.monthly}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border/50" />
                    <XAxis dataKey="month" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
                    <YAxis tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} tickFormatter={v => `${(v / 1000).toFixed(0)}k`} />
                    <ChartTooltip content={<ChartTooltipContent formatter={(value) => fmt(Number(value))} />} />
                    <Bar dataKey="revenus" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="depenses" fill="hsl(var(--destructive))" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ChartContainer>
              )}
            </CardContent>
          </Card>
        )}

        {/* Budget vs actual - only for specific month */}
        {budgetComparison && budgetComparison.length > 0 && (
          <Card>
            <CardHeader><CardTitle className="text-base">Budget vs Réel</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {budgetComparison.map(a => (
                <div key={a.cat.name} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full" style={{ backgroundColor: a.cat.color }} />
                      <span className="font-medium">{a.cat.name}</span>
                    </div>
                    <span className={`font-mono text-xs ${a.pct >= 100 ? "text-destructive font-bold" : "text-muted-foreground"}`}>
                      {fmt(a.spent)} / {fmt(a.budget)}
                    </span>
                  </div>
                  <Progress value={Math.min(a.pct, 100)} className={`h-2 ${a.pct >= 100 ? "[&>div]:bg-destructive" : ""}`} />
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        <div className="grid gap-4 lg:grid-cols-2">
          {/* Top categories donut */}
          <Card>
            <CardHeader><CardTitle className="text-base">Top catégories</CardTitle></CardHeader>
            <CardContent>
              {isLoading ? <Skeleton className="h-[300px] w-full" /> : !data?.topCategories?.length ? (
                <div className="flex h-[300px] items-center justify-center"><p className="text-sm text-muted-foreground">Aucune donnée</p></div>
              ) : (
                <div className="flex flex-col items-center gap-4">
                  <ChartContainer config={{}} className="h-[220px] w-full">
                    <PieChart>
                      <Pie data={data.topCategories.slice(0, 8)} dataKey="amount" nameKey="name" cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={2} strokeWidth={2} stroke="hsl(var(--background))" className="cursor-pointer">
                        {data.topCategories.slice(0, 8).map((entry, i) => {
                          const color = entry.color || COLORS[i % COLORS.length];
                          return <Cell key={i} fill={color} onClick={() => navigateToCategory(entry.categoryId)} className="cursor-pointer" />;
                        })}
                        <Label 
                          content={({ viewBox }) => {
                            if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                              return (
                                <text x={viewBox.cx} y={viewBox.cy} textAnchor="middle" dominantBaseline="central">
                                  <tspan x={viewBox.cx} y={viewBox.cy} className="fill-foreground text-sm font-bold">
                                    {fmt(totalExpenses)}
                                  </tspan>
                                  <tspan x={viewBox.cx} y={(viewBox.cy || 0) + 16} className="fill-muted-foreground text-xs">
                                    Total dépenses
                                  </tspan>
                                </text>
                              );
                            }
                          }}
                        />
                      </Pie>
                      <ChartTooltip content={<ChartTooltipContent 
                        formatter={(value, name) => {
                          const pct = totalExpenses > 0 ? ((Number(value) / totalExpenses) * 100).toFixed(1) : 0;
                          return [`${fmt(Number(value))} (${pct}%)`, name];
                        }} 
                      />} />
                    </PieChart>
                  </ChartContainer>
                  <div className="space-y-2 w-full">
                    {data.topCategories.slice(0, 8).map((c, i) => {
                      const color = c.color || COLORS[i % COLORS.length];
                      const pct = totalExpenses > 0 ? (c.amount / totalExpenses) * 100 : 0;
                      return (
                        <button key={c.name} className="flex items-center justify-between w-full hover:bg-muted/50 rounded px-2 py-1.5 transition-colors cursor-pointer text-left" onClick={() => navigateToCategory(c.categoryId)}>
                          <div className="flex items-center gap-2 flex-1 min-w-0">
                            <div className="h-3 w-3 rounded-full shrink-0" style={{ backgroundColor: color }} />
                            <span className="text-sm text-muted-foreground truncate">
                              {c.icon && <span className="mr-1.5">{c.icon}</span>}
                              {c.name}
                            </span>
                          </div>
                          <div className="flex items-center gap-3 ml-2">
                            <div className="flex-1 min-w-[80px]">
                              <div className="relative h-2 w-full overflow-hidden rounded-full bg-muted">
                                <div 
                                  className="h-full transition-all" 
                                  style={{ 
                                    width: `${Math.min(pct, 100)}%`,
                                    backgroundColor: color
                                  }} 
                                />
                              </div>
                            </div>
                            <div className="text-right min-w-[80px]">
                              <div className="text-sm font-medium">{fmt(c.amount)}</div>
                              <div className="text-xs text-muted-foreground">{pct.toFixed(1)}%</div>
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Partner comparison */}
          <Card>
            <CardHeader><CardTitle className="text-base flex items-center gap-2"><Users className="h-4 w-4" /> Comparatif par partenaire</CardTitle></CardHeader>
            <CardContent>
              {isLoading ? <Skeleton className="h-[300px] w-full" /> : !data?.partnerData?.length ? (
                <div className="flex h-[300px] items-center justify-center"><p className="text-sm text-muted-foreground">Aucune donnée</p></div>
              ) : (
                <div className="space-y-6">
                  <div className="flex gap-3">
                    {data.partnerData.map(p => (
                      <div key={p.type} className="flex-1 rounded-lg border p-3">
                        <p className="text-xs text-muted-foreground">{p.label}</p>
                        <p className="text-lg font-bold">{fmt(p.total)}</p>
                      </div>
                    ))}
                  </div>
                  {data.partnerData.map(p => (
                    <div key={p.type} className="space-y-2">
                      <h4 className="text-sm font-medium flex items-center gap-2">
                        {p.label}
                        <Badge variant="secondary" className="font-mono text-xs">{fmt(p.total)}</Badge>
                      </h4>
                      <div className="space-y-1.5">
                        {p.categories.slice(0, 5).map(cat => {
                          const pct = p.total > 0 ? (cat.amount / p.total) * 100 : 0;
                          return (
                            <div key={cat.name} className="space-y-0.5">
                              <div className="flex items-center justify-between text-xs">
                                <span className="text-muted-foreground">{cat.name}</span>
                                <span className="font-medium">{fmt(cat.amount)}</span>
                              </div>
                              <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                                <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${pct}%` }} />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}

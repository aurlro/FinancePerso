import { useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TrendingDown, TrendingUp, Wallet, PiggyBank, ChevronLeft, ChevronRight } from "lucide-react";
import { useDashboardStats, useCategoryBreakdown, useMonthlyEvolution, useAccountTypeBreakdown } from "@/hooks/useDashboard";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { format, addMonths, subMonths, isSameMonth } from "date-fns";
import { fr } from "date-fns/locale";

function fmt(n: number) {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";
}

export default function Dashboard() {
  const [selectedMonth, setSelectedMonth] = useState(new Date());
  const isCurrentMonth = isSameMonth(selectedMonth, new Date());

  const { data: stats, isLoading: loadingStats } = useDashboardStats(selectedMonth);
  const { data: catBreakdown, isLoading: loadingCat } = useCategoryBreakdown(selectedMonth);
  const { data: monthlyData, isLoading: loadingMonthly } = useMonthlyEvolution();
  const { data: accountData, isLoading: loadingAccounts } = useAccountTypeBreakdown(selectedMonth);

  const hasData = stats && (stats.totalExpenses > 0 || stats.totalIncome > 0);

  const statCards = [
    { title: "Reste à vivre", value: stats ? fmt(stats.resteAVivre) : "—", icon: Wallet, description: format(selectedMonth, "MMMM yyyy", { locale: fr }) },
    { title: "Dépenses", value: stats ? fmt(stats.totalExpenses) : "—", icon: TrendingDown, description: format(selectedMonth, "MMMM yyyy", { locale: fr }), negative: true },
    { title: "Revenus", value: stats ? fmt(stats.totalIncome) : "—", icon: TrendingUp, description: format(selectedMonth, "MMMM yyyy", { locale: fr }) },
    { title: "Épargne nette", value: stats ? fmt(stats.epargneNette) : "—", icon: PiggyBank, description: format(selectedMonth, "MMMM yyyy", { locale: fr }) },
  ];

  return (
    <AppLayout title="Dashboard">
      <div className="space-y-6">
        {/* Month navigation */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold tracking-tight capitalize">
              {format(selectedMonth, "MMMM yyyy", { locale: fr })}
            </h2>
            <p className="text-muted-foreground">
              {hasData ? "Résumé de vos finances." : "Importez vos premiers relevés pour commencer l'analyse."}
            </p>
          </div>
          <div className="flex items-center gap-1">
            <Button variant="outline" size="icon" className="h-8 w-8" onClick={() => setSelectedMonth(subMonths(selectedMonth, 1))}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" className="h-8 px-3 text-xs" disabled={isCurrentMonth} onClick={() => setSelectedMonth(new Date())}>
              Aujourd'hui
            </Button>
            <Button variant="outline" size="icon" className="h-8 w-8" disabled={isCurrentMonth} onClick={() => setSelectedMonth(addMonths(selectedMonth, 1))}>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Stats cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {statCards.map((stat) => (
            <Card key={stat.title} className="transition-shadow hover:shadow-md">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
                <stat.icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                {loadingStats ? <Skeleton className="h-8 w-24" /> : <div className="text-2xl font-bold">{stat.value}</div>}
                <p className="text-xs text-muted-foreground capitalize">{stat.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts row */}
        <div className="grid gap-4 lg:grid-cols-2">
          {/* Donut chart */}
          <Card>
            <CardHeader><CardTitle className="text-base">Répartition par catégorie</CardTitle></CardHeader>
            <CardContent>
              {loadingCat ? (
                <Skeleton className="h-[300px] w-full" />
              ) : !catBreakdown?.length ? (
                <div className="flex h-[300px] items-center justify-center"><p className="text-sm text-muted-foreground">Aucune donnée disponible</p></div>
              ) : (
                <div className="flex flex-col items-center gap-4">
                  <ChartContainer config={{}} className="h-[250px] w-full">
                    <PieChart>
                      <Pie data={catBreakdown} dataKey="amount" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} strokeWidth={2} stroke="hsl(var(--background))">
                        {catBreakdown.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                      </Pie>
                      <ChartTooltip content={<ChartTooltipContent formatter={(value) => fmt(Number(value))} />} />
                    </PieChart>
                  </ChartContainer>
                  <div className="flex flex-wrap justify-center gap-2">
                    {catBreakdown.slice(0, 8).map((c) => (
                      <div key={c.name} className="flex items-center gap-1.5 text-xs">
                        <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: c.color }} />
                        <span className="text-muted-foreground">{c.name}</span>
                        <span className="font-medium">{fmt(c.amount)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Line chart */}
          <Card>
            <CardHeader><CardTitle className="text-base">Évolution mensuelle</CardTitle></CardHeader>
            <CardContent>
              {loadingMonthly ? (
                <Skeleton className="h-[300px] w-full" />
              ) : !monthlyData?.some((m) => m.depenses > 0 || m.revenus > 0) ? (
                <div className="flex h-[300px] items-center justify-center"><p className="text-sm text-muted-foreground">Aucune donnée disponible</p></div>
              ) : (
                <ChartContainer config={{ depenses: { label: "Dépenses", color: "hsl(var(--destructive))" }, revenus: { label: "Revenus", color: "hsl(160 84% 39%)" } }} className="h-[300px] w-full">
                  <LineChart data={monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border/50" />
                    <XAxis dataKey="month" className="text-xs" tick={{ fill: "hsl(var(--muted-foreground))" }} />
                    <YAxis className="text-xs" tick={{ fill: "hsl(var(--muted-foreground))" }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                    <ChartTooltip content={<ChartTooltipContent formatter={(value) => fmt(Number(value))} />} />
                    <Line type="monotone" dataKey="revenus" stroke="hsl(160 84% 39%)" strokeWidth={2} dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="depenses" stroke="hsl(var(--destructive))" strokeWidth={2} dot={{ r: 4 }} />
                  </LineChart>
                </ChartContainer>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Account type comparison */}
        <Card>
          <CardHeader><CardTitle className="text-base">Comparatif par type de compte</CardTitle></CardHeader>
          <CardContent>
            {loadingAccounts ? (
              <Skeleton className="h-[250px] w-full" />
            ) : !accountData?.length ? (
              <div className="flex h-[200px] items-center justify-center"><p className="text-sm text-muted-foreground">Aucune donnée disponible</p></div>
            ) : (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {accountData.map((acc) => (
                  <div key={acc.type} className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">{acc.label}</h4>
                      <Badge variant="secondary" className="font-mono text-xs">{fmt(acc.amount)}</Badge>
                    </div>
                    <div className="space-y-2">
                      {acc.categories.map((cat) => {
                        const pct = acc.amount > 0 ? (cat.amount / acc.amount) * 100 : 0;
                        return (
                          <div key={cat.name} className="space-y-1">
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
    </AppLayout>
  );
}

import { useState, useCallback } from "react";
import { useNavigate, Link } from "react-router-dom";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TrendingDown, TrendingUp, Wallet, PiggyBank, ChevronLeft, ChevronRight, ArrowLeftRight, Info } from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
// CHANGED: Import from new API hooks instead of Supabase hooks
import { useDashboardStats, useCategoryBreakdown, useMonthlyEvolution, useAccountTypeBreakdown } from "@/hooks/useDashboardApi";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { BudgetAlerts } from "@/components/BudgetAlerts";
import { BudgetForecast } from "@/components/BudgetForecast";
import { MonthlyRecapWidget } from "@/components/MonthlyRecapWidget";
import { CoupleBalanceWidget } from "@/components/CoupleBalanceWidget";
import { SavingsGoalsWidget } from "@/components/SavingsGoalsWidget";
import { useOnboardingStatus } from "@/hooks/useOnboardingStatus";
import { Onboarding } from "@/components/Onboarding";
import { format, addMonths, subMonths, isSameMonth } from "date-fns";
import { fr } from "date-fns/locale";

function fmt(n: number) {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";
}

export default function Dashboard() {
  const navigate = useNavigate();
  const { needsOnboarding, isLoading: onboardingLoading, initialStep, markOnboardingComplete } = useOnboardingStatus();
  const [selectedMonth, setSelectedMonth] = useState(new Date());
  const isCurrentMonth = isSameMonth(selectedMonth, new Date());

  const navigateToCategory = useCallback((categoryId: string | null) => {
    const monthParam = format(selectedMonth, "yyyy-MM");
    const params = new URLSearchParams({ month: monthParam });
    if (categoryId) params.set("category", categoryId);
    navigate(`/transactions?${params.toString()}`);
  }, [selectedMonth, navigate]);

  // CHANGED: Using new API hooks - format date as YYYY-MM string
  const monthStr = format(selectedMonth, "yyyy-MM");
  const { data: stats, isLoading: loadingStats } = useDashboardStats(monthStr);
  const { data: catBreakdownData, isLoading: loadingCat } = useCategoryBreakdown(monthStr);
  const { data: monthlyEvolutionData, isLoading: loadingMonthly } = useMonthlyEvolution();
  const { data: accountData, isLoading: loadingAccounts } = useAccountTypeBreakdown(selectedMonth);
  
  // Adaptation des données API (snake_case) vers le format attendu par le composant
  const statsAdapted = stats ? {
    resteAVivre: stats.reste_a_vivre,
    totalExpenses: stats.total_expenses,
    totalIncome: stats.total_income,
    epargneNette: stats.epargne_nette,
    excludedTransfers: 0, // TODO: ajouter à l'API
    excludedContributions: 0, // TODO: ajouter à l'API
  } : null;
  
  const catBreakdown = catBreakdownData?.categories?.map((c: any) => ({
    id: c.name,
    name: c.name,
    amount: c.amount,
    color: c.color,
  })) || [];
  
  const monthlyData = monthlyEvolutionData ? monthlyEvolutionData.months.map((m: string, i: number) => ({
    month: m,
    revenus: monthlyEvolutionData.income[i],
    depenses: monthlyEvolutionData.expenses[i],
  })) : [];

  if (onboardingLoading) {
    return (
      <AppLayout title="Dashboard">
        <div className="space-y-4">
          <Skeleton className="h-12 w-64" />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[1,2,3,4].map(i => <Skeleton key={i} className="h-32" />)}
          </div>
        </div>
      </AppLayout>
    );
  }

  if (needsOnboarding) {
    return <Onboarding initialStep={initialStep} onComplete={() => markOnboardingComplete.mutate()} />;
  }

  const hasData = statsAdapted && (statsAdapted.totalExpenses > 0 || statsAdapted.totalIncome > 0);

  const statCards = [
    { title: "Reste à vivre", value: statsAdapted ? fmt(statsAdapted.resteAVivre) : "—", icon: Wallet, description: format(selectedMonth, "MMMM yyyy", { locale: fr }) },
    { title: "Dépenses", value: statsAdapted ? fmt(statsAdapted.totalExpenses) : "—", icon: TrendingDown, description: format(selectedMonth, "MMMM yyyy", { locale: fr }), negative: true },
    { title: "Revenus", value: statsAdapted ? fmt(statsAdapted.totalIncome) : "—", icon: TrendingUp, description: format(selectedMonth, "MMMM yyyy", { locale: fr }) },
    { title: "Épargne nette", value: statsAdapted ? fmt(statsAdapted.epargneNette) : "—", icon: PiggyBank, description: format(selectedMonth, "MMMM yyyy", { locale: fr }) },
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
              {hasData ? "Résumé de vos finances." : (
                <Link to="/import" className="underline hover:text-foreground transition-colors">
                  Importez vos premiers relevés pour commencer l'analyse.
                </Link>
              )}
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

        {/* Monthly recap widget */}
        <MonthlyRecapWidget />
        <CoupleBalanceWidget month={selectedMonth} />

        {/* Savings goals */}
        <SavingsGoalsWidget />

        {/* Budget alerts */}
        <BudgetAlerts month={selectedMonth} />

        {/* Budget forecast */}
        <BudgetForecast month={selectedMonth} />

        {/* Excluded internals indicator */}
        {statsAdapted && (statsAdapted.excludedTransfers > 0 || statsAdapted.excludedContributions > 0) && (
          <div className="flex items-center gap-2 rounded-lg border border-dashed border-muted-foreground/30 bg-muted/30 px-4 py-2.5 text-sm text-muted-foreground">
            <ArrowLeftRight className="h-4 w-4 shrink-0" />
            <span>
              <strong className="font-medium text-foreground">{fmt(statsAdapted.excludedTransfers + statsAdapted.excludedContributions)}</strong> de mouvements internes exclus du calcul
            </span>
            <Tooltip>
              <TooltipTrigger asChild>
                <Info className="h-3.5 w-3.5 shrink-0 cursor-help" />
              </TooltipTrigger>
              <TooltipContent side="bottom" className="max-w-[280px] text-xs">
                <p className="font-medium mb-1">Détail des exclusions :</p>
                {statsAdapted.excludedTransfers > 0 && <p>• Virements internes : {fmt(statsAdapted.excludedTransfers)}</p>}
                {statsAdapted.excludedContributions > 0 && <p>• Contributions partenaire : {fmt(statsAdapted.excludedContributions)}</p>}
                <p className="mt-1 text-muted-foreground">Ces montants ne sont comptés ni en revenus ni en dépenses.</p>
              </TooltipContent>
            </Tooltip>
          </div>
        )}

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
                      <Pie data={catBreakdown} dataKey="amount" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} strokeWidth={2} stroke="hsl(var(--background))" style={{ cursor: "pointer" }} onClick={(_: any, index: number) => navigateToCategory(catBreakdown[index].id)}>
                        {catBreakdown.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                      </Pie>
                      <ChartTooltip content={<ChartTooltipContent formatter={(value) => fmt(Number(value))} />} />
                    </PieChart>
                  </ChartContainer>
                  <div className="flex flex-wrap justify-center gap-2">
                    {catBreakdown.slice(0, 8).map((c) => (
                      <button key={c.name} className="flex items-center gap-1.5 text-xs hover:bg-muted rounded-md px-1.5 py-1 transition-colors" onClick={() => navigateToCategory(c.id)}>
                        <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: c.color }} />
                        <span className="text-muted-foreground">{c.name}</span>
                        <span className="font-medium">{fmt(c.amount)}</span>
                      </button>
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

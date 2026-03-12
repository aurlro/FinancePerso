import { useState } from "react";
import { Link } from "react-router-dom";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, PieChart, Pie, Cell } from "recharts";
import { ChevronLeft, ChevronRight, Scale, TrendingUp, TrendingDown, ArrowRight, AlertTriangle } from "lucide-react";
import { useCoupleBalance } from "@/hooks/useCoupleBalance";
import { BalanceHistoryChart } from "@/components/BalanceHistoryChart";
import { format, subMonths } from "date-fns";
import { fr } from "date-fns/locale";

function fmt(n: number) {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";
}

const MEMBER_COLORS = ["hsl(217, 91%, 60%)", "hsl(280, 65%, 60%)"];
const CAT_COLORS = [
  "hsl(160, 84%, 39%)", "hsl(217, 91%, 60%)", "hsl(38, 92%, 50%)",
  "hsl(280, 65%, 60%)", "hsl(0, 72%, 51%)", "hsl(190, 80%, 42%)",
];

export default function CoupleBalance() {
  const [month, setMonth] = useState(new Date());
  const { data, isLoading, isError, error } = useCoupleBalance(month);

  return (
    <AppLayout title="Équilibre du couple">
      <div className="space-y-6">
        {/* Header with month navigation */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold tracking-tight capitalize">
              Équilibre {format(month, "MMMM yyyy", { locale: fr })}
            </h2>
            <p className="text-muted-foreground">Contributions, dépenses et balance entre partenaires</p>
          </div>
          <div className="flex items-center gap-1">
            <Button variant="outline" size="icon" className="h-8 w-8" onClick={() => setMonth(m => subMonths(m, 1))}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" className="h-8 px-3 text-xs" onClick={() => setMonth(new Date())}>
              Ce mois
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
        ) : isError ? (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              <Scale className="h-10 w-10 mx-auto mb-4 opacity-50" />
              {(error as Error)?.message === "No household" ? (
                <>
                  <p className="font-medium text-foreground">Vous n'avez pas encore de foyer</p>
                  <p className="text-sm mt-1">Créez ou rejoignez un foyer dans les paramètres pour commencer à suivre vos dépenses à deux.</p>
                  <Button variant="outline" size="sm" className="mt-4" asChild>
                    <Link to="/settings">Aller aux paramètres</Link>
                  </Button>
                </>
              ) : (
                <>
                  <p className="font-medium text-foreground">Impossible de charger les données</p>
                  <p className="text-sm mt-1">Une erreur est survenue. Réessayez dans quelques instants.</p>
                </>
              )}
            </CardContent>
          </Card>
        ) : !data || data.members.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              <Scale className="h-10 w-10 mx-auto mb-4 opacity-50" />
              <p className="font-medium text-foreground">Aucun membre dans le foyer</p>
              <p className="text-sm mt-1">Ajoutez des membres dans <Link to="/settings?tab=household" className="underline font-medium text-foreground hover:text-primary transition-colors">Paramètres → Foyer</Link> pour répartir les dépenses.</p>
              <Button variant="outline" size="sm" className="mt-4" asChild>
                <Link to="/settings">Configurer le foyer</Link>
              </Button>
            </CardContent>
          </Card>
        ) : data.totalJointExpenses === 0 && data.totalJointDeposits === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              <Scale className="h-10 w-10 mx-auto mb-4 opacity-50" />
              <p className="font-medium text-foreground">Aucune transaction sur le compte joint</p>
              <p className="text-sm mt-1">Importez des relevés pour votre compte joint ou changez de mois pour voir les données.</p>
              <div className="flex items-center justify-center gap-2 mt-4">
                <Button variant="outline" size="sm" asChild>
                  <Link to="/import">Importer des transactions</Link>
                </Button>
                <Button variant="outline" size="sm" asChild>
                  <Link to="/accounts">Gérer les comptes</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Balance due card - the main highlight */}
            {data.balanceDue && (
              <Card className="border-primary/50 bg-primary/5">
                <CardContent className="py-5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Scale className="h-5 w-5 text-primary" />
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Rééquilibrage nécessaire</p>
                        <p className="text-lg font-bold">
                          {data.balanceDue.fromName} <ArrowRight className="inline h-4 w-4 mx-1" /> {data.balanceDue.toName}
                        </p>
                      </div>
                    </div>
                    <p className="text-2xl font-bold text-primary">{fmt(data.balanceDue.amount)}</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {!data.balanceDue && data.totalJointExpenses > 0 && (
              <Card className="border-primary/50 bg-primary/5">
                <CardContent className="py-5 text-center">
                  <Scale className="h-5 w-5 text-primary mx-auto mb-2" />
                  <p className="font-medium text-primary">Tout est équilibré ce mois-ci ! 🎉</p>
                </CardContent>
              </Card>
            )}

            {/* Unattributed warning */}
            {data.unattributed.count > 0 && (
              <Card className="border-warning/50 bg-warning/5">
                <CardContent className="py-3 flex items-center gap-3">
                  <AlertTriangle className="h-4 w-4 text-warning shrink-0" />
                  <p className="text-sm flex-1">
                    <span className="font-medium">{data.unattributed.count} transactions non attribuées</span> ({fmt(data.unattributed.spending + data.unattributed.deposits)}).
                    Configurez les identifiants de carte dans <Link to="/settings?tab=household" className="underline font-medium text-foreground hover:text-primary transition-colors">Paramètres → Foyer</Link>.
                  </p>
                  <Button variant="outline" size="sm" className="shrink-0 text-xs" asChild>
                    <Link to="/settings?tab=household">Configurer</Link>
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* KPI row */}
            <div className="grid gap-4 sm:grid-cols-3">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Dépenses joint totales</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{fmt(data.totalJointExpenses)}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Ratio cible : {Math.round(data.contributionRatio * 100)}/{Math.round((1 - data.contributionRatio) * 100)}
                  </p>
                </CardContent>
              </Card>
              {data.members.map((m, i) => (
                <Card key={m.userId}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                      <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: MEMBER_COLORS[i] }} />
                      {m.displayName}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Déposé</span>
                        <span className="font-medium text-primary">+{fmt(m.deposits)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Dépensé</span>
                        <span className="font-medium text-destructive">-{fmt(m.spending)}</span>
                      </div>
                      <div className="flex justify-between text-sm pt-1 border-t mt-1">
                        <span className="text-muted-foreground font-medium">Solde net</span>
                        <span className={`font-bold ${m.deposits - m.spending >= 0 ? "text-primary" : "text-destructive"}`}>
                          {m.deposits - m.spending >= 0 ? "+" : ""}{fmt(m.deposits - m.spending)}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              {/* Contributions comparison */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Qui a déposé quoi</CardTitle>
                  <CardDescription>Contributions au compte joint</CardDescription>
                </CardHeader>
                <CardContent>
                  {data.totalJointDeposits === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-8">Aucun dépôt ce mois</p>
                  ) : (
                    <div className="space-y-3">
                      {data.members.map((m, i) => {
                        const pct = data.totalJointDeposits > 0 ? (m.deposits / data.totalJointDeposits) * 100 : 0;
                        return (
                          <div key={m.userId} className="space-y-1.5">
                            <div className="flex items-center justify-between text-sm">
                              <div className="flex items-center gap-2">
                                <div className="h-3 w-3 rounded-full" style={{ backgroundColor: MEMBER_COLORS[i] }} />
                                <span className="font-medium">{m.displayName}</span>
                              </div>
                              <span className="font-mono text-xs">{fmt(m.deposits)} ({pct.toFixed(0)}%)</span>
                            </div>
                            <Progress value={pct} className="h-2" style={{ ["--progress-color" as any]: MEMBER_COLORS[i] }} />
                          </div>
                        );
                      })}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Spending comparison */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Qui a dépensé quoi</CardTitle>
                  <CardDescription>Dépenses sur le compte joint</CardDescription>
                </CardHeader>
                <CardContent>
                  {data.totalJointExpenses === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-8">Aucune dépense ce mois</p>
                  ) : (
                    <ChartContainer
                      config={Object.fromEntries(data.members.map((m, i) => [m.displayName, { label: m.displayName, color: MEMBER_COLORS[i] }]))}
                      className="h-[200px] w-full"
                    >
                      <BarChart data={data.members.map(m => ({ name: m.displayName, amount: m.spending }))}>
                        <CartesianGrid strokeDasharray="3 3" className="stroke-border/50" />
                        <XAxis dataKey="name" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
                        <YAxis tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} tickFormatter={v => `${(v / 1000).toFixed(0)}k`} />
                        <ChartTooltip content={<ChartTooltipContent formatter={(v) => fmt(Number(v))} />} />
                        <Bar dataKey="amount" radius={[4, 4, 0, 0]}>
                          {data.members.map((_, i) => <Cell key={i} fill={MEMBER_COLORS[i]} />)}
                        </Bar>
                      </BarChart>
                    </ChartContainer>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Category breakdown per member */}
            <div className="grid gap-4 lg:grid-cols-2">
              {data.members.map((m, mi) => (
                <Card key={m.userId}>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full" style={{ backgroundColor: MEMBER_COLORS[mi] }} />
                      Top catégories — {m.displayName}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {m.categoryBreakdown.length === 0 ? (
                      <p className="text-sm text-muted-foreground text-center py-6">Aucune dépense attribuée</p>
                    ) : (
                      <div className="space-y-2">
                        {m.categoryBreakdown.slice(0, 6).map((cat, ci) => {
                          const pct = m.spending > 0 ? (cat.amount / m.spending) * 100 : 0;
                          return (
                            <div key={cat.name} className="flex items-center justify-between text-sm">
                              <div className="flex items-center gap-2 min-w-0">
                                <div className="h-2.5 w-2.5 rounded-full shrink-0" style={{ backgroundColor: cat.color }} />
                                <span className="truncate text-muted-foreground">{cat.name}</span>
                              </div>
                              <div className="flex items-center gap-2 shrink-0">
                                <span className="font-medium">{fmt(cat.amount)}</span>
                                <Badge variant="outline" className="text-[10px] px-1.5">{pct.toFixed(0)}%</Badge>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Balance history chart */}
            <BalanceHistoryChart />

            {/* Ratio comparison */}
            {data.members.length === 2 && data.totalJointExpenses > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Ratio réel vs cible</CardTitle>
                  <CardDescription>
                    Répartition effective des dépenses comparée au ratio configuré ({Math.round(data.contributionRatio * 100)}/{Math.round((1 - data.contributionRatio) * 100)})
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {data.members.map((m, i) => {
                      const actualPct = (m.spending / data.totalJointExpenses) * 100;
                      const targetPct = i === 0 ? data.contributionRatio * 100 : (1 - data.contributionRatio) * 100;
                      const diff = actualPct - targetPct;
                      return (
                        <div key={m.userId} className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                              <div className="h-3 w-3 rounded-full" style={{ backgroundColor: MEMBER_COLORS[i] }} />
                              <span className="font-medium">{m.displayName}</span>
                            </div>
                            <div className="flex items-center gap-3 text-xs">
                              <span className="text-muted-foreground">Cible : {targetPct.toFixed(0)}%</span>
                              <span className="font-medium">Réel : {actualPct.toFixed(0)}%</span>
                              <span className={`font-bold ${Math.abs(diff) < 3 ? "text-primary" : "text-destructive"}`}>
                                {diff > 0 ? "+" : ""}{diff.toFixed(1)}%
                              </span>
                            </div>
                          </div>
                          <div className="relative h-3 rounded-full bg-muted overflow-hidden">
                            <div
                              className="absolute h-full rounded-full transition-all"
                              style={{ width: `${Math.min(actualPct, 100)}%`, backgroundColor: MEMBER_COLORS[i] }}
                            />
                            <div
                              className="absolute h-full w-0.5 bg-foreground/60"
                              style={{ left: `${targetPct}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>
    </AppLayout>
  );
}

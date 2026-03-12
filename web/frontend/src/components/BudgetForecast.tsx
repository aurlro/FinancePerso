import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useForecast } from "@/hooks/useForecast";
import { Skeleton } from "@/components/ui/skeleton";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function fmt(n: number) {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + " €";
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border bg-background px-3 py-2 text-xs shadow-xl">
      <p className="font-medium mb-1">{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.dataKey} className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full" style={{ backgroundColor: entry.color }} />
          <span className="text-muted-foreground">{entry.name}</span>
          <span className="font-medium ml-auto">{fmt(entry.value)}</span>
        </div>
      ))}
    </div>
  );
};

export function BudgetForecast({ month }: { month?: Date }) {
  const { data, isLoading } = useForecast(month);

  if (isLoading) return <Skeleton className="h-[300px] w-full" />;
  if (!data || data.categories.length === 0) return null;

  const withBudget = data.categories.filter(c => c.budget !== null && c.budget > 0);
  if (withBudget.length === 0) return null;

  const chartData = withBudget.slice(0, 6).map(c => ({
    name: c.name.length > 12 ? c.name.slice(0, 11) + "…" : c.name,
    Réel: Math.round(c.spentThisMonth),
    Projeté: Math.round(c.projected),
    Budget: Math.round(c.budget!),
  }));

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center justify-between">
          <span>Prévisions de fin de mois</span>
          <span className="text-xs font-normal text-muted-foreground">
            Jour {data.dayOfMonth}/{data.daysInMonth}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
              <XAxis
                dataKey="name"
                tick={{ fontSize: 11 }}
                tickLine={false}
                axisLine={false}
                className="fill-muted-foreground"
              />
              <YAxis
                tick={{ fontSize: 11 }}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => `${v} €`}
                width={65}
                className="fill-muted-foreground"
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: "hsl(var(--muted))", opacity: 0.5 }} />
              <Legend
                iconType="circle"
                iconSize={8}
                wrapperStyle={{ fontSize: 12, paddingTop: 8 }}
              />
              <Bar dataKey="Réel" fill="hsl(var(--primary))" radius={[3, 3, 0, 0]} />
              <Bar dataKey="Projeté" fill="hsl(var(--primary) / 0.35)" radius={[3, 3, 0, 0]} />
              <Bar dataKey="Budget" fill="hsl(var(--muted-foreground) / 0.3)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Dépassements */}
        {withBudget.slice(0, 6).filter(c => c.projected > c.budget!).length > 0 && (
          <div className="space-y-1">
            {withBudget.slice(0, 6).filter(c => c.projected > c.budget!).map(c => (
              <p key={c.categoryId || "uncat"} className="text-xs text-destructive">
                ⚠ {c.name} : dépassement estimé de {fmt(c.projected - c.budget!)}
              </p>
            ))}
          </div>
        )}

        {/* Summary */}
        {data.totalBudget > 0 && (
          <div className="pt-2 border-t flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Total projeté</span>
            <div className="flex items-center gap-2">
              <span className="font-semibold">{fmt(data.totalProjected)}</span>
              <span className="text-muted-foreground">/ {fmt(data.totalBudget)}</span>
              {data.totalProjected > data.totalBudget ? (
                <Badge variant="destructive" className="text-[10px] px-1.5 py-0">Dépassement</Badge>
              ) : (
                <Badge variant="secondary" className="text-[10px] px-1.5 py-0">OK</Badge>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

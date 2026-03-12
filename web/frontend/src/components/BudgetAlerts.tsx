import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { AlertTriangle, Info, AlertOctagon } from "lucide-react";
import { useBudgets } from "@/hooks/useBudgets";
import { useCategoryBreakdown } from "@/hooks/useDashboard";
import { useCategories } from "@/hooks/useCategories";
import { useForecast } from "@/hooks/useForecast";

function fmt(n: number) {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + " €";
}

type AlertLevel = "info" | "warning" | "danger";

function getLevel(pct: number): AlertLevel {
  if (pct >= 100) return "danger";
  if (pct >= 80) return "warning";
  return "info";
}

function getIcon(level: AlertLevel) {
  if (level === "danger") return <AlertOctagon className="h-4 w-4" />;
  if (level === "warning") return <AlertTriangle className="h-4 w-4" />;
  return <Info className="h-4 w-4" />;
}

function getVariant(level: AlertLevel): "destructive" | "default" {
  return level === "danger" ? "destructive" : "default";
}

export function BudgetAlerts({ month }: { month?: Date }) {
  const { data: budgets } = useBudgets();
  const { data: breakdown } = useCategoryBreakdown(month);
  const { data: categories } = useCategories();
  const { data: forecast } = useForecast(month);

  if (!budgets?.length || !breakdown?.length) return null;

  const spentMap = new Map(breakdown.map(b => [b.name, b.amount]));
  const forecastMap = new Map(
    forecast?.categories.map(f => [f.categoryId, f.projected]) || []
  );

  const alerts = budgets
    .map(b => {
      const cat = categories?.find(c => c.id === b.category_id);
      if (!cat) return null;
      const spent = spentMap.get(cat.name) || 0;
      const pct = b.monthly_amount > 0 ? (spent / b.monthly_amount) * 100 : 0;
      const projected = forecastMap.get(b.category_id) || 0;
      const projectedPct = b.monthly_amount > 0 ? (projected / b.monthly_amount) * 100 : 0;
      return { cat, budget: b.monthly_amount, spent, pct, projected, projectedPct };
    })
    .filter(Boolean)
    .filter(a => a!.pct >= 60)
    .sort((a, b) => b!.pct - a!.pct) as {
      cat: { name: string; color: string | null };
      budget: number;
      spent: number;
      pct: number;
      projected: number;
      projectedPct: number;
    }[];

  if (!alerts.length) return null;

  return (
    <div className="space-y-2">
      {alerts.map(a => {
        const level = getLevel(a.pct);
        return (
          <Alert key={a.cat.name} variant={getVariant(level)} className="py-3">
            {getIcon(level)}
            <AlertTitle className="text-sm flex items-center gap-2">
              <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: a.cat.color || "hsl(var(--muted-foreground))" }} />
              {a.cat.name}
              <span className="ml-auto font-mono text-xs">
                {fmt(a.spent)} / {fmt(a.budget)}
              </span>
            </AlertTitle>
            <AlertDescription className="mt-1.5">
              <Progress value={Math.min(a.pct, 100)} className="h-2" />
              <span className="text-xs mt-1 block">
                {level === "danger"
                  ? `Dépassement de ${fmt(a.spent - a.budget)} (${Math.round(a.pct)}%)`
                  : level === "warning"
                  ? `${Math.round(a.pct)}% du budget utilisé`
                  : `Vous avez déjà utilisé ${Math.round(a.pct)}% de votre budget`}
                {a.projectedPct > 100 && level !== "danger" && (
                  <> — projection fin de mois : <strong className="text-destructive">{fmt(a.projected)}</strong></>
                )}
              </span>
            </AlertDescription>
          </Alert>
        );
      })}
    </div>
  );
}

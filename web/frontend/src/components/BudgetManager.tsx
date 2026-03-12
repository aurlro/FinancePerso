import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Trash2, Plus } from "lucide-react";
import { useCategories } from "@/hooks/useCategories";
import { useBudgets, useUpsertBudget, useDeleteBudget } from "@/hooks/useBudgets";
import { useHousehold } from "@/hooks/useHousehold";

function fmt(n: number) {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + " €";
}

export function BudgetManager() {
  const { data: categories, isLoading: loadingCats } = useCategories();
  const { data: budgets, isLoading: loadingBudgets } = useBudgets();
  const { data: profile } = useHousehold();
  const upsertBudget = useUpsertBudget();
  const deleteBudget = useDeleteBudget();

  const [selectedCat, setSelectedCat] = useState("");
  const [amount, setAmount] = useState("");

  const household = profile?.households as any;

  if (loadingCats || loadingBudgets) return <Skeleton className="h-40 w-full" />;

  const budgetMap = new Map(budgets?.map(b => [b.category_id, b]) || []);
  const catsWithBudget = categories?.filter(c => budgetMap.has(c.id)) || [];
  const catsWithoutBudget = categories?.filter(c => !budgetMap.has(c.id)) || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Budgets mensuels par catégorie</CardTitle>
        <CardDescription>Définissez un plafond mensuel par catégorie pour recevoir des alertes de dépassement.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Add budget */}
        <div className="flex gap-2">
          <Select value={selectedCat} onValueChange={setSelectedCat}>
            <SelectTrigger className="flex-1">
              <SelectValue placeholder="Catégorie" />
            </SelectTrigger>
            <SelectContent>
              {catsWithoutBudget.map(c => (
                <SelectItem key={c.id} value={c.id}>
                  <div className="flex items-center gap-2">
                    <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: c.color || "#6b7280" }} />
                    {c.name}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Input
            type="number"
            value={amount}
            onChange={e => setAmount(e.target.value)}
            placeholder="Montant €"
            className="w-28"
          />
          <Button
            onClick={() => {
              if (household && selectedCat && amount) {
                upsertBudget.mutate({ householdId: household.id, categoryId: selectedCat, amount: Number(amount) });
                setSelectedCat("");
                setAmount("");
              }
            }}
            disabled={!selectedCat || !amount || upsertBudget.isPending}
          >
            <Plus className="h-4 w-4 mr-1" /> Ajouter
          </Button>
        </div>

        {/* Existing budgets */}
        {catsWithBudget.length > 0 && (
          <div className="space-y-2">
            {catsWithBudget.map(cat => {
              const budget = budgetMap.get(cat.id)!;
              return (
                <div key={cat.id} className="flex items-center justify-between p-3 rounded-lg border">
                  <div className="flex items-center gap-3">
                    <div className="h-4 w-4 rounded-full" style={{ backgroundColor: cat.color || "#6b7280" }} />
                    <span className="text-sm font-medium">{cat.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      defaultValue={budget.monthly_amount}
                      className="w-24 h-8 text-sm"
                      onBlur={e => {
                        const val = Number(e.target.value);
                        if (val !== budget.monthly_amount && val > 0) {
                          upsertBudget.mutate({ householdId: household.id, categoryId: cat.id, amount: val });
                        }
                      }}
                    />
                    <span className="text-xs text-muted-foreground">€/mois</span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 text-destructive"
                      onClick={() => deleteBudget.mutate(budget.id)}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

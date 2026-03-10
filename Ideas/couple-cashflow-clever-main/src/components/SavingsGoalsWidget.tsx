import { useState } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Target, Plus, Trash2, CheckCircle2 } from "lucide-react";
import { useSavingsGoals, useAddSavingsGoal, useUpdateSavingsGoal, useDeleteSavingsGoal } from "@/hooks/useSavingsGoals";
import { useHousehold } from "@/hooks/useHousehold";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

function fmt(n: number) {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + " €";
}

export function SavingsGoalsWidget() {
  const { data: profile } = useHousehold();
  const { data: goals, isLoading } = useSavingsGoals();
  const addGoal = useAddSavingsGoal();
  const updateGoal = useUpdateSavingsGoal();
  const deleteGoal = useDeleteSavingsGoal();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [target, setTarget] = useState("");
  const [deadline, setDeadline] = useState("");
  const [addAmountId, setAddAmountId] = useState<string | null>(null);
  const [addAmount, setAddAmount] = useState("");

  const householdId = profile?.household_id;
  const activeGoals = goals?.filter(g => !g.is_completed) || [];

  const handleCreate = () => {
    if (!householdId || !name || !target) return;
    addGoal.mutate({
      householdId,
      name,
      targetAmount: parseFloat(target),
      deadline: deadline || undefined,
    }, {
      onSuccess: () => { setOpen(false); setName(""); setTarget(""); setDeadline(""); },
    });
  };

  const handleAddAmount = (goalId: string, currentAmount: number) => {
    const amount = parseFloat(addAmount);
    if (isNaN(amount) || amount <= 0) return;
    updateGoal.mutate({ id: goalId, current_amount: currentAmount + amount }, {
      onSuccess: () => { setAddAmountId(null); setAddAmount(""); toast.success(`+${fmt(amount)} ajouté`); },
    });
  };

  if (isLoading) return <Skeleton className="h-32 w-full" />;
  if (!goals?.length && !householdId) return null;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-base flex items-center gap-2">
          <Target className="h-4 w-4" />
          Objectifs d'épargne
        </CardTitle>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm" className="gap-1 text-xs">
              <Plus className="h-3.5 w-3.5" /> Ajouter
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Nouvel objectif d'épargne</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <div>
                <Label>Nom</Label>
                <Input placeholder="Ex: Vacances été" value={name} onChange={e => setName(e.target.value)} />
              </div>
              <div>
                <Label>Montant cible (€)</Label>
                <Input type="number" placeholder="5000" value={target} onChange={e => setTarget(e.target.value)} />
              </div>
              <div>
                <Label>Date limite (optionnel)</Label>
                <Input type="date" value={deadline} onChange={e => setDeadline(e.target.value)} />
              </div>
              <Button onClick={handleCreate} disabled={!name || !target || addGoal.isPending} className="w-full">
                Créer l'objectif
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </CardHeader>
      <CardContent>
        {!activeGoals.length ? (
          <div className="text-center py-4 space-y-2">
            <p className="text-sm text-muted-foreground">
              Aucun objectif en cours. Créez-en un pour suivre votre épargne !
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {activeGoals.map(g => {
              const pct = g.target_amount > 0 ? Math.min((g.current_amount / g.target_amount) * 100, 100) : 0;
              return (
                <div key={g.id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{g.name}</span>
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-muted-foreground">{fmt(g.current_amount)} / {fmt(g.target_amount)}</span>
                      {pct >= 100 && (
                        <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => updateGoal.mutate({ id: g.id, is_completed: true })}>
                          <CheckCircle2 className="h-4 w-4 text-primary" />
                        </Button>
                      )}
                      <Button variant="ghost" size="icon" className="h-6 w-6 text-destructive" onClick={() => deleteGoal.mutate(g.id)}>
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                  <Progress value={pct} className="h-2" />
                  <div className="flex items-center gap-2">
                    {addAmountId === g.id ? (
                      <>
                        <Input
                          type="number"
                          placeholder="Montant"
                          className="h-7 text-xs w-24"
                          value={addAmount}
                          onChange={e => setAddAmount(e.target.value)}
                          onKeyDown={e => e.key === "Enter" && handleAddAmount(g.id, g.current_amount)}
                        />
                        <Button size="sm" className="h-7 text-xs" onClick={() => handleAddAmount(g.id, g.current_amount)}>OK</Button>
                        <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={() => setAddAmountId(null)}>Annuler</Button>
                      </>
                    ) : (
                      <Button variant="outline" size="sm" className="h-7 text-xs gap-1" onClick={() => setAddAmountId(g.id)}>
                        <Plus className="h-3 w-3" /> Ajouter
                      </Button>
                    )}
                    {g.deadline && (
                      <span className="text-[10px] text-muted-foreground ml-auto">
                        Échéance : {new Date(g.deadline).toLocaleDateString("fr-FR")}
                      </span>
                    )}
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

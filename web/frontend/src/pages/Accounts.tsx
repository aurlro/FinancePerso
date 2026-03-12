import { useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { useAccounts, useCreateAccount, useDeleteAccount, useUpdateAccount, useHouseholdId } from "@/hooks/useAccounts";
import { Landmark, Plus, Trash2, Pencil, TrendingUp, TrendingDown, ArrowLeftRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

const ACCOUNT_TYPE_LABELS: Record<string, string> = {
  perso_a: "Personnel A",
  perso_b: "Personnel B",
  joint: "Joint",
};

const ACCOUNT_TYPE_COLORS: Record<string, string> = {
  perso_a: "bg-blue-500/10 text-blue-600 dark:text-blue-400",
  perso_b: "bg-purple-500/10 text-purple-600 dark:text-purple-400",
  joint: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
};

function fmt(n: number) {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";
}

function useAccountSummaries() {
  return useQuery({
    queryKey: ["account-summaries"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("transactions")
        .select("bank_account_id, amount, is_internal_transfer, categories(exclude_from_income)");
      if (error) throw error;

      const map = new Map<string, { income: number; expenses: number; transfers: number; count: number }>();
      for (const t of data || []) {
        const entry = map.get(t.bank_account_id) || { income: 0, expenses: 0, transfers: 0, count: 0 };
        entry.count++;
        if (t.is_internal_transfer) {
          entry.transfers += Math.abs(t.amount);
        } else if ((t.categories as any)?.exclude_from_income) {
          // excluded
        } else if (t.amount > 0) {
          entry.income += t.amount;
        } else {
          entry.expenses += Math.abs(t.amount);
        }
        map.set(t.bank_account_id, entry);
      }
      return map;
    },
  });
}

export default function Accounts() {
  const { data: accounts, isLoading } = useAccounts();
  const { data: householdId } = useHouseholdId();
  const { data: summaries } = useAccountSummaries();
  const createAccount = useCreateAccount();
  const updateAccount = useUpdateAccount();
  const deleteAccount = useDeleteAccount();

  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [bankName, setBankName] = useState("");
  const [accountType, setAccountType] = useState<"perso_a" | "perso_b" | "joint">("joint");

  // Edit state
  const [editId, setEditId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const [editBank, setEditBank] = useState("");
  const [editType, setEditType] = useState<"perso_a" | "perso_b" | "joint">("joint");

  const handleCreate = () => {
    if (!name.trim() || !householdId) return;
    createAccount.mutate(
      { name: name.trim(), bank_name: bankName.trim() || null, account_type: accountType, household_id: householdId },
      { onSuccess: () => { setOpen(false); setName(""); setBankName(""); setAccountType("joint"); } }
    );
  };

  const startEdit = (acc: any) => {
    setEditId(acc.id);
    setEditName(acc.name);
    setEditBank(acc.bank_name || "");
    setEditType(acc.account_type);
  };

  const saveEdit = () => {
    if (!editId || !editName.trim()) return;
    updateAccount.mutate(
      { id: editId, name: editName.trim(), bank_name: editBank.trim() || null, account_type: editType },
      { onSuccess: () => setEditId(null) }
    );
  };

  return (
    <AppLayout title="Comptes bancaires">
      <div className="flex justify-end mb-4">
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="h-4 w-4 mr-2" />Ajouter un compte</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Nouveau compte</DialogTitle></DialogHeader>
            <div className="space-y-4 mt-2">
              <div className="space-y-2">
                <Label>Nom du compte</Label>
                <Input placeholder="Compte courant" value={name} onChange={e => setName(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>Banque (optionnel)</Label>
                <Input placeholder="Crédit Agricole" value={bankName} onChange={e => setBankName(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>Type de compte</Label>
                <Select value={accountType} onValueChange={(v: "perso_a" | "perso_b" | "joint") => setAccountType(v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="perso_a">Personnel A</SelectItem>
                    <SelectItem value="perso_b">Personnel B</SelectItem>
                    <SelectItem value="joint">Joint</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button className="w-full" onClick={handleCreate} disabled={createAccount.isPending || !name.trim()}>
                {createAccount.isPending ? "Création…" : "Créer le compte"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-28 w-full rounded-lg" />)}
        </div>
      ) : !accounts?.length ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Landmark className="h-10 w-10 text-muted-foreground/50 mb-4" />
            <h3 className="text-lg font-medium">Aucun compte</h3>
            <p className="text-sm text-muted-foreground mt-1">Ajoutez vos comptes bancaires pour commencer.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {accounts.map(acc => {
            const summary = summaries?.get(acc.id);
            const isEditing = editId === acc.id;

            return (
              <Card key={acc.id} className="group">
                <CardContent className="py-4 px-5">
                  {isEditing ? (
                    <div className="space-y-3">
                      <div className="grid gap-3 sm:grid-cols-3">
                        <div className="space-y-1">
                          <Label className="text-xs">Nom</Label>
                          <Input value={editName} onChange={e => setEditName(e.target.value)} className="h-9" />
                        </div>
                        <div className="space-y-1">
                          <Label className="text-xs">Banque</Label>
                          <Input value={editBank} onChange={e => setEditBank(e.target.value)} className="h-9" placeholder="Optionnel" />
                        </div>
                        <div className="space-y-1">
                          <Label className="text-xs">Type</Label>
                          <Select value={editType} onValueChange={(v: "perso_a" | "perso_b" | "joint") => setEditType(v)}>
                            <SelectTrigger className="h-9"><SelectValue /></SelectTrigger>
                            <SelectContent>
                              <SelectItem value="perso_a">Personnel A</SelectItem>
                              <SelectItem value="perso_b">Personnel B</SelectItem>
                              <SelectItem value="joint">Joint</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div className="flex gap-2 justify-end">
                        <Button variant="outline" size="sm" onClick={() => setEditId(null)}>Annuler</Button>
                        <Button size="sm" onClick={saveEdit} disabled={updateAccount.isPending}>Enregistrer</Button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Landmark className="h-5 w-5 text-muted-foreground" />
                          <div>
                            <p className="font-medium">{acc.name}</p>
                            {acc.bank_name && <p className="text-xs text-muted-foreground">{acc.bank_name}</p>}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary" className={ACCOUNT_TYPE_COLORS[acc.account_type]}>
                            {ACCOUNT_TYPE_LABELS[acc.account_type]}
                          </Badge>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={() => startEdit(acc)}
                          >
                            <Pencil className="h-3.5 w-3.5" />
                          </Button>
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
                              >
                                <Trash2 className="h-3.5 w-3.5 text-destructive" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Supprimer ce compte ?</AlertDialogTitle>
                                <AlertDialogDescription>
                                  Cette action supprimera le compte « {acc.name} » et toutes ses transactions associées. Cette action est irréversible.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Annuler</AlertDialogCancel>
                                <AlertDialogAction
                                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                  onClick={() => deleteAccount.mutate(acc.id)}
                                >
                                  Supprimer
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </div>

                      {/* Account summary stats */}
                      {summary && summary.count > 0 && (
                        <div className="mt-3 pt-3 border-t flex flex-wrap gap-x-6 gap-y-1">
                          <div className="flex items-center gap-1.5 text-xs">
                            <TrendingUp className="h-3.5 w-3.5 text-primary" />
                            <span className="text-muted-foreground">Revenus</span>
                            <span className="font-medium text-primary">{fmt(summary.income)}</span>
                          </div>
                          <div className="flex items-center gap-1.5 text-xs">
                            <TrendingDown className="h-3.5 w-3.5 text-destructive" />
                            <span className="text-muted-foreground">Dépenses</span>
                            <span className="font-medium text-destructive">{fmt(summary.expenses)}</span>
                          </div>
                          {summary.transfers > 0 && (
                            <div className="flex items-center gap-1.5 text-xs">
                              <ArrowLeftRight className="h-3.5 w-3.5 text-muted-foreground" />
                              <span className="text-muted-foreground">Virements</span>
                              <span className="font-medium">{fmt(summary.transfers)}</span>
                            </div>
                          )}
                          <div className="flex items-center gap-1.5 text-xs">
                            <span className="text-muted-foreground">{summary.count} transactions</span>
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </AppLayout>
  );
}

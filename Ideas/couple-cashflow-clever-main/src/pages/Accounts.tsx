import { useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useAccounts, useCreateAccount, useDeleteAccount, useHouseholdId } from "@/hooks/useAccounts";
import { Landmark, Plus, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

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

export default function Accounts() {
  const { data: accounts, isLoading } = useAccounts();
  const { data: householdId } = useHouseholdId();
  const createAccount = useCreateAccount();
  const deleteAccount = useDeleteAccount();

  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [bankName, setBankName] = useState("");
  const [accountType, setAccountType] = useState<"perso_a" | "perso_b" | "joint">("joint");

  const handleCreate = () => {
    if (!name.trim() || !householdId) return;
    createAccount.mutate(
      { name: name.trim(), bank_name: bankName.trim() || null, account_type: accountType, household_id: householdId },
      { onSuccess: () => { setOpen(false); setName(""); setBankName(""); setAccountType("joint"); } }
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
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-20 w-full rounded-lg" />)}
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
        <div className="grid gap-3">
          {accounts.map(acc => (
            <Card key={acc.id} className="group">
              <CardContent className="flex items-center justify-between py-4 px-5">
                <div className="flex items-center gap-3">
                  <Landmark className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">{acc.name}</p>
                    {acc.bank_name && <p className="text-xs text-muted-foreground">{acc.bank_name}</p>}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant="secondary" className={ACCOUNT_TYPE_COLORS[acc.account_type]}>
                    {ACCOUNT_TYPE_LABELS[acc.account_type]}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => deleteAccount.mutate(acc.id)}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </AppLayout>
  );
}

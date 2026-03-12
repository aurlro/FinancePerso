import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import {
  User, Home, Tag, Send, Trash2, Check, X, Plus, Pencil,
  Users, Clock, Mail, Wallet, ShieldOff, Database, AlertTriangle,
} from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { useAuth } from "@/hooks/useAuth";
import {
  useHousehold, useHouseholdMembers, useUpdateProfile, useUpdateHousehold,
  useInvitations, useSendInvitation, useDeleteInvitation, useAcceptInvitation,
  useAddGhostMember, useUpdateGhostMember, useDeleteGhostMember, useToggleMemberActive,
} from "@/hooks/useHousehold";
import { useCategories } from "@/hooks/useCategories";
import { useCreateCategory, useUpdateCategory, useDeleteCategory } from "@/hooks/useCategoryManagement";
import { BudgetManager } from "@/components/BudgetManager";
import { format, startOfMonth, endOfMonth, subMonths } from "date-fns";
import { fr } from "date-fns/locale";

const COLORS = [
  "#ef4444", "#f97316", "#eab308", "#22c55e", "#06b6d4",
  "#3b82f6", "#8b5cf6", "#ec4899", "#6b7280", "#14b8a6",
];

export default function SettingsPage() {
  const [searchParams] = useSearchParams();
  const defaultTab = searchParams.get("tab") || "profile";

  return (
    <AppLayout title="Paramètres">
      <Tabs defaultValue={defaultTab} className="space-y-6">
        <TabsList className="flex-wrap">
          <TabsTrigger value="profile"><User className="h-4 w-4 mr-1.5" />Profil</TabsTrigger>
          <TabsTrigger value="household"><Home className="h-4 w-4 mr-1.5" />Foyer</TabsTrigger>
          <TabsTrigger value="categories"><Tag className="h-4 w-4 mr-1.5" />Catégories</TabsTrigger>
          <TabsTrigger value="budgets"><Wallet className="h-4 w-4 mr-1.5" />Budgets</TabsTrigger>
          <TabsTrigger value="data"><Database className="h-4 w-4 mr-1.5" />Données</TabsTrigger>
        </TabsList>

        <TabsContent value="profile"><ProfileTab /></TabsContent>
        <TabsContent value="household"><HouseholdTab /></TabsContent>
        <TabsContent value="categories"><CategoriesTab /></TabsContent>
        <TabsContent value="budgets"><BudgetManager /></TabsContent>
        <TabsContent value="data"><DataTab /></TabsContent>
      </Tabs>
    </AppLayout>
  );
}

/* ─── Profile ───────────────────────────────────────── */
function ProfileTab() {
  const { user } = useAuth();
  const { data: profile, isLoading } = useHousehold();
  const updateProfile = useUpdateProfile();
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [cardId, setCardId] = useState("");
  const [initialized, setInitialized] = useState(false);

  if (isLoading) return <Skeleton className="h-40 w-full" />;

  if (profile && !initialized) {
    setName(profile.display_name || "");
    setCardId((profile as any).card_identifier || "");
    setInitialized(true);
  }

  const saveCardId = async () => {
    const { error } = await supabase
      .from("profiles")
      .update({ card_identifier: cardId.trim() || null } as any)
      .eq("id", user!.id);
    if (error) {
      toast.error("Erreur lors de la sauvegarde");
    } else {
      toast.success("Identifiant de carte mis à jour");
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Mon profil</CardTitle>
          <CardDescription>{user?.email}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="displayName">Nom d'affichage</Label>
            <div className="flex gap-2">
              <Input id="displayName" value={name} onChange={(e) => setName(e.target.value.slice(0, 50))} placeholder="Votre prénom" maxLength={50} />
              <Button onClick={() => updateProfile.mutate({ displayName: name.trim().slice(0, 50) })} disabled={updateProfile.isPending || !name.trim()}>Enregistrer</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><Wallet className="h-4 w-4" /> Identifiant de carte</CardTitle>
          <CardDescription>Motif présent dans vos libellés bancaires pour vous identifier sur le compte joint.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input value={cardId} onChange={(e) => setCardId(e.target.value.slice(0, 50))} placeholder="Ex: CB *4521 ou DUPONT" maxLength={50} />
            <Button onClick={saveCardId}>Enregistrer</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/* ─── Household ─────────────────────────────────────── */
function HouseholdTab() {
  const { data: profile, isLoading } = useHousehold();
  const { data: members } = useHouseholdMembers();
  const { data: invitations } = useInvitations();
  const updateHousehold = useUpdateHousehold();
  const sendInvitation = useSendInvitation();
  const deleteInvitation = useDeleteInvitation();
  const acceptInvitation = useAcceptInvitation();
  const addGhost = useAddGhostMember();
  const updateGhost = useUpdateGhostMember();
  const deleteGhost = useDeleteGhostMember();
  const toggleActive = useToggleMemberActive();
  const queryClient = useQueryClient();
  const { user } = useAuth();

  const [householdName, setHouseholdName] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [ratio, setRatio] = useState("50");
  const [currency, setCurrency] = useState("EUR");
  const [initialized, setInitialized] = useState(false);
  const [ghostName, setGhostName] = useState("");
  const [ghostCard, setGhostCard] = useState("");
  const [editingMemberId, setEditingMemberId] = useState<string | null>(null);
  const [editMemberName, setEditMemberName] = useState("");
  const [editMemberCard, setEditMemberCard] = useState("");

  if (isLoading) return <Skeleton className="h-60 w-full" />;

  const household = profile?.households as any;
  if (household && !initialized) {
    setHouseholdName(household.name || "");
    setRatio(household.contribution_ratio != null ? String(Math.round(household.contribution_ratio * 100)) : "50");
    setCurrency(household.currency || "EUR");
    setInitialized(true);
  }

  const sortedMembers = [...(members || [])].sort((a: any, b: any) => {
    if (a.is_active !== b.is_active) return a.is_active ? -1 : 1;
    return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
  });

  const saveRatio = async () => {
    if (!household) return;
    const val = Math.max(0, Math.min(100, Number(ratio))) / 100;
    const { error } = await supabase.from("households").update({ contribution_ratio: val } as any).eq("id", household.id);
    if (error) toast.error("Erreur lors de la sauvegarde");
    else { toast.success("Ratio de contribution mis à jour"); queryClient.invalidateQueries({ queryKey: ["profile"] }); }
  };

  const saveCurrency = async (val: string) => {
    setCurrency(val);
    if (!household) return;
    const { error } = await supabase.from("households").update({ currency: val } as any).eq("id", household.id);
    if (error) toast.error("Erreur lors de la sauvegarde");
    else { toast.success("Devise mise à jour"); queryClient.invalidateQueries({ queryKey: ["profile"] }); }
  };

  const myPendingInvites = invitations?.filter((i: any) => i.invited_email === user?.email && i.status === "pending") || [];
  const sentInvites = invitations?.filter((i: any) => i.household_id === household?.id) || [];

  return (
    <div className="space-y-6">
      {myPendingInvites.length > 0 && (
        <Card className="border-primary">
          <CardHeader><CardTitle className="text-base flex items-center gap-2"><Mail className="h-4 w-4" /> Invitations reçues</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {myPendingInvites.map((inv: any) => (
              <div key={inv.id} className="flex items-center justify-between p-3 rounded-lg border bg-muted/50">
                <span className="text-sm">Vous avez été invité(e) à rejoindre un foyer</span>
                <Button size="sm" onClick={() => acceptInvitation.mutate(inv.id)}><Check className="h-3.5 w-3.5 mr-1" /> Accepter</Button>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle className="text-base">Nom du foyer</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input value={householdName} onChange={(e) => setHouseholdName(e.target.value)} placeholder="Nom du foyer" />
            <Button onClick={() => household && updateHousehold.mutate({ householdId: household.id, name: householdName })} disabled={updateHousehold.isPending}>Enregistrer</Button>
          </div>
        </CardContent>
      </Card>

      {/* Currency */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Devise</CardTitle>
          <CardDescription>Devise utilisée pour l'affichage des montants</CardDescription>
        </CardHeader>
        <CardContent>
          <Select value={currency} onValueChange={saveCurrency}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="EUR">€ Euro (EUR)</SelectItem>
              <SelectItem value="USD">$ Dollar (USD)</SelectItem>
              <SelectItem value="GBP">£ Livre (GBP)</SelectItem>
              <SelectItem value="CHF">CHF Franc suisse</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Contribution ratio */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><Wallet className="h-4 w-4" /> Ratio de contribution</CardTitle>
          <CardDescription>Part des dépenses communes attribuée au premier membre (en %).</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 items-center">
            <Input type="number" min="0" max="100" value={ratio} onChange={(e) => setRatio(e.target.value)} className="w-24" />
            <span className="text-sm text-muted-foreground">% / {100 - Number(ratio)}%</span>
            <Button onClick={saveRatio} className="ml-auto">Enregistrer</Button>
          </div>
        </CardContent>
      </Card>

      {/* Members */}
      <Card>
        <CardHeader><CardTitle className="text-base flex items-center gap-2"><Users className="h-4 w-4" /> Membres ({members?.length || 0})</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {sortedMembers.map((m: any) => {
            const isMe = m.user_id === user?.id;
            const isEditing = editingMemberId === m.id;

            if (isEditing) {
              return (
                <div key={m.id} className="flex items-center gap-2 p-3 rounded-lg border">
                  <Input value={editMemberName} onChange={(e) => setEditMemberName(e.target.value)} placeholder="Nom" className="h-8" />
                  <Input value={editMemberCard} onChange={(e) => setEditMemberCard(e.target.value)} placeholder="Identifiant carte" className="h-8" />
                  <Button size="sm" onClick={() => { updateGhost.mutate({ id: m.id, displayName: editMemberName, cardIdentifier: editMemberCard }); setEditingMemberId(null); }}><Check className="h-3.5 w-3.5" /></Button>
                  <Button size="sm" variant="ghost" onClick={() => setEditingMemberId(null)}><X className="h-3.5 w-3.5" /></Button>
                </div>
              );
            }

            return (
              <div key={m.id} className={`flex items-center justify-between p-3 rounded-lg border ${!m.is_active ? 'border-dashed opacity-70' : ''}`}>
                <div>
                  <p className="text-sm font-medium">{m.display_name || "Sans nom"}</p>
                  {m.card_identifier && <p className="text-xs text-muted-foreground">Carte : {m.card_identifier}</p>}
                </div>
                <div className="flex items-center gap-2">
                  {isMe && <Badge variant="outline">Vous</Badge>}
                  <div className="flex items-center gap-1.5">
                    <Switch
                      checked={m.is_active}
                      onCheckedChange={(checked) => toggleActive.mutate({ id: m.id, isActive: checked })}
                    />
                    <span className="text-xs text-muted-foreground w-12">{m.is_active ? "Actif" : "Inactif"}</span>
                  </div>
                  {!isMe && (
                    <>
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => { setEditingMemberId(m.id); setEditMemberName(m.display_name); setEditMemberCard(m.card_identifier || ""); }}><Pencil className="h-3.5 w-3.5" /></Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => deleteGhost.mutate(m.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>

      {/* Add ghost member */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><Plus className="h-4 w-4" /> Ajouter un membre non-actif</CardTitle>
          <CardDescription>Ajoutez une personne qui n'utilise pas l'application.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label>Nom d'affichage</Label>
              <Input value={ghostName} onChange={(e) => setGhostName(e.target.value)} placeholder="Ex: Élise" />
            </div>
            <div className="space-y-1.5">
              <Label>Identifiant de carte (optionnel)</Label>
              <Input value={ghostCard} onChange={(e) => setGhostCard(e.target.value)} placeholder="Ex: CB *7890" />
            </div>
          </div>
          <Button onClick={() => { if (household && ghostName.trim()) { addGhost.mutate({ householdId: household.id, displayName: ghostName.trim(), cardIdentifier: ghostCard }); setGhostName(""); setGhostCard(""); } }} disabled={addGhost.isPending || !ghostName.trim()}>
            <Plus className="h-4 w-4 mr-1" /> Ajouter
          </Button>
        </CardContent>
      </Card>

      {/* Invite */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Inviter un partenaire</CardTitle>
          <CardDescription>Envoyez une invitation par email.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input type="email" value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)} placeholder="email@exemple.com" />
            <Button onClick={() => { if (household && inviteEmail) { sendInvitation.mutate({ householdId: household.id, email: inviteEmail }); setInviteEmail(""); } }} disabled={sendInvitation.isPending || !inviteEmail}>
              <Send className="h-4 w-4 mr-1" /> Inviter
            </Button>
          </div>
          {sentInvites.length > 0 && (
            <>
              <Separator />
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">Invitations envoyées</p>
                {sentInvites.map((inv: any) => (
                  <div key={inv.id} className="flex items-center justify-between p-2 rounded border text-sm">
                    <div className="flex items-center gap-2"><Mail className="h-3.5 w-3.5 text-muted-foreground" /><span>{inv.invited_email}</span></div>
                    <div className="flex items-center gap-2">
                      <Badge variant={inv.status === "pending" ? "outline" : inv.status === "accepted" ? "default" : "secondary"}>
                        {inv.status === "pending" ? "En attente" : inv.status === "accepted" ? "Acceptée" : inv.status}
                      </Badge>
                      {inv.status === "pending" && (
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => deleteInvitation.mutate(inv.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/* ─── Categories ────────────────────────────────────── */
function CategoriesTab() {
  const { data: categories, isLoading } = useCategories();
  const { data: profile } = useHousehold();
  const createCategory = useCreateCategory();
  const updateCategory = useUpdateCategory();
  const deleteCategory = useDeleteCategory();
  const queryClient = useQueryClient();

  const [newName, setNewName] = useState("");
  const [newColor, setNewColor] = useState(COLORS[0]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const [editColor, setEditColor] = useState("");

  const household = profile?.households as any;

  if (isLoading) return <Skeleton className="h-40 w-full" />;

  const defaultCats = categories?.filter((c) => c.is_default) || [];
  const customCats = categories?.filter((c) => !c.is_default) || [];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader><CardTitle className="text-base">Ajouter une catégorie</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Nom de la catégorie" />
            <Button onClick={() => { if (household && newName.trim()) { createCategory.mutate({ name: newName.trim(), color: newColor, householdId: household.id }); setNewName(""); } }} disabled={createCategory.isPending || !newName.trim()}>
              <Plus className="h-4 w-4 mr-1" /> Ajouter
            </Button>
          </div>
          <div className="flex gap-1.5">
            {COLORS.map((c) => (
              <button key={c} onClick={() => setNewColor(c)} className="h-7 w-7 rounded-full border-2 transition-transform hover:scale-110" style={{ backgroundColor: c, borderColor: newColor === c ? "hsl(var(--foreground))" : "transparent" }} />
            ))}
          </div>
        </CardContent>
      </Card>

      {customCats.length > 0 && (
        <Card>
          <CardHeader><CardTitle className="text-base">Catégories personnalisées ({customCats.length})</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {customCats.map((cat) => (
              <div key={cat.id} className="flex items-center justify-between p-3 rounded-lg border">
                {editingId === cat.id ? (
                  <div className="flex items-center gap-2 flex-1">
                    <Input value={editName} onChange={(e) => setEditName(e.target.value)} className="h-8" />
                    <div className="flex gap-1">
                      {COLORS.map((c) => (
                        <button key={c} onClick={() => setEditColor(c)} className="h-5 w-5 rounded-full border" style={{ backgroundColor: c, borderColor: editColor === c ? "hsl(var(--foreground))" : "transparent" }} />
                      ))}
                    </div>
                    <Button size="sm" onClick={() => { updateCategory.mutate({ id: cat.id, name: editName, color: editColor }); setEditingId(null); }}><Check className="h-3.5 w-3.5" /></Button>
                    <Button size="sm" variant="ghost" onClick={() => setEditingId(null)}><X className="h-3.5 w-3.5" /></Button>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center gap-3">
                      <div className="h-4 w-4 rounded-full" style={{ backgroundColor: cat.color || "#6b7280" }} />
                      <span className="text-sm font-medium">{cat.name}</span>
                    </div>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => { setEditingId(cat.id); setEditName(cat.name); setEditColor(cat.color || COLORS[0]); }}><Pencil className="h-3.5 w-3.5" /></Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" onClick={() => deleteCategory.mutate(cat.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Catégories par défaut ({defaultCats.length})</CardTitle>
          <CardDescription>Vous pouvez exclure des catégories du calcul des revenus ou des dépenses.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {defaultCats.map((cat) => (
              <div key={cat.id} className="flex items-center justify-between p-2 rounded-lg border">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full" style={{ backgroundColor: cat.color || "#6b7280" }} />
                  <span className="text-sm font-medium">{cat.name}</span>
                </div>
                <div className="flex items-center gap-4">
                  <CategoryToggle categoryId={cat.id} field="exclude_from_income" label="Exclure revenus" initialValue={!!(cat as any).exclude_from_income} />
                  <CategoryToggle categoryId={cat.id} field="exclude_from_expenses" label="Exclure dépenses" initialValue={!!(cat as any).exclude_from_expenses} />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Same toggles for custom categories */}
      {customCats.length > 0 && (
        <Card>
          <CardHeader><CardTitle className="text-base">Exclusions des catégories personnalisées</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-2">
              {customCats.map((cat) => (
                <div key={cat.id} className="flex items-center justify-between p-2 rounded-lg border">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full" style={{ backgroundColor: cat.color || "#6b7280" }} />
                    <span className="text-sm font-medium">{cat.name}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <CategoryToggle categoryId={cat.id} field="exclude_from_income" label="Exclure revenus" initialValue={!!(cat as any).exclude_from_income} />
                    <CategoryToggle categoryId={cat.id} field="exclude_from_expenses" label="Exclure dépenses" initialValue={!!(cat as any).exclude_from_expenses} />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

/* ─── Category Toggle ───────────────────────────────── */
function CategoryToggle({ categoryId, field, label, initialValue }: { categoryId: string; field: string; label: string; initialValue: boolean }) {
  const [checked, setChecked] = useState(initialValue);
  const queryClient = useQueryClient();

  const toggle = async (value: boolean) => {
    setChecked(value);
    const { error } = await supabase.from("categories").update({ [field]: value } as any).eq("id", categoryId);
    if (error) { toast.error("Erreur"); setChecked(!value); }
    else { queryClient.invalidateQueries({ queryKey: ["categories"] }); queryClient.invalidateQueries({ queryKey: ["dashboard"] }); }
  };

  return (
    <div className="flex items-center gap-1.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      <Switch checked={checked} onCheckedChange={toggle} />
    </div>
  );
}

/* ─── Data Management ───────────────────────────────── */
function DataTab() {
  const { data: profile } = useHousehold();
  const queryClient = useQueryClient();
  const [selectedMonth, setSelectedMonth] = useState(format(new Date(), "yyyy-MM"));
  const [confirmText, setConfirmText] = useState("");
  const [deletingMonth, setDeletingMonth] = useState(false);
  const [deletingAll, setDeletingAll] = useState(false);
  const [deletingRules, setDeletingRules] = useState(false);
  const [deletingGoals, setDeletingGoals] = useState(false);

  const household = profile?.households as any;

  // Generate last 24 months for selector
  const months = Array.from({ length: 24 }, (_, i) => {
    const d = subMonths(new Date(), i);
    return { value: format(d, "yyyy-MM"), label: format(d, "MMMM yyyy", { locale: fr }) };
  });

  const deleteMonthTransactions = async () => {
    if (!household) return;
    setDeletingMonth(true);
    try {
      const [year, month] = selectedMonth.split("-").map(Number);
      const start = format(startOfMonth(new Date(year, month - 1)), "yyyy-MM-dd");
      const end = format(endOfMonth(new Date(year, month - 1)), "yyyy-MM-dd");

      // Get accounts for this household
      const { data: accounts } = await supabase.from("bank_accounts").select("id").eq("household_id", household.id);
      if (!accounts?.length) { toast.info("Aucun compte trouvé"); return; }

      const accountIds = accounts.map((a: any) => a.id);
      const { error, count } = await supabase
        .from("transactions")
        .delete()
        .in("bank_account_id", accountIds)
        .gte("date", start)
        .lte("date", end);

      if (error) throw error;
      toast.success(`Transactions de ${months.find(m => m.value === selectedMonth)?.label} supprimées`);
      queryClient.invalidateQueries();
    } catch (e: any) {
      toast.error(e.message || "Erreur lors de la suppression");
    } finally {
      setDeletingMonth(false);
    }
  };

  const deleteAllTransactions = async () => {
    if (!household || confirmText !== "SUPPRIMER") return;
    setDeletingAll(true);
    try {
      const { data: accounts } = await supabase.from("bank_accounts").select("id").eq("household_id", household.id);
      if (!accounts?.length) { toast.info("Aucun compte trouvé"); return; }

      const accountIds = accounts.map((a: any) => a.id);
      const { error } = await supabase.from("transactions").delete().in("bank_account_id", accountIds);
      if (error) throw error;
      toast.success("Toutes les transactions ont été supprimées");
      setConfirmText("");
      queryClient.invalidateQueries();
    } catch (e: any) {
      toast.error(e.message || "Erreur lors de la suppression");
    } finally {
      setDeletingAll(false);
    }
  };

  const deleteAllRules = async () => {
    if (!household) return;
    setDeletingRules(true);
    try {
      const { error } = await supabase.from("categorization_rules").delete().eq("household_id", household.id);
      if (error) throw error;
      toast.success("Toutes les règles ont été supprimées");
      queryClient.invalidateQueries({ queryKey: ["rules"] });
    } catch (e: any) {
      toast.error(e.message || "Erreur");
    } finally {
      setDeletingRules(false);
    }
  };

  const deleteAllGoals = async () => {
    if (!household) return;
    setDeletingGoals(true);
    try {
      const { error } = await supabase.from("savings_goals").delete().eq("household_id", household.id);
      if (error) throw error;
      toast.success("Tous les objectifs ont été supprimés");
      queryClient.invalidateQueries({ queryKey: ["savings-goals"] });
    } catch (e: any) {
      toast.error(e.message || "Erreur");
    } finally {
      setDeletingGoals(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Delete by month */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><Clock className="h-4 w-4" /> Supprimer les transactions d'un mois</CardTitle>
          <CardDescription>Supprime toutes les transactions du mois sélectionné. Action irréversible.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2 items-end">
            <div className="space-y-1.5 flex-1">
              <Label>Mois</Label>
              <Select value={selectedMonth} onValueChange={setSelectedMonth}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {months.map((m) => (
                    <SelectItem key={m.value} value={m.value} className="capitalize">{m.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" disabled={deletingMonth}>
                  <Trash2 className="h-4 w-4 mr-1" /> Supprimer
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Supprimer les transactions ?</AlertDialogTitle>
                  <AlertDialogDescription>
                    Toutes les transactions de <strong className="capitalize">{months.find(m => m.value === selectedMonth)?.label}</strong> seront définitivement supprimées. Cette action est irréversible.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Annuler</AlertDialogCancel>
                  <AlertDialogAction onClick={deleteMonthTransactions} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Supprimer</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </CardContent>
      </Card>

      {/* Delete all transactions */}
      <Card className="border-destructive/30">
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2 text-destructive"><AlertTriangle className="h-4 w-4" /> Supprimer toutes les transactions</CardTitle>
          <CardDescription>Supprime définitivement toutes les transactions de tous vos comptes. Action irréversible.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Tapez <strong>SUPPRIMER</strong> pour confirmer</Label>
            <Input value={confirmText} onChange={(e) => setConfirmText(e.target.value)} placeholder="SUPPRIMER" className="max-w-xs" />
          </div>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" disabled={confirmText !== "SUPPRIMER" || deletingAll}>
                <Trash2 className="h-4 w-4 mr-1" /> Tout supprimer
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Êtes-vous absolument certain ?</AlertDialogTitle>
                <AlertDialogDescription>Cette action supprimera TOUTES les transactions de votre foyer. Il n'y a aucun moyen de les récupérer.</AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Annuler</AlertDialogCancel>
                <AlertDialogAction onClick={deleteAllTransactions} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Oui, tout supprimer</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </CardContent>
      </Card>

      <Separator />

      {/* Reset rules */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Réinitialiser les règles de catégorisation</CardTitle>
          <CardDescription>Supprime toutes vos règles de catégorisation automatique.</CardDescription>
        </CardHeader>
        <CardContent>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="outline" className="text-destructive border-destructive/30" disabled={deletingRules}>
                <Trash2 className="h-4 w-4 mr-1" /> Réinitialiser les règles
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Supprimer toutes les règles ?</AlertDialogTitle>
                <AlertDialogDescription>Toutes vos règles de catégorisation seront supprimées. Vous pourrez en recréer par la suite.</AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Annuler</AlertDialogCancel>
                <AlertDialogAction onClick={deleteAllRules} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Supprimer</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </CardContent>
      </Card>

      {/* Reset savings goals */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Réinitialiser les objectifs d'épargne</CardTitle>
          <CardDescription>Supprime tous vos objectifs d'épargne et leur progression.</CardDescription>
        </CardHeader>
        <CardContent>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="outline" className="text-destructive border-destructive/30" disabled={deletingGoals}>
                <Trash2 className="h-4 w-4 mr-1" /> Réinitialiser les objectifs
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Supprimer tous les objectifs ?</AlertDialogTitle>
                <AlertDialogDescription>Tous vos objectifs d'épargne seront supprimés définitivement.</AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Annuler</AlertDialogCancel>
                <AlertDialogAction onClick={deleteAllGoals} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Supprimer</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </CardContent>
      </Card>
    </div>
  );
}

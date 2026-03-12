import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Sparkles, Home, Users, CreditCard, Upload, ChevronRight, ChevronLeft,
  Plus, Trash2, UserPlus, Send, Check, FileUp, ArrowRight,
} from "lucide-react";
import { useHousehold, useUpdateHousehold, useHouseholdMembers, useAddGhostMember, useSendInvitation, useToggleMemberActive, useDeleteMember } from "@/hooks/useHousehold";
import { useAccounts, useCreateAccount, useHouseholdId } from "@/hooks/useAccounts";
import { useAuth } from "@/hooks/useAuth";
import { parseCsv, parseDate, parseAmount, BANK_PRESETS, type ParsedCsv, type BankPreset } from "@/lib/csv-parser";
import { categorize, hashTransaction } from "@/lib/categorization-engine";
import { useCategories } from "@/hooks/useCategories";
import { useRules } from "@/hooks/useRules";
import { supabase } from "@/integrations/supabase/client";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

const STEPS = [
  { label: "Bienvenue", icon: Sparkles },
  { label: "Foyer", icon: Home },
  { label: "Membres", icon: Users },
  { label: "Comptes", icon: CreditCard },
  { label: "Import", icon: Upload },
];

const ACCOUNT_TYPES = [
  { value: "perso_a" as const, label: "💳 Mon compte perso", description: "Vos dépenses personnelles (shopping, hobbies...)" },
  { value: "perso_b" as const, label: "💳 Compte de mon partenaire", description: "Ses dépenses personnelles" },
  { value: "joint" as const, label: "🏠 Notre compte commun", description: "Dépenses partagées : loyer, courses, factures..." },
];

const ACCOUNT_TYPES_NO_JOINT = [
  { value: "perso_a" as const, label: "💳 Mon compte perso", description: "Vos dépenses personnelles" },
  { value: "perso_b" as const, label: "💳 Compte de mon partenaire", description: "Ses dépenses personnelles" },
];

interface Props {
  initialStep?: number;
  onComplete: () => void;
}

export function Onboarding({ initialStep = 1, onComplete }: Props) {
  const [step, setStep] = useState(initialStep);
  const progress = (step / STEPS.length) * 100;

  const next = () => setStep((s) => Math.min(s + 1, 5));
  const prev = () => setStep((s) => Math.max(s - 1, 1));

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Progress header */}
      <div className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-muted-foreground">
              Étape {step} sur {STEPS.length}
            </span>
            <div className="flex gap-1.5">
              {STEPS.map((s, i) => {
                const Icon = s.icon;
                const isActive = i + 1 === step;
                const isDone = i + 1 < step;
                return (
                  <div
                    key={i}
                    className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs transition-colors ${
                      isActive ? "bg-primary text-primary-foreground" :
                      isDone ? "bg-primary/10 text-primary" :
                      "bg-muted text-muted-foreground"
                    }`}
                  >
                    <Icon className="h-3 w-3" />
                    <span className="hidden sm:inline">{s.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
          <Progress value={progress} className="h-1.5" />
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex items-start justify-center px-4 py-8">
        <div key={step} className="w-full max-w-2xl animate-slide-in-up">
          {step === 1 && <StepWelcome onNext={next} />}
          {step === 2 && <StepHousehold onNext={next} onPrev={prev} />}
          {step === 3 && <StepMembers onNext={next} onPrev={prev} />}
          {step === 4 && <StepAccounts onNext={next} onPrev={prev} />}
          {step === 5 && <StepImport onComplete={onComplete} onPrev={prev} />}
        </div>
      </div>
    </div>
  );
}

/* ─── Step 1: Welcome ─────────────────────────────── */
function StepWelcome({ onNext }: { onNext: () => void }) {
  const { data: profile } = useHousehold();
  const displayName = profile?.display_name?.split(" ")[0] || "vous";

  return (
    <Card className="text-center">
      <CardContent className="pt-10 pb-8 space-y-6">
        <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-primary/10 mx-auto">
          <Sparkles className="h-8 w-8 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Bienvenue, {displayName} ! 🎉
          </h1>
          <p className="text-muted-foreground mt-2 max-w-md mx-auto">
            Configurons ensemble votre espace en quelques étapes simples.
          </p>
        </div>
        <div className="text-left max-w-sm mx-auto space-y-3">
          {[
            { emoji: "🏠", text: "Créez votre foyer et ajoutez vos proches" },
            { emoji: "🏦", text: "Configurez vos comptes bancaires" },
            { emoji: "📊", text: "Importez vos relevés pour analyser vos finances" },
          ].map((item, i) => (
            <div key={i} className="flex items-center gap-3 text-sm">
              <span className="text-lg">{item.emoji}</span>
              <span>{item.text}</span>
            </div>
          ))}
        </div>
        <Button size="lg" onClick={onNext} className="mt-4">
          Commencer <ChevronRight className="h-4 w-4 ml-1" />
        </Button>
      </CardContent>
    </Card>
  );
}

/* ─── Step 2: Household ───────────────────────────── */
function StepHousehold({ onNext, onPrev }: { onNext: () => void; onPrev: () => void }) {
  const { data: profile } = useHousehold();
  const updateHousehold = useUpdateHousehold();
  const household = profile?.households as any;
  const [name, setName] = useState(household?.name || "Mon foyer");

  const handleSave = () => {
    if (household && name.trim()) {
      updateHousehold.mutate({ householdId: household.id, name: name.trim() }, { onSuccess: onNext });
    } else {
      onNext();
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Home className="h-5 w-5 text-primary" /> Nommez votre foyer
        </CardTitle>
        <CardDescription>
          Ce nom apparaîtra dans votre tableau de bord.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="household-name">Nom du foyer</Label>
          <Input
            id="household-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ex: Foyer Dupont"
            maxLength={50}
            autoComplete="organization"
            autoFocus
          />
        </div>
        <NavButtons onPrev={onPrev} onNext={handleSave} nextLoading={updateHousehold.isPending} />
      </CardContent>
    </Card>
  );
}

/* ─── Step 3: Members ─────────────────────────────── */
function StepMembers({ onNext, onPrev }: { onNext: () => void; onPrev: () => void }) {
  const { data: profile } = useHousehold();
  const { data: members } = useHouseholdMembers();
  const addGhost = useAddGhostMember();
  const sendInvitation = useSendInvitation();
  const toggleActive = useToggleMemberActive();
  const deleteMember = useDeleteMember();
  const household = profile?.households as any;

  const [ghostName, setGhostName] = useState("");
  const [ghostCard, setGhostCard] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [mode, setMode] = useState<"ghost" | "invite" | null>(null);

  const handleAddGhost = () => {
    if (ghostName.trim()) {
      addGhost.mutate(
        { name: ghostName.trim(), color: "#3b82f6", isActive: true },
        { onSuccess: () => { setGhostName(""); setGhostCard(""); setMode(null); } }
      );
    }
  };

  const handleInvite = () => {
    if (inviteEmail.trim()) {
      sendInvitation.mutate(
        inviteEmail.trim(),
        { onSuccess: () => { setInviteEmail(""); setMode(null); } }
      );
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users className="h-5 w-5 text-primary" /> Membres du foyer
        </CardTitle>
        <CardDescription>
          Ajoutez votre partenaire ou d'autres membres. 
          <span className="block mt-1 text-xs">
            <strong>Actif</strong> = se connecte à l'app (vous, partenaire). 
            <strong>Non-actif</strong> = participe aux dépenses mais ne se connecte pas (enfant, animal...).
          </span>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Current members */}
        <div className="space-y-2">
          {members?.map((m: any) => (
            <div key={m.id} className="flex items-center justify-between p-3 rounded-lg border">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{m.name || m.display_name}</span>
                {m.role === "owner" && <Badge variant="default" className="text-[10px]">Propriétaire</Badge>}
              </div>
              <div className="flex items-center gap-2">
                <Button 
                  variant={m.isActive ? "default" : "outline"} 
                  size="sm"
                  className="h-7 text-xs"
                  onClick={() => toggleActive.mutate({ id: m.id, isActive: !m.isActive })}
                  title={m.isActive ? "Se connecte à l'application" : "Ne se connecte pas (participe aux dépenses)"}
                >
                  {m.isActive ? "👤 Connecté" : "🚫 Hors-ligne"}
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="h-7 w-7 p-0 text-destructive"
                  onClick={() => deleteMember.mutate(m.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
          {members?.length === 1 && members[0].id === "mem-owner" && (
            <div className="p-4 rounded-lg border border-dashed bg-muted/30 text-center text-sm text-muted-foreground">
              Vous êtes connecté. Ajoutez votre partenaire (s'il se connecte) ou d'autres membres.
            </div>
          )}
        </div>

        {/* Add actions */}
        {!mode && (
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" onClick={() => setMode("ghost")}>
              <UserPlus className="h-4 w-4 mr-1.5" /> Ajouter un membre
            </Button>
            <Button variant="outline" size="sm" onClick={() => setMode("invite")}>
              <Send className="h-4 w-4 mr-1.5" /> Inviter par email
            </Button>
          </div>
        )}

        {mode === "ghost" && (
          <div className="space-y-3 p-4 rounded-lg border border-dashed bg-muted/30">
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="space-y-1.5">
                <Label htmlFor="ghost-member-name">Nom</Label>
                <Input
                  id="ghost-member-name"
                  name="ghostMemberName"
                  value={ghostName}
                  onChange={(e) => setGhostName(e.target.value)}
                  placeholder="Ex: Élise"
                  autoComplete="name"
                  autoFocus
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="ghost-member-card">Identifiant carte (optionnel)</Label>
                <Input
                  id="ghost-member-card"
                  name="ghostMemberCard"
                  value={ghostCard}
                  onChange={(e) => setGhostCard(e.target.value)}
                  placeholder="Ex: CB *7890"
                  autoComplete="off"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button size="sm" onClick={handleAddGhost} disabled={addGhost.isPending || !ghostName.trim()}>
                <Plus className="h-4 w-4 mr-1" /> Ajouter
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setMode(null)}>Annuler</Button>
            </div>
          </div>
        )}

        {mode === "invite" && (
          <div className="space-y-3 p-4 rounded-lg border border-dashed bg-muted/30">
            <div className="space-y-1.5">
              <Label htmlFor="invite-email">Email du partenaire</Label>
              <Input
                id="invite-email"
                name="inviteEmail"
                type="email"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                placeholder="email@exemple.com"
                autoComplete="email"
                autoFocus
              />
            </div>
            <div className="flex gap-2">
              <Button size="sm" onClick={handleInvite} disabled={sendInvitation.isPending || !inviteEmail.trim()}>
                <Send className="h-4 w-4 mr-1" /> Envoyer
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setMode(null)}>Annuler</Button>
            </div>
          </div>
        )}

        <NavButtons onPrev={onPrev} onNext={onNext} nextLabel="Continuer" skipLabel="Passer" onSkip={onNext} />
      </CardContent>
    </Card>
  );
}

/* ─── Step 4: Accounts ────────────────────────────── */
function StepAccounts({ onNext, onPrev }: { onNext: () => void; onPrev: () => void }) {
  const { data: accounts } = useAccounts();
  const householdId = useHouseholdId(); // ✅ Correction: pas de destructuration { data: ... }
  const createAccount = useCreateAccount();
  const [name, setName] = useState("");
  const [bank, setBank] = useState("");
  const [type, setType] = useState<"perso_a" | "perso_b" | "joint">("joint");
  const [hasJointAccount, setHasJointAccount] = useState(true);

  const handleAdd = () => {
    if (householdId && name.trim()) {
      createAccount.mutate(
        { 
          household_id: householdId, 
          name: name.trim(), 
          bank_name: bank.trim() || undefined, // ✅ Correction: undefined au lieu de null
          account_type: type,
          balance: 0, // ✅ Correction: ajout du balance requis
        },
        { onSuccess: () => { setName(""); setBank(""); setType("joint"); } }
      );
    }
  };

  const canContinue = (accounts?.length ?? 0) > 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="h-5 w-5 text-primary" /> Vos comptes bancaires
        </CardTitle>
        <CardDescription>
          Ajoutez vos comptes personnels et/ou votre compte commun.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Toggle compte joint */}
        <div className="flex items-center justify-between p-3 rounded-lg border bg-muted/30">
          <div>
            <span className="text-sm font-medium">Compte commun (joint)</span>
            <p className="text-xs text-muted-foreground">
              {hasJointAccount 
                ? "Vous pourrez suivre les dépenses communes" 
                : "Chaque membre aura uniquement son compte perso"}
            </p>
          </div>
          <Button
            variant={hasJointAccount ? "default" : "outline"}
            size="sm"
            onClick={() => setHasJointAccount(!hasJointAccount)}
          >
            {hasJointAccount ? "✓ Activé" : "Désactivé"}
          </Button>
        </div>
        {/* Existing accounts */}
        {accounts && accounts.length > 0 && (
          <div className="space-y-2">
            {accounts.map((a) => (
              <div key={a.id} className="flex items-center justify-between p-3 rounded-lg border bg-muted/30">
                <div>
                  <span className="text-sm font-medium">{a.name}</span>
                  {a.bank_name && <span className="text-xs text-muted-foreground ml-2">({a.bank_name})</span>}
                </div>
                <Badge variant="secondary">
                  {ACCOUNT_TYPES.find((t) => t.value === a.account_type)?.label || a.account_type}
                </Badge>
              </div>
            ))}
          </div>
        )}

        {/* Add form */}
        <div className="space-y-3 p-4 rounded-lg border border-dashed bg-muted/30">
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="space-y-1.5">
              <Label htmlFor="account-name">Nom du compte *</Label>
              <Input
                id="account-name"
                name="accountName"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Ex: Compte courant"
                autoComplete="off"
                autoFocus
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="bank-name">Banque</Label>
              <Input
                id="bank-name"
                name="bankName"
                value={bank}
                onChange={(e) => setBank(e.target.value)}
                placeholder="Ex: Boursorama"
                autoComplete="off"
              />
            </div>
            <div className="space-y-1.5">
              <Label>Type {hasJointAccount ? "(compte commun disponible)" : "(sans compte commun)"}</Label>
              <Select value={type} onValueChange={(v: any) => setType(v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {(hasJointAccount ? ACCOUNT_TYPES : ACCOUNT_TYPES_NO_JOINT).map((t) => (
                    <SelectItem key={t.value} value={t.value}>
                      {t.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <p className="text-xs text-muted-foreground">
            {(hasJointAccount ? ACCOUNT_TYPES : ACCOUNT_TYPES_NO_JOINT).find((t) => t.value === type)?.description}
          </p>
          <Button size="sm" onClick={handleAdd} disabled={createAccount.isPending || !name.trim()}>
            <Plus className="h-4 w-4 mr-1" /> Ajouter le compte
          </Button>
        </div>

        <NavButtons onPrev={onPrev} onNext={onNext} nextDisabled={!canContinue} nextLabel="Continuer" />
        {!canContinue && (
          <p className="text-xs text-muted-foreground text-center">Ajoutez au moins un compte pour continuer.</p>
        )}
      </CardContent>
    </Card>
  );
}

/* ─── Step 5: Import ──────────────────────────────── */
function StepImport({ onComplete, onPrev }: { onComplete: () => void; onPrev: () => void }) {
  const { data: accounts } = useAccounts();
  const { data: categories } = useCategories();
  const { data: rules } = useRules();
  const queryClient = useQueryClient();

  const [csv, setCsv] = useState<ParsedCsv | null>(null);
  const [fileName, setFileName] = useState("");
  const [accountId, setAccountId] = useState("");
  const [dateCol, setDateCol] = useState("");
  const [labelCol, setLabelCol] = useState("");
  const [amountCol, setAmountCol] = useState("");
  const [debitCol, setDebitCol] = useState("");
  const [creditCol, setCreditCol] = useState("");
  const [useDebitCredit, setUseDebitCredit] = useState(false);
  const [imported, setImported] = useState(false);

  const handleFile = useCallback((file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const parsed = parseCsv(text);
      setCsv(parsed);
      setFileName(file.name);
      const preset = BANK_PRESETS.find(p =>
        parsed.headers.some(h => h.toLowerCase() === p.dateColumn.toLowerCase()) &&
        parsed.headers.some(h => h.toLowerCase() === p.labelColumn.toLowerCase())
      );
      if (preset) applyPreset(preset, parsed.headers);
    };
    reader.readAsText(file, "UTF-8");
  }, []);

  const applyPreset = (preset: BankPreset, headers: string[]) => {
    const find = (n: string) => headers.find(h => h.toLowerCase() === n.toLowerCase()) || "";
    setDateCol(find(preset.dateColumn));
    setLabelCol(find(preset.labelColumn));
    if (preset.debitColumn && preset.creditColumn) {
      setUseDebitCredit(true);
      setDebitCol(find(preset.debitColumn));
      setCreditCol(find(preset.creditColumn));
      setAmountCol("");
    } else {
      setUseDebitCredit(false);
      setAmountCol(find(preset.amountColumn));
    }
  };

  const previewData = csv && dateCol && labelCol && (amountCol || useDebitCredit)
    ? csv.rows.map((row) => {
        const date = parseDate(row[dateCol] || "");
        const label = row[labelCol] || "";
        let amount: number | null = null;
        if (useDebitCredit) {
          const debit = parseAmount(row[debitCol] || "");
          const credit = parseAmount(row[creditCol] || "");
          if (debit && debit !== 0) amount = -Math.abs(debit);
          else if (credit && credit !== 0) amount = Math.abs(credit);
          else amount = 0;
        } else {
          amount = parseAmount(row[amountCol] || "");
        }
        const categoryId = rules ? categorize(label, rules as any) : null;
        return { date, label, amount, categoryId, valid: !!date && amount !== null };
      }).filter(r => r.label.trim() !== "")
    : [];

  const validCount = previewData.filter(r => r.valid).length;

  const importMutation = useMutation({
    mutationFn: async () => {
      if (!accountId) throw new Error("Sélectionnez un compte");
      const validRows = previewData.filter(r => r.valid && r.date && r.amount !== null);
      const toInsert = validRows.map(r => ({
        date: r.date!,
        label: r.label,
        amount: r.amount!,
        bank_account_id: accountId,
        category_id: r.categoryId,
        import_hash: hashTransaction(r.date!, r.label, r.amount!),
      }));
      for (let i = 0; i < toInsert.length; i += 500) {
        const batch = toInsert.slice(i, i + 500);
        const { error } = await supabase.from("transactions").insert(batch);
        if (error) throw error;
      }
      return toInsert.length;
    },
    onSuccess: (count) => {
      toast.success(`${count} transactions importées ! 🎉`);
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["transaction-count"] });
      setImported(true);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (imported) {
    return (
      <Card className="text-center">
        <CardContent className="pt-10 pb-8 space-y-6">
          <div className="text-6xl">🎉</div>
          <div>
            <h2 className="text-2xl font-bold">C'est parti !</h2>
            <p className="text-muted-foreground mt-2">
              Votre espace est prêt. Découvrez votre tableau de bord.
            </p>
          </div>
          <Button size="lg" onClick={onComplete}>
            Voir mon dashboard <ArrowRight className="h-4 w-4 ml-1" />
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5 text-primary" /> Premier import
        </CardTitle>
        <CardDescription>
          Importez votre premier relevé CSV pour commencer l'analyse.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {!csv ? (
          <div
            className="flex flex-col items-center justify-center py-12 border-2 border-dashed border-border rounded-lg cursor-pointer hover:border-primary/50 transition-colors"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f?.name.endsWith(".csv")) handleFile(f); }}
            onClick={() => document.getElementById("onboarding-csv")?.click()}
          >
            <FileUp className="h-8 w-8 text-muted-foreground/50 mb-3" />
            <p className="text-sm font-medium">Glissez-déposez votre CSV</p>
            <p className="text-xs text-muted-foreground mt-1">ou cliquez pour sélectionner</p>
            <input id="onboarding-csv" type="file" accept=".csv" className="hidden" onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }} />
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm">
              <FileUp className="h-4 w-4 text-primary" />
              <span className="font-medium">{fileName}</span>
              <Badge variant="secondary">{csv.rows.length} lignes</Badge>
            </div>

            <div className="space-y-2">
              <Label htmlFor="target-account">Compte cible</Label>
              <Select value={accountId} onValueChange={setAccountId}>
                <SelectTrigger id="target-account">
                  <SelectValue placeholder={accounts === undefined ? "Chargement..." : "Sélectionner un compte"} />
                </SelectTrigger>
                <SelectContent>
                  {accounts?.length === 0 && (
                    <SelectItem value="" disabled>Aucun compte disponible</SelectItem>
                  )}
                  {accounts?.map(a => (
                    <SelectItem key={a.id} value={a.id}>
                      {a.name} {a.bank_name ? `(${a.bank_name})` : ""} 
                      <span className="text-muted-foreground text-xs ml-1">
                        {a.account_type === "joint" ? "- Commun" : a.account_type === "perso_a" ? "- Perso A" : "- Perso B"}
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {accounts?.length === 0 && (
                <p className="text-xs text-destructive">
                  Aucun compte trouvé. Veuillez d'abord créer un compte à l'étape précédente.
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="bank-format">Format bancaire</Label>
              <Select onValueChange={(v) => { const p = BANK_PRESETS[parseInt(v)]; if (p) applyPreset(p, csv.headers); }}>
                <SelectTrigger id="bank-format"><SelectValue placeholder="Détection auto ou choisir…" /></SelectTrigger>
                <SelectContent>
                  {BANK_PRESETS.map((p, i) => <SelectItem key={i} value={String(i)}>{p.name}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <div className="space-y-1.5">
                <Label htmlFor="col-date">Date</Label>
                <Select value={dateCol} onValueChange={setDateCol}>
                  <SelectTrigger id="col-date"><SelectValue placeholder="—" /></SelectTrigger>
                  <SelectContent>{csv.headers.map(h => <SelectItem key={h} value={h}>{h}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="col-label">Libellé</Label>
                <Select value={labelCol} onValueChange={setLabelCol}>
                  <SelectTrigger id="col-label"><SelectValue placeholder="—" /></SelectTrigger>
                  <SelectContent>{csv.headers.map(h => <SelectItem key={h} value={h}>{h}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              {!useDebitCredit ? (
                <div className="space-y-1.5">
                  <Label htmlFor="col-amount">Montant</Label>
                  <Select value={amountCol} onValueChange={setAmountCol}>
                    <SelectTrigger id="col-amount"><SelectValue placeholder="—" /></SelectTrigger>
                    <SelectContent>{csv.headers.map(h => <SelectItem key={h} value={h}>{h}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
              ) : (
                <>
                  <div className="space-y-1.5">
                    <Label htmlFor="col-debit">Débit</Label>
                    <Select value={debitCol} onValueChange={setDebitCol}>
                      <SelectTrigger id="col-debit"><SelectValue placeholder="—" /></SelectTrigger>
                      <SelectContent>{csv.headers.map(h => <SelectItem key={h} value={h}>{h}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="col-credit">Crédit</Label>
                    <Select value={creditCol} onValueChange={setCreditCol}>
                      <SelectTrigger id="col-credit"><SelectValue placeholder="—" /></SelectTrigger>
                      <SelectContent>{csv.headers.map(h => <SelectItem key={h} value={h}>{h}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                </>
              )}
            </div>

            <Button variant="outline" size="sm" onClick={() => { setUseDebitCredit(!useDebitCredit); setAmountCol(""); setDebitCol(""); setCreditCol(""); }}>
              {useDebitCredit ? "Montant unique" : "Débit / Crédit séparés"}
            </Button>

            {validCount > 0 && (
              <div className="flex items-center justify-between p-3 rounded-lg border bg-muted/30">
                <span className="text-sm"><strong>{validCount}</strong> transactions prêtes</span>
                <Button onClick={() => importMutation.mutate()} disabled={importMutation.isPending || !accountId}>
                  {importMutation.isPending ? "Import en cours…" : "Importer"} <Check className="h-4 w-4 ml-1" />
                </Button>
              </div>
            )}
          </div>
        )}

        <NavButtons
          onPrev={onPrev}
          onNext={onComplete}
          nextLabel="Je ferai ça plus tard"
          nextVariant="ghost"
        />
      </CardContent>
    </Card>
  );
}

/* ─── Nav Buttons ─────────────────────────────────── */
function NavButtons({
  onPrev,
  onNext,
  nextLabel = "Continuer",
  skipLabel,
  onSkip,
  nextDisabled = false,
  nextLoading = false,
  nextVariant = "default",
}: {
  onPrev?: () => void;
  onNext: () => void;
  nextLabel?: string;
  skipLabel?: string;
  onSkip?: () => void;
  nextDisabled?: boolean;
  nextLoading?: boolean;
  nextVariant?: "default" | "ghost";
}) {
  return (
    <div className="flex items-center justify-between pt-4 border-t">
      {onPrev ? (
        <Button variant="ghost" size="sm" onClick={onPrev}>
          <ChevronLeft className="h-4 w-4 mr-1" /> Retour
        </Button>
      ) : <div />}
      <div className="flex gap-2">
        {skipLabel && onSkip && (
          <Button variant="ghost" size="sm" onClick={onSkip}>{skipLabel}</Button>
        )}
        <Button
          size="sm"
          variant={nextVariant}
          onClick={onNext}
          disabled={nextDisabled || nextLoading}
        >
          {nextLoading ? "Chargement…" : nextLabel}
          <ChevronRight className="h-4 w-4 ml-1" />
        </Button>
      </div>
    </div>
  );
}

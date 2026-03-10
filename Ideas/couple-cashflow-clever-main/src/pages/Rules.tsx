import { useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, Pencil, Trash2, FlaskConical, FileText, Play, Loader2, UserCheck } from "lucide-react";
import { useRules } from "@/hooks/useRules";
import { useCategories } from "@/hooks/useCategories";
import { useAttributionRules } from "@/hooks/useAttributionRules";
import { useHouseholdMembers } from "@/hooks/useHousehold";
import { useHouseholdId } from "@/hooks/useAccounts";
import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";
import { RegexBuilder } from "@/components/rules/RegexBuilder";
import { LiveRegexPreview } from "@/components/rules/LiveRegexPreview";

// ─── Categorization Rule Form ───

interface CatRuleForm {
  name: string;
  regex_pattern: string;
  category_id: string;
  priority: number;
  is_active: boolean;
}
const emptyCatForm: CatRuleForm = { name: "", regex_pattern: "", category_id: "", priority: 0, is_active: true };

// ─── Attribution Rule Form ───

interface AttrRuleForm {
  name: string;
  regex_pattern: string;
  member_id: string;
  priority: number;
  is_active: boolean;
}
const emptyAttrForm: AttrRuleForm = { name: "", regex_pattern: "", member_id: "", priority: 0, is_active: true };

export default function Rules() {
  const { data: rules, isLoading } = useRules();
  const { data: categories } = useCategories();
  const { data: attrRules, isLoading: attrLoading } = useAttributionRules();
  const { data: householdMembers } = useHouseholdMembers();
  const { data: householdId } = useHouseholdId();
  const qc = useQueryClient();

  // ─── Categorization state ───
  const [catOpen, setCatOpen] = useState(false);
  const [catEditingId, setCatEditingId] = useState<string | null>(null);
  const [catForm, setCatForm] = useState<CatRuleForm>(emptyCatForm);
  const [testInput, setTestInput] = useState("");

  // ─── Attribution state ───
  const [attrOpen, setAttrOpen] = useState(false);
  const [attrEditingId, setAttrEditingId] = useState<string | null>(null);
  const [attrForm, setAttrForm] = useState<AttrRuleForm>(emptyAttrForm);
  const [attrTestInput, setAttrTestInput] = useState("");

  // ─── Rule match stats ───
  const { data: ruleStats } = useQuery({
    queryKey: ["rule-stats"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("transactions")
        .select("label, category_id")
        .not("category_id", "is", null);
      if (error) throw error;
      const statsMap = new Map<string, number>();
      if (!rules) return statsMap;
      for (const tx of data || []) {
        for (const rule of rules as any[]) {
          if (!rule.is_active) continue;
          try {
            if (new RegExp(rule.regex_pattern, "i").test(tx.label) && tx.category_id === rule.category_id) {
              statsMap.set(rule.id, (statsMap.get(rule.id) || 0) + 1);
              break;
            }
          } catch { /* skip */ }
        }
      }
      return statsMap;
    },
    enabled: !!rules?.length,
  });

  // ─── Categorization mutations ───

  const testResult = (() => {
    if (!catForm.regex_pattern || !testInput) return null;
    try { return new RegExp(catForm.regex_pattern, "i").test(testInput); } catch { return "invalid" as const; }
  })();

  const saveCatMutation = useMutation({
    mutationFn: async (data: CatRuleForm) => {
      if (!householdId) throw new Error("Pas de foyer");
      const payload = { ...data, household_id: householdId };
      if (catEditingId) {
        const { error } = await supabase.from("categorization_rules").update(payload).eq("id", catEditingId);
        if (error) throw error;
      } else {
        const { error } = await supabase.from("categorization_rules").insert(payload);
        if (error) throw error;
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["categorization_rules"] });
      qc.invalidateQueries({ queryKey: ["rule-stats"] });
      toast.success(catEditingId ? "Règle modifiée" : "Règle créée");
      closeCatDialog();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deleteCatMutation = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("categorization_rules").delete().eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["categorization_rules"] }); toast.success("Règle supprimée"); },
    onError: (e: Error) => toast.error(e.message),
  });

  const bulkApplyMutation = useMutation({
    mutationFn: async () => {
      if (!rules?.length) throw new Error("Aucune règle active");
      const { data: uncategorized, error } = await supabase.from("transactions").select("id, label").is("category_id", null).limit(1000);
      if (error) throw error;
      if (!uncategorized?.length) return 0;
      const byCat = new Map<string, string[]>();
      for (const tx of uncategorized) {
        for (const rule of rules as any[]) {
          if (!rule.is_active) continue;
          try {
            if (new RegExp(rule.regex_pattern, "i").test(tx.label)) {
              const list = byCat.get(rule.category_id) || [];
              list.push(tx.id);
              byCat.set(rule.category_id, list);
              break;
            }
          } catch { /* skip */ }
        }
      }
      let count = 0;
      for (const [catId, txIds] of byCat) {
        const { error: e } = await supabase.from("transactions").update({ category_id: catId }).in("id", txIds);
        if (!e) count += txIds.length;
      }
      return count;
    },
    onSuccess: (count) => {
      qc.invalidateQueries({ queryKey: ["transactions"] });
      qc.invalidateQueries({ queryKey: ["rule-stats"] });
      toast.success(`${count} transaction${count! > 1 ? "s" : ""} catégorisée${count! > 1 ? "s" : ""}`);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  function closeCatDialog() { setCatOpen(false); setCatEditingId(null); setCatForm(emptyCatForm); setTestInput(""); }
  function openCatEdit(rule: any) {
    setCatEditingId(rule.id);
    setCatForm({ name: rule.name, regex_pattern: rule.regex_pattern, category_id: rule.category_id, priority: rule.priority, is_active: rule.is_active });
    setCatOpen(true);
  }

  // ─── Attribution mutations ───

  const attrTestResult = (() => {
    if (!attrForm.regex_pattern || !attrTestInput) return null;
    try { return new RegExp(attrForm.regex_pattern, "i").test(attrTestInput); } catch { return "invalid" as const; }
  })();

  const saveAttrMutation = useMutation({
    mutationFn: async (data: AttrRuleForm) => {
      if (!householdId) throw new Error("Pas de foyer");
      const payload = { ...data, household_id: householdId };
      if (attrEditingId) {
        const { error } = await supabase.from("attribution_rules").update(payload).eq("id", attrEditingId);
        if (error) throw error;
      } else {
        const { error } = await supabase.from("attribution_rules").insert(payload);
        if (error) throw error;
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["attribution_rules"] });
      toast.success(attrEditingId ? "Règle modifiée" : "Règle créée");
      closeAttrDialog();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deleteAttrMutation = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("attribution_rules").delete().eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["attribution_rules"] }); toast.success("Règle supprimée"); },
    onError: (e: Error) => toast.error(e.message),
  });

  const bulkApplyAttrMutation = useMutation({
    mutationFn: async () => {
      if (!attrRules?.length) throw new Error("Aucune règle active");
      const { data: unattributed, error } = await supabase.from("transactions").select("id, label").is("attributed_to", null).limit(1000);
      if (error) throw error;
      if (!unattributed?.length) return 0;
      const byMember = new Map<string, string[]>();
      for (const tx of unattributed) {
        for (const rule of attrRules as any[]) {
          if (!rule.is_active) continue;
          try {
            if (new RegExp(rule.regex_pattern, "i").test(tx.label)) {
              const list = byMember.get(rule.member_id) || [];
              list.push(tx.id);
              byMember.set(rule.member_id, list);
              break;
            }
          } catch { /* skip */ }
        }
      }
      let count = 0;
      for (const [memberId, txIds] of byMember) {
        const { error: e } = await supabase.from("transactions").update({ attributed_to: memberId }).in("id", txIds);
        if (!e) count += txIds.length;
      }
      return count;
    },
    onSuccess: (count) => {
      qc.invalidateQueries({ queryKey: ["transactions"] });
      toast.success(`${count} transaction${count! > 1 ? "s" : ""} attribuée${count! > 1 ? "s" : ""}`);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  function closeAttrDialog() { setAttrOpen(false); setAttrEditingId(null); setAttrForm(emptyAttrForm); setAttrTestInput(""); }
  function openAttrEdit(rule: any) {
    setAttrEditingId(rule.id);
    setAttrForm({ name: rule.name, regex_pattern: rule.regex_pattern, member_id: rule.member_id, priority: rule.priority, is_active: rule.is_active });
    setAttrOpen(true);
  }

  const catMap = new Map((categories || []).map((c) => [c.id, c]));
  const memberMap = new Map((householdMembers || []).map((m) => [m.id, m]));

  return (
    <AppLayout title="Règles">
      <Tabs defaultValue="categorization" className="space-y-4">
        <TabsList>
          <TabsTrigger value="categorization">Catégorisation</TabsTrigger>
          <TabsTrigger value="attribution">Attribution</TabsTrigger>
        </TabsList>

        {/* ═══════════════ CATEGORIZATION TAB ═══════════════ */}
        <TabsContent value="categorization">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between flex-wrap gap-2">
              <CardTitle className="text-base">Règles Regex — Catégorisation</CardTitle>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => bulkApplyMutation.mutate()} disabled={bulkApplyMutation.isPending || !rules?.length}>
                  {bulkApplyMutation.isPending ? <Loader2 className="mr-1.5 h-4 w-4 animate-spin" /> : <Play className="mr-1.5 h-4 w-4" />}
                  Appliquer en masse
                </Button>
                <Dialog open={catOpen} onOpenChange={(v) => { if (!v) closeCatDialog(); else setCatOpen(true); }}>
                  <DialogTrigger asChild>
                    <Button size="sm" onClick={() => { setCatForm(emptyCatForm); setCatEditingId(null); }}>
                      <Plus className="mr-1.5 h-4 w-4" /> Ajouter
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader><DialogTitle>{catEditingId ? "Modifier la règle" : "Nouvelle règle"}</DialogTitle></DialogHeader>
                    <div className="space-y-4 pt-2">
                      <div className="space-y-1.5">
                        <Label>Nom</Label>
                        <Input value={catForm.name} onChange={(e) => setCatForm({ ...catForm, name: e.target.value.slice(0, 100) })} placeholder="Ex: Loyer" maxLength={100} />
                      </div>
                      <div className="space-y-1.5">
                        <Label>Pattern Regex</Label>
                        <Input value={catForm.regex_pattern} onChange={(e) => setCatForm({ ...catForm, regex_pattern: e.target.value.slice(0, 500) })} placeholder="Ex: loyer|bailleur" className="font-mono text-sm" maxLength={500} />
                        <RegexBuilder onApply={(p) => setCatForm({ ...catForm, regex_pattern: catForm.regex_pattern ? `${catForm.regex_pattern}|${p}` : p })} />
                      </div>
                      <div className="space-y-1.5">
                        <Label className="flex items-center gap-1.5"><FlaskConical className="h-3.5 w-3.5" /> Tester</Label>
                        <Input value={testInput} onChange={(e) => setTestInput(e.target.value)} placeholder="Tapez un libellé…" />
                        {testResult !== null && (
                          <p className={`text-xs font-medium ${testResult === "invalid" ? "text-destructive" : testResult ? "text-green-600 dark:text-green-400" : "text-destructive"}`}>
                            {testResult === "invalid" ? "⚠ Regex invalide" : testResult ? "✓ Match !" : "✗ Pas de match"}
                          </p>
                        )}
                      </div>
                      <LiveRegexPreview pattern={catForm.regex_pattern} enabled={catOpen} />
                      <div className="space-y-1.5">
                        <Label>Catégorie</Label>
                        <Select value={catForm.category_id} onValueChange={(v) => setCatForm({ ...catForm, category_id: v })}>
                          <SelectTrigger><SelectValue placeholder="Choisir…" /></SelectTrigger>
                          <SelectContent>
                            {(categories || []).map((c) => (
                              <SelectItem key={c.id} value={c.id}>
                                <span className="flex items-center gap-2">
                                  <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: c.color || "#94a3b8" }} />
                                  {c.name}
                                </span>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                          <Label>Priorité</Label>
                          <Input type="number" value={catForm.priority} onChange={(e) => setCatForm({ ...catForm, priority: parseInt(e.target.value) || 0 })} />
                        </div>
                        <div className="flex items-end gap-2 pb-0.5">
                          <Switch checked={catForm.is_active} onCheckedChange={(v) => setCatForm({ ...catForm, is_active: v })} id="cat-active" />
                          <Label htmlFor="cat-active">Active</Label>
                        </div>
                      </div>
                      <Button className="w-full" disabled={!catForm.name || !catForm.regex_pattern || !catForm.category_id || saveCatMutation.isPending} onClick={() => saveCatMutation.mutate(catForm)}>
                        {saveCatMutation.isPending ? "Enregistrement…" : catEditingId ? "Enregistrer" : "Créer la règle"}
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-3">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}</div>
              ) : !rules?.length ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <FileText className="h-10 w-10 text-muted-foreground/50 mb-3" />
                  <p className="text-sm text-muted-foreground">Aucune règle. Cliquez sur « Ajouter » pour commencer.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Nom</TableHead>
                        <TableHead>Regex</TableHead>
                        <TableHead>Catégorie</TableHead>
                        <TableHead className="text-center">Priorité</TableHead>
                        <TableHead className="text-center">Matchs</TableHead>
                        <TableHead className="text-center">Active</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {(rules as any[]).map((rule) => {
                        const cat = catMap.get(rule.category_id);
                        const matchCount = ruleStats?.get(rule.id) || 0;
                        return (
                          <TableRow key={rule.id}>
                            <TableCell className="font-medium">{rule.name}</TableCell>
                            <TableCell><code className="rounded bg-muted px-1.5 py-0.5 text-xs font-mono">{rule.regex_pattern}</code></TableCell>
                            <TableCell>
                              {cat ? (
                                <Badge variant="secondary" className="gap-1.5">
                                  <span className="h-2 w-2 rounded-full" style={{ backgroundColor: cat.color || "#94a3b8" }} />
                                  {cat.name}
                                </Badge>
                              ) : "—"}
                            </TableCell>
                            <TableCell className="text-center">{rule.priority}</TableCell>
                            <TableCell className="text-center"><Badge variant="outline" className="font-mono text-xs">{matchCount}</Badge></TableCell>
                            <TableCell className="text-center"><Badge variant={rule.is_active ? "default" : "outline"}>{rule.is_active ? "Oui" : "Non"}</Badge></TableCell>
                            <TableCell className="text-right">
                              <div className="flex justify-end gap-1">
                                <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => openCatEdit(rule)}><Pencil className="h-3.5 w-3.5" /></Button>
                                <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive" onClick={() => deleteCatMutation.mutate(rule.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ═══════════════ ATTRIBUTION TAB ═══════════════ */}
        <TabsContent value="attribution">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between flex-wrap gap-2">
              <CardTitle className="text-base">Règles Regex — Attribution</CardTitle>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => bulkApplyAttrMutation.mutate()} disabled={bulkApplyAttrMutation.isPending || !attrRules?.length}>
                  {bulkApplyAttrMutation.isPending ? <Loader2 className="mr-1.5 h-4 w-4 animate-spin" /> : <Play className="mr-1.5 h-4 w-4" />}
                  Appliquer en masse
                </Button>
                <Dialog open={attrOpen} onOpenChange={(v) => { if (!v) closeAttrDialog(); else setAttrOpen(true); }}>
                  <DialogTrigger asChild>
                    <Button size="sm" onClick={() => { setAttrForm(emptyAttrForm); setAttrEditingId(null); }}>
                      <Plus className="mr-1.5 h-4 w-4" /> Ajouter
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader><DialogTitle>{attrEditingId ? "Modifier la règle" : "Nouvelle règle d'attribution"}</DialogTitle></DialogHeader>
                    <div className="space-y-4 pt-2">
                      <div className="space-y-1.5">
                        <Label>Nom</Label>
                        <Input value={attrForm.name} onChange={(e) => setAttrForm({ ...attrForm, name: e.target.value.slice(0, 100) })} placeholder="Ex: Courses Élise" maxLength={100} />
                      </div>
                      <div className="space-y-1.5">
                        <Label>Pattern Regex</Label>
                        <Input value={attrForm.regex_pattern} onChange={(e) => setAttrForm({ ...attrForm, regex_pattern: e.target.value.slice(0, 500) })} placeholder="Ex: pharmacie|monoprix" className="font-mono text-sm" maxLength={500} />
                        <RegexBuilder onApply={(p) => setAttrForm({ ...attrForm, regex_pattern: attrForm.regex_pattern ? `${attrForm.regex_pattern}|${p}` : p })} />
                      </div>
                      <div className="space-y-1.5">
                        <Label className="flex items-center gap-1.5"><FlaskConical className="h-3.5 w-3.5" /> Tester</Label>
                        <Input value={attrTestInput} onChange={(e) => setAttrTestInput(e.target.value)} placeholder="Tapez un libellé…" />
                        {attrTestResult !== null && (
                          <p className={`text-xs font-medium ${attrTestResult === "invalid" ? "text-destructive" : attrTestResult ? "text-green-600 dark:text-green-400" : "text-destructive"}`}>
                            {attrTestResult === "invalid" ? "⚠ Regex invalide" : attrTestResult ? "✓ Match !" : "✗ Pas de match"}
                          </p>
                        )}
                      </div>
                      <div className="space-y-1.5">
                        <Label>Membre</Label>
                        <Select value={attrForm.member_id} onValueChange={(v) => setAttrForm({ ...attrForm, member_id: v })}>
                          <SelectTrigger><SelectValue placeholder="Choisir…" /></SelectTrigger>
                          <SelectContent>
                            {(householdMembers || []).map((m) => (
                              <SelectItem key={m.id} value={m.id}>{m.display_name}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                          <Label>Priorité</Label>
                          <Input type="number" value={attrForm.priority} onChange={(e) => setAttrForm({ ...attrForm, priority: parseInt(e.target.value) || 0 })} />
                        </div>
                        <div className="flex items-end gap-2 pb-0.5">
                          <Switch checked={attrForm.is_active} onCheckedChange={(v) => setAttrForm({ ...attrForm, is_active: v })} id="attr-active" />
                          <Label htmlFor="attr-active">Active</Label>
                        </div>
                      </div>
                      <Button className="w-full" disabled={!attrForm.name || !attrForm.regex_pattern || !attrForm.member_id || saveAttrMutation.isPending} onClick={() => saveAttrMutation.mutate(attrForm)}>
                        {saveAttrMutation.isPending ? "Enregistrement…" : attrEditingId ? "Enregistrer" : "Créer la règle"}
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              {attrLoading ? (
                <div className="space-y-3">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}</div>
              ) : !attrRules?.length ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <UserCheck className="h-10 w-10 text-muted-foreground/50 mb-3" />
                  <p className="text-sm text-muted-foreground">Aucune règle d'attribution. Cliquez sur « Ajouter » pour commencer.</p>
                  <p className="text-xs text-muted-foreground mt-1">Les règles sont aussi créées automatiquement lorsque vous attribuez manuellement des transactions.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Nom</TableHead>
                        <TableHead>Regex</TableHead>
                        <TableHead>Membre</TableHead>
                        <TableHead className="text-center">Priorité</TableHead>
                        <TableHead className="text-center">Active</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {(attrRules as any[]).map((rule) => {
                        const member = memberMap.get(rule.member_id);
                        return (
                          <TableRow key={rule.id}>
                            <TableCell className="font-medium">{rule.name}</TableCell>
                            <TableCell><code className="rounded bg-muted px-1.5 py-0.5 text-xs font-mono">{rule.regex_pattern}</code></TableCell>
                            <TableCell>
                              {member ? <Badge variant="secondary">{member.display_name}</Badge> : "—"}
                            </TableCell>
                            <TableCell className="text-center">{rule.priority}</TableCell>
                            <TableCell className="text-center"><Badge variant={rule.is_active ? "default" : "outline"}>{rule.is_active ? "Oui" : "Non"}</Badge></TableCell>
                            <TableCell className="text-right">
                              <div className="flex justify-end gap-1">
                                <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => openAttrEdit(rule)}><Pencil className="h-3.5 w-3.5" /></Button>
                                <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive" onClick={() => deleteAttrMutation.mutate(rule.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </AppLayout>
  );
}

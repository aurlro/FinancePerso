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
import { Plus, Pencil, Trash2, FlaskConical, FileText } from "lucide-react";
import { useRules } from "@/hooks/useRules";
import { useCategories } from "@/hooks/useCategories";
import { useHouseholdId } from "@/hooks/useAccounts";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";

interface RuleFormData {
  name: string;
  regex_pattern: string;
  category_id: string;
  priority: number;
  is_active: boolean;
}

const emptyForm: RuleFormData = { name: "", regex_pattern: "", category_id: "", priority: 0, is_active: true };

export default function Rules() {
  const { data: rules, isLoading } = useRules();
  const { data: categories } = useCategories();
  const { data: householdId } = useHouseholdId();
  const qc = useQueryClient();

  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<RuleFormData>(emptyForm);
  const [testInput, setTestInput] = useState("");

  const testResult = (() => {
    if (!form.regex_pattern || !testInput) return null;
    try {
      return new RegExp(form.regex_pattern, "i").test(testInput);
    } catch {
      return "invalid";
    }
  })();

  const saveMutation = useMutation({
    mutationFn: async (data: RuleFormData) => {
      if (!householdId) throw new Error("Pas de foyer");
      const payload = { ...data, household_id: householdId };
      if (editingId) {
        const { error } = await supabase.from("categorization_rules").update(payload).eq("id", editingId);
        if (error) throw error;
      } else {
        const { error } = await supabase.from("categorization_rules").insert(payload);
        if (error) throw error;
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["categorization_rules"] });
      toast.success(editingId ? "Règle modifiée" : "Règle créée");
      closeDialog();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("categorization_rules").delete().eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["categorization_rules"] });
      toast.success("Règle supprimée");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  function closeDialog() {
    setOpen(false);
    setEditingId(null);
    setForm(emptyForm);
    setTestInput("");
  }

  function openEdit(rule: any) {
    setEditingId(rule.id);
    setForm({
      name: rule.name,
      regex_pattern: rule.regex_pattern,
      category_id: rule.category_id,
      priority: rule.priority,
      is_active: rule.is_active,
    });
    setOpen(true);
  }

  const catMap = new Map((categories || []).map((c) => [c.id, c]));

  return (
    <AppLayout title="Règles de catégorisation">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Règles Regex</CardTitle>
          <Dialog open={open} onOpenChange={(v) => { if (!v) closeDialog(); else setOpen(true); }}>
            <DialogTrigger asChild>
              <Button size="sm" onClick={() => { setForm(emptyForm); setEditingId(null); }}>
                <Plus className="mr-1.5 h-4 w-4" /> Ajouter
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-lg">
              <DialogHeader>
                <DialogTitle>{editingId ? "Modifier la règle" : "Nouvelle règle"}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 pt-2">
                <div className="space-y-1.5">
                  <Label>Nom</Label>
                  <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Ex: Loyer" />
                </div>
                <div className="space-y-1.5">
                  <Label>Pattern Regex</Label>
                  <Input value={form.regex_pattern} onChange={(e) => setForm({ ...form, regex_pattern: e.target.value })} placeholder="Ex: loyer|bailleur" className="font-mono text-sm" />
                </div>
                <div className="space-y-1.5">
                  <Label className="flex items-center gap-1.5"><FlaskConical className="h-3.5 w-3.5" /> Tester le regex</Label>
                  <Input value={testInput} onChange={(e) => setTestInput(e.target.value)} placeholder="Tapez un libellé de transaction…" />
                  {testResult !== null && (
                    <p className={`text-xs font-medium ${testResult === "invalid" ? "text-destructive" : testResult ? "text-green-600 dark:text-green-400" : "text-destructive"}`}>
                      {testResult === "invalid" ? "⚠ Regex invalide" : testResult ? "✓ Match !" : "✗ Pas de match"}
                    </p>
                  )}
                </div>
                <div className="space-y-1.5">
                  <Label>Catégorie</Label>
                  <Select value={form.category_id} onValueChange={(v) => setForm({ ...form, category_id: v })}>
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
                    <Input type="number" value={form.priority} onChange={(e) => setForm({ ...form, priority: parseInt(e.target.value) || 0 })} />
                  </div>
                  <div className="flex items-end gap-2 pb-0.5">
                    <Switch checked={form.is_active} onCheckedChange={(v) => setForm({ ...form, is_active: v })} id="active" />
                    <Label htmlFor="active">Active</Label>
                  </div>
                </div>
                <Button className="w-full" disabled={!form.name || !form.regex_pattern || !form.category_id || saveMutation.isPending} onClick={() => saveMutation.mutate(form)}>
                  {saveMutation.isPending ? "Enregistrement…" : editingId ? "Enregistrer" : "Créer la règle"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}</div>
          ) : !rules?.length ? (
            <div className="flex flex-col items-center justify-center py-12">
              <FileText className="h-10 w-10 text-muted-foreground/50 mb-3" />
              <p className="text-sm text-muted-foreground">Aucune règle. Cliquez sur "Ajouter" pour commencer.</p>
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
                    <TableHead className="text-center">Active</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rules.map((rule: any) => {
                    const cat = catMap.get(rule.category_id);
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
                        <TableCell className="text-center">
                          <Badge variant={rule.is_active ? "default" : "outline"}>{rule.is_active ? "Oui" : "Non"}</Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-1">
                            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => openEdit(rule)}><Pencil className="h-3.5 w-3.5" /></Button>
                            <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive" onClick={() => deleteMutation.mutate(rule.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
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
    </AppLayout>
  );
}

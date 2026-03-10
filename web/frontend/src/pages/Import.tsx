import { useState, useCallback, useMemo } from "react";
import { AppLayout } from "@/components/AppLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Upload, FileUp, CheckCircle2, AlertTriangle, ArrowRight, ArrowLeftRight } from "lucide-react";
import { parseCsv, parseDate, parseAmount, BANK_PRESETS, type ParsedCsv, type BankPreset } from "@/lib/csv-parser";
import { categorize, hashTransaction, detectTransfersAgainstExisting, detectInternalTransfers, attributeByRules } from "@/lib/categorization-engine";
import { useAccounts } from "@/hooks/useAccounts";
import { useCategories } from "@/hooks/useCategories";
import { useRules } from "@/hooks/useRules";
import { useAttributionRules } from "@/hooks/useAttributionRules";
import { useHouseholdMembers } from "@/hooks/useHousehold";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

type Step = "upload" | "mapping" | "preview" | "done";

export default function ImportPage() {
  const { data: accounts } = useAccounts();
  const { data: categories } = useCategories();
  const { data: rules } = useRules();
  const { data: attrRules } = useAttributionRules();
  const { data: householdMembers } = useHouseholdMembers();
  const queryClient = useQueryClient();

  const [step, setStep] = useState<Step>("upload");
  const [csv, setCsv] = useState<ParsedCsv | null>(null);
  const [fileName, setFileName] = useState("");
  const [accountId, setAccountId] = useState("");

  // Mapping state
  const [dateCol, setDateCol] = useState("");
  const [labelCol, setLabelCol] = useState("");
  const [amountCol, setAmountCol] = useState("");
  const [debitCol, setDebitCol] = useState("");
  const [creditCol, setCreditCol] = useState("");
  const [useDebitCredit, setUseDebitCredit] = useState(false);

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
      if (preset) {
        applyPreset(preset, parsed.headers);
      }
      setStep("mapping");
    };
    reader.readAsText(file, "UTF-8");
  }, []);

  const applyPreset = (preset: BankPreset, headers: string[]) => {
    const find = (name: string) => headers.find(h => h.toLowerCase() === name.toLowerCase()) || "";
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
      setDebitCol("");
      setCreditCol("");
    }
  };

  // Build preview data
  const previewData = useMemo(() => {
    if (!csv || !dateCol || !labelCol || (!amountCol && !useDebitCredit)) return [];
    return csv.rows.map((row) => {
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
      const categoryName = categoryId && categories
        ? categories.find(c => c.id === categoryId)?.name || null
        : null;
      return { date, label, amount, categoryId, categoryName, valid: !!date && amount !== null };
    }).filter(r => r.label.trim() !== "");
  }, [csv, dateCol, labelCol, amountCol, debitCol, creditCol, useDebitCredit, rules, categories]);

  // Fetch existing transactions for transfer detection in preview
  const { data: existingTxs } = useQuery({
    queryKey: ["existing-txs-for-transfer", accountId, previewData.length],
    enabled: !!accountId && previewData.length > 0,
    queryFn: async () => {
      const dates = previewData.filter(r => r.valid && r.date).map(r => r.date!);
      if (!dates.length) return [];
      const minDate = new Date(Math.min(...dates.map(d => new Date(d).getTime())) - 30 * 86400000).toISOString().split("T")[0];
      const maxDate = new Date(Math.max(...dates.map(d => new Date(d).getTime())) + 30 * 86400000).toISOString().split("T")[0];
      const { data, error } = await supabase
        .from("transactions")
        .select("id, date, amount, bank_account_id")
        .gte("date", minDate)
        .lte("date", maxDate)
        .limit(1000);
      if (error) throw error;
      return data || [];
    },
  });

  // Detect transfers in preview: cross-DB + within new batch
  const transferIndices = useMemo(() => {
    if (!accountId || !previewData.length) return new Set<number>();
    const indices = new Set<number>();

    const newTxs = previewData
      .map((r, i) => ({ date: r.date || "", amount: r.amount || 0, bank_account_id: accountId, index: i }))
      .filter(r => r.date);

    // Against existing DB transactions
    if (existingTxs?.length) {
      const matches = detectTransfersAgainstExisting(newTxs, existingTxs);
      matches.forEach(m => indices.add(m.newIndex));
    }

    // Within the new batch itself (if importing to multiple accounts – rare but handle)
    const internalSet = detectInternalTransfers(newTxs);
    internalSet.forEach(i => indices.add(i));

    return indices;
  }, [previewData, existingTxs, accountId]);

  const validCount = previewData.filter(r => r.valid).length;
  const invalidCount = previewData.filter(r => !r.valid).length;
  const transferCount = transferIndices.size;

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

      const insertedIds: string[] = [];
      for (let i = 0; i < toInsert.length; i += 500) {
        const batch = toInsert.slice(i, i + 500);
        const { data, error } = await supabase.from("transactions").insert(batch).select("id");
        if (error) throw error;
        if (data) insertedIds.push(...data.map(d => d.id));
      }

      // Post-import: detect transfers against existing
      if (insertedIds.length > 0) {
        const { data: allRecent, error: fetchErr } = await supabase
          .from("transactions")
          .select("id, date, amount, bank_account_id, is_internal_transfer")
          .gte("date", new Date(Math.min(...validRows.map(r => new Date(r.date!).getTime())) - 30 * 86400000).toISOString().split("T")[0])
          .limit(1000);
        if (fetchErr) throw fetchErr;

        const insertedSet = new Set(insertedIds);
        const newTxs = (allRecent || []).filter(t => insertedSet.has(t.id)).map((t, i) => ({
          ...t, index: i, id_real: t.id
        }));
        const existingDbTxs = (allRecent || []).filter(t => !insertedSet.has(t.id));

        const matches = detectTransfersAgainstExisting(
          newTxs.map(t => ({ date: t.date, amount: t.amount, bank_account_id: t.bank_account_id, index: t.index })),
          existingDbTxs
        );

        let transfersDetected = 0;
        for (const match of matches) {
          const newTx = newTxs[match.newIndex];
          if (!newTx) continue;
          // Cross-link both transactions
          await supabase.from("transactions").update({
            is_internal_transfer: true,
            matched_transfer_id: match.existingId,
          }).eq("id", newTx.id_real);
          await supabase.from("transactions").update({
            is_internal_transfer: true,
            matched_transfer_id: newTx.id_real,
          }).eq("id", match.existingId);
          transfersDetected++;
        }

        if (transfersDetected > 0) {
          toast.info(`${transfersDetected} virement(s) interne(s) détecté(s)`);
        }
      }

      // Post-import: attribution cascade
      if (insertedIds.length > 0) {
        const selectedAccount = accounts?.find(a => a.id === accountId);
        const { data: newTxsData } = await supabase
          .from("transactions")
          .select("id, label")
          .in("id", insertedIds);

        if (newTxsData) {
          const toAttribute = new Map<string, string>(); // txId → memberId

          // 1. Personal account → owner
          if (selectedAccount?.account_type !== "joint" && selectedAccount?.owner_user_id) {
            const ownerMember = householdMembers?.find(m => m.user_id === selectedAccount.owner_user_id);
            if (ownerMember) {
              for (const tx of newTxsData) {
                toAttribute.set(tx.id, ownerMember.id);
              }
            }
          }

          // 2. Card identifier matching (overrides personal account for joint)
          const membersWithCards = householdMembers?.filter(m => m.card_identifier) || [];
          if (membersWithCards.length) {
            for (const tx of newTxsData) {
              for (const member of membersWithCards) {
                if (tx.label.toLowerCase().includes(member.card_identifier!.toLowerCase())) {
                  toAttribute.set(tx.id, member.id);
                  break;
                }
              }
            }
          }

          // 3. Attribution rules (regex-based)
          if (attrRules?.length) {
            const sortedRules = [...attrRules].sort((a, b) => b.priority - a.priority);
            for (const tx of newTxsData) {
              if (toAttribute.has(tx.id)) continue; // already attributed
              const memberId = attributeByRules(tx.label, sortedRules as any);
              if (memberId) toAttribute.set(tx.id, memberId);
            }
          }

          // Batch update
          if (toAttribute.size > 0) {
            const byMember = new Map<string, string[]>();
            for (const [txId, memberId] of toAttribute) {
              const list = byMember.get(memberId) || [];
              list.push(txId);
              byMember.set(memberId, list);
            }
            for (const [mId, ids] of byMember) {
              for (let i = 0; i < ids.length; i += 500) {
                await supabase.from("transactions").update({ attributed_to: mId } as any).in("id", ids.slice(i, i + 500));
              }
            }
            toast.info(`${toAttribute.size} transaction(s) attribuée(s) automatiquement`);
          }
        }
      }

      return toInsert.length;
    },
    onSuccess: (count) => {
      toast.success(`${count} transactions importées`);
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      setStep("done");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith(".csv")) handleFile(file);
  }, [handleFile]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }, [handleFile]);

  return (
    <AppLayout title="Import CSV">
      {step === "upload" && (
        <Card>
          <CardContent
            className="flex flex-col items-center justify-center py-16 border-2 border-dashed border-border rounded-lg cursor-pointer hover:border-primary/50 transition-colors"
            onDragOver={e => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => document.getElementById("csv-input")?.click()}
          >
            <Upload className="h-10 w-10 text-muted-foreground/50 mb-4" />
            <h3 className="text-lg font-medium">Importer des relevés</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Glissez-déposez votre fichier CSV ou cliquez pour sélectionner.
            </p>
            <input id="csv-input" type="file" accept=".csv" className="hidden" onChange={handleInputChange} />
          </CardContent>
        </Card>
      )}

      {step === "mapping" && csv && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <FileUp className="h-4 w-4" />
                {fileName} — {csv.rows.length} lignes
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Compte bancaire cible</Label>
                <Select value={accountId} onValueChange={setAccountId}>
                  <SelectTrigger><SelectValue placeholder="Sélectionner un compte" /></SelectTrigger>
                  <SelectContent>
                    {accounts?.map(a => (
                      <SelectItem key={a.id} value={a.id}>{a.name} {a.bank_name ? `(${a.bank_name})` : ""}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {!accounts?.length && <p className="text-xs text-destructive">Créez d'abord un compte dans la page Comptes.</p>}
              </div>

              <div className="space-y-2">
                <Label>Format bancaire</Label>
                <Select onValueChange={(v) => {
                  const preset = BANK_PRESETS[parseInt(v)];
                  if (preset) applyPreset(preset, csv.headers);
                }}>
                  <SelectTrigger><SelectValue placeholder="Détection auto ou choisir…" /></SelectTrigger>
                  <SelectContent>
                    {BANK_PRESETS.map((p, i) => (
                      <SelectItem key={i} value={String(i)}>{p.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Colonne Date</Label>
                  <Select value={dateCol} onValueChange={setDateCol}>
                    <SelectTrigger><SelectValue placeholder="—" /></SelectTrigger>
                    <SelectContent>
                      {csv.headers.map(h => <SelectItem key={h} value={h}>{h}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Colonne Libellé</Label>
                  <Select value={labelCol} onValueChange={setLabelCol}>
                    <SelectTrigger><SelectValue placeholder="—" /></SelectTrigger>
                    <SelectContent>
                      {csv.headers.map(h => <SelectItem key={h} value={h}>{h}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                {!useDebitCredit ? (
                  <div className="space-y-2">
                    <Label>Colonne Montant</Label>
                    <Select value={amountCol} onValueChange={setAmountCol}>
                      <SelectTrigger><SelectValue placeholder="—" /></SelectTrigger>
                      <SelectContent>
                        {csv.headers.map(h => <SelectItem key={h} value={h}>{h}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                ) : (
                  <>
                    <div className="space-y-2">
                      <Label>Colonne Débit</Label>
                      <Select value={debitCol} onValueChange={setDebitCol}>
                        <SelectTrigger><SelectValue placeholder="—" /></SelectTrigger>
                        <SelectContent>
                          {csv.headers.map(h => <SelectItem key={h} value={h}>{h}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Colonne Crédit</Label>
                      <Select value={creditCol} onValueChange={setCreditCol}>
                        <SelectTrigger><SelectValue placeholder="—" /></SelectTrigger>
                        <SelectContent>
                          {csv.headers.map(h => <SelectItem key={h} value={h}>{h}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                  </>
                )}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => { setUseDebitCredit(!useDebitCredit); setAmountCol(""); setDebitCol(""); setCreditCol(""); }}
              >
                {useDebitCredit ? "Utiliser une colonne Montant unique" : "Utiliser Débit / Crédit séparés"}
              </Button>
            </CardContent>
          </Card>

          {/* Preview */}
          {previewData.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-3 flex-wrap">
                  Aperçu
                  <Badge variant="secondary" className="bg-emerald-500/10 text-emerald-600">
                    <CheckCircle2 className="h-3 w-3 mr-1" />{validCount} valides
                  </Badge>
                  {invalidCount > 0 && (
                    <Badge variant="secondary" className="bg-orange-500/10 text-orange-600">
                      <AlertTriangle className="h-3 w-3 mr-1" />{invalidCount} erreurs
                    </Badge>
                  )}
                  {transferCount > 0 && (
                    <Badge variant="secondary" className="bg-blue-500/10 text-blue-600">
                      <ArrowLeftRight className="h-3 w-3 mr-1" />{transferCount} virement(s)
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="rounded-md border overflow-auto max-h-[400px]">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Date</TableHead>
                        <TableHead>Libellé</TableHead>
                        <TableHead className="text-right">Montant</TableHead>
                        <TableHead>Catégorie</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {previewData.slice(0, 50).map((row, i) => (
                        <TableRow key={i} className={`${!row.valid ? "opacity-50" : ""} ${transferIndices.has(i) ? "opacity-60 bg-muted/30" : ""}`}>
                          <TableCell className="whitespace-nowrap">
                            {row.date || "—"}
                            {transferIndices.has(i) && (
                              <Badge variant="outline" className="ml-2 text-[10px] px-1.5 py-0 text-blue-600 border-blue-300">
                                <ArrowLeftRight className="h-2.5 w-2.5 mr-0.5" />Virement
                              </Badge>
                            )}
                          </TableCell>
                          <TableCell className="max-w-[300px] truncate">{row.label}</TableCell>
                          <TableCell className={`text-right font-mono whitespace-nowrap ${row.amount !== null && row.amount < 0 ? "text-destructive" : "text-emerald-600 dark:text-emerald-400"}`}>
                            {row.amount !== null ? `${row.amount > 0 ? "+" : ""}${row.amount.toFixed(2)} €` : "—"}
                          </TableCell>
                          <TableCell>
                            {row.categoryName ? (
                              <Badge variant="secondary" className="text-xs">{row.categoryName}</Badge>
                            ) : (
                              <span className="text-xs text-muted-foreground">—</span>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
                {previewData.length > 50 && (
                  <p className="text-xs text-muted-foreground mt-2">… et {previewData.length - 50} autres lignes</p>
                )}
              </CardContent>
            </Card>
          )}

          <div className="flex justify-between">
            <Button variant="outline" onClick={() => { setStep("upload"); setCsv(null); }}>Annuler</Button>
            <Button
              onClick={() => importMutation.mutate()}
              disabled={!accountId || validCount === 0 || importMutation.isPending}
            >
              {importMutation.isPending ? "Import en cours…" : (
                <>Importer {validCount} transactions <ArrowRight className="h-4 w-4 ml-2" /></>
              )}
            </Button>
          </div>
        </div>
      )}

      {step === "done" && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <CheckCircle2 className="h-10 w-10 text-emerald-500 mb-4" />
            <h3 className="text-lg font-medium">Import terminé !</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Vos transactions ont été importées et catégorisées.
            </p>
            <div className="flex gap-3 mt-6">
              <Button variant="outline" onClick={() => { setStep("upload"); setCsv(null); }}>
                Importer un autre fichier
              </Button>
              <Button onClick={() => window.location.href = "/transactions"}>
                Voir les transactions
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </AppLayout>
  );
}

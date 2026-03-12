import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Eye } from "lucide-react";

function highlightMatch(label: string, pattern: string): React.ReactNode {
  try {
    const re = new RegExp(`(${pattern})`, "gi");
    const parts = label.split(re);
    if (parts.length === 1) return <span className="text-muted-foreground">{label}</span>;
    return (
      <span>
        {parts.map((part, i) =>
          re.test(part) ? (
            <mark key={i} className="bg-primary/20 text-primary font-medium rounded-sm px-0.5">
              {part}
            </mark>
          ) : (
            <span key={i} className="text-muted-foreground">{part}</span>
          )
        )}
      </span>
    );
  } catch {
    return <span className="text-muted-foreground">{label}</span>;
  }
}

interface Props {
  pattern: string;
  enabled: boolean;
}

export function LiveRegexPreview({ pattern, enabled }: Props) {
  const { data: recentTx, isLoading } = useQuery({
    queryKey: ["recent-tx-for-regex"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("transactions")
        .select("id, label")
        .order("date", { ascending: false })
        .limit(20);
      if (error) throw error;
      return data;
    },
    enabled,
    staleTime: 60_000,
  });

  const { matched, unmatched } = useMemo(() => {
    if (!recentTx || !pattern) return { matched: [], unmatched: recentTx || [] };
    try {
      const re = new RegExp(pattern, "i");
      const m: typeof recentTx = [];
      const u: typeof recentTx = [];
      for (const tx of recentTx) {
        (re.test(tx.label) ? m : u).push(tx);
      }
      return { matched: m, unmatched: u };
    } catch {
      return { matched: [], unmatched: recentTx };
    }
  }, [recentTx, pattern]);

  if (isLoading) return <div className="space-y-1.5">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-6 w-full" />)}</div>;

  if (!recentTx?.length) return <p className="text-xs text-muted-foreground">Aucune transaction récente.</p>;

  const matchCount = matched.length;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground flex items-center gap-1">
          <Eye className="h-3 w-3" /> Prévisualisation sur les 20 dernières transactions
        </p>
        {pattern && (
          <Badge variant={matchCount > 0 ? "default" : "outline"} className="text-xs">
            {matchCount}/{recentTx.length} matchs
          </Badge>
        )}
      </div>
      <ScrollArea className="h-48 rounded-md border bg-muted/30 p-2">
        <ul className="space-y-1 text-xs font-mono">
          {matched.map((tx) => (
            <li key={tx.id} className="flex items-center gap-2 rounded px-1.5 py-1 bg-primary/5">
              <span className="shrink-0 text-primary">✓</span>
              {highlightMatch(tx.label, pattern)}
            </li>
          ))}
          {unmatched.map((tx) => (
            <li key={tx.id} className="flex items-center gap-2 rounded px-1.5 py-1 opacity-50">
              <span className="shrink-0">·</span>
              <span>{tx.label}</span>
            </li>
          ))}
        </ul>
      </ScrollArea>
    </div>
  );
}

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Wand2 } from "lucide-react";

type Mode = "contains" | "oneOf" | "startsWith" | "endsWith";

const modes: { key: Mode; label: string; hint: string }[] = [
  { key: "contains", label: "Contient", hint: "Un mot ou expression" },
  { key: "oneOf", label: "Un parmi", hint: "Mots séparés par des virgules" },
  { key: "startsWith", label: "Commence par", hint: "Début du libellé" },
  { key: "endsWith", label: "Finit par", hint: "Fin du libellé" },
];

function escapeRegex(s: string) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function buildPattern(mode: Mode, input: string): string {
  const trimmed = input.trim();
  if (!trimmed) return "";
  switch (mode) {
    case "contains":
      return escapeRegex(trimmed);
    case "oneOf":
      return trimmed
        .split(",")
        .map((w) => escapeRegex(w.trim()))
        .filter(Boolean)
        .join("|");
    case "startsWith":
      return `^${escapeRegex(trimmed)}`;
    case "endsWith":
      return `${escapeRegex(trimmed)}$`;
  }
}

interface Props {
  onApply: (pattern: string) => void;
}

export function RegexBuilder({ onApply }: Props) {
  const [active, setActive] = useState<Mode | null>(null);
  const [input, setInput] = useState("");

  function apply() {
    const pattern = buildPattern(active!, input);
    if (pattern) {
      onApply(pattern);
      setInput("");
      setActive(null);
    }
  }

  return (
    <div className="space-y-2">
      <p className="text-xs text-muted-foreground flex items-center gap-1">
        <Wand2 className="h-3 w-3" /> Assistant regex — cliquez un mode puis saisissez votre texte
      </p>
      <div className="flex flex-wrap gap-1.5">
        {modes.map((m) => (
          <Badge
            key={m.key}
            variant={active === m.key ? "default" : "outline"}
            className="cursor-pointer select-none"
            onClick={() => { setActive(active === m.key ? null : m.key); setInput(""); }}
          >
            {m.label}
          </Badge>
        ))}
        <Badge variant="secondary" className="cursor-default opacity-70">
          🔤 Casse ignorée (auto)
        </Badge>
      </div>
      {active && (
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={modes.find((m) => m.key === active)?.hint}
            className="text-sm"
            onKeyDown={(e) => e.key === "Enter" && apply()}
          />
          <Button size="sm" onClick={apply} disabled={!input.trim()}>
            Insérer
          </Button>
        </div>
      )}
    </div>
  );
}

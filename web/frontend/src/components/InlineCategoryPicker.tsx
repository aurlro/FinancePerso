import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { Check, Pencil } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Category } from "@/hooks/useCategories";

interface Props {
  categoryId: string | null;
  categoryName: string | null;
  categories: Category[];
  onSelect: (categoryId: string | null) => void;
  disabled?: boolean;
}

export function InlineCategoryPicker({ categoryId, categoryName, categories, onSelect, disabled }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild disabled={disabled}>
        <button className="inline-flex items-center gap-1 group text-left cursor-pointer rounded px-1 -mx-1 hover:bg-accent transition-colors">
          {categoryName ? (
            <Badge variant="secondary" className="text-xs">{categoryName}</Badge>
          ) : (
            <span className="text-xs text-muted-foreground">—</span>
          )}
          <Pencil className="h-3 w-3 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-[220px] p-0" align="start">
        <Command>
          <CommandInput placeholder="Rechercher…" />
          <CommandList>
            <CommandEmpty>Aucune catégorie</CommandEmpty>
            <CommandGroup>
              <CommandItem
                onSelect={() => { onSelect(null); setOpen(false); }}
                className="text-muted-foreground"
              >
                Aucune
                {!categoryId && <Check className="ml-auto h-4 w-4" />}
              </CommandItem>
              {categories.map(c => (
                <CommandItem
                  key={c.id}
                  value={c.name}
                  onSelect={() => { onSelect(c.id); setOpen(false); }}
                >
                  {c.color && (
                    <span className="h-3 w-3 rounded-full mr-2 shrink-0" style={{ backgroundColor: c.color }} />
                  )}
                  {c.name}
                  {categoryId === c.id && <Check className={cn("ml-auto h-4 w-4")} />}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

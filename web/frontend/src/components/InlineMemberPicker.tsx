import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { Check, User, Users } from "lucide-react";
import { cn } from "@/lib/utils";

interface Member {
  id: string;
  display_name: string;
  is_active: boolean;
  is_couple: boolean;
}

interface Props {
  memberId: string | null;
  memberName: string | null;
  members: Member[];
  onSelect: (memberId: string | null) => void;
  disabled?: boolean;
}

export function InlineMemberPicker({ memberId, memberName, members, onSelect, disabled }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild disabled={disabled}>
        <button className="inline-flex items-center gap-1 group text-left cursor-pointer rounded px-1 -mx-1 hover:bg-accent transition-colors">
          {memberName ? (
            <Badge variant="secondary" className="text-xs gap-1">
              {/* Show couple icon for couple member, user icon for others */}
              {members.find(m => m.id === memberId)?.is_couple ? (
                <>
                  <span className="text-xs">👫</span>
                  {memberName}
                  <Badge variant="outline" className="ml-1 text-[9px] px-1 py-0">commun</Badge>
                </>
              ) : (
                <>
                  <User className="h-2.5 w-2.5" />
                  {memberName}
                </>
              )}
            </Badge>
          ) : (
            <span className="text-xs text-muted-foreground">—</span>
          )}
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0" align="start">
        <Command>
          <CommandInput placeholder="Rechercher…" />
          <CommandList>
            <CommandEmpty>Aucun membre</CommandEmpty>
            <CommandGroup>
              <CommandItem
                onSelect={() => { onSelect(null); setOpen(false); }}
                className="text-muted-foreground"
              >
                Non attribué
                {!memberId && <Check className="ml-auto h-4 w-4" />}
              </CommandItem>
              {members.map(m => (
                <CommandItem
                  key={m.id}
                  value={m.display_name}
                  onSelect={() => { onSelect(m.id); setOpen(false); }}
                >
                  {m.is_couple ? (
                    <>
                      <span className="text-sm mr-2 shrink-0">👫</span>
                      {m.display_name}
                      <Badge variant="outline" className="ml-1 text-[9px] px-1 py-0">commun</Badge>
                    </>
                  ) : (
                    <>
                      <User className="h-3 w-3 mr-2 shrink-0" />
                      {m.display_name}
                      {!m.is_active && (
                        <Badge variant="outline" className="ml-1 text-[9px] px-1 py-0">fantôme</Badge>
                      )}
                    </>
                  )}
                  {memberId === m.id && <Check className={cn("ml-auto h-4 w-4")} />}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

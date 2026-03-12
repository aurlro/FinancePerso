import { useState } from "react";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useTransactionComments, useAddTransactionComment } from "@/hooks/useTransactionComments";
import { useAuth } from "@/hooks/useAuth";
import { useHousehold } from "@/hooks/useHousehold";
import { Send, Loader2 } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { fr } from "date-fns/locale";

interface Props {
  transactionId: string | null;
  transactionLabel?: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function TransactionComments({ transactionId, transactionLabel, open, onOpenChange }: Props) {
  const { user } = useAuth();
  const { data: profile } = useHousehold();
  const { data: comments, isLoading } = useTransactionComments(open ? transactionId : null);
  const addComment = useAddTransactionComment();
  const [content, setContent] = useState("");

  const handleSubmit = () => {
    if (!content.trim() || !transactionId) return;
    addComment.mutate(
      {
        transactionId,
        content: content.trim(),
        displayName: profile?.display_name || user?.email || "Moi",
      },
      { onSuccess: () => setContent("") }
    );
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="flex flex-col w-full sm:max-w-md">
        <SheetHeader>
          <SheetTitle className="text-base">Commentaires</SheetTitle>
          {transactionLabel && (
            <p className="text-xs text-muted-foreground truncate">{transactionLabel}</p>
          )}
        </SheetHeader>

        <ScrollArea className="flex-1 pr-2 mt-4">
          {isLoading ? (
            <div className="flex justify-center py-8"><Loader2 className="h-5 w-5 animate-spin text-muted-foreground" /></div>
          ) : !comments?.length ? (
            <p className="text-sm text-muted-foreground text-center py-8">Aucun commentaire</p>
          ) : (
            <div className="space-y-3">
              {comments.map((c) => {
                const isMine = c.user_id === user?.id;
                return (
                  <div key={c.id} className={`flex flex-col ${isMine ? "items-end" : "items-start"}`}>
                    <div className={`max-w-[85%] rounded-xl px-3 py-2 text-sm ${isMine ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                      {!isMine && <p className="text-[10px] font-medium opacity-70 mb-0.5">{c.display_name}</p>}
                      <p className="whitespace-pre-wrap break-words">{c.content}</p>
                    </div>
                    <span className="text-[10px] text-muted-foreground mt-0.5 px-1">
                      {formatDistanceToNow(new Date(c.created_at), { addSuffix: true, locale: fr })}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </ScrollArea>

        <div className="flex gap-2 pt-3 border-t mt-auto">
          <Textarea
            placeholder="Ajouter un commentaire…"
            className="min-h-[40px] max-h-[100px] resize-none text-sm"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
            }}
          />
          <Button size="icon" className="shrink-0" onClick={handleSubmit} disabled={!content.trim() || addComment.isPending}>
            {addComment.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
}

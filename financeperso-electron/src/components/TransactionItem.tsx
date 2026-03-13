import * as React from "react"
import { cn } from "@/lib/utils"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { Edit2, Trash2, Check, AlertCircle } from "lucide-react"

export interface TransactionMember {
  id: number
  name: string
  color: string
  emoji: string
  type?: 'primary' | 'secondary'
}

export interface Transaction {
  id: string
  date: string
  description: string
  amount: number
  category?: {
    name: string
    emoji: string
  }
  status?: "pending" | "validated" | "categorized"
  type?: "income" | "expense"
  member?: TransactionMember
}

export interface TransactionItemProps {
  transaction: Transaction
  onEdit?: (transaction: Transaction) => void
  onDelete?: (transaction: Transaction) => void
  onValidate?: (transaction: Transaction) => void
  className?: string
  showMember?: boolean
}

function MemberBadge({ member, size = 'sm' }: { member?: TransactionMember; size?: 'sm' | 'md' }) {
  if (!member) return null

  const sizeClasses = {
    sm: 'w-5 h-5 text-xs',
    md: 'w-7 h-7 text-sm',
  }

  return (
    <div
      className={cn(
        'rounded-full flex items-center justify-center border-2 shrink-0',
        sizeClasses[size]
      )}
      style={{ 
        backgroundColor: `${member.color}20`,
        borderColor: member.color 
      }}
      title={member.name}
    >
      <span>{member.emoji}</span>
    </div>
  )
}

export function TransactionItem({
  transaction,
  onEdit,
  onDelete,
  onValidate,
  className,
  showMember = true,
}: TransactionItemProps) {
  const [isHovered, setIsHovered] = React.useState(false)

  const amount = transaction.amount
  const isIncome = amount > 0 || transaction.type === "income"
  const displayAmount = Math.abs(amount)

  // Format date
  const formattedDate = new Date(transaction.date).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  })

  const statusConfig = {
    pending: { variant: "warning" as const, label: "À valider" },
    validated: { variant: "success" as const, label: "Validé" },
    categorized: { variant: "default" as const, label: "Catégorisé" },
  }

  // Déterminer la couleur de fond basée sur le membre
  const memberBgColor = transaction.member 
    ? `${transaction.member.color}08` // 08 = ~3% opacity
    : undefined

  return (
    <div
      className={cn(
        "group flex items-center justify-between rounded-lg border p-4 transition-colors hover:bg-gray-50",
        transaction.status === "pending" && "border-amber-200 bg-amber-50/30",
        className
      )}
      style={memberBgColor ? { backgroundColor: memberBgColor } : undefined}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Left: Date & Description */}
      <div className="flex items-center gap-4 min-w-0 flex-1">
        {/* Member Badge (if showing) */}
        {showMember && transaction.member && (
          <MemberBadge member={transaction.member} size="md" />
        )}
        <div className="flex flex-col items-center justify-center w-12 text-center">
          <span className="text-xs text-muted-foreground uppercase">
            {new Date(transaction.date).toLocaleDateString("fr-FR", {
              month: "short",
            })}
          </span>
          <span className="text-lg font-semibold text-gray-900">
            {new Date(transaction.date).getDate()}
          </span>
        </div>

        <div className="min-w-0 flex-1">
          <p className="font-medium text-gray-900 truncate">
            {transaction.description}
          </p>
          <div className="flex items-center gap-2 mt-0.5">
            {transaction.category ? (
              <span className="text-sm text-muted-foreground flex items-center gap-1">
                <span>{transaction.category.emoji}</span>
                <span>{transaction.category.name}</span>
                {transaction.member && (
                  <>
                    <span className="mx-1">•</span>
                    <MemberBadge member={transaction.member} size="sm" />
                    <span className="text-xs">{transaction.member.name}</span>
                  </>
                )}
              </span>
            ) : (
              <span className="flex items-center gap-1 text-sm text-amber-600">
                <AlertCircle className="h-3 w-3" />
                Non catégorisé
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Right: Amount & Actions */}
      <div className="flex items-center gap-4">
        {/* Status Badge */}
        {transaction.status && (
          <Badge
            variant={statusConfig[transaction.status].variant}
            className="hidden sm:inline-flex"
          >
            {statusConfig[transaction.status].label}
          </Badge>
        )}

        {/* Amount */}
        <div className="text-right min-w-[100px]">
          <p
            className={cn(
              "font-semibold",
              isIncome ? "text-emerald-600" : "text-red-600"
            )}
          >
            {isIncome ? "+" : "-"}
            {displayAmount.toFixed(2)}€
          </p>
        </div>

        {/* Hover Actions */}
        <div
          className={cn(
            "flex items-center gap-1 transition-opacity",
            isHovered ? "opacity-100" : "opacity-0"
          )}
        >
          {onValidate && transaction.status === "pending" && (
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-emerald-600 hover:bg-emerald-50"
              onClick={() => onValidate(transaction)}
              title="Valider"
            >
              <Check className="h-4 w-4" />
            </Button>
          )}
          {onEdit && (
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-gray-600 hover:bg-gray-100"
              onClick={() => onEdit(transaction)}
              title="Modifier"
            >
              <Edit2 className="h-4 w-4" />
            </Button>
          )}
          {onDelete && (
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-red-600 hover:bg-red-50"
              onClick={() => onDelete(transaction)}
              title="Supprimer"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

// Transaction list component
export interface TransactionListProps {
  transactions: Transaction[]
  onEdit?: (transaction: Transaction) => void
  onDelete?: (transaction: Transaction) => void
  onValidate?: (transaction: Transaction) => void
  className?: string
  emptyMessage?: string
}

export function TransactionList({
  transactions,
  onEdit,
  onDelete,
  onValidate,
  className,
  emptyMessage = "Aucune transaction",
}: TransactionListProps) {
  if (transactions.length === 0) {
    return (
      <div className="rounded-lg border border-dashed p-8 text-center text-muted-foreground">
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className={cn("space-y-2", className)}>
      {transactions.map((transaction) => (
        <TransactionItem
          key={transaction.id}
          transaction={transaction}
          onEdit={onEdit}
          onDelete={onDelete}
          onValidate={onValidate}
        />
      ))}
    </div>
  )
}

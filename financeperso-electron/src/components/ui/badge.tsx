import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-emerald-100 text-emerald-700 hover:bg-emerald-200",
        secondary:
          "border-transparent bg-gray-100 text-gray-700 hover:bg-gray-200",
        success:
          "border-transparent bg-emerald-50 text-emerald-600 hover:bg-emerald-100",
        warning:
          "border-transparent bg-amber-50 text-amber-600 hover:bg-amber-100",
        danger:
          "border-transparent bg-red-50 text-red-600 hover:bg-red-100",
        info:
          "border-transparent bg-blue-50 text-blue-600 hover:bg-blue-100",
        outline: "text-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }

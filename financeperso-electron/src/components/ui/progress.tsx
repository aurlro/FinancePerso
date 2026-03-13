import * as React from "react"
import { cn } from "@/lib/utils"
import { cva, type VariantProps } from "class-variance-authority"

const progressVariants = cva(
  "h-full transition-all duration-300 ease-out rounded-full",
  {
    variants: {
      variant: {
        default: "bg-emerald-500",
        success: "bg-emerald-500",
        warning: "bg-amber-500",
        danger: "bg-red-500",
        info: "bg-blue-500",
        secondary: "bg-gray-500",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface ProgressProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof progressVariants> {
  value: number
  max?: number
  showLabel?: boolean
  size?: "sm" | "default" | "lg"
}

function Progress({
  className,
  value,
  max = 100,
  variant,
  showLabel = false,
  size = "default",
  ...props
}: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
  
  const sizeClasses = {
    sm: "h-1.5",
    default: "h-2.5",
    lg: "h-4",
  }

  // Auto-variant based on percentage if not specified
  const autoVariant = !variant
    ? percentage >= 90
      ? "danger"
      : percentage >= 75
      ? "warning"
      : "success"
    : variant

  return (
    <div className={cn("w-full", className)} {...props}>
      <div
        className={cn(
          "w-full overflow-hidden rounded-full bg-gray-100",
          sizeClasses[size]
        )}
      >
        <div
          className={cn(progressVariants({ variant: autoVariant }))}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>
      {showLabel && (
        <div className="mt-1 flex justify-between text-xs text-muted-foreground">
          <span>{value.toLocaleString()}€</span>
          <span>{percentage.toFixed(0)}%</span>
        </div>
      )}
    </div>
  )
}

export { Progress, progressVariants }

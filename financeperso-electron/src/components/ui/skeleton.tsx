import { cn } from "@/lib/utils"
import { cva, type VariantProps } from "class-variance-authority"

const skeletonVariants = cva(
  "animate-pulse bg-muted",
  {
    variants: {
      variant: {
        default: "rounded-md",
        circle: "rounded-full",
        card: "rounded-lg",
      },
      size: {
        default: "h-4 w-full",
        sm: "h-3 w-3/4",
        lg: "h-6 w-full",
        xl: "h-8 w-full",
        full: "h-full w-full",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface SkeletonProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof skeletonVariants> {}

function Skeleton({ className, variant, size, ...props }: SkeletonProps) {
  return (
    <div
      className={cn(skeletonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Skeleton, skeletonVariants }

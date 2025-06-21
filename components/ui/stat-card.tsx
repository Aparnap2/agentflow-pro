import { Card, CardContent } from "@/components/ui/card"
import type { LucideIcon } from "lucide-react"

interface StatCardProps {
  title: string
  value: string | number
  description: string
  icon: LucideIcon
  trend?: string
  color?: "blue" | "green" | "purple" | "orange" | "red"
}

export function StatCard({ title, value, description, icon: Icon, trend, color = "blue" }: StatCardProps) {
  const colorClasses = {
    blue: "from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 border-blue-200 text-blue-600",
    green: "from-green-50 to-green-100 dark:from-green-950 dark:to-green-900 border-green-200 text-green-600",
    purple: "from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900 border-purple-200 text-purple-600",
    orange: "from-orange-50 to-orange-100 dark:from-orange-950 dark:to-orange-900 border-orange-200 text-orange-600",
    red: "from-red-50 to-red-100 dark:from-red-950 dark:to-red-900 border-red-200 text-red-600",
  }

  return (
    <Card className={`bg-gradient-to-br ${colorClasses[color]}`}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium opacity-70">{title}</p>
            <p className="text-3xl font-bold">{value}</p>
            <p className="text-xs opacity-60 mt-1">{description}</p>
            {trend && <p className="text-xs font-medium mt-1">{trend}</p>}
          </div>
          <Icon className="w-8 h-8 opacity-80" />
        </div>
      </CardContent>
    </Card>
  )
}

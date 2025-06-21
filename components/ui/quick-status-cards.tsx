import { Card, CardContent } from "@/components/ui/card"
import { TrendingUp, TrendingDown, AlertCircle, CheckCircle, Clock, DollarSign } from "lucide-react"
import type { SystemMetrics } from "@/types/monitoring"

interface QuickStatusCardsProps {
  metrics: SystemMetrics
}

export function QuickStatusCards({ metrics }: QuickStatusCardsProps) {
  const cards = [
    {
      title: "Active Actions",
      value: metrics.activeActions,
      total: metrics.totalActions,
      icon: Clock,
      color: "blue",
      trend: "+12%",
      trendUp: true,
    },
    {
      title: "Success Rate",
      value: `${metrics.successRate}%`,
      icon: CheckCircle,
      color: "green",
      trend: "+2.3%",
      trendUp: true,
    },
    {
      title: "Avg Execution",
      value: metrics.avgExecutionTime,
      icon: TrendingUp,
      color: "purple",
      trend: "-15s",
      trendUp: true,
    },
    {
      title: "Today's Cost",
      value: `$${metrics.totalCost.toFixed(2)}`,
      icon: DollarSign,
      color: "orange",
      trend: "-8%",
      trendUp: false,
    },
    {
      title: "API Calls",
      value: metrics.apiCallsToday.toLocaleString(),
      icon: AlertCircle,
      color: "red",
      trend: "+23%",
      trendUp: true,
    },
    {
      title: "Tokens Used",
      value: `${(metrics.tokensUsedToday / 1000).toFixed(1)}K`,
      icon: TrendingUp,
      color: "indigo",
      trend: "+5%",
      trendUp: true,
    },
  ]

  const getColorClasses = (color: string) => {
    const colors = {
      blue: "bg-blue-50 dark:bg-blue-950 text-blue-600 border-blue-200",
      green: "bg-green-50 dark:bg-green-950 text-green-600 border-green-200",
      purple: "bg-purple-50 dark:bg-purple-950 text-purple-600 border-purple-200",
      orange: "bg-orange-50 dark:bg-orange-950 text-orange-600 border-orange-200",
      red: "bg-red-50 dark:bg-red-950 text-red-600 border-red-200",
      indigo: "bg-indigo-50 dark:bg-indigo-950 text-indigo-600 border-indigo-200",
    }
    return colors[color as keyof typeof colors] || colors.blue
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {cards.map((card) => (
        <Card key={card.title} className={`border ${getColorClasses(card.color)}`}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <card.icon className="w-4 h-4" />
              <div className="flex items-center gap-1">
                {card.trendUp ? (
                  <TrendingUp className="w-3 h-3 text-green-500" />
                ) : (
                  <TrendingDown className="w-3 h-3 text-red-500" />
                )}
                <span className={`text-xs ${card.trendUp ? "text-green-600" : "text-red-600"}`}>{card.trend}</span>
              </div>
            </div>
            <div>
              <p className="text-lg font-bold">{card.value}</p>
              <p className="text-xs opacity-70">{card.title}</p>
              {card.total && <p className="text-xs opacity-50">of {card.total} total</p>}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
